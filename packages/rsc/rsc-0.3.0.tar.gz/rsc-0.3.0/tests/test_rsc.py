import unittest
from rsc import assign_var, calculate

class TestRSCCalculator(unittest.TestCase):

    def setUp(self):
        # Clear variables before each test
        assign_var("a", None)
        assign_var("b", None)
        assign_var("c", None)

    def test_basic_math(self):
        self.assertEqual(calculate("1 + 2 * 3"), 7)
        self.assertEqual(calculate("10 / 2"), 5.0)
        self.assertEqual(calculate("10 x 3"), 30)

    def test_variables(self):
        assign_var("x", 10)
        assign_var("y", 5)
        self.assertEqual(calculate("x + y"), 15)
        self.assertEqual(calculate("x * y"), 50)

    def test_assignment(self):
        self.assertEqual(calculate("a = 10"), 10)
        self.assertEqual(calculate("a * 2"), 20)

    def test_factorial(self):
        self.assertEqual(calculate("5!"), 120)
        assign_var("n", 4)
        self.assertEqual(calculate("n!"), 24)

    def test_functions(self):
        self.assertAlmostEqual(calculate("sin(pi / 2)"), 1.0, places=7)
        self.assertAlmostEqual(calculate("log(e)"), 1.0, places=7)
        self.assertAlmostEqual(calculate("sqrt(16)"), 4.0, places=7)

    def test_errors(self):
        self.assertTrue("Error" in calculate("unknown_var + 1"))
        self.assertTrue("Error" in calculate("10 / 0"))
        self.assertTrue("Error" in calculate("5 + "))

if __name__ == "__main__":
    unittest.main()
