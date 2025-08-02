##########################################################################################
# tests/test_matrix3_euler.py
##########################################################################################

import numpy as np
import unittest

from polymath import Matrix3


class Test_Matrix3_euler(unittest.TestCase):

    def runTest(self):

        np.random.seed(5072)

        DEL = 1.e-12

        N = 30
        euler = (np.random.rand(N) * 2.*np.pi,
                 np.random.rand(N) * 2.*np.pi,
                 np.random.rand(N) * 2.*np.pi)

        a = Matrix3.from_euler(*euler)

        test = a * a.T
        for i in range(N):
            for j in range(3):
                for k in range(3):
                    self.assertAlmostEqual(test.values[i,j,k], int(j==k), delta=DEL)
                    self.assertAlmostEqual(test.values[i,j,k], int(j==k), delta=DEL)

        # Conversion to Euler angles and back always returns the same matrix
        for code in Matrix3._AXES2TUPLE.keys():
            angles = a.to_euler(axes=code)
            b = Matrix3.from_euler(*angles, axes=code)

            self.assertLess(np.abs(a.values - b.values).max(), DEL)

##########################################################################################
