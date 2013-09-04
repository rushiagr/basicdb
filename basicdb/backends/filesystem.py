import errno
import glob
import md5
import os
import re
import shutil
import time

import basicdb
import basicdb.backends
import basicdb.sqlparser as sqlparser

class FileSystemBackend(basicdb.backends.StorageBackend):
    _domains = {}

    def __init__(self, base_dir='/tmp/mystor'):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def _md5_hex(self, s):
        return md5.md5(s).hexdigest()

    def _attr_value_filename(self, domain_name, item_name, attr_name, attr_value):
        return os.path.join(self._attr_dir(domain_name, item_name, attr_name),
                            self._md5_hex(attr_value))

    def _reset(self):
        # What to put here as some sort of safeguard?
        try:
            shutil.rmtree(self.base_dir)
        except OSError, e:
            if e.errno == errno.ENOENT:
                pass
            else:
                raise
        os.mkdir(self.base_dir)

    def _domain_dir(self, domain_name):
        return os.path.join(self.base_dir, domain_name)

    def _item_dir(self, domain_name, item_name):
        return os.path.join(self._domain_dir(domain_name), item_name)

    def _attr_dir(self, domain_name, item_name, attr_name):
        return os.path.join(self._item_dir(domain_name, item_name), attr_name)

    def create_domain(self, domain_name):
        try:
            os.mkdir(self._domain_dir(domain_name))
        except OSError, e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

    def delete_domain(self, domain_name):
        try:
            shutil.rmtree(self._domain_dir(domain_name))
        except OSError, e:
            if e.errno == errno.ENOENT:
                pass
            else:
                raise

    def list_domains(self):
        return [d.split('/')[-1] for d in glob.glob(os.path.join(self.base_dir, '*'))]

    def delete_attribute_all(self, domain_name, item_name, attr_name):
        attr_dir = self._attr_dir(domain_name, item_name, attr_name)
        if os.path.exists(attr_dir):
            shutil.rmtree(attr_dir)

    def delete_attribute_value(self, domain_name, item_name, attr_name, attr_value):
        try:
            os.unlink(self._attr_value_filename(domain_name, item_name, attr_name, attr_value))
        except OSError, e:
            if e.errno == errno.ENOENT:
                pass
            else:
                raise
        try:
            os.rmdir(self._attr_dir(domain_name, item_name, attr_name))
        except OSError, e:
            if e.errno in (errno.ENOTEMPTY, errno.ENOENT):
                pass
            else:
                raise

    def add_attribute_value(self, domain_name, item_name, attr_name, attr_value):
        try:
            os.makedirs(self._attr_dir(domain_name, item_name, attr_name))
        except OSError, e:
            if e.errno == errno.EEXIST:
                pass

        with file(self._attr_value_filename(domain_name, item_name,
                                            attr_name, attr_value), 'w') as fp:
            fp.write(attr_value)

    def get_attributes(self, domain_name, item_name):
        retval = {}
        for attr_dir in glob.glob(os.path.join(self._item_dir(domain_name, item_name), '*')):
            attr_name = attr_dir.split('/')[-1]
            retval[attr_name] = set()
            for attr_value_file in glob.glob(os.path.join(attr_dir, '*')):
                with file(attr_value_file, 'r') as fp:
                    retval[attr_name].add(fp.read())
        return retval

    def _get_all_items_names(self, domain_name):
        return [d.split('/')[-1] for d in glob.glob(os.path.join(self._domain_dir(domain_name), '*'))]

    def _get_all_items(self, domain_name):
        retval = {}
        for item_name in self._get_all_items_names(domain_name):
            retval[item_name] = self.get_attributes(domain_name, item_name)
        return retval

    def select(self, sql_expr):
        parsed = sqlparser.simpleSQL.parseString(sql_expr)
        domain_name = parsed.tables[0] # Only one table supported
        desired_attributes = parsed.columns

        filters = []
        if parsed.where:
            for clause in parsed.where[0][1:]:
                col_name, rel, rval = clause
                if rel == '=':
                    filters += [lambda x:any([f == rval for f in x.get(col_name, [])])]
                elif rel == 'like':
                    regex = re.compile(rval.replace('_', '.').replace('%', '.*'))
                    filters += [lambda x:any([regex.match(f) for f in x.get(col_name, [])])]

        matching_items = {}
        for item, item_attrs in self._get_all_items(domain_name).iteritems():
            if all(f(item_attrs) for f in filters):
                matching_items[item] = item_attrs

        if desired_attributes == '*':
            result = matching_items
        else:
            result = {}

            for item, item_attrs in matching_items.iteritems():
                matching_attributes = dict([(attr_name, attr_values) for attr_name, attr_values in item_attrs.iteritems() if attr_name in desired_attributes.asList()])
                if matching_attributes:
                    result[item] = matching_attributes

        return result

    def domain_metadata(self, domain_name):
        return {"ItemCount": len(self._get_all_items_names(domain_name)),
                "ItemNamesSizeBytes": '120',
                "AttributeNameCount": '12',
                "AttributeNamesSizeBytes": '120',
                "AttributeValueCount": '120',
                "AttributeValuesSizeBytes": '100020',
                "Timestamp": str(int(time.time()))}

    def check_expectation(self, domain_name, item_name, expectation):
        attr_name, attr_value_expected = expectation

        attrs = self.get_attributes(domain_name, item_name)

        attr_value = attrs.get(attr_name, False)

        if attr_value == False:
            if attr_value_expected == False:
                return True
            return False
        elif attr_value_expected == True:
            return True
        else:
            return attr_value_expected in attr_value


driver = FileSystemBackend()