##########################################################################################
# tests/test_qube_unit.py
##########################################################################################

import numpy as np
import unittest

from polymath import Boolean, Matrix3, Quaternion, Scalar, Unit


class Test_Qube_unit(unittest.TestCase):

    def runTest(self):

        ##################################################################################
        # set_unit(self, unit, override=False)
        ##################################################################################

        a = Scalar((1.,2.,3.))
        self.assertEqual(a.units, None)
        self.assertTrue(np.all(a.values == (1,2,3)))

        a.set_unit(Unit.KM)
        self.assertEqual(a.units, Unit.KM)
        self.assertTrue(np.all(a.values == (1,2,3)))

        a.set_unit(Unit.CM)
        self.assertEqual(a.units, Unit.CM)
        self.assertTrue(np.all(a.values == (1,2,3)))

        self.assertRaises(ValueError, a.set_unit, Unit.DEG)   # incompatible

        a.set_unit(Unit.M)
        self.assertEqual(a.units, Unit.M)
        self.assertTrue(np.all(a.values == (1,2,3)))

        a = a.as_readonly()
        self.assertTrue(a.readonly)
        self.assertRaises(ValueError, a.set_unit, Unit.KM)

        a.set_unit(Unit.KM, override=True)
        self.assertTrue(a.readonly)
        self.assertEqual(a.units, Unit.KM)
        self.assertTrue(np.all(a.values == (1,2,3)))

        # Classes for which units are not allowed
        a = Matrix3([(1,0,0),(0,1,0),(0,0,1)])
        self.assertRaises(TypeError, a.set_unit, Unit.KM)

        a = Quaternion((1,0,0,0))
        self.assertRaises(TypeError, a.set_unit, Unit.KM)

        a = Boolean([True, False])
        self.assertRaises(TypeError, a.set_unit, Unit.KM)

        ##################################################################################
        # without_unit(self, recursive=True)
        ##################################################################################

        a = Scalar((1.,2.,3.), unit=Unit.KM)
        b = a.without_unit()
        self.assertEqual(a.units, Unit.KM)

        self.assertEqual(b.units, None)
        self.assertTrue(np.all(a.values == b.values))

        self.assertEqual(a.readonly, False)
        self.assertEqual(b.readonly, False)

        a = a.as_readonly()
        self.assertEqual(a.readonly, True)

        b = a.without_unit()
        self.assertEqual(b.readonly, True)
        self.assertEqual(b.units, None)
        self.assertTrue(np.all(b.values == (1,2,3)))

        ##################################################################################
        # into_unit(self, recursive=True)
        ##################################################################################

        a = Scalar((1.,2.,3.))
        self.assertEqual(a.units, None)
        self.assertTrue(np.all(a.values == (1,2,3)))

        a.set_unit(Unit.M)
        self.assertEqual(a.units, Unit.M)
        self.assertTrue(np.all(a.values == (1,2,3)))

        vals = a.into_unit()
        self.assertTrue(np.all(vals == (1000, 2000, 3000)))

        vals = a.into_unit(recursive=True)
        self.assertTrue(np.all(vals[0] == (1000, 2000, 3000)))
        self.assertTrue(vals[1] == {})

        a = Scalar((1.,2.,3.), unit=Unit.M)
        da_dt = Scalar((4., 5., 6.), unit=Unit.CM/Unit.S)
        a.insert_deriv('t', da_dt)

        vals = a.into_unit(recursive=False)
        self.assertTrue(np.all(vals == (1000, 2000, 3000)))

        vals = a.into_unit(recursive=True)
        self.assertTrue(np.all(vals[0] == (1000, 2000, 3000)))
        self.assertEqual(set(vals[1].keys()), {'t'})
        self.assertTrue(np.all(vals[1]['t'] == (400000, 500000, 600000)))

##########################################################################################
