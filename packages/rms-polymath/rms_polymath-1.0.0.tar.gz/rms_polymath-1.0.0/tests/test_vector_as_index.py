##########################################################################################
# tests/test_vector_as_index.py
#
# vector.as_index()
# vector.as_index_and_mask()
##########################################################################################

import numpy as np
import unittest

from polymath import Vector, Qube


class Test_Vector_as_index(unittest.TestCase):

    def runTest(self):

        # Array to test for indexing
        array = np.arange(1000).reshape(10,10,10)

        # Use NumPy to create an index for every multiple of 13
        index1 = np.where(array % 13 == 0)

        # There are 77 elements. Reshape into a 7x11 array
        index2 = (index1[0].reshape((7,11)),
                  index1[1].reshape((7,11)),
                  index1[2].reshape((7,11)))

        # Convert to a 3-vector of indices
        values = np.empty((7,11,3), dtype='int')
        values[...,0] = index2[0]
        values[...,1] = index2[1]
        values[...,2] = index2[2]

        vec = Vector(values)

        # Index into array
        index13 = vec.as_index()

        # Show that the index has been recovered
        indexed = array[index13]
        self.assertEqual(indexed.shape, (7,11))
        self.assertEqual(indexed.shape, vec.shape)
        self.assertTrue(np.all(indexed % 13) == 0)
        self.assertTrue(np.all(indexed.ravel() // 13 == np.arange(77)))

        # Try indexing a Qube instead of a NumPy array
        qube = Qube(array)
        self.assertEqual(qube[index13].shape, (7,11))
        self.assertEqual(qube[index13] % 13, 0)
        self.assertEqual(qube[index13].flatten() // 13, np.arange(77))

        # Try indexing a Qube instead of a NumPy array
        qube = Qube(array)
        self.assertEqual(qube[index13].shape, (7,11))
        self.assertEqual(qube[index13] % 13, 0)
        self.assertEqual(qube[index13].flatten() // 13, np.arange(77))

        # Mask the first two items in the vector
        mask = np.zeros(vec.shape, dtype='bool')
        mask[0,0] = True
        mask[0,1] = True
        vec_one_masked = Vector(vec, mask)

        # This will create a flattened array with the first two items missing
        new_index = vec_one_masked.as_index(masked=None)
        self.assertEqual(qube[new_index].shape, (7*11-2,))
        self.assertEqual(qube[new_index] // 13, np.arange(2,77))

        # This will fill in the last item of the array in place of the first two
        # items
        new_index = vec_one_masked.as_index(masked=(9,9,9))
        self.assertEqual(qube[new_index].shape, (7,11))
        self.assertEqual(qube[new_index][0,0], 999)
        self.assertEqual(qube[new_index][0,1], 999)

        flattened = qube[new_index].flatten()
        self.assertEqual(flattened[2:], 13 * np.arange(2,77))

        # as_index_and_mask()
        vec = Vector([1.,2.,3.])
        with self.assertRaises(TypeError) as cm:
            vec.as_index_and_mask()
        self.assertEqual(str(cm.exception), 'floating-point indexing is not permitted')

        vec = Vector(np.arange(12).reshape(6,2), drank=1)
        with self.assertRaises(ValueError) as cm:
            vec.as_index_and_mask()
        self.assertEqual(str(cm.exception), 'Vector.as_index_and_mask() does not support '
                                            'denominators')

        vec = Vector([1,2,3], True)
        self.assertEqual(vec.as_index_and_mask(purge=True), ((), False))

        indx, mask = vec.as_index_and_mask(purge=False)
        self.assertEqual(indx, (1,2,3))
        self.assertEqual(mask, True)

        indx, mask = vec.as_index_and_mask(purge=False, masked=0)
        self.assertEqual(indx, (0,0,0))
        self.assertEqual(mask, True)

        vals = np.arange(9).reshape(3,3)
        vec = Vector(vals, [False, False, True])
        indx, mask = vec.as_index_and_mask(purge=True)
        self.assertTrue(np.all(indx[0] == (0,3)))
        self.assertTrue(np.all(indx[1] == (1,4)))
        self.assertTrue(np.all(indx[2] == (2,5)))
        self.assertEqual(mask, False)

        vec = Vector(vals, [False, False, True])
        indx, mask = vec.as_index_and_mask(purge=False)
        self.assertTrue(np.all(indx[0] == (0,3,6)))
        self.assertTrue(np.all(indx[1] == (1,4,7)))
        self.assertTrue(np.all(indx[2] == (2,5,8)))
        self.assertTrue(np.all(mask == [False, False, True]))

        vec = Vector(vals, [False, False, True])
        indx, mask = vec.as_index_and_mask(purge=False, masked=0)
        self.assertTrue(np.all(indx[0] == (0,3,0)))
        self.assertTrue(np.all(indx[1] == (1,4,0)))
        self.assertTrue(np.all(indx[2] == (2,5,0)))
        self.assertTrue(np.all(mask == [False, False, True]))

##########################################################################################
