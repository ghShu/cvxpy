from cvxpy.expressions.expression import *
from cvxpy.expressions.variable import Variable
from cvxpy.expressions.constant import Constant
from cvxpy.expressions.parameter import Parameter
from cvxpy.expressions.containers import Variables
from cvxpy.expressions.curvature import Curvature
import cvxpy.interface.matrix_utilities as intf
from collections import deque
import unittest

class TestExpressions(unittest.TestCase):
    """ Unit tests for the expression/expression module. """
    def setUp(self):
        self.x = Variable(2, name='x')
        self.y = Variable(3, name='y')
        self.z = Variable(2, name='z')

        self.A = Variable(2,2,name='A')
        self.B = Variable(2,2,name='B')
        self.C = Variable(3,2,name='C')
        self.intf = intf.DEFAULT_INTERFACE()

    # Test the Variable class.
    def test_variable(self):
        x = Variable(2)
        y = Variable(2)
        assert y.name() != x.name()

        x = Variable(2, name='x')
        y = Variable()
        self.assertEqual(x.name(), 'x')
        self.assertEqual(x.size, (2,1))
        self.assertEqual(y.size, (1,1))
        self.assertEqual(x.curvature, Curvature.AFFINE)
        self.assertEqual(x.canonicalize(), (x, []))

        # identity = x.coefficients(self.intf)[x.id]
        # self.assertEqual(identity.size, (2,2))
        # self.assertEqual(identity[0,0], 1)
        # self.assertEqual(identity[0,1], 0)
        # self.assertEqual(identity[1,0], 0)
        # self.assertEqual(identity[1,1], 1)
        # Test terms and variables.
        self.assertEqual(x.variables()[x.id], x)
        self.assertEqual(x.terms(), [x])

    # Test the Variables class.
    def test_variables(self):
        v = Variables(['y',3],'x','z',['A',3,4])
        self.assertEqual(v.y.name(), 'y')
        self.assertEqual(v.y.size, (3,1))
        self.assertEqual(v.x.name(), 'x')
        self.assertEqual(v.x.size, (1,1))
        self.assertEqual(v.z.name(), 'z')
        self.assertEqual(v.z.size, (1,1))
        self.assertEqual(v.A.name(), 'A')
        self.assertEqual(v.A.size, (3,4))

    # Test the Constant class.
    def test_constants(self):
        c = Constant(2)
        self.assertEqual(c.name(), str(2))

        c = Constant(2, name="c")
        self.assertEqual(c.name(), "c")
        self.assertEqual(c.value, 2)
        self.assertEqual(c.size, (1,1))
        self.assertEqual(c.variables(), {})
        self.assertEqual(c.curvature, Curvature.CONSTANT)
        self.assertEqual(c.canonicalize(), (c, []))
        # self.assertEqual(c.terms(), [c])

    # Test the Parameter class.
    def test_parameters(self):
        p = Parameter('p')
        self.assertEqual(p.name(), "p")

    # Test the AddExpresion class.
    def test_add_expression(self):
        # Vectors
        c = Constant([2,2])
        exp = self.x + c
        self.assertEqual(exp.curvature, Curvature.AFFINE)
        self.assertEqual(exp.canonicalize(), (exp, []))
        self.assertEqual(exp.name(), self.x.name() + " + " + c.name())
        self.assertEqual(exp.size, (2,1))

        z = Variable(2, name='z')
        exp = exp + z + self.x
        # self.assertItemsEqual(exp.variables().keys(), [self.x.id, z.id])

        # self.assertItemsEqual(exp.terms(), [self.x, self.x, z, c])

        with self.assertRaises(Exception) as cm:
            (self.x + self.y).size
        self.assertEqual(str(cm.exception), "Incompatible dimensions.")

        # Matrices
        exp = self.A + self.B
        self.assertEqual(exp.curvature, Curvature.AFFINE)
        self.assertEqual(exp.size, (2,2))

        with self.assertRaises(Exception) as cm:
            (self.A + self.C).size
        self.assertEqual(str(cm.exception), "Incompatible dimensions.")


    # Test the SubExpresion class.
    def test_sub_expression(self):
        # Vectors
        c = Constant([2,2])
        exp = self.x - c
        self.assertEqual(exp.curvature, Curvature.AFFINE)
        self.assertEqual(exp.canonicalize(), (exp, []))
        self.assertEqual(exp.name(), self.x.name() + " - " + Constant([2,2]).name())
        self.assertEqual(exp.size, (2,1))

        z = Variable(2, name='z')
        exp = exp - z - self.x
        # self.assertItemsEqual(exp.variables().keys(), [self.x.id, z.id])
        # self.assertItemsEqual(exp.terms(), [self.x, self.x, c, z])

        with self.assertRaises(Exception) as cm:
            (self.x - self.y).size
        self.assertEqual(str(cm.exception), "Incompatible dimensions.")

        # Matrices
        exp = self.A - self.B
        self.assertEqual(exp.curvature, Curvature.AFFINE)
        self.assertEqual(exp.size, (2,2))

        with self.assertRaises(Exception) as cm:
            (self.A - self.C)
        self.assertEqual(str(cm.exception), "Incompatible dimensions.")

    # Test the MulExpresion class.
    def test_mul_expression(self):
        # Vectors
        c = Constant([[2],[2]])
        exp = c*self.x
        self.assertEqual(exp.curvature, Curvature.AFFINE)
        self.assertEqual(exp.canonicalize(), (exp, []))
        self.assertEqual(exp.name(), Constant(c).name() + " * " + self.x.name())
        self.assertEqual(exp.size, (1,1))

        # self.assertItemsEqual(exp.terms(), [self.x, c])

        one = Constant(1)
        two = Constant(2)
        new_exp = two*(exp + one)
        # self.assertEqual(new_exp.variables(), exp.variables())
        # self.assertItemsEqual(new_exp.terms(), [self.x, one, two, c])

        with self.assertRaises(Exception) as cm:
            ([2,2,3]*self.x)
        const_name = Constant([2,2,3]).name()
        self.assertEqual(str(cm.exception), 
            "Incompatible dimensions.")

        # Matrices
        with self.assertRaises(Exception) as cm:
            Constant([[2, 1],[2, 2]]) * self.C
        self.assertEqual(str(cm.exception), "Incompatible dimensions.")

        with self.assertRaises(Exception) as cm:
            (self.A * self.C)
        self.assertEqual(str(cm.exception), "Cannot multiply on the left by a non-constant.")

        # Constant expressions
        T = Constant([[1,2,3],[3,5,5]])
        exp = (T + T) * self.B
        self.assertEqual(exp.curvature, Curvature.AFFINE)
        self.assertEqual(exp.size, (3,2))

        # self.assertItemsEqual(exp.terms(), [self.B, T, T])

    # Test the NegExpression class.
    def test_neg_expression(self):
        # Vectors
        exp = -self.x
        self.assertEqual(exp.curvature, Curvature.AFFINE)
        self.assertEqual(exp.canonicalize(), (exp, []))
        self.assertEqual(exp.name(), "-%s" % self.x.name())
        self.assertEqual(exp.size, self.x.size)
        # self.assertEqual(exp.terms(), [self.x])

        exp = self.x + self.z
        self.assertEquals((-exp).variables(), exp.variables())

        # Matrices
        exp = -self.C
        self.assertEqual(exp.curvature, Curvature.AFFINE)
        self.assertEqual(exp.size, (3,2))

    # Test promotion of scalar constants.
    def test_scalar_const_promotion(self):
        # Vectors
        exp = self.x + 2
        self.assertEqual(exp.curvature, Curvature.AFFINE)
        self.assertEqual(exp.canonicalize(), (exp, []))
        self.assertEqual(exp.name(), self.x.name() + " + " + Constant(2).name())
        self.assertEqual(exp.size, (2,1))

        self.assertEqual((4 - self.x).size, (2,1))
        self.assertEqual((4 * self.x).size, (2,1))
        self.assertEqual((4 <= self.x).size, (2,1))
        self.assertEqual((4 == self.x).size, (2,1))
        self.assertEqual((self.x >= 4).size, (2,1))

        # Matrices
        exp = (self.A + 2) + 4
        self.assertEqual(exp.curvature, Curvature.AFFINE)
        self.assertEqual((3 * self.A).size, (2,2))

        self.assertEqual(exp.size, (2,2))

    # Test indexing expression.
    def test_index_expression(self):
        # Tuple of integers as key.
        exp = self.x[1,0]
        self.assertEqual(exp.name(), "x[1,0]")
        self.assertEqual(exp.curvature, Curvature.AFFINE)
        self.assertEquals(exp.size, (1,1))

        with self.assertRaises(Exception) as cm:
            (self.x[2,0]).canonicalize()
        self.assertEqual(str(cm.exception), "Invalid indices 2,0 for 'x'.")
