##########################################################################################
# tests/test_scalar_minimum.py
##########################################################################################

import numpy as np
import unittest

from polymath import Scalar


class Test_Scalar_minimum(unittest.TestCase):

    def runTest(self):

        np.random.seed(2251)

        self.assertRaises(ValueError, Scalar.minimum)

        a = Scalar(np.random.randn(10,1))
        self.assertEqual(Scalar.minimum(a), a)
        self.assertEqual(Scalar.minimum(a,100), a)
        self.assertEqual(Scalar.minimum(a,100,Scalar.MASKED), a)

        b = Scalar(np.random.randn(4,1,10))
        self.assertEqual(Scalar.minimum(a,b).shape, (4,10,10))

        ab = Scalar.minimum(a,b,100,Scalar.MASKED)
        ab2 = Scalar(np.minimum(a.values,b.values))
        self.assertEqual(ab, ab2)

        a = Scalar(np.random.randn(10,1), np.random.randn(10,1) < -0.5)
        b = Scalar(np.random.randn(4,1,10), np.random.randn(4,1,10) < -0.5)
        ab = Scalar.minimum(a,b)

        for i in range(4):
            for j in range(10):
                for k in range(10):
                    if a.mask[j,0] and b.mask[i,0,k]:
                        self.assertTrue(ab[i,j,k].mask)
                    elif a.mask[j,0]:
                        self.assertEqual(ab[i,j,k].vals, b[i,0,k].vals)
                        self.assertFalse(ab[i,j,k].mask)
                    elif b.mask[i,0,k]:
                        self.assertEqual(ab[i,j,k].vals, a[j,0].vals)
                        self.assertFalse(ab[i,j,k].mask)
                    else:
                        self.assertEqual(ab[i,j,k], min(a[j,0],b[i,0,k]))
                        self.assertFalse(ab[i,j,k].mask)

##########################################################################################
