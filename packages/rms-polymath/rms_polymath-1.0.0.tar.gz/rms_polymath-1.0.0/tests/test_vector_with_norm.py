##########################################################################################
# tests/test_vector_with_norm.py
##########################################################################################

import numpy as np
import unittest

from polymath import Vector


class Test_Vector_with_norm(unittest.TestCase):

    def runTest(self):

        np.random.seed(3456)

        for norm in (1., 1.75):

            # Single values
            x = Vector((1.,2.,4.,8.))
            u = x.with_norm(norm=norm)

            self.assertAlmostEqual(np.sum(u.values**2), norm**2, delta=1.e-15)
            self.assertAlmostEqual(x.dot(u), x.norm() * norm, delta=1.e-15)

            x = Vector((1.,2.,4.,8.), mask=True)
            u = x.with_norm(norm=norm)
            self.assertTrue(u.mask is True)

            x = Vector((0.,0.,0.,0.,0.), mask=False)
            u = x.with_norm(norm=norm)
            self.assertTrue(u.mask is True)

            # Arrays and masks
            x = Vector(np.zeros((30,7)))
            u = x.with_norm(norm=norm)
            self.assertTrue(np.all(u.mask))

            x = Vector(np.random.randn(30,7))
            u = x.with_norm(norm=norm)
            self.assertTrue(not np.any(u.mask))

            N = 100
            x = Vector(np.random.randn(N,7),
                       mask=(np.random.randn(N) < -0.3))    # Mask out a fraction
            u = x.with_norm(norm=norm)

            self.assertTrue(np.all(u.mask == x.mask))

            utest = u[~u.mask]
            for i in range(len(utest)):
                self.assertAlmostEqual(utest[i].norm(), norm, delta=1.e-15)

            zeros = (np.random.randn(N) < 0.3)
            x.values[zeros] = 0.
            u = x.with_norm(norm=norm)
            for i in range(N):
                if zeros[i]:
                    self.assertTrue(u[i].mask)
                else:
                    self.assertEqual(u[i].mask, x[i].mask)
                    if not u[i].mask:
                        self.assertAlmostEqual(u[i].norm(), norm, delta=1.e-15)

            # Derivatives, denom = ()
            N = 100
            x = Vector(np.random.randn(N,3))

            x.insert_deriv('t', Vector(np.random.randn(N,3)))
            x.insert_deriv('v', Vector(np.random.randn(N,3,3), drank=1,
                                       mask=(np.random.randn(N) < -0.4)))

            self.assertIn('t', x.derivs)
            self.assertTrue(hasattr(x, 'd_dt'))
            self.assertIn('v', x.derivs)
            self.assertTrue(hasattr(x, 'd_dv'))

            y = x.with_norm(recursive=False)
            self.assertNotIn('t', y.derivs)
            self.assertFalse(hasattr(y, 'd_dt'))
            self.assertNotIn('v', y.derivs)
            self.assertFalse(hasattr(y, 'd_dv'))

            y = x.with_norm(norm=norm)
            self.assertIn('t', y.derivs)
            self.assertTrue(hasattr(y, 'd_dt'))
            self.assertIn('v', y.derivs)
            self.assertTrue(hasattr(y, 'd_dv'))

            EPS = 1.e-6
            y1 = (x + (EPS,0,0)).with_norm(norm=norm)
            y0 = (x - (EPS,0,0)).with_norm(norm=norm)
            dy_dx0 = 0.5 * (y1 - y0) / EPS

            y1 = (x + (0,EPS,0)).with_norm(norm=norm)
            y0 = (x - (0,EPS,0)).with_norm(norm=norm)
            dy_dx1 = 0.5 * (y1 - y0) / EPS

            y1 = (x + (0,0,EPS)).with_norm(norm=norm)
            y0 = (x - (0,0,EPS)).with_norm(norm=norm)
            dy_dx2 = 0.5 * (y1 - y0) / EPS

            dy_dt = (dy_dx0 * x.d_dt.values[:,0] +
                     dy_dx1 * x.d_dt.values[:,1] +
                     dy_dx2 * x.d_dt.values[:,2])

            dy_dv0 = (dy_dx0 * x.d_dv.values[:,0,0] +
                      dy_dx1 * x.d_dv.values[:,1,0] +
                      dy_dx2 * x.d_dv.values[:,2,0])

            dy_dv1 = (dy_dx0 * x.d_dv.values[:,0,1] +
                      dy_dx1 * x.d_dv.values[:,1,1] +
                      dy_dx2 * x.d_dv.values[:,2,1])

            dy_dv2 = (dy_dx0 * x.d_dv.values[:,0,2] +
                      dy_dx1 * x.d_dv.values[:,1,2] +
                      dy_dx2 * x.d_dv.values[:,2,2])

            for i in range(N):
                for k in range(3):
                    self.assertAlmostEqual(y.d_dt.values[i,k], dy_dt.values[i,k],
                                           delta=EPS)
                    self.assertAlmostEqual(y.d_dv.values[i,k,0], dy_dv0.values[i,k],
                                           delta=EPS)
                    self.assertAlmostEqual(y.d_dv.values[i,k,1], dy_dv1.values[i,k],
                                           delta=EPS)
                    self.assertAlmostEqual(y.d_dv.values[i,k,2], dy_dv2.values[i,k],
                                           delta=EPS)

            # Read-only status should be preserved
            N = 10
            y = Vector(np.random.randn(N,3))
            x = Vector(np.random.randn(N,3))

            self.assertFalse(x.readonly)
            self.assertFalse(x.with_norm(norm=norm).readonly)
            self.assertFalse(x.as_readonly().with_norm(norm=norm).readonly)

##########################################################################################
