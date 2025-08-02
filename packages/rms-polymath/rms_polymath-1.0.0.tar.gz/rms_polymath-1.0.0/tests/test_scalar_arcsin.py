##########################################################################################
# tests/test_scalar_arcsin.py
##########################################################################################

import numpy as np
import unittest

from polymath import Scalar, Unit


class Test_Scalar_arcsin(unittest.TestCase):

    def runTest(self):

        np.random.seed(7221)

        # Individual values
        self.assertEqual(Scalar(-0.3).arcsin(), np.arcsin(-0.3))
        self.assertEqual(type(Scalar(-0.3).arcsin()), Scalar)

        self.assertEqual(Scalar(0.).arcsin(), np.arcsin(0.))
        self.assertEqual(Scalar(0).arcsin(), 0.)

        self.assertAlmostEqual(Scalar( 1.).arcsin(),  np.pi/2., 1.e-15)
        self.assertAlmostEqual(Scalar(-1.).arcsin(), -np.pi/2., 1.e-15)
        self.assertEqual(Scalar(0).arcsin(), 0.)

        # Multiple values
        self.assertEqual(Scalar((-0.1,0.,0.1)).arcsin(), np.arcsin((-0.1,0.,0.1)))
        self.assertEqual(type(Scalar((-0.1,0.,0.1)).arcsin()), Scalar)

        # Arrays
        N = 1000
        x = Scalar(np.random.randn(N))
        y = x.arcsin()
        for i in range(N):
            if abs(x.values[i]) <= 1.:
                self.assertEqual(y[i], np.arcsin(x.values[i]))
                self.assertFalse(y.mask[i])
            else:
                self.assertTrue(y.mask[i])

        for i in range(N-1):
            if np.all(np.abs(x.values[i:i+2]) <= 1):
                self.assertEqual(y[i:i+2], np.arcsin(x.values[i:i+2]))

        # Test valid unit
        values = np.random.randn(10)
        random = Scalar(values, unit=Unit.KM)
        self.assertRaises(ValueError, Scalar.arcsin, random)

        values = np.random.randn(10)
        random = Scalar(values, unit=Unit.SECONDS)
        self.assertRaises(ValueError, Scalar.arcsin, random)

        values = np.random.randn(10)
        random = Scalar(values, unit=Unit.DEG)
        self.assertRaises(ValueError, Scalar.arcsin, random)

        values = np.random.randn(10)
        random = Scalar(values, unit=Unit.RAD)
        self.assertRaises(ValueError, Scalar.arcsin, random)

        x = Scalar(3.25, unit=Unit.UNITLESS)
        self.assertTrue(x.arcsin().mask)

        x = Scalar(3.25, unit=Unit.UNITLESS)
        self.assertRaises(ValueError, x.arcsin, recursive=True, check=False)

        x = Scalar(0.25, unit=Unit.UNITLESS)
        self.assertFalse(x.arcsin().mask)
        self.assertEqual(x.arcsin(), np.arcsin(x.values))

        # Units should be removed
        values = np.random.randn(10)
        random = Scalar(values, unit=Unit.UNITLESS)
        self.assertTrue(random.arcsin().unit_ is None)

        # Masks
        N = 100
        x = Scalar(np.random.randn(N), mask=(np.random.randn(N) < -1.))
        y = x.arcsin()
        self.assertTrue(np.all(y.mask[x.mask]))

        # Derivatives
        N = 100
        x = Scalar(np.random.randn(N))
        x.insert_deriv('t', Scalar(np.random.randn(N)))

        self.assertIn('t', x.derivs)
        self.assertTrue(hasattr(x, 'd_dt'))

        self.assertIn('t', x.arcsin().derivs)
        self.assertTrue(hasattr(x.arcsin(), 'd_dt'))

        EPS = 1.e-6
        y1 = (x + EPS).arcsin()
        y0 = (x - EPS).arcsin()
        dy_dx = 0.5 * (y1 - y0) / EPS
        dy_dt = x.arcsin().d_dt

        DEL = 3.e-6
        for i in range(N):
            if not dy_dt[i].mask and abs(dy_dt[i]) < 10:    # big errors near end points
                self.assertAlmostEqual(dy_dx[i] * x.d_dt[i], dy_dt[i], delta=DEL)

        # Derivatives should be removed if necessary
        self.assertEqual(x.arcsin(recursive=False).derivs, {})
        self.assertTrue(hasattr(x, 'd_dt'))
        self.assertFalse(hasattr(x.arcsin(recursive=False), 'd_dt'))

        # Read-only status should NOT be preserved
        N = 10
        x = Scalar(np.random.randn(N))
        self.assertFalse(x.readonly)
        self.assertFalse(x.arcsin().readonly)
        self.assertTrue(x.as_readonly().readonly)
        self.assertFalse(x.as_readonly().arcsin().readonly)

        # Without Checking
        N = 1000
        x = Scalar(np.random.randn(N))
        self.assertRaises(ValueError, x.arcsin, check=False)

        x = Scalar(np.random.randn(N).clip(-1,1))
        self.assertEqual(x.arcsin(), np.arcsin(x.values))

##########################################################################################
