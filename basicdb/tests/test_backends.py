import testtools as unittest

import basicdb.backends
import basicdb.exceptions as exc

class BaseStorageBackendTests(unittest.TestCase):
    def test_create_domain_raises_not_implemented(self):
        backend = basicdb.backends.StorageBackend()
        self.assertRaises(NotImplementedError, backend.create_domain, "owner", "domain-name")

    def test_delete_domain_raises_not_implemented(self):
        backend = basicdb.backends.StorageBackend()
        self.assertRaises(NotImplementedError, backend.delete_domain, "owner", "domain-name")

    def test_domain_metadata_raises_not_implemented(self):
        backend = basicdb.backends.StorageBackend()
        self.assertRaises(NotImplementedError, backend.domain_metadata, "owner", "domain-name")

    def test_list_domains_raises_not_implemented(self):
        backend = basicdb.backends.StorageBackend()
        self.assertRaises(NotImplementedError, backend.list_domains, "owner")

    def test_add_attribute_value_raises_not_implemented(self):
        backend = basicdb.backends.StorageBackend()
        self.assertRaises(NotImplementedError, backend.add_attribute_value, "owner", "domain", "item", "attrname", "attrvalue")

    def test_delete_attribute_all_raises_not_implemented(self):
        backend = basicdb.backends.StorageBackend()
        self.assertRaises(NotImplementedError, backend.delete_attribute_all, "owner", "domain", "item", "attrname")

    def test_delete_attribute_value_raises_not_implemented(self):
        backend = basicdb.backends.StorageBackend()
        self.assertRaises(NotImplementedError, backend.delete_attribute_value, "owner", "domain", "item", "attrname", "attrvalue")

    def test_put_attributes_raises_exception_if_expectations_are_not_met(self):
        self.check_expectations_call_args = []
        self.add_attributes_call_args = []
        self.replace_attributes_call_args = []

        class TestStoreBackend(basicdb.backends.StorageBackend):
            def check_expectations(self2, *args):
                False

        backend = TestStoreBackend()
        self.assertRaises(basicdb.exceptions.ConditionalCheckFailed,
                          backend.put_attributes, "owner", "domain", "item",
                          {"attr1": set(["attr1val1", "attr1val2"])},
                          {"attr2": set(["attr2val1"])},
                          [("attr3", True)])

    def test_put_attributes(self):
        self.check_expectations_call_args = []
        self.add_attributes_call_args = []
        self.replace_attributes_call_args = []

        class TestStoreBackend(basicdb.backends.StorageBackend):
            def check_expectations(self2, *args):
                self.check_expectations_call_args += [args]
                return True

            def add_attributes(self2, *args):
                self.assertTrue(self.check_expectations_call_args,
                                "check_expectations was not called before adding attributes")
                self.add_attributes_call_args += [args]

            def replace_attributes(self2, *args):
                self.assertTrue(self.check_expectations_call_args,
                                "check_expectations was not called before replacing attributes")
                self.replace_attributes_call_args += [args]

        backend = TestStoreBackend()
        backend.put_attributes("owner", "domain", "item",
                               {"attr1": set(["attr1val1", "attr1val2"])},
                               {"attr2": set(["attr2val1"])},
                               [("attr3", True)])
        self.assertIn(("owner", "domain", "item", [("attr3", True)]),
                      self.check_expectations_call_args)
        self.assertIn(("owner", "domain", "item", {"attr1": set(["attr1val1", "attr1val2"])}),
                      self.add_attributes_call_args)
        self.assertIn(("owner", "domain", "item", {"attr2": set(["attr2val1"])}),
                      self.replace_attributes_call_args)

    def test_batch_put_attributes(self):
        self.put_attributes_call_args = []
        class TestStoreBackend(basicdb.backends.StorageBackend):
            def put_attributes(self2, *args):
                self.put_attributes_call_args += [args]

        backend = TestStoreBackend()
        backend.batch_put_attributes("owner", "domain",
                                     {"item1": {"attr1": set(["attr1val1", "attr1val2"])}},
                                     {"item2": {"attr2": set(["attr2val1"])}})

        self.assertIn(("owner", "domain", "item1", {"attr1": set(["attr1val1", "attr1val2"])}, {}),
                      self.put_attributes_call_args)
        self.assertIn(("owner", "domain", "item2", {}, {"attr2": set(["attr2val1"])}),
                      self.put_attributes_call_args)

    def test_batch_delete_attributes(self):
        self.delete_attributes_call_args = []
        class TestStoreBackend(basicdb.backends.StorageBackend):
            def delete_attributes(self2, *args):
                self.delete_attributes_call_args += [args]

        backend = TestStoreBackend()
        backend.batch_delete_attributes("owner", "domain",
                                        {"item1": {"attr1": set(["attr1val1", "attr1val2"])},
                                        "item2": {"attr2": set(["attr2val1"])}})

        self.assertIn(("owner", "domain", "item1", {"attr1": set(["attr1val1", "attr1val2"])}),
                      self.delete_attributes_call_args)
        self.assertIn(("owner", "domain", "item2", {"attr2": set(["attr2val1"])}),
                      self.delete_attributes_call_args)

    def test_get_attributes_raises_not_implemented(self):
        backend = basicdb.backends.StorageBackend()
        self.assertRaises(NotImplementedError, backend.get_attributes, "owner", "domain", "item")

    def test_add_attributes(self):
        self.add_attribute_call_args = []

        class TestStoreBackend(basicdb.backends.StorageBackend):
            def add_attribute(self2, *args):
                self.add_attribute_call_args += [args]

        backend = TestStoreBackend()
        backend.add_attributes("owner", "domain", "item", {"attr1": set(["attr1val1", "attr1val2"]),
                                                      "attr2": set(["attr2val1"])})

        self.assertEquals(len(self.add_attribute_call_args), 2)
        self.assertIn(("owner", "domain", "item", "attr1", set(["attr1val1", "attr1val2"])),
                      self.add_attribute_call_args)
        self.assertIn(("owner", "domain", "item", "attr2", set(["attr2val1"])),
                      self.add_attribute_call_args)

    def test_add_attribute(self):
        self.add_attribute_value_call_args = []

        class TestStoreBackend(basicdb.backends.StorageBackend):
            def add_attribute_value(self2, *args):
                self.add_attribute_value_call_args += [args]

        backend = TestStoreBackend()
        backend.add_attribute("owner", "domain", "item", "attr1", set(["attr1val1", "attr1val2"]))
        self.assertIn(("owner", "domain", "item", "attr1", "attr1val1"),
                      self.add_attribute_value_call_args)
        self.assertIn(("owner", "domain", "item", "attr1", "attr1val2"),
                      self.add_attribute_value_call_args)


    def test_replace_attributes(self):
        self.replace_attribute_call_args = []

        class TestStoreBackend(basicdb.backends.StorageBackend):
            def replace_attribute(self2, *args):
                self.replace_attribute_call_args += [args]

        backend = TestStoreBackend()
        backend.replace_attributes("owner", "domain", "item", {"attr1": set(["attr1val1", "attr1val2"]),
                                                               "attr2": set(["attr2val1"])})

        self.assertEquals(len(self.replace_attribute_call_args), 2)
        self.assertIn(("owner", "domain", "item", "attr1", set(["attr1val1", "attr1val2"])),
                      self.replace_attribute_call_args)
        self.assertIn(("owner", "domain", "item", "attr2", set(["attr2val1"])),
                      self.replace_attribute_call_args)

    def test_replace_attribute(self):
        self.delete_attributes_call_args = []
        self.add_attribute_call_args = []

        class TestStoreBackend(basicdb.backends.StorageBackend):
            def delete_attributes(self2, *args):
                self.delete_attributes_call_args += [args]

            def add_attribute(self2, *args):
                self.assertIsNot(self.delete_attributes_call_args, None,
                                 "Attribute wasn't deleted first")
                self.add_attribute_call_args += [args]

        backend = TestStoreBackend()
        backend.replace_attribute("owner", "domain", "item", "attr1", set(["attr1val1", "attr1val2"]))

        self.assertIn(("owner", "domain", "item", {"attr1": set([basicdb.AllAttributes])}), self.delete_attributes_call_args)
        self.assertIn(("owner", "domain", "item", "attr1", set(["attr1val1", "attr1val2"])),
                      self.add_attribute_call_args)

    def test_delete_attributes(self):
        self.delete_attribute_call_args = []

        class TestStoreBackend(basicdb.backends.StorageBackend):
            def delete_attribute(self2, *args):
                self.delete_attribute_call_args += [args]

        backend = TestStoreBackend()
        backend.delete_attributes("owner", "domain", "item", {"attr1": set(["attr1val1", "attr1val2"])})

        self.assertIn(("owner", "domain", "item", "attr1", set(["attr1val1", "attr1val2"])),
                      self.delete_attribute_call_args)

    def test_delete_attribute_only_calls_delete_all_if_all_should_be_removed(self):
        self.delete_attribute_all_call_args = []
        class TestStoreBackend(basicdb.backends.StorageBackend):
            def delete_attribute_all(self2, *args):
                self.delete_attribute_all_call_args += [args]

            def delete_attribute_value(self2, *args):
                self.fail("Should not have called delete_attribute_value")

        backend = TestStoreBackend()
        backend.delete_attribute("owner", "domain", "item", "attr1", set(["attr1val1", basicdb.AllAttributes, "attr1val2"]))
        self.assertEquals([("owner", "domain", "item", "attr1")], self.delete_attribute_all_call_args)

    def test_delete_attribute(self):
        self.delete_attribute_value_call_args = []
        class TestStoreBackend(basicdb.backends.StorageBackend):
            def delete_attribute_all(self2, *args):
                self.fail("Should not have called delete_attribute_all")

            def delete_attribute_value(self2, *args):
                self.delete_attribute_value_call_args += [args]

        backend = TestStoreBackend()
        backend.delete_attribute("owner", "domain", "item", "attr1", set(["attr1val1", "attr1val2"]))
        self.assertIn(("owner", "domain", "item", "attr1", "attr1val1"), self.delete_attribute_value_call_args)
        self.assertIn(("owner", "domain", "item", "attr1", "attr1val2"), self.delete_attribute_value_call_args)

    def test_select_raises_not_implemented(self):
        backend = basicdb.backends.StorageBackend()
        self.assertRaises(NotImplementedError, backend.select, "owner", "SELECT somethign FROM somewhere")

    def test_check_expectation_raises_not_implemented(self):
        backend = basicdb.backends.StorageBackend()
        self.assertRaises(NotImplementedError,
                          backend.check_expectation, "owner", 'domain', 'item', ('foo', 'bar'))

    def test_check_expectations(self):
        self.check_expectation_call_args = []
        class TestStoreBackend(basicdb.backends.StorageBackend):
            def check_expectation(self2, *args):
                self.check_expectation_call_args += [args]

        backend = TestStoreBackend()
        backend.check_expectations("owner", "domain", "item", [("attr1", "val1"), ("attr1", "val2"), ("attr2", "val3")])
        self.assertIn(("owner", "domain", "item", ("attr1", "val1")), self.check_expectation_call_args)
        self.assertIn(("owner", "domain", "item", ("attr1", "val2")), self.check_expectation_call_args)
        self.assertIn(("owner", "domain", "item", ("attr2", "val3")), self.check_expectation_call_args)


class _GenericBackendDriverTest(object):
    def test_create_list_delete_domain(self):
        self.assertEquals(self.backend.list_domains("owner"), [])

        self.backend.create_domain("owner", "domain1")
        self.assertEquals(set(self.backend.list_domains("owner")), set(["domain1"]))

        self.backend.create_domain("owner", "domain2")
        self.assertEquals(set(self.backend.list_domains("owner")), set(["domain1", "domain2"]))

        self.backend.delete_domain("owner", "domain1")
        self.assertEquals(set(self.backend.list_domains("owner")), set(["domain2"]))

        self.backend.delete_domain("owner", "domain2")
        self.assertEquals(self.backend.list_domains("owner"), [])

    def test_domain_metadata(self):
        self.backend.create_domain("owner", "domain1")
        self.backend.domain_metadata("owner", "domain1")

    def test_batch_put_attributes(self):
        self.backend.create_domain("owner", "domain1")
        self.backend.batch_put_attributes("owner", "domain1",
                                          {"item1": {"a": set(["b", "c"])},
                                           "item2": {"d": set(["e", "f"])}},
                                          {})

        self.assertEquals(self.backend.get_attributes("owner", "domain1", "item1"),
                          {"a": set(["b", "c"])})
        self.assertEquals(self.backend.get_attributes("owner", "domain1", "item2"),
                          {"d": set(["e", "f"])})

        self.backend.batch_put_attributes("owner", "domain1",
                                          {"item1": {"a": set(["e"])}},
                                          {"item2": {"d": set(["a", "b"])}})

        self.assertEquals(self.backend.get_attributes("owner", "domain1", "item1"),
                          {"a": set(["b", "c", "e"])})
        self.assertEquals(self.backend.get_attributes("owner", "domain1", "item2"),
                          {"d": set(["a", "b"])})

    def test_put_get_attributes(self):
        self.backend.create_domain("owner", "domain1")
        self.backend.put_attributes("owner", "domain1", "item1",
                                    {"a": set(["b", "c"])},
                                    {"d": set(["e"])})

        self.assertEquals(self.backend.get_attributes("owner", "domain1", "item1"),
                          {"a": set(["b", "c"]), "d": set(["e"])})

        self.backend.put_attributes("owner", "domain1", "item1",
                                    {"d": set(["f", "g"])},
                                    {"a": set(["h"])})

        self.assertEquals(self.backend.get_attributes("owner", "domain1", "item1"),
                          {"a": set(["h"]), "d": set(["e", "f", "g"])})

    def test_delete_attributes_non_existant_item(self):
        self.backend.create_domain("owner", "domain1")
        self.backend.delete_attributes("owner", "domain1", "item1",
                                       {"a": set(["b"]),
                                        "b": set([basicdb.AllAttributes])})

    def test_delete_attributes_non_existant_domain(self):
        self.backend.delete_attributes("owner", "domain1", "item1",
                                       {"a": set(["b"]),
                                        "b": set([basicdb.AllAttributes])})

    def test_delete_attributes(self):
        self.backend.create_domain("owner", "domain1")
        self.backend.put_attributes("owner", "domain1", "item1",
                                    {"a": set(["b", "c"]),
                                     "d": set(["e"]),
                                     "f": set(["g"])},
                                     {})

        self.backend.delete_attributes("owner", "domain1", "item1",
                                       {"a": set([basicdb.AllAttributes]),
                                        "d": set(["f"]),
                                        "f": set(["g"])})

        self.assertEquals(self.backend.get_attributes("owner", "domain1", "item1"),
                          {"d": set(["e"])})

    def test_batch_delete_attributes(self):
        self.backend.create_domain("owner", "domain1")
        self.backend.put_attributes("owner", "domain1", "item1",
                                    {"a": set(["b", "c"]),
                                     "d": set(["e"]),
                                     "f": set(["g"])},
                                     {})

        self.backend.put_attributes("owner", "domain1", "item2",
                                    {"h": set(["i"]),
                                     "j": set(["k"])},
                                     {})

        self.backend.batch_delete_attributes("owner", "domain1",
                                             {"item1":
                                               {"a": set([basicdb.AllAttributes]),
                                                "d": set(["f"]),
                                                "f": set(["g"])},
                                              "item2":
                                               {"j": set(["k"])}})

        self.assertEquals(self.backend.get_attributes("owner", "domain1", "item1"),
                          {"d": set(["e"])})

        self.assertEquals(self.backend.get_attributes("owner", "domain1", "item2"),
                          {"h": set(["i"])})

    def _load_sample_query_data_set(self):
        self.backend.create_domain('owner', 'mydomain')
        self.backend.put_attributes('owner', 'mydomain', "0385333498",
                                    {"Title": set(["The Sirens of Titan"]),
                                     "Author": set(["Kurt Vonnegut"]),
                                     "Year": set(["1959"]),
                                     "Pages": set(["00336"]),
                                     "Keyword": set(["Book", "Paperback"]),
                                     "Rating": set(["*****", "5 stars", "Excellent"])}, {})

        self.backend.put_attributes('owner', 'mydomain', "0802131786",
                                    {"Title": set(["Tropic of Cancer"]),
                                     "Author": set(["Henry Miller"]),
                                     "Year": set(["1934"]),
                                     "Pages": set(["00318"]),
                                     "Keyword": set(["Book"]),
                                     "Rating": set(["****"])}, {})

        self.backend.put_attributes('owner', 'mydomain', "1579124585",
                                    {"Title": set(["The Right Stuff"]),
                                     "Author": set(["Tom Wolfe"]),
                                     "Year": set(["1979"]),
                                     "Pages": set(["00304"]),
                                     "Keyword": set(["Book", "Hardcover", "American"]),
                                     "Rating": set(["****", "4 stars"])}, {})

        self.backend.put_attributes('owner', 'mydomain', "B000T9886K",
                                    {"Title": set(["In Between"]),
                                     "Author": set(["Paul Van Dyk"]),
                                     "Year": set(["2007"]),
                                     "Keyword": set(["CD", "Trance"]),
                                     "Rating": set(["4 stars"])}, {})

        self.backend.put_attributes('owner', 'mydomain', "B00005JPLW",
                                    {"Title": set(["300"]),
                                     "Author": set(["Zack Snyder"]),
                                     "Year": set(["2007"]),
                                     "Keyword": set(["DVD", "Action", "Frank Miller"]),
                                     "Rating": set(["***", "3 stars", "Not bad"])}, {})

        self.backend.put_attributes('owner', 'mydomain', "B000SF3NGK",
                                    {"Title": set(["Heaven's Gonna Burn Your Eyes"]),
                                     "Author": set(["Thievery Corporation"]),
                                     "Year": set(["2002"]),
                                     "Rating": set(["*****"])}, {})

    def test_select2(self):
        self._load_sample_query_data_set()
        def f(expr, items, ordered=False):
            if not ordered:
                wrap = set
            else:
                wrap = list

            self.assertEquals(wrap(self.backend.select_wrapper("owner", expr)[0]),
                              wrap(items), expr)

        f("select * from mydomain where Title = 'The Right Stuff'",
          ["1579124585"])

        f("select * from mydomain where Year > '1985'",
          ["B000T9886K", "B00005JPLW", "B000SF3NGK"])

        f("select * from mydomain where Rating like '****%'",
          ["0385333498", "1579124585", "0802131786", "B000SF3NGK"])

        f("select * from mydomain where Pages < '00320'",
          ["1579124585", "0802131786"])

        f("select * from mydomain where Year > '1975' and Year < '2008'",
          ["1579124585", "B000T9886K", "B00005JPLW", "B000SF3NGK"])

        f("select * from mydomain where Year between '1975' and '2008'",
          ["1579124585", "B000T9886K", "B00005JPLW", "B000SF3NGK"])

        f("select * from mydomain where Rating = '***' or Rating = '*****'",
          ["0385333498", "B00005JPLW", "B000SF3NGK"])

        f("select * from mydomain where (Year > '1950' and Year < '1960') "
          "or Year like '193%' or Year = '2007'",
          ["0385333498", "0802131786", "B000T9886K", "B00005JPLW"])

        f("select * from mydomain where (Year > '1950' and Year < '1960') "
          "or Year like '193%' or Year = '2007'",
          ["0385333498", "0802131786", "B000T9886K", "B00005JPLW"])

        f("select * from mydomain where Rating = '4 stars' or Rating = '****'",
          ["1579124585", "0802131786", "B000T9886K"])

        f("select * from mydomain where Rating in ('4 stars', '****')",
          ["1579124585", "0802131786", "B000T9886K"])

        f("select * from mydomain where Keyword = 'Book' and Keyword = 'Hardcover'",
          [])

        f("select * from mydomain where every(Keyword) in ('Book', 'Paperback')",
          ["0385333498", "0802131786"])

        f("select * from mydomain where Keyword = 'Book' intersection Keyword = 'Hardcover'",
          ["1579124585"])

        f("select * from mydomain where Year < '1980' order by Year asc",
          ["0802131786", "0385333498", "1579124585"], ordered=True)

        f("select * from mydomain where Year < '1980' order by Year",
          ["0802131786", "0385333498", "1579124585"], ordered=True)

        f("select * from mydomain where Year = '2007' intersection Author is not null order by Author desc",
          ["B00005JPLW", "B000T9886K"], ordered=True)

        self.assertRaises(exc.InvalidSortExpressionException, f, "select * from mydomain order by Year asc", [])

        f("select * from mydomain where Year < '1980' order by Year limit 2",
          ["0802131786", "0385333498"])

        f("select itemName() from mydomain where itemName() like 'B000%' order by itemName()",
          ["B00005JPLW", "B000SF3NGK", "B000T9886K"])

        def g(expr, expected):
            order, results = self.backend.select_wrapper("owner", expr)
            self.assertEquals(order, ['mydomain'])
            self.assertEquals(results['mydomain']['count'].pop(), expected)

        g("select count(*) from mydomain where Title = 'The Right Stuff'", "1")
        g("select count(*) from mydomain where Year > '1985'", "3")
        g("select count(*) from mydomain limit 500", "6")
        g("select count(*) from mydomain limit 4", "4")

    def test_select(self):
        self.backend.create_domain("owner", "domain1")
        self.backend.put_attributes("owner", "domain1", "item1",
                                    {"shape": set(["square", "triangle"]),
                                     "colour": set(["Blue"])}, {})
        self.backend.put_attributes("owner", "domain1", "item2",
                                    {"colour": set(["Blue"])}, {})
        self.backend.put_attributes("owner", "domain1", "item3",
                                    {"shape": set(["round"]),
                                     "colour": set(["Red"])}, {})

        self.assertEquals(self.backend.select_wrapper("owner", "SELECT * FROM domain1")[1],
                          {"item1": {"shape": set(["square", "triangle"]),
                                     "colour": set(["Blue"])},
                           "item2": {"colour": set(["Blue"])},
                           "item3": {"shape": set(["round"]),
                                     "colour": set(["Red"])}})

        self.assertEquals(self.backend.select_wrapper("owner", "SELECT shape FROM domain1")[1],
                          {"item1": {"shape": set(["square", "triangle"])},
                           "item3": {"shape": set(["round"])}})

        self.assertEquals(self.backend.select_wrapper("owner", "SELECT shape FROM domain1 WHERE colour LIKE 'Blue'")[1],
                          {"item1": {"shape": set(["square", "triangle"])}})

        self.assertEquals(self.backend.select_wrapper("owner", "SELECT shape FROM domain1 WHERE shape = 'triangle'")[1],
                          {"item1": {"shape": set(["square", "triangle"])}})

    def test_unknown_attribute_condition_raises_attribute_does_not_exist(self):
        self.backend.create_domain("owner", "domain1")
        self.backend.put_attributes("owner", "domain1",
                                    "item1",
                                    {'attr1': set(['attr1val1'])},
                                    {}, [])
        self.assertRaises(basicdb.exceptions.AttributeDoesNotExist, self.backend.put_attributes, "owner", "domain1", "item1", {'attr2': set(["attr2val1"])}, {}, [('attr3', 'attr3val1')])

    def test_multi_valued_attribute_raises_multi_valued_attribute(self):
        self.backend.create_domain("owner", "domain1")
        self.backend.put_attributes("owner", "domain1", "item1",
                                    {'attr1': set(['attr1val1', 'attr1val2'])},
                                    {}, [])
        self.assertRaises(basicdb.exceptions.MultiValuedAttribute, self.backend.put_attributes, "owner", "domain1", "item1", {'attr2': set(["attr2val1"])}, {}, [('attr1', 'attr1val1')])

    def test_wrong_value_raises_conditional_check_failed(self):
        self.backend.create_domain("owner", "domain1")
        self.backend.put_attributes("owner", "domain1", "item1",
                                    {'attr1': set(['attr1val1'])},
                                    {}, [])
        self.assertRaises(basicdb.exceptions.WrongValueFound, self.backend.put_attributes, "owner", "domain1", "item1", {'attr2': set(["attr2val1"])}, {}, [('attr1', 'attr1val2')])

    def test_unexpected_attribute_raises_unexpected_value(self):
        self.backend.create_domain("owner", "domain1")
        self.backend.put_attributes("owner", "domain1", "item1",
                                    {'attr1': set(['attr1val1'])},
                                    {}, [])
        self.assertRaises(basicdb.exceptions.FoundUnexpectedAttribute, self.backend.put_attributes, "owner", "domain1", "item1", {'attr2': set(["attr2val1"])}, {}, [('attr1', False)])

    def test_expected_attribute_value_succeeds(self):
        self.backend.create_domain("owner", "domain1")
        self.backend.put_attributes("owner", "domain1", "item1",
                                    {'attr1': set(['attr1val1'])},
                                    {}, [])
        self.backend.put_attributes("owner", "domain1", "item1",
                                    {'attr2': set(["attr2val1"])}, {},
                                    [('attr1', 'attr1val1')])

    def test_expected_attribute_succeeds(self):
        self.backend.create_domain("owner", "domain1")
        self.backend.put_attributes("owner", "domain1", "item1",
                                    {'attr1': set(['attr1val1'])},
                                    {}, [])
        self.backend.put_attributes("owner", "domain1", "item1",
                                    {'attr2': set(["attr2val1"])}, {},
                                    [('attr1', True)])


class FakeBackendDriverTest(_GenericBackendDriverTest, unittest.TestCase):
    def setUp(self):
        super(FakeBackendDriverTest, self).setUp()
        self.backend = basicdb.backends.fake.driver()

    def tearDown(self):
        super(FakeBackendDriverTest, self).tearDown()
        self.backend._reset()

class FilesystemBackendDriverTest(_GenericBackendDriverTest, unittest.TestCase):
    def setUp(self):
        super(FilesystemBackendDriverTest, self).setUp()
        import basicdb.backends.filesystem
        self.backend = basicdb.backends.filesystem.driver()

    def tearDown(self):
        super(FilesystemBackendDriverTest, self).tearDown()
        self.backend._reset()

class RiakBackendDriverTest(_GenericBackendDriverTest, unittest.TestCase):
    def setUp(self):
        import os
        if 'ENABLE_RIAK_TESTS' not in os.environ:
            self.skip("Riak tests not enabled (set ENABLE_RIAK_TESTS "
                      "env to enable)")
        super(RiakBackendDriverTest, self).setUp()
        import basicdb.backends.riak
        import uuid
        self.backend = basicdb.backends.riak.driver(base_bucket='testbucket%s' % (uuid.uuid4().hex,))

    def tearDown(self):
        super(RiakBackendDriverTest, self).tearDown()
        self.backend._reset()
