"""
This python module provides functionality to parse the methods of a
XSIGMA object.

"""

import string, re, sys
import types

# set this to 1 if you want to see debugging messages - very useful if
# you have problems
DEBUG = True


def debug(msg):
    if DEBUG:
        print(msg)


class XsigmaDirMethodParser:
    """Parses the methods from dir(xsigma_obj)."""

    write_to_json_methods_ = []
    # stores the read_from_json methods_
    read_from_json_methods_ = []
    # stores the write_to_binary methods_
    write_to_binary_methods_ = []
    # stores the read_from_binary methods_
    read_from_binary_methods_ = []

    def initialize_methods(self, xsigma_obj):
        debug("XsigmaDirMethodParser::initialize_methods()")
        self.methods_ = dir(xsigma_obj)[:]

    def parse_methods(self, xsigma_obj):
        debug("XsigmaDirMethodParser:: parse_methods()")
        self.initialize_methods(xsigma_obj)
        debug("XsigmaDirMethodParser:: parse_methods() - initialized methods")

        for method in self.methods_[:]:
            # finding all the methods_ that set the state.
            if method.find("write_to_json") >= 0:

                try:
                    eval("xsigma_obj.write_to_json")("a.json", xsigma_obj)
                except AttributeError:
                    self.write_to_json_methods_.append(method)
                    self.methods_.remove(method)
            elif method.find("read_from_json") >= 0:
                try:
                    eval("xsigma_obj.write_to_json")("a.json", xsigma_obj)
                    eval("xsigma_obj.read_from_json")("a.json")
                except AttributeError:
                    self.read_from_binary_methods_.append(method)
                    self.methods_.remove(method)
            elif method.find("write_to_binary") >= 0:
                try:
                    eval("xsigma_obj.write_to_binary")("a.bin", xsigma_obj)
                except AttributeError:
                    self.write_to_binary_methods_.append(method)
                    self.methods_.remove(method)
            elif method.find("read_from_binary") >= 0:
                try:
                    eval("xsigma_obj.write_to_binary")("a.bin", xsigma_obj)
                    eval("xsigma_obj.read_from_binary")("a.bin")
                except AttributeError:
                    self.read_from_binary_methods_.append(method)
                    self.methods_.remove(method)

        self.clean_up_methods(xsigma_obj)

    def clean_up_methods(self, xsigma_obj):
        self.clean_write_to_json_methods(xsigma_obj)
        self.clean_read_from_json_methods(xsigma_obj)
        self.clean_write_to_binary_methods(xsigma_obj)
        self.clean_read_from_binary_methods(xsigma_obj)

    def clean_write_to_json_methods(self, xsigma_obj):
        debug("XsigmaDirMethodParser::clean_write_to_json_methods()")
        for method in self.write_to_json_methods_[:]:
            try:
                eval("xsigma_obj.write_to_json")("a.json", xsigma_obj)
            except (TypeError, AttributeError):
                pass
            else:
                self.write_to_json_methods_.remove(method)

    def clean_read_from_json_methods(self, xsigma_obj):
        debug("XsigmaDirMethodParser:: clean_read_from_json_methods()")
        for method in self.read_from_json_methods_[:]:
            try:
                eval("xsigma_obj.write_to_json")("a.json", xsigma_obj)
                val = eval("xsigma_obj.read_from_json")("a.json")
            except (TypeError, AttributeError):
                self.read_from_json_methods_.remove(method)
            else:
                if val is None:
                    self.read_from_json_methods_.remove(method)

    def clean_write_to_binary_methods(self, xsigma_obj):
        debug("XsigmaDirMethodParser:: clean_write_to_json_methods()")
        for method in self.write_to_binary_methods_[:]:
            try:
                eval("xsigma_obj.write_to_binary")("a.bin", xsigma_obj)
            except (TypeError, AttributeError):
                pass
            else:
                self.write_to_binary_methods_.remove(method)

    def clean_read_from_binary_methods(self, xsigma_obj):
        debug("XsigmaDirMethodParser:: clean_read_from_binary_methods()")
        for method in self.read_from_binary_methods_[:]:
            try:
                eval("xsigma_obj.write_to_binary")("a.bin", xsigma_obj)
                val = eval("xsigma_obj.read_from_binary")("a.bin")
            except (TypeError, AttributeError):
                pass
            else:
                self.read_from_binary_methods_.remove(method)

    def write_to_json_methods(self):
        return self.write_to_json_methods_

    def read_from_json_methods(self):
        return self.read_from_json_methods_

    def write_to_binary_methods(self):
        return self.write_to_binary_methods_

    def read_from_binary_methods(self):
        return self.read_from_binary_methods_


class XsigmaPrintMethodParser:
    """This class finds the methods_ for a given xsigmaObject.  It uses
    the output from xsigmaObject->Print() (or in Python str(xsigmaObject))
    and output from the XsigmaDirMethodParser to obtain the methods_."""

    def parse_methods(self, xsigma_obj):
        "Parse for the methods_."
        debug("XsigmaPrintMethodParser:: parse_methods()")

        if self._initialize_methods(xsigma_obj):
            return

        for method in self.methods_[:]:
            # removing methods_ that have nothing to the right of the ':'
            if (method[1] == "") or (method[1].find("none") > -1):
                self.methods_.remove(method)

        for method in self.methods_:
            # toggle methods_ are first identified
            if (method[1] == "write_to_json") or (method[1] == "read_from_json"):
                try:
                    eval("xsigma_obj.write_to_json")("a.json", xsigma_obj)
                    val = eval("xsigma_obj.read_from_json")("a.json")
                except AttributeError:
                    pass
            elif (method[1] == "write_to_binary") or (method[1] == "read_from_binary"):
                try:
                    eval("xsigma_obj.write_to_binary")("a.bin", xsigma_obj)
                    val = eval("xsigma_obj.read_from_binary")("a.bin")
                except AttributeError:
                    pass

        self._clean_up_methods(xsigma_obj)

    def _get_str_obj(self, xsigma_obj):
        debug("XsigmaPrintMethodParser:: _get_str_obj()")
        self.methods_ = str(xsigma_obj)
        self.methods_ = self.methods_.split("\n")
        del self.methods_[0]

    def _initialize_methods(self, xsigma_obj):
        "Do the basic parsing and setting up"
        debug("XsigmaPrintMethodParser:: _initialize_methods()")
        dir_p = XsigmaDirMethodParser()
        dir_p.parse_methods(xsigma_obj)

        try:
            junk = xsigma_obj.__class__
        except AttributeError:
            pass
        else:
            self.write_to_json_methods_ = dir_p.write_to_json_methods()
            self.read_from_json_methods_ = dir_p.read_from_json_methods()
            self.write_to_binary_methods_ = dir_p.write_to_binary_methods()
            self.read_from_binary_methods_ = dir_p.read_from_binary_methods()
            return 1

        self.dir_write_to_json_methods_ = dir_p.write_to_json_methods()
        self.dir_read_from_json_methods_ = dir_p.read_from_json_methods()
        self.dir_write_to_binary_methods_ = dir_p.write_to_binary_methods()
        self.dir_read_from_binary_methods_ = dir_p.read_from_binary_methods()

        self._get_str_obj(xsigma_obj)
        patn = re.compile(r"  \S")

        for method in self.methods_[:]:
            if not patn.match(method):
                self.methods_.remove(method)

        for method in self.methods_[:]:
            if method.find(":") == -1:
                self.methods_.remove(method)

        for i in range(0, len(self.methods_)):
            strng = self.methods_[i]
            strng = strng.replace(" ", "")
            self.methods_[i] = strng.split(":")

        self.write_to_json_methods_ = []
        self.read_from_json_methods_ = []
        self.write_to_binary_methods_ = []
        self.read_from_binary_methods_ = []

        return 0

    def _clean_up_methods(self, xsigma_obj):
        "Merge dir and str methods_.  Finish up."
        debug("XsigmaPrintMethodParser:: _clean_up_methods()")
        for meth_list in (
            (self.dir_write_to_json_methods_, self.write_to_json_methods_),
            (self.dir_read_from_json_methods_, self.read_from_json_methods_),
            (self.dir_write_to_binary_methods_, self.write_to_binary_methods_),
            (self.dir_read_from_binary_methods_, self.read_from_binary_methods_),
        ):
            for method in meth_list[0]:
                try:
                    meth_list[1].index(method)
                except ValueError:
                    meth_list[1].append(method)

        self.write_to_json_methods_.sort()
        self.read_from_json_methods_.sort()
        self.write_to_binary_methods_.sort()
        self.read_from_binary_methods_.sort()

    def write_to_json_methods(self):
        return self.write_to_json_methods_

    def read_from_json_methods(self):
        return self.read_from_json_methods_

    def write_to_binary_methods(self):
        return self.write_to_binary_methods_

    def read_from_binary_methods(self):
        return self.read_from_binary_methods_
