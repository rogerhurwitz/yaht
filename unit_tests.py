import sys
import unittest

sys.path.insert(0, "src")

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover("tests")
    runner = unittest.TextTestRunner()
    runner.run(suite)
