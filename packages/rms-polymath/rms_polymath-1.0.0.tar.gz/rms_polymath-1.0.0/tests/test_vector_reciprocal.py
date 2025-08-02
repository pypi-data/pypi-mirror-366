##########################################################################################
# tests/test_vector_reciprocal.py
##########################################################################################

import numpy as np
import unittest

from polymath import Pair, Vector, Vector3


class Test_Vector_reciprocal(unittest.TestCase):

    def runTest(self):

        np.random.seed(4912)

        vec = Pair([[1,0],[0,2]], drank=1)
        inverse = vec.reciprocal()
        self.assertTrue(np.all(inverse == [[1,0],[0,0.5]]))
        self.assertIs(type(inverse), type(vec))

        vec = Vector3([[0,1,0],[0,0,2],[4,0,0]], drank=1)
        inverse = vec.reciprocal()
        self.assertTrue(np.all(inverse == [[0,0,0.25],[1,0,0],[0,0.5,0]]))
        self.assertIs(type(inverse), type(vec))

        N = 100
        vec = Vector(np.random.randn(N,4,4), drank=1)
        inverse = vec.reciprocal()
        product = vec.vals @ inverse.vals
        diffs = product - [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
        # print(np.abs(diffs).max())
        self.assertTrue(np.abs(diffs).max() < 1.e-13)

        # Determinant == 0
        vec = Pair(np.zeros((2,2)), drank=1)
        with self.assertRaises(ValueError) as cm:
            inverse = vec.reciprocal(nozeros=True)
        self.assertEqual(str(cm.exception), 'Matrix.inverse() input is singular')

        inverse = vec.reciprocal()
        self.assertTrue(inverse.mask)

        # Invalid input
        with self.assertRaises(TypeError) as cm:
            inverse = Vector3(np.arange(9).reshape(3,3)).reciprocal()
        self.assertEqual(str(cm.exception), 'Vector3.reciprocal() is not supported '
                                            'unless it represents a Jacobian')

##########################################################################################
