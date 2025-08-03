# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 08:38:54 2022

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import unittest
from collections import OrderedDict

import numpy as np

from mth5.io.nims import Response

# =============================================================================


class TestNIMSResponse(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.response = Response()
        self.maxDiff = None

    def test_get_electric_hp(self):
        with self.subTest("PC"):
            pc_hp = self.response.get_electric_high_pass(hardware="pc")
            pc_dict = OrderedDict(
                [
                    ("calibration_date", "1980-01-01"),
                    ("gain", 1.0),
                    ("name", "nims_1_pole_butterworth"),
                    ("normalization_factor", 1.0),
                    ("poles", np.array([-3.333333e-05 + 0.0j])),
                    ("type", "zpk"),
                    ("units_in", "V"),
                    ("units_out", "V"),
                    ("zeros", np.array([0.0 + 0.0j])),
                ]
            )

            self.assertDictEqual(pc_dict, pc_hp.to_dict(single=True))

        with self.subTest("HP"):
            hp_hp = self.response.get_electric_high_pass(hardware="HP")
            hp_dict = OrderedDict(
                [
                    ("calibration_date", "1980-01-01"),
                    ("gain", 1.0),
                    ("name", "nims_1_pole_butterworth"),
                    ("normalization_factor", 1.0),
                    ("poles", np.array([-1.66667e-04 + 0.0j])),
                    ("type", "zpk"),
                    ("units_in", "V"),
                    ("units_out", "V"),
                    ("zeros", np.array([0.0 + 0.0j])),
                ]
            )

            self.assertDictEqual(hp_dict, hp_hp.to_dict(single=True))

    def test_dipole_filter(self):
        dp = self.response.dipole_filter(100)
        dp_dict = OrderedDict(
            [
                ("calibration_date", "1980-01-01"),
                ("gain", 100.0),
                ("name", "dipole_100.00"),
                ("type", "coefficient"),
                ("units_in", "V/m"),
                ("units_out", "V"),
            ]
        )

        self.assertDictEqual(dp_dict, dp.to_dict(single=True))

    def test_get_electric_filters(self):
        ex = self.response.get_channel_response("ex", 100)

        with self.subTest("length"):
            self.assertEqual(6, len(ex.filters_list))

        with self.subTest("units_in"):
            self.assertEqual("mV/km", ex.units_in)

        with self.subTest("units_out"):
            self.assertEqual("count", ex.units_out)

    def test_get_magnetic_filters(self):
        hx = self.response.get_channel_response("hx")

        with self.subTest("length"):
            self.assertEqual(3, len(hx.filters_list))

        with self.subTest("units_in"):
            self.assertEqual("nT", hx.units_in)

        with self.subTest("units_out"):
            self.assertEqual("count", hx.units_out)


# =============================================================================
# Run
# =============================================================================
if __name__ == "__main__":
    unittest.main()
