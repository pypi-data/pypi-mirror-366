##########################################################################################
# tests/test_matrix3_quaternion.py
##########################################################################################

import numpy as np
import unittest

from polymath import Matrix, Matrix3, Quaternion


class Test_Matrix3_quaternion(unittest.TestCase):

    def runTest(self):

        np.random.seed(4851)

        N = 100
        q = Quaternion(np.random.randn(N,4)).unit()

        mats = Matrix3.as_matrix3(q)
        q2 = mats.to_quaternion()

        DEL = 3.e-14
        for i in range(N):
            # The sign of the whole quaternion might be reversed.
            t  = q.vals  * np.sign( q.vals[...,0])[:,np.newaxis]
            t2 = q2.vals * np.sign(q2.vals[...,0])[:,np.newaxis]
            self.assertTrue(np.max(np.abs(t - t2)) < DEL)

        ########################
        # Test derivatives
        ########################

        N = 100
        q = Quaternion(np.random.randn(N,4)).unit()
        q.insert_deriv('t', Quaternion(np.random.randn(N,4)))

        m = Matrix3.as_matrix3(q, recursive=True)
        self.assertTrue(hasattr(m, 'd_dt'))
        q2 = Matrix3.to_quaternion(m, recursive=False)

        DEL = 1.e-14
        for i in range(N):
            # The sign of the whole quaternion might be reversed.
            t  = q.vals  * np.sign( q.vals[...,0])[:,np.newaxis]
            t2 = q2.vals * np.sign(q2.vals[...,0])[:,np.newaxis]
            self.assertTrue(np.max(np.abs(t - t2)) < DEL)

        EPS = 1.e-6
        dq = q.d_dt * EPS
        q_prime = q.wod + dq
        m_prime = Matrix3.as_matrix3(q_prime)

        dm = Matrix(m_prime) - Matrix(m)

        DEL = 1.e-4
        for i in range(N):
            self.assertLess((dm[i]/EPS - m.d_dt[i]).rms(), DEL)

##########################################################################################
