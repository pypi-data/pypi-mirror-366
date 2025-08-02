##########################################################################################
# tests/test_scalar_log.py
##########################################################################################

import numpy as np
import unittest

from polymath import Scalar, Unit


class Test_Scalar_log(unittest.TestCase):

    def runTest(self):

        np.random.seed(8622)

        # Individual values
        self.assertEqual(Scalar(0.3).log(), np.log(0.3))
        self.assertEqual(type(Scalar(0.3).log()), Scalar)

        self.assertEqual(Scalar(1.).log(), np.log(1.))
        self.assertEqual(Scalar(1).log(), 0.)

        # Multiple values
        self.assertEqual(Scalar((1,2,3)).log(), np.log((1,2,3)))
        self.assertEqual(type(Scalar((1,2,3)).log()), Scalar)

        # Arrays
        N = 1000
        x = Scalar(np.random.randn(N))
        y = x.log()
        for i in range(N):
            if x.values[i] > 0.:
                self.assertEqual(y[i], np.log(x.values[i]))
                self.assertFalse(y.mask[i])
            else:
                self.assertTrue(y.mask[i])

        for i in range(N-1):
            if np.all(x.values[i:i+2] >= 0):
                self.assertEqual(y[i:i+2], np.log(x.values[i:i+2]))

        # Test valid unit
        values = np.abs(np.random.randn(10))
        random = Scalar(values, unit=Unit.KM)
        self.assertEqual(random.log(), Scalar(np.log(values)))

        values = np.abs(np.random.randn(10))
        random = Scalar(values, unit=Unit.SECONDS)
        self.assertEqual(random.log(), Scalar(np.log(values)))

        values = np.abs(np.random.randn(10))
        random = Scalar(values, unit=Unit.DEG)
        self.assertEqual(random.log(), Scalar(np.log(values)))

        values = np.abs(np.random.randn(10))
        random = Scalar(values, unit=Unit.UNITLESS)
        self.assertEqual(random.log(), Scalar(np.log(values)))

        x = Scalar(4., unit=Unit.UNITLESS)
        self.assertFalse(x.log().mask)

        x = Scalar(-4., unit=Unit.UNITLESS)
        self.assertTrue(x.log().mask)

        # Unit should be removed
        random = Scalar(values, unit=Unit.DEG)
        self.assertTrue(random.log()._unit is None)

        # Masks
        N = 100
        x = Scalar(np.random.randn(N), mask=(np.random.randn(N) < -1.))
        y = x.log()
        self.assertTrue(np.all(y.mask[x.mask]))

        # Derivatives
        N = 100
        x = Scalar(np.random.randn(N))
        x.insert_deriv('t', Scalar(np.random.randn(N)))

        self.assertIn('t', x.derivs)
        self.assertTrue(hasattr(x, 'd_dt'))

        self.assertIn('t', x.log().derivs)
        self.assertTrue(hasattr(x.log(), 'd_dt'))

        EPS = 1.e-6
        y1 = (x + EPS).log()
        y0 = (x - EPS).log()
        dy_dx = 0.5 * (y1 - y0) / EPS
        dy_dt = x.log().d_dt

        DEL = 1.e-5
        for i in range(N):
            self.assertAlmostEqual(dy_dx[i] * x.d_dt[i], dy_dt[i],
                                   delta = DEL * abs(dy_dt[i]))

        # Derivatives should be removed if necessary
        self.assertEqual(x.log(recursive=False).derivs, {})
        self.assertTrue(hasattr(x, 'd_dt'))
        self.assertFalse(hasattr(x.log(recursive=False), 'd_dt'))

        # Read-only status should NOT be preserved
        N = 10
        x = Scalar(np.random.randn(N))
        self.assertFalse(x.readonly)
        self.assertFalse(x.log().readonly)
        self.assertTrue(x.as_readonly().readonly)
        self.assertFalse(x.as_readonly().log().readonly)

        # Without Checking
        N = 1000
        x = Scalar(np.random.randn(N))
        self.assertRaises(ValueError, x.log, check=False)

        x = Scalar(np.random.randn(N).clip(1.e-99,1.e99))
        self.assertEqual(x.log(), np.log(x.values))

##########################################################################################
