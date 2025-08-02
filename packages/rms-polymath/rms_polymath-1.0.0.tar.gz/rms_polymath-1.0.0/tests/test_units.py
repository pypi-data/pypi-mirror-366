##########################################################################################
# test/test_units.py
##########################################################################################

import unittest
import numpy as np

from polymath import Unit


class Test_Units(unittest.TestCase):

    def runTest(self):

        self.assertEqual(repr(Unit.KM),                 "Unit(km)")
        self.assertEqual(repr(Unit.KM*Unit.KM),         "Unit(km**2)")
        self.assertEqual(repr(Unit.KM**2),              "Unit(km**2)")
        self.assertEqual(repr(Unit.KM**(-2)),           "Unit(km**(-2))")
        self.assertEqual(repr(Unit.KM/Unit.S),          "Unit(km/s)")
        self.assertEqual(repr((Unit.KM/Unit.S)**2),     "Unit(km**2/s**2)")
        self.assertEqual(repr((Unit.KM/Unit.S)**(-2)),  "Unit(s**2/km**2)")

        self.assertEqual(str(Unit.KM),                  "km")
        self.assertEqual(str(Unit.KM*Unit.KM),          "km**2")
        self.assertEqual(str(Unit.KM**2),               "km**2")
        self.assertEqual(str(Unit.KM**(-2)),            "km**(-2)")
        self.assertEqual(str(Unit.KM/Unit.S),           "km/s")
        self.assertEqual(str((Unit.KM/Unit.S)**2),      "km**2/s**2")
        self.assertEqual(str((Unit.KM/Unit.S)**(-2)),   "s**2/km**2")

        self.assertEqual((Unit.KM/Unit.S).exponents, (1,-1,0))
        self.assertEqual((Unit.KM/Unit.S/Unit.S).exponents, (1,-2,0))

        self.assertEqual(Unit.KM.convert(3.,Unit.CM), 3.e5)
        self.assertTrue(np.all(Unit.KM.convert(np.array([1.,2.,3.]), Unit.CM) ==
                               [1.e5, 2.e5, 3.e5]))

        self.assertTrue(np.all(Unit.DEGREES.convert(np.array([1.,2.,3.]),
                               Unit.ARCSEC) == [3600., 7200., 10800.]))

        self.assertTrue(np.all((Unit.DEG/Unit.S).convert(np.array([1.,2.,3.]),
                                Unit.ARCSEC/Unit.S) == [3600., 7200., 10800.]))

        self.assertTrue(np.all((Unit.DEG/Unit.H).convert(np.array([1.,2.,3.]),
                                Unit.ARCSEC/Unit.S) == [1., 2., 3.]))

        self.assertTrue(np.all((Unit.DEG*Unit.S).convert(np.array([1.,2.,3.]),
                                Unit.ARCSEC*Unit.H) == [1., 2., 3.]))

        self.assertTrue(np.all((Unit.DEG**2).convert(np.array([1.,2.,3.]),
                                Unit.ARCMIN*Unit.ARCSEC) ==
                                [3600*60, 3600*60*2, 3600*60*3]))

        eps = 1.e-15
        test = Unit.DEG.from_this(np.array([1.,2.,3.]))
        self.assertTrue(np.all([np.pi/180., np.pi/90., np.pi/60.] < test + eps))
        self.assertTrue(np.all([np.pi/180., np.pi/90., np.pi/60.] > test - eps))

        test = Unit.DEG.into_this(test)
        self.assertTrue(np.all(np.array([1., 2., 3.]) < test + eps))
        self.assertTrue(np.all(np.array([1., 2., 3.]) > test - eps))

        self.assertFalse(Unit.CM == Unit.M)
        self.assertTrue( Unit.CM != Unit.M)
        self.assertTrue( Unit.M  != Unit.SEC)
        self.assertEqual(Unit.M.factor, Unit.MRAD.factor)
        self.assertTrue( Unit.CM, Unit((1,0,0), (10., 1.e6, 0)))

        test = Unit.ROTATION/Unit.S
        self.assertEqual(test.get_name(), "rotation/s")

        unit = Unit.KM**3/Unit.S*Unit.RAD*Unit.KM**(-2) / Unit.RAD
        self.assertEqual(repr(unit), "Unit(km/s)")
        self.assertEqual(str(unit), "km/s")

        unit = (Unit.KM**3/Unit.S*Unit.RAD*Unit.KM**(-2) /
                             Unit.MRAD*Unit.MSEC/(Unit.KM/Unit.S) /
                             Unit.S)
        unit.name = None
        self.assertEqual(repr(unit), "Unit()")

        self.assertEqual(repr(Unit.S * 60), "Unit(min)")
        self.assertEqual(str(Unit.S * 60), "min")

        self.assertEqual(repr(60 * Unit.S), "Unit(min)")

        self.assertEqual(repr(Unit.H/3600), "Unit(s)")
        self.assertEqual(repr((1000/Unit.KM)**(-2)), "Unit(m**2)")

        self.assertTrue( Unit.can_match(None, None))
        self.assertTrue( Unit.can_match(None, Unit.UNITLESS))
        self.assertTrue( Unit.can_match(None, Unit.KM))
        self.assertTrue( Unit.can_match(Unit.KM, None))
        self.assertTrue( Unit.can_match(Unit.CM, Unit.KM))
        self.assertFalse(Unit.can_match(Unit.S, Unit.KM))
        self.assertFalse(Unit.can_match(Unit.S, Unit.UNITLESS))

        self.assertTrue( Unit.do_match(None, None))
        self.assertTrue( Unit.do_match(None, Unit.UNITLESS))
        self.assertFalse(Unit.do_match(None, Unit.KM))
        self.assertFalse(Unit.do_match(Unit.KM, None))
        self.assertTrue( Unit.do_match(Unit.CM, Unit.KM))
        self.assertFalse(Unit.do_match(Unit.S, Unit.KM))
        self.assertFalse(Unit.do_match(Unit.S, Unit.UNITLESS))

        self.assertEqual(Unit.KM, (Unit.KM**2).sqrt())

##########################################################################################
