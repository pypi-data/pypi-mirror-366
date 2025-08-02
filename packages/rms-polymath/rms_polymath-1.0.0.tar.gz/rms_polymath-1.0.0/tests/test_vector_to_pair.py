##########################################################################################
# tests/test_vector_to_pair.py
##########################################################################################

import numpy as np
import unittest

from polymath import Vector


class Test_Vector_to_pair(unittest.TestCase):

    def runTest(self):

        np.random.seed(1458)

        N = 100
        for size in (2,3,4):
            for mask in (True, False, np.random.randn(N) > 0.7):
                derivs = {'t': Vector(np.random.randn(N,size)),
                          'x': Vector(np.random.randn(N,size,2), drank=1)}
                vec = Vector(np.random.randn(N,size), mask=mask, derivs=derivs)
                for i0 in range(-size, size):
                    for i1 in range(-size, size):
                        if (i0 - i1) % size == 0:
                            with self.assertRaises(IndexError) as cm:
                                pair = vec.to_pair((i0,i1))
                            self.assertEqual(str(cm.exception),
                                             'duplicated axes in Vector.to_pair(): '
                                             f'{i0}, {i1}')
                        else:
                            pair = vec.to_pair((i0,i1), recursive=False)
                            self.assertTrue(np.all(pair._values[:,0]
                                                   == vec._values[:,i0]))
                            self.assertTrue(np.all(pair._values[:,1]
                                                   == vec._values[:,i1]))
                            self.assertIs(pair._mask, vec._mask)
                            self.assertEqual(pair._derivs, {})

                            pair = vec.to_pair((i0,i1), recursive=True)
                            self.assertTrue(np.all(pair._values[:,0] ==
                                                   vec._values[:,i0]))
                            self.assertTrue(np.all(pair._values[:,1] ==
                                                   vec._values[:,i1]))
                            self.assertIs(pair._mask, vec._mask)

                            self.assertTrue(np.all(pair._derivs['t']._values[:,0] ==
                                                   vec._derivs['t']._values[:,i0]))
                            self.assertTrue(np.all(pair._derivs['t']._values[:,1] ==
                                                   vec._derivs['t']._values[:,i1]))
                            self.assertTrue(np.all(pair._derivs['x']._values[:,0] ==
                                                   vec._derivs['x']._values[:,i0]))
                            self.assertTrue(np.all(pair._derivs['x']._values[:,1] ==
                                                   vec._derivs['x']._values[:,i1]))

                    with self.assertRaises(IndexError) as cm:
                        pair = vec.to_pair((1,size))
                    self.assertEqual(str(cm.exception),
                                     f'axes[1] out of range ({-size},{size}) in '
                                     'Vector.to_pair()')

##########################################################################################
