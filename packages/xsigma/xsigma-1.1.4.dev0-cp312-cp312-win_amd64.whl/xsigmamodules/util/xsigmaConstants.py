"""
This file is obsolete.
All the constants are part of the base xsigma module.
"""

# Some constants used throughout code

XSIGMA_FLOAT_MAX = 1.0e38
XSIGMA_INT_MAX = 2147483647  # 2^31 - 1

# These types are returned by GetDataType to indicate pixel type.
XSIGMA_VOID = 0
XSIGMA_BIT = 1
XSIGMA_CHAR = 2
XSIGMA_SIGNED_CHAR = 15
XSIGMA_UNSIGNED_CHAR = 3
XSIGMA_SHORT = 4
XSIGMA_UNSIGNED_SHORT = 5
XSIGMA_INT = 6
XSIGMA_UNSIGNED_INT = 7
XSIGMA_LONG = 8
XSIGMA_UNSIGNED_LONG = 9
XSIGMA_FLOAT = 10
XSIGMA_DOUBLE = 11

# These types are not currently supported by GetDataType, but are
# for completeness.
XSIGMA_STRING = 13
XSIGMA_OPAQUE = 14

XSIGMA_LONG_LONG = 16
XSIGMA_UNSIGNED_LONG_LONG = 17

# These types are required by xsigmaVariant and xsigmaVariantArray
XSIGMA_VARIANT = 20
XSIGMA_OBJECT = 21

# Some constant required for correct template performance
XSIGMA_BIT_MIN = 0
XSIGMA_BIT_MAX = 1
XSIGMA_CHAR_MIN = -128
XSIGMA_CHAR_MAX = 127
XSIGMA_UNSIGNED_CHAR_MIN = 0
XSIGMA_UNSIGNED_CHAR_MAX = 255
XSIGMA_SHORT_MIN = -32768
XSIGMA_SHORT_MAX = 32767
XSIGMA_UNSIGNED_SHORT_MIN = 0
XSIGMA_UNSIGNED_SHORT_MAX = 65535
XSIGMA_INT_MIN = -XSIGMA_INT_MAX - 1
XSIGMA_INT_MAX = XSIGMA_INT_MAX
# XSIGMA_UNSIGNED_INT_MIN = 0
# XSIGMA_UNSIGNED_INT_MAX = 4294967295
XSIGMA_LONG_MIN = -XSIGMA_INT_MAX - 1
XSIGMA_LONG_MAX = XSIGMA_INT_MAX
# XSIGMA_UNSIGNED_LONG_MIN = 0
# XSIGMA_UNSIGNED_LONG_MAX = 4294967295
XSIGMA_FLOAT_MIN = -XSIGMA_FLOAT_MAX
XSIGMA_FLOAT_MAX = XSIGMA_FLOAT_MAX
XSIGMA_DOUBLE_MIN = -1.0e99
XSIGMA_DOUBLE_MAX = 1.0e99

# These types define error codes for xsigma functions
XSIGMA_OK = 1
XSIGMA_ERROR = 2

# A macro to get the name of a type
__xsigmaTypeNameDict = {
    XSIGMA_VOID: "void",
    XSIGMA_DOUBLE: "double",
    XSIGMA_FLOAT: "float",
    XSIGMA_LONG: "long",
    XSIGMA_UNSIGNED_LONG: "unsigned long",
    XSIGMA_INT: "int",
    XSIGMA_UNSIGNED_INT: "unsigned int",
    XSIGMA_SHORT: "short",
    XSIGMA_UNSIGNED_SHORT: "unsigned short",
    XSIGMA_CHAR: "char",
    XSIGMA_UNSIGNED_CHAR: "unsigned char",
    XSIGMA_SIGNED_CHAR: "signed char",
    XSIGMA_LONG_LONG: "long long",
    XSIGMA_UNSIGNED_LONG_LONG: "unsigned long long",
    XSIGMA_BIT: "bit",
}


def ScalarToTypeNameMacro(type):
    return __xsigmaTypeNameDict[type]
