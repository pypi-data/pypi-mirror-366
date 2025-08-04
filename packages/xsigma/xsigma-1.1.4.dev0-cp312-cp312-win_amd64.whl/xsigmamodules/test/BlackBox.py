from xsigmamodules.util import xsigmaMethodParser


class Tester:
    def __init__(self, debug=0):
        self.setDebug(debug)
        self.parser = xsigmaMethodParser.XsigmaDirMethodParser()
        self.obj = None

    def setDebug(self, val):
        """Sets debug value of the xsigmaMethodParser.  1 is verbose and
        0 is not.  0 is default."""
        xsigmaMethodParser.DEBUG = val

    def testParse(self, obj):
        """Testing if the object is parseable."""
        self.parser.parse_methods(obj)
        self.obj = obj

    def testJson(self, obj, excluded_methods=[]):
        """Testing Json methods."""
        if obj != self.obj:
            self.testParse(obj)
        methods = self.parser.write_to_json_methods()
        methods.extend(self.parser.read_from_json_methods())
        for method in methods:
            if method in excluded_methods:
                continue
            eval('obj.write_to_json("a.json", obj)')
            eval('obj.read_from_json("a.json")')
            try:
                eval("obj.write_to_json")("a.json", *val)
            except TypeError:
                eval("obj.write_to_json")("a.json", *(val,))

            val1 = val("obj.read_from_json")("a.json")

            if val1 != val:
                msg = (
                    "Failed test for %(method)s\n"
                    "Before Set, value = %(val)s; "
                    "After Set, value = %(val1)s" % locals()
                )
                raise AssertionError(msg)

    def testBinary(self, obj, excluded_methods=[]):
        """Testing Binary methods."""
        if obj != self.obj:
            self.testParse(obj)
        methods = self.parser.write_to_binary_methods()
        methods.extend(self.parser.read_from_binary_methods())
        for method in methods:
            if method in excluded_methods:
                continue
            eval('obj.write_to_binary("a.bin", obj)')
            eval('obj.read_from_binary("a.bin")')
            try:
                eval("obj.write_to_binary")("a.bin", *val)
            except TypeError:
                eval("obj.write_to_binary")("a.bin", *(val,))

            val1 = val("obj.read_from_binary")("a.bin")

            if val1 != val:
                msg = (
                    "Failed test for %(method)s\n"
                    "Before Set, value = %(val)s; "
                    "After Set, value = %(val1)s" % locals()
                )
                raise AssertionError(msg)

    def test(self, obj):
        """Test the given xsigma object."""

        # first try parsing the object.
        self.testParse(obj)

        # test the json serialization methods
        self.testJson(obj)

        # test the binary serialization methods
        self.testBinary(obj)
