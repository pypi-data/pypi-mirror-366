##########################################################################################
# tests/test_quaternion_euler.py
##########################################################################################

import numpy as np
import unittest

from polymath import Quaternion


class Test_Quaternion_euler(unittest.TestCase):

    def runTest(self):

        np.random.seed(7599)

        # Quaternion to Euler and back, one Quaternion
        for code in Quaternion._AXES2TUPLE.keys():
            a = Quaternion(np.random.rand(4)).unit()
            euler = a.to_euler(code)
            b = Quaternion.from_euler(*euler, axes=code)

        DEL = 1.e-14
        for j in range(4):
            self.assertAlmostEqual(a.values[j], b.values[j], delta=DEL)

        # Quaternion to Euler and back, N Quaternions
        N = 100
        for code in Quaternion._AXES2TUPLE.keys():
            a = Quaternion(np.random.rand(N,4)).unit()
            euler = a.to_euler(code)
            b = Quaternion.from_euler(*euler, axes=code)

        DEL = 1.e-14
        for i in range(N):
            for j in range(4):
                self.assertAlmostEqual(a.values[i,j], b.values[i,j], delta=DEL)

        # Quaternion to Matrix3 to Euler and back
        N = 100
        for code in Quaternion._AXES2TUPLE.keys():
            a = Quaternion(np.random.rand(N,4)).unit()
            mats = a.to_matrix3()
            euler = mats.to_euler(code)
            b = Quaternion.from_euler(*euler, axes=code)

        DEL = 1.e-14
        for i in range(N):
            for j in range(4):
                self.assertAlmostEqual(a.values[i,j], b.values[i,j], delta=DEL)

##########################################################################################
