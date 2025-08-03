import io
import sys
import unittest

from printtostderr.core import main, printtostderr


class TestMainAndPrintToStderr(unittest.TestCase):

    def test_printtostderr(self):
        """Test if printtostderr prints correctly to sys.stderr."""
        stderr = io.StringIO()
        original_stderr = sys.stderr
        try:
            sys.stderr = stderr
            printtostderr("This is a test", 123, "!", sep="-", end="\n")
            output = stderr.getvalue()
        finally:
            sys.stderr = original_stderr
        self.assertEqual(output, "This is a test-123-!\n")

    def test_main_with_args(self):
        """Test main with specific arguments."""
        stderr = io.StringIO()
        original_stderr = sys.stderr
        try:
            sys.stderr = stderr
            main(["arg1", "arg2", "arg3"])
            output = stderr.getvalue()
        finally:
            sys.stderr = original_stderr
        self.assertEqual(output, "arg1 arg2 arg3\n")

    def test_main_without_args(self):
        """Test main with no arguments."""
        stderr = io.StringIO()
        original_stderr = sys.stderr
        try:
            sys.stderr = stderr
            main(args=())
            output = stderr.getvalue()
        finally:
            sys.stderr = original_stderr
        self.assertEqual(output, "\n")


if __name__ == "__main__":
    unittest.main()
