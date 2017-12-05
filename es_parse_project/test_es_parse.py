# -*- coding:utf-8 -*-
from __future__ import print_function
import unittest
from jsonparser import *


class TestEsParse(unittest.TestCase):
    def test_es_loads(self):
        pass

    def test_constum(self):
        print("\n------------test constum-----------")

        dstr1 = """[
                    1,2,3,
                    4,
                    [5, 6, 7],
                    {1:2, 3:4}
                    ]"""
        dstr2 = """ {1,2,3}"""
        dstr3 = "{[1,2]:,3}"

        print(es_loads(dstr1))
        print(es_loads(dstr2))
        print(es_loads(dstr3))

    def testnum(self):
        print("\n------------test number-----------")
        self.assertEqual(type(self.parse("24")), type(1))
        self.assertEqual(type(self.parse("1e4")), type(10000))
        self.assertEqual(type(self.parse("-1.5")), type(-1.5))
        self.assertEqual(type(self.parse("1.5e3")), type(1.500))

    def testliteral(self):
        print("\n------------test literal----------")
        self.assertEqual(type(self.parse("      null")), type(None))
        self.assertEqual(type(self.parse(" \t null")), type(None))
        self.assertEqual(type(self.parse(" \n false")), type(False))
        self.assertEqual(type(self.parse(" \n null")), type(None))
        self.assertEqual(type(self.parse("  true")), type(True))

    def teststring(self):
        print("\n------------test string----------")
        self.assertEqual(type(self.parse("\" \\\\line1\\nline2 \"")), type("string"))         # input \\  is \
        self.assertEqual(type(self.parse("\"  abc\\def\"")), type("string"))
        self.assertEqual(type(self.parse("\"      null\"")), type("string"))
        self.assertEqual(type(self.parse("\"hello world!\"")), type("string"))
        self.assertEqual(type(self.parse("\"   \u751F\u5316\u5371\u673A  \"")), type("string"))

    def testarray(self):
        print("\n------------test array----------")
        self.assertEqual(type(self.parse("[13,2,3]")), type([]))
        self.assertEqual(type(self.parse("[13,[2,3]]")), type([]))
        self.assertEqual(type(self.parse("[  13  , [ 2, 3],[4,5]]")), type([]))
        self.assertEqual(type(self.parse("[13,true]")), type([]))
        self.assertEqual(type(self.parse("[[11,12],[21,22]]")), type([]))
        self.assertEqual(type(self.parse("[[11,  [111  ,112],  13],[21,22]]")), type([]))
        self.assertEqual(type(self.parse("[[11,{\"name\":\"zz\",\"age\":24},13],[21,22]]")), type([]))

    def testobject(self):
        print("\n------------test object----------")
        self.assertEqual(type(self.parse("{\"name\":\"zz\",\"age\":24}")), type({}))
        self.assertEqual(type(self.parse("{\"name\":\"zz\",\"daylist\":[6,7]}")), type({}))
        self.assertEqual(type(self.parse(
            "{\"name\":{\"firstname\":\"zhao\",\"lastname\":\"zhang\"},\"age\":24,\"frient\":[1,2,3]}")), type({}))

    @staticmethod
    def parse(strng):
        print("input string = " + strng)
        res = es_loads(strng)
        print("output: ", end=" ")
        print(res)
        return res


if __name__ == '__main__':
    unittest.main()
