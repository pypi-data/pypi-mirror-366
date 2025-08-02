##########################################################################################
# tests/test_pair_swapxy.py
##########################################################################################

import numpy as np
import unittest

from polymath import Pair


class Test_Pair_clip2d(unittest.TestCase):

    def runTest(self):

        a = Pair([[1,2],[3,4],[5,6]])

        self.assertEqual(a.clip2d([2,3],[4,5], remask=False), [[2,3],[3,4],[4,5]])
        self.assertTrue(np.all(a.clip2d([2,3],[4,5], remask=True).mask ==
                                        [True,False,True]))

        self.assertEqual(a.clip2d(None,[4,5], remask=False), [[1,2],[3,4],[4,5]])
        self.assertTrue(np.all(a.clip2d(None,[4,5], remask=True).mask ==
                                        [False,False,True]))

        lower = Pair([2,3], True)
        self.assertEqual(a.clip2d(lower,[4,5], remask=False), [[1,2],[3,4],[4,5]])
        self.assertTrue(np.all(a.clip2d(lower,[4,5], remask=True).mask ==
                                        [False,False,True]))

##########################################################################################
