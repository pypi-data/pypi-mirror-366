""" This module attempts to make it easy to create XSIGMA-Python
unittests.  The module uses unittest for the test interface.  For more
documentation on what unittests are and how to use them, please read
these:

   http://www.python.org/doc/current/lib/module-unittest.html

   http://www.diveintopython.org/roman_divein.html


This XSIGMA-Python test module supports regression based tests with multiple
regressions per test suite and multiple regressions per individual test as well.
It also prints information appropriate for CDash
(http://open.kitware.com/).

This module defines several useful classes and functions to make
writing tests easy.  The most important of these are:

class xsigmaTest:
   Subclass this for your tests.  It also has a few useful internal
   functions that can be used to do some simple blackbox testing.

compareRegression(regression_filename, base_regression_filename, threshold=0.15):
   Compares renwin with regression and generates regression if it does not
   exist.  The threshold determines how closely the regressions must match.
   The function also handles multiple regressions and finds the best
   matching regression.

compareWithSavedData(regression_filename, base_regression_filename, threshold=0.15):
   Compares given source regression (in the form of a xsigmaRegressionData) with
   saved regression and generates the regression if it does not exist.  The
   threshold determines how closely the regressions must match.  The
   function also handles multiple regressions and finds the best matching
   regression.

getAbsRegressionPath(img_basename):
   Returns the full path to the regression given the basic regression name.

main(cases):
   Does the testing given a list of tuples containing test classes and
   the starting string of the functions used for testing.

Examples:

  The best way to learn on how to use this module is to look at a few
  examples.  The end of this file contains a trivial example.  Please
  also look at the following examples:

    Rendering/Testing/Python/TestTkRenderWidget.py,
    Rendering/Testing/Python/TestTkRenderWindowInteractor.py
"""

from __future__ import absolute_import
import sys, os, time
import os.path
import unittest, getopt
from xsigmamodules.Core import timerLog
from xsigmamodules.TestingUtil import regressionTestReader, regressionTestWriter
from . import BlackBox

# location of the XSIGMA data files.  Set via command line args or
# environment variable.
XSIGMA_DATA_ROOT = ""

# a list of paths to specific input data files
XSIGMA_DATA_PATHS = []

# location of the XSIGMA baseline regressions.  Set via command line args or
# environment variable.
XSIGMA_BASELINE_ROOT = ""

# location of the XSIGMA difference regressions for failed tests.  Set via
# command line args or environment variable.
XSIGMA_TEMP_DIR = ""

# a list of paths to validated output files
XSIGMA_BASELINE_PATHS = []

# Verbosity of the test messages (used by unittest)
_VERBOSE = 0

# This will be set to 1 when the regression test will not be performed.
# This option is used internally by the script and set via command
# line arguments.
_NO_REGRESSION = 0


def skip():
    """Cause the test to be skipped due to insufficient requirements."""
    sys.exit(0)


class xsigmaTest(unittest.TestCase):
    """A simple default XSIGMA test class that defines a few useful
    blackbox tests that can be readily used.  Derive your test cases
    from this class and use the following if you'd like to.

    Note: Unittest instantiates this class (or your subclass) each
    time it tests a method.  So if you do not want that to happen when
    generating XSIGMA pipelines you should create the pipeline in the
    class definition as done below for _blackbox.
    """

    _blackbox = BlackBox.Tester(debug=0)

    def _testParse(self, obj):
        """Does a blackbox test by attempting to parse the class for
        its various methods using xsigmaMethodParser.  This is a useful
        test because it gets all the methods, parses
        them and sorts them into different classes of objects."""
        self._blackbox.testParse(obj)

    def _testJson(self, obj, excluded_methods=[]):
        """Checks the Json method pairs by setting the value using
        the current state and making sure that it equals the value it
        was originally.  This effectively calls _testParse
        internally."""
        self._blackbox.testJson(obj, excluded_methods)

    def _testBinary(self, obj, excluded_methods=[]):
        """Checks the Binary methods by setting the value on and off
        and making sure that the GetMethod returns the set value.
        This effectively calls _testParse internally."""
        self._blackbox.testBinary(obj, excluded_methods)

    def pathToData(self, filename):
        """Given a filename with no path (i.e., no leading directories
        prepended), return the full path to a file as specified on the
        command line with a '-D' option.

        As an example, if a test is run with "-D /path/to/grid.vtu"
        then calling

            self.pathToData('grid.vtu')

        in your test will return "/path/to/grid.vtu". This is
        useful in combination with ExternalData, where data may be
        staged by CTest to a user-configured directory at build time.

        In order for this method to work, you must specify
        the JUST_VALID option for your test in CMake.
        """
        global XSIGMA_DATA_PATHS
        if not filename:
            return XSIGMA_DATA_PATHS
        for path in XSIGMA_DATA_PATHS:
            if filename == os.path.split(path)[-1]:
                return path
        return filename

    def pathToValidatedOutput(self, filename):
        """Given a filename with no path (i.e., no leading directories
        prepended), return the full path to a file as specified on the
        command line with a '-V' option.

        As an example, if a test is run with
        "-V /path/to/validRegression.regression" then calling

            self.pathToData('validRegression.regression')

        in your test will return "/path/to/validRegression.regression". This is
        useful in combination with ExternalData, where data may be
        staged by CTest to a user-configured directory at build time.

        In order for this method to work, you must specify
        the JUST_VALID option for your test in CMake.
        """
        global XSIGMA_BASELINE_PATHS
        if not filename:
            return XSIGMA_BASELINE_PATHS
        for path in XSIGMA_BASELINE_PATHS:
            if filename == os.path.split(path)[-1]:
                return path
        return filename

    def assertRegressionMatch(self, NewInput, baseline, **kwargs):
        """Throw an error if a rendering in the render window does not match the baseline regression.

        This method accepts a threshold keyword argument (with a default of 0.15)
        that specifies how different a baseline may be before causing a failure.
        """
        absoluteBaseline = baseline
        try:
            open(absoluteBaseline, "r")
        except:
            absoluteBaseline = getAbsRegressionPath(baseline)

        absoluteNewInput = NewInput
        try:
            open(absoluteNewInput, "r")
        except:
            absoluteNewInput = getAbsRegressionPath(NewInput)
        compareRegression(absoluteNewInput, absoluteBaseline, **kwargs)


def getAbsRegressionPath(img_basename):
    """Returns the full path to the regression given the basic regression
    name."""
    global XSIGMA_BASELINE_ROOT
    print(XSIGMA_BASELINE_ROOT)
    return os.path.join(XSIGMA_BASELINE_ROOT, img_basename)


def _getTempRegressionPath(img_fname):
    x = os.path.join(XSIGMA_TEMP_DIR, os.path.split(img_fname)[1])
    return os.path.abspath(x)


def compareWithSavedData(regression_filename, base_regression_filename, threshold=0):
    """Compares a source regression (regression_filename, which is a xsigmaRegressionData) with
    the saved regression file whose name is given in the second argument.
    If the regression file does not exist the regression is generated and
    stored.  If not the source regression is compared to that of the
    figure.  This function also handles multiple regressions and finds the
    best matching regression.
    """
    global _NO_REGRESSION
    if _NO_REGRESSION:
        return
    print(base_regression_filename)
    f_base, f_ext = os.path.splitext(base_regression_filename)

    if not os.path.isfile(base_regression_filename):
        _handleNewRegression(regression_filename)
        raise RuntimeError("new regression as base regression file does not exist")

    base_regression_reader = regressionTestReader()
    base_regression_reader.update(base_regression_filename)

    regression_reader = regressionTestReader()
    regression_reader.update(regression_filename)

    min_err = regression_reader.relatifL2Norm(base_regression_reader)

    err_index = 0
    count = 0
    if min_err > threshold:
        count = 1
        test_failed = 1
        err_index = -1
        while 1:  # keep trying regressions till we get the best match.
            new_fname = f_base + "_%d.regression" % count
            if not os.path.exists(new_fname):
                # no other regression exists.
                break
            # since file exists check if it matches.
            base_regression_reader.read(new_fname)
            alt_err = regression_reader.relatifL2Norm(base_regression_reader)
            if alt_err < threshold:
                # matched,
                err_index = count
                test_failed = 0
                min_err = alt_err
                break
            else:
                if alt_err < min_err:
                    # regression is a better match.
                    err_index = count
                    min_err = alt_err

            count = count + 1
        # closes while loop.

        if test_failed:
            _handleFailedRegression(regression_filename, base_regression_filename)
            # Print for CDash.
            _printCDashRegressionError(min_err, err_index, f_base)
            msg = "Failed regression test: %f\n" % min_err
            sys.tracebacklimit = 0
            raise RuntimeError(msg)
    # output the regression error even if a test passed
    _printCDashRegressionSuccess(min_err, err_index)


def compareRegression(regression_filename, base_regression_filename, threshold=0):
    """Compares regression_filename contents with the base_regression_filename
    file whose name is given in the second argument.  If the regression
    file does not exist the regression is generated and stored.  If not the
    regression in the render window is compared to that of the figure.
    This function also handles multiple regressions and finds the best
    matching regression."""

    global _NO_REGRESSION
    if _NO_REGRESSION:
        return

    try:
        compareWithSavedData(regression_filename, base_regression_filename, threshold)
    except RuntimeError:
        compareWithSavedData(regression_filename, base_regression_filename, threshold)
    return


def _printCDashRegressionError(min_err, err_index, img_base):
    """Prints the XML data necessary for CDash."""
    img_base = _getTempRegressionPath(img_base)
    print("Failed regression test with error: %f" % min_err)
    print(
        '<DartMeasurement name="RegressionError" type="numeric/double"> '
        "%f </DartMeasurement>" % min_err
    )
    if err_index <= 0:
        print(
            '<DartMeasurement name="BaselineRegression" type="text/string">Standard</DartMeasurement>'
        )
    else:
        print(
            '<DartMeasurement name="BaselineRegression" type="numeric/integer"> '
            "%d </DartMeasurement>" % err_index
        )

    print(
        '<DartMeasurementFile name="TestRegression" type="regression/regression"> '
        "%s </DartMeasurementFile>" % (img_base + ".regression")
    )

    print(
        '<DartMeasurementFile name="DifferenceRegression" type="regression/regression"> '
        "%s </DartMeasurementFile>" % (img_base + ".diff.regression")
    )
    print(
        '<DartMeasurementFile name="ValidRegression" type="regression/regression"> '
        "%s </DartMeasurementFile>" % (img_base + ".valid.regression")
    )


def _printCDashRegressionNotFoundError(base_regression_filename):
    """Prints the XML data necessary for Dart when the baseline regression is not found."""
    print(
        '<DartMeasurement name="RegressionNotFound" type="text/string">'
        + base_regression_filename
        + "</DartMeasurement>"
    )


def _printCDashRegressionSuccess(min_err, err_index):
    "Prints XML data for Dart when regression test succeeded."
    print(
        '<DartMeasurement name="RegressionError" type="numeric/double"> '
        "%f </DartMeasurement>" % min_err
    )
    if err_index <= 0:
        print(
            '<DartMeasurement name="BaselineRegression" type="text/string">Standard</DartMeasurement>'
        )
    else:
        print(
            '<DartMeasurement name="BaselineRegression" type="numeric/integer"> '
            "%d </DartMeasurement>" % err_index
        )


def _handleFailedRegression(regression_filename, base_regression_filename):
    """Writes all the necessary regressions when an regression comparison
    failed."""
    f_base, f_ext = os.path.splitext(base_regression_filename)
    writer = regressionTestWriter(_getTempRegressionPath(f_base + ".diff.regression"))
    writer.writeDiff(regression_filename, base_regression_filename)

    writer = regressionTestWriter(_getTempRegressionPath(f_base + ".old.regression"))
    writer.write(base_regression_filename)

    writer = regressionTestWriter(_getTempRegressionPath(f_base + ".new.regression"))
    writer.write(regression_filename)


def _handleNewRegression(regression_filename):
    """Writes new regressions when an regression comparison
    does not exist."""
    f_base, f_ext = os.path.splitext(regression_filename)
    writer = regressionTestWriter(_getTempRegressionPath(f_base + ".new.regression"))
    writer.write(regression_filename)


def main(cases):
    """Pass a list of tuples containing test classes and the starting
    string of the functions used for testing.

    Example:

    main ([(xsigmaTestClass, 'test'), (xsigmaTestClass1, 'test')])
    """

    processCmdLine()

    timer = timerLog()
    s_time = timer.GetCPUTime()
    s_wall_time = time.time()

    # run the tests
    result = test(cases)

    tot_time = timer.GetCPUTime() - s_time
    tot_wall_time = float(time.time() - s_wall_time)

    # output measurements for CDash
    print(
        '<DartMeasurement name="WallTime" type="numeric/double"> '
        " %f </DartMeasurement>" % tot_wall_time
    )
    print(
        '<DartMeasurement name="CPUTime" type="numeric/double"> '
        " %f </DartMeasurement>" % tot_time
    )

    # Delete these to eliminate debug leaks warnings.
    del cases

    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)


def test(cases):
    """Pass a list of tuples containing test classes and the
    functions used for testing.

    It returns a unittest._TextTestResult object.

    Example:

      test = test_suite([(xsigmaTestClass, 'test'),
                        (xsigmaTestClass1, 'test')])
    """
    # Make the test suites from the arguments.
    suites = []
    for case in cases:
        suites.append(unittest.makeSuite(case[0], case[1]))
    test_suite = unittest.TestSuite(suites)

    # Now run the tests.
    runner = unittest.TextTestRunner(verbosity=_VERBOSE)
    result = runner.run(test_suite)

    return result


def usage():
    msg = """Usage:\nTestScript.py [options]\nWhere options are:\n

    -D /path/to/XSIGMAData
    --data-dir /path/to/XSIGMAData

          Directory containing XSIGMA Data use for tests.  If this option
          is not set via the command line the environment variable
          XSIGMA_DATA_ROOT is used.  If the environment variable is not
          set the value defaults to '../../../../../XSIGMAData'.

    -B /path/to/valid/regression_dir/
    --baseline-root /path/to/valid/regression_dir/

          This is a path to the directory containing the valid regressions
          for comparison.  If this option is not set via the command
          line the environment variable XSIGMA_BASELINE_ROOT is used.  If
          the environment variable is not set the value defaults to
          the same value set for -D (--data-dir).

    -T /path/to/valid/temporary_dir/
    --temp-dir /path/to/valid/temporary_dir/

          This is a path to the directory where the regression differences
          are written.  If this option is not set via the command line
          the environment variable XSIGMA_TEMP_DIR is used.  If the
          environment variable is not set the value defaults to
          '../../../../Testing/Temporary'.

    -V /path/to/validated/output.regression
    --validated-output /path/to/valid/output.regression

          This is a path to a file (usually but not always an regression)
          which is compared to data generated by the test.

    -v level
    --verbose level

          Sets the verbosity of the test runner.  Valid values are 0,
          1, and 2 in increasing order of verbosity.

    -n
    --no-regression

          Does not do any regression comparisons.  This is useful if you
          want to run the test and not worry about test regressions or
          regression failures etc.

    -h
    --help

                 Prints this message.

"""
    return msg


def parseCmdLine():
    arguments = sys.argv[1:]

    options = "B:D:T:V:v:hnI"
    long_options = [
        "baseline-root=",
        "data-dir=",
        "temp-dir=",
        "validated-output=",
        "verbose=",
        "help",
        "no-regression",
        "interact",
    ]

    try:
        opts, args = getopt.getopt(arguments, options, long_options)
    except getopt.error as msg:
        print(usage())
        print("-" * 70)
        print(msg)
        sys.exit(1)

    return opts, args


def processCmdLine():
    opts, args = parseCmdLine()

    global XSIGMA_DATA_ROOT, XSIGMA_BASELINE_ROOT, XSIGMA_TEMP_DIR, XSIGMA_BASELINE_PATHS
    global _VERBOSE, _NO_REGRESSION

    # setup defaults
    try:
        XSIGMA_DATA_ROOT = os.environ["XSIGMA_DATA_ROOT"]
    except KeyError:
        XSIGMA_DATA_ROOT = os.path.normpath("../../../../../XSIGMAData")

    try:
        XSIGMA_BASELINE_ROOT = os.environ["XSIGMA_BASELINE_ROOT"]
    except KeyError:
        pass

    try:
        XSIGMA_TEMP_DIR = os.environ["XSIGMA_TEMP_DIR"]
    except KeyError:
        XSIGMA_TEMP_DIR = os.path.normpath("../../../../Testing/Temporary")

    for o, a in opts:
        if o in ("-D", "--data-dir"):
            oa = os.path.abspath(a)
            if os.path.isfile(oa):
                XSIGMA_DATA_PATHS.append(oa)
            else:
                XSIGMA_DATA_ROOT = oa
        if o in ("-B", "--baseline-root"):
            XSIGMA_BASELINE_ROOT = os.path.abspath(a)
        if o in ("-T", "--temp-dir"):
            XSIGMA_TEMP_DIR = os.path.abspath(a)
        if o in ("-V", "--validated-output"):
            XSIGMA_BASELINE_PATHS.append(os.path.abspath(a))
        if o in ("-n", "--no-regression"):
            _NO_REGRESSION = 1
        if o in ("-v", "--verbose"):
            try:
                _VERBOSE = int(a)
            except:
                msg = "Verbosity should be an integer.  0, 1, 2 are valid."
                print(msg)
                sys.exit(1)
        if o in ("-h", "--help"):
            print(usage())
            sys.exit()

    if not XSIGMA_BASELINE_ROOT:  # default value.
        XSIGMA_BASELINE_ROOT = XSIGMA_DATA_ROOT


if __name__ == "__main__":
    ######################################################################
    # A Trivial test case to illustrate how this module works.
    class SampleTest(xsigmaTest):
        from xsigmamodules.Util import key

        obj = key("A")

        def testParse(self):
            "Test if class is parseable"
            self._testParse(self.obj)

        def testJson(self):
            "Testing Json methods"
            self._testJson(self.obj)

        def testBinary(self):
            "Testing Binary methods"
            self._testBinary(self.obj)

    # Test with the above trivial sample test.
    main([(SampleTest, "test")])
