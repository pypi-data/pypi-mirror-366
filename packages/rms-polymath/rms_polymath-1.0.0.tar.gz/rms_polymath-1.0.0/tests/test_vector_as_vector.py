##########################################################################################
# tests/test_vector_as_vector.py
##########################################################################################

import numpy as np
import unittest

from polymath import Matrix, Pair, Scalar, Unit, Vector


class Test_Vector_as_vector(unittest.TestCase):

    def runTest(self):

        np.random.seed(4469)

        N = 10
        a = Vector(np.random.randn(N,6))
        da_dt = Vector(np.random.randn(N,6))
        a.insert_deriv('t', da_dt)

        b = Vector.as_vector(a, recursive=False)
        self.assertTrue(hasattr(a, 'd_dt'))
        self.assertFalse(hasattr(b, 'd_dt'))

        # Matrix case, Nx1
        a = Matrix(np.random.randn(N,7,1), unit=Unit.REV)
        da_dt = Matrix(np.random.randn(N,7,1,6), drank=1)
        a.insert_deriv('t', da_dt)

        b = Vector.as_vector(a)
        self.assertTrue(type(b), Vector)
        self.assertEqual(a.unit_, b.unit_)
        self.assertEqual(a.shape, b.shape)
        self.assertEqual(a.numer, (7,1))
        self.assertEqual(b.numer, (7,))
        self.assertTrue(np.all(a.values.ravel() == b.values.ravel()))

        self.assertTrue(hasattr(b, 'd_dt'))
        self.assertEqual(b.d_dt.shape, b.shape)
        self.assertEqual(b.d_dt.numer, (7,))
        self.assertEqual(b.d_dt.denom, (6,))
        self.assertTrue(np.all(a.d_dt.values.ravel() == b.d_dt.values.ravel()))

        b = Vector.as_vector(a, recursive=False)
        self.assertFalse(hasattr(b, 'd_dt'))

        # Matrix case, 1xN
        a = Matrix(np.random.randn(N,1,7), unit=Unit.REV)
        da_dt = Matrix(np.random.randn(N,1,7,6), drank=1)
        a.insert_deriv('t', da_dt)

        b = Vector.as_vector(a)
        self.assertTrue(type(b), Vector)
        self.assertEqual(a.unit_, b.unit_)
        self.assertEqual(a.shape, b.shape)
        self.assertEqual(a.numer, (1,7))
        self.assertEqual(b.numer, (7,))
        self.assertTrue(np.all(a.values.ravel() == b.values.ravel()))

        self.assertTrue(hasattr(b, 'd_dt'))
        self.assertEqual(b.d_dt.shape, b.shape)
        self.assertEqual(b.d_dt.numer, (7,))
        self.assertEqual(b.d_dt.denom, (6,))
        self.assertTrue(np.all(a.d_dt.values.ravel() == b.d_dt.values.ravel()))

        b = Vector.as_vector(a, recursive=False)
        self.assertFalse(hasattr(b, 'd_dt'))

        # Scalar case
        a = Scalar(np.random.randn(N), unit=Unit.UNITLESS)
        da_dt = Scalar(np.random.randn(N,6), drank=1)
        a.insert_deriv('t', da_dt)

        b = Vector.as_vector(a)
        self.assertTrue(type(b), Vector)
        self.assertEqual(a.unit_, b.unit_)
        self.assertEqual(a.shape, b.shape)
        self.assertEqual(a.numer, ())
        self.assertEqual(b.numer, (1,))
        self.assertTrue(np.all(a.values.ravel() == b.values.ravel()))

        self.assertTrue(hasattr(b, 'd_dt'))
        self.assertEqual(b.d_dt.shape, b.shape)
        self.assertEqual(b.d_dt.numer, (1,))
        self.assertTrue(np.all(a.d_dt.values.ravel() == b.d_dt.values.ravel()))

        b = Vector.as_vector(a, recursive=False)
        self.assertFalse(hasattr(b, 'd_dt'))

        a = Scalar(7.)
        b = Vector.as_vector(a)
        self.assertEqual(b._values, 7.)
        self.assertEqual(b._numer, (1,))

        a = Scalar(np.arange(60).reshape(20,3), drank=1)
        b = Vector.as_vector(a)
        self.assertTrue(np.all(b.vals[:,0,:] == a.vals))
        self.assertEqual(b.shape, (20,))
        self.assertEqual(b.item, (1,3))

        # Pair case
        a = Pair(np.random.randn(N,2), unit=Unit.DEG)
        da_dt = Pair(np.random.randn(N,2,6), drank=1)
        a.insert_deriv('t', da_dt)

        b = Vector.as_vector(a)
        self.assertTrue(type(b), Vector)
        self.assertEqual(a.unit_, b.unit_)
        self.assertEqual(a.shape, b.shape)
        self.assertEqual(a.numer, b.numer)
        self.assertTrue(np.all(a.values.ravel() == b.values.ravel()))

        self.assertTrue(hasattr(b, 'd_dt'))
        self.assertEqual(b.d_dt.shape, b.shape)
        self.assertEqual(b.d_dt.numer, a.numer)
        self.assertTrue(np.all(a.d_dt.values.ravel() == b.d_dt.values.ravel()))

        b = Vector.as_vector(a, recursive=False)
        self.assertFalse(hasattr(b, 'd_dt'))

        # Other cases
        b = Vector.as_vector((1,2,3))
        self.assertTrue(type(b), Vector)
        self.assertTrue(b.unit_ is None)
        self.assertEqual(b.shape, ())
        self.assertEqual(b.numer, (3,))
        self.assertEqual(b, (1,2,3))

        a = np.arange(120).reshape((2,4,3,5))
        b = Vector.as_vector(a)
        self.assertTrue(type(b), Vector)
        self.assertTrue(b.unit_ is None)
        self.assertEqual(b.shape, (2,4,3))
        self.assertEqual(b.numer, (5,))
        self.assertEqual(b, a)

##########################################################################################
