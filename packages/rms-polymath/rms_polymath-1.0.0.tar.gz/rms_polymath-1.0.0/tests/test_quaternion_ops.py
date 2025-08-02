##########################################################################################
# tests/test_quaternion_ops.py
##########################################################################################

import numpy as np
import unittest

from polymath import Quaternion


class Test_Quaternion_ops(unittest.TestCase):

    def runTest(self):

        np.random.seed(8291)

        N = 3
        M = 2
        a = Quaternion(np.random.randn(N,1,4))
        a.insert_deriv('t', Quaternion(np.random.randn(N,1,4,2), drank=1))

        b = Quaternion(np.random.randn(M,4))
        b.insert_deriv('t', Quaternion(np.random.randn(M,4,2), drank=1))

        self.assertEqual(a, a * Quaternion.IDENTITY)
        self.assertEqual(a, a / Quaternion.IDENTITY)

        self.assertEqual(a, a + Quaternion.ZERO)
        self.assertEqual(a, a - Quaternion.ZERO)

        # Multiply...
        (sa,va) = a.to_parts()
        (sb,vb) = b.to_parts()

        # Formula from http://en.wikipedia.org/wiki/Quaternion
        sab = sa * sb - va.dot(vb)
        vab = sa * vb + sb * va + va.cross(vb)

        ab = Quaternion.from_parts(sab, vab)

        DEL = 1.e-14
        self.assertTrue((ab - a*b).rms().max() < DEL)

        dab_dt = a.wod * b.d_dt + a.d_dt * b.wod
        self.assertTrue((dab_dt - (a*b).d_dt).rms().max() < DEL)

        # Divide...
        test = ab / b
        self.assertTrue((test - a).rms().max() < DEL)

        b_inv = b.reciprocal()
        test = ab * b_inv
        self.assertTrue((test - a).rms().max() < DEL)

        dtest_dt = ab.d_dt * b_inv.wod + ab.wod * b_inv.d_dt
        self.assertTrue((dtest_dt - a.d_dt).rms().max() < DEL)

##########################################################################################
