##########################################################################################
# Matrix.column_vector() and Matrix.column_vectors()
##########################################################################################

import numpy as np
import unittest

from polymath import Matrix, Vector, Vector3, Unit


class Test_Matrix_column_vectors(unittest.TestCase):

    def runTest(self):

        np.random.seed(2897)

        N = 100
        a = Matrix(np.random.randn(N,7,1))
        b = a.column_vector(0)
        self.assertTrue(np.all(a.values.ravel() == b.values.ravel()))
        self.assertEqual(a.shape, b.shape)
        self.assertEqual(a.values.shape, (N,7,1))
        self.assertEqual(b.values.shape, (N,7))
        self.assertEqual(type(b), Vector)

        c = a.column_vectors()
        self.assertTrue(np.all(a.values.ravel() == c[0].values.ravel()))
        self.assertEqual(a.shape, c[0].shape)
        self.assertEqual(b, c[0])
        self.assertEqual(type(c[0]), Vector)

        N = 100
        a = Matrix(np.random.randn(N,3,2))
        b = a.column_vector(0)
        self.assertEqual(a.shape, b.shape)
        self.assertEqual(a.values.shape, (N,3,2))
        self.assertEqual(b.values.shape, (N,3))
        self.assertEqual(type(b), Vector3)

        self.assertEqual(type(a.column_vector(0, classes=Vector)), Vector)

        c = a.column_vectors()
        self.assertEqual(a.shape, c[0].shape)
        self.assertEqual(b, c[0])
        self.assertEqual(type(c[0]), Vector3)

        # check unit and masks
        N = 100
        a = Matrix(np.random.randn(N,4,4), mask=(np.random.randn(N) < -0.5),
                   unit=Unit.RAD)
        c = a.column_vectors()
        self.assertEqual(a.unit_, c[0].unit_)

        b = a.column_vector(1)
        self.assertEqual(b, c[1])
        self.assertEqual(a.unit_, b.unit_)

        self.assertTrue(np.all(b.values == a.values[...,1]))
        self.assertTrue(np.all(b.mask == a.mask))

        b[0].values[0] = 22.
        self.assertEqual(a[0].values[0,1], 22.)

        # check derivatives
        N = 100
        a = Matrix(np.random.randn(N,3,4), mask=(np.random.randn(N) < -0.5))
        da_dt = Matrix(np.random.randn(N,3,4))
        da_dv = Matrix(np.random.randn(N,3,4,2), drank=1)

        a.insert_deriv('t', da_dt)
        a.insert_deriv('v', da_dv)
        self.assertTrue(hasattr(a, 'd_dt'))
        self.assertTrue(hasattr(a, 'd_dv'))

        b = a.column_vector(3, recursive=False)
        self.assertFalse(hasattr(b, 'd_dt'))
        self.assertFalse(hasattr(b, 'd_dv'))

        b = a.column_vector(3, recursive=True)
        self.assertTrue(hasattr(b, 'd_dt'))
        self.assertTrue(hasattr(b, 'd_dv'))

        self.assertEqual(b.d_dt.shape, a.shape)
        self.assertEqual(b.d_dt.numer, (3,))
        self.assertEqual(b.d_dt.denom, ())

        self.assertEqual(b.d_dv.shape, a.shape)
        self.assertEqual(b.d_dv.numer, (3,))
        self.assertEqual(b.d_dv.denom, (2,))

        self.assertTrue(np.all(a.values[...,3] == b.values))
        self.assertTrue(np.all(a.mask == b.mask))
        self.assertTrue(np.all(a.d_dt.values[...,3] == b.d_dt.values))
        self.assertTrue(np.all(a.d_dv.values[...,3,:] == b.d_dv.values))

        c = a.column_vectors(recursive=False)[3]
        self.assertFalse(hasattr(c, 'd_dt'))
        self.assertFalse(hasattr(c, 'd_dv'))

        c = a.column_vectors(recursive=True)[3]
        self.assertTrue(hasattr(c, 'd_dt'))
        self.assertTrue(hasattr(c, 'd_dv'))

        self.assertEqual(c.d_dt.shape, a.shape)
        self.assertEqual(c.d_dt.numer, (3,))
        self.assertEqual(c.d_dt.denom, ())

        self.assertEqual(c.d_dv.shape, a.shape)
        self.assertEqual(c.d_dv.numer, (3,))
        self.assertEqual(c.d_dv.denom, (2,))

        self.assertTrue(np.all(a.values[...,3] == c.values))
        self.assertTrue(np.all(a.mask == c.mask))
        self.assertTrue(np.all(a.d_dt.values[...,3] == c.d_dt.values))
        self.assertTrue(np.all(a.d_dv.values[...,3,:] == c.d_dv.values))

        # read-only status
        N = 10
        a = Matrix(np.random.randn(N,4,4), mask=(np.random.randn(N) < -0.5))
        self.assertFalse(a.readonly)

        b = a.column_vector(3)
        self.assertFalse(b.readonly)

        c = a.column_vectors()[3]
        self.assertFalse(c.readonly)

        a = Matrix(np.random.randn(N,4,4), mask=(np.random.randn(N) < -0.5))
        a = a.as_readonly()
        self.assertTrue(a.readonly)

        b = a.column_vector(3)
        self.assertTrue(b.readonly) # preserved because of overlapping memory

        c = a.column_vectors()[3]
        self.assertTrue(c.readonly) # preserved because of overlapping memory

##########################################################################################
