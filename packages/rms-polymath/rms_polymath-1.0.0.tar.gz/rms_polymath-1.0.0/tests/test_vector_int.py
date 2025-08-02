##########################################################################################
# tests/test_vector_int.py
##########################################################################################

import numpy as np
import unittest

from polymath import Pair, Unit, Vector, Vector3


class Test_Vector_int(unittest.TestCase):

    def runTest(self):

        np.random.seed(5394)

        # int input
        a = Vector(np.arange(30).reshape(10,3))
        b = a.int()
        self.assertIs(a, b)

        a = Vector3(np.arange(30).reshape(10,3), unit=Unit.KM)
        with self.assertRaises(ValueError) as cm:
            b = a.int()
        self.assertEqual(str(cm.exception), 'Vector3.int() unit is not permitted: km')

        a = Pair(np.arange(60).reshape(10,2,3), drank=1)
        with self.assertRaises(ValueError) as cm:
            b = a.int()
        self.assertEqual(str(cm.exception), 'Pair.int() does not support denominators')

        a = Pair(np.arange(-40.,40.).reshape(-1,2)/10.)
        b = a.int()
        self.assertTrue(np.all(b.vals == np.floor(a.vals)))
        self.assertTrue(b.is_int())
        self.assertFalse(b.mask)

        a = Pair(np.arange(-40.,40.).reshape(-1,2)/10.)
        b = a.int(remask=True)
        self.assertTrue(np.all(b.vals == np.floor(a.vals)))
        self.assertTrue(b.is_int())
        self.assertTrue(np.all(b.vals[b.mask] < 0))
        self.assertTrue(np.all(b.vals[~b.mask] >= 0))

        # top = 2
        a = Pair(np.arange(-40.,40.).reshape(-1,2)/10.)
        b = a.int(top=(2,3))

        # TBD!

##########################################################################################
