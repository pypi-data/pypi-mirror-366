##########################################################################################
# tests/test_scalar_arccos.py
##########################################################################################

import numpy as np
import unittest

from polymath import Scalar, Unit


class Test_Scalar_arccos(unittest.TestCase):

    def runTest(self):

        np.random.seed(8994)

        # Individual values
        self.assertEqual(Scalar(-0.3).arccos(), np.arccos(-0.3))
        self.assertEqual(type(Scalar(-0.3).arccos()), Scalar)

        self.assertEqual(Scalar(0.).arccos(), np.arccos(0.))
        self.assertEqual(Scalar(1).arccos(), 0.)

        self.assertAlmostEqual(Scalar( 1.).arccos(), 0.,       1.e-15)
        self.assertAlmostEqual(Scalar(-1.).arccos(), np.pi,    1.e-15)
        self.assertAlmostEqual(Scalar( 0.).arccos(), np.pi/2., 1.e-15)

        # Multiple values
        self.assertEqual(Scalar((-0.1,0.,0.1)).arccos(), np.arccos((-0.1,0.,0.1)))
        self.assertEqual(type(Scalar((-0.1,0.,0.1)).arccos()), Scalar)

        # Arrays
        N = 1000
        x = Scalar(np.random.randn(N))
        y = x.arccos()
        for i in range(N):
            if abs(x.values[i]) <= 1.:
                self.assertEqual(y[i], np.arccos(x.values[i]))
                self.assertFalse(y.mask[i])
            else:
                self.assertTrue(y.mask[i])

        for i in range(N-1):
            if np.all(np.abs(x.values[i:i+2]) <= 1):
                self.assertEqual(y[i:i+2], np.arccos(x.values[i:i+2]))

        # Test valid unit
        values = np.random.randn(10)
        random = Scalar(values, unit=Unit.KM)
        self.assertRaises(ValueError, Scalar.arccos, random)

        values = np.random.randn(10)
        random = Scalar(values, unit=Unit.SECONDS)
        self.assertRaises(ValueError, Scalar.arccos, random)

        values = np.random.randn(10)
        random = Scalar(values, unit=Unit.DEG)
        self.assertRaises(ValueError, Scalar.arccos, random)

        values = np.random.randn(10)
        random = Scalar(values, unit=Unit.RAD)
        self.assertRaises(ValueError, Scalar.arccos, random)

        x = Scalar(3.25, unit=Unit.UNITLESS)
        self.assertTrue(x.arccos().mask)

        x = Scalar(3.25, unit=Unit.UNITLESS)
        self.assertRaises(ValueError, x.arccos, recursive=True, check=False)

        x = Scalar(0.25, unit=Unit.UNITLESS)
        self.assertFalse(x.arccos().mask)
        self.assertEqual(x.arccos(), np.arccos(x.values))

        # Units should be removed
        values = np.random.randn(10)
        random = Scalar(values, unit=Unit.UNITLESS)
        self.assertTrue(random.arccos().unit_ is None)

        # Masks
        N = 100
        x = Scalar(np.random.randn(N), mask=(np.random.randn(N) < -1.))
        y = x.arccos()
        self.assertTrue(np.all(y.mask[x.mask]))

        # Derivatives
        N = 100
        x = Scalar(np.random.randn(N))
        x.insert_deriv('t', Scalar(np.random.randn(N)))

        self.assertIn('t', x.derivs)
        self.assertTrue(hasattr(x, 'd_dt'))

        self.assertIn('t', x.arccos().derivs)
        self.assertTrue(hasattr(x.arccos(), 'd_dt'))

        EPS = 1.e-6
        y1 = (x + EPS).arccos()
        y0 = (x - EPS).arccos()
        dy_dx = 0.5 * (y1 - y0) / EPS
        dy_dt = x.arccos().d_dt

        DEL = 5.e-6
        for i in range(N):
            if not dy_dt[i].mask and abs(dy_dt[i]) < 10:  # big errors near end points
                self.assertAlmostEqual(dy_dx[i] * x.d_dt[i], dy_dt[i], delta=DEL)

        # Derivatives should be removed if necessary
        self.assertEqual(x.arccos(recursive=False).derivs, {})
        self.assertTrue(hasattr(x, 'd_dt'))
        self.assertFalse(hasattr(x.arccos(recursive=False), 'd_dt'))

        # Read-only status should NOT be preserved
        N = 10
        x = Scalar(np.random.randn(N))
        self.assertFalse(x.readonly)
        self.assertFalse(x.arccos().readonly)
        self.assertTrue(x.as_readonly().readonly)
        self.assertFalse(x.as_readonly().arccos().readonly)

        # Without Checking
        N = 1000
        x = Scalar(np.random.randn(N))
        self.assertRaises(ValueError, x.arccos, check=False)

        x = Scalar(np.random.randn(N).clip(-1,1))
        self.assertEqual(x.arccos(), np.arccos(x.values))

##########################################################################################
