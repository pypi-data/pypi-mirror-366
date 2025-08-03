# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 12:46:55 2021

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import unittest
from pathlib import Path
import pandas as pd
from loguru import logger

from mth5.clients.make_mth5 import MakeMTH5
from mth5.clients.fdsn import FDSN
from obspy.clients.fdsn.header import FDSNNoDataException

expected_csv = Path(__file__).parent.joinpath("expected.csv")
expected_df = pd.read_csv(expected_csv)
# =============================================================================
# Test various inputs for getting metadata
# =============================================================================


@unittest.skipIf(
    "peacock" not in str(Path(__file__).as_posix()),
    "Downloading from IRIS takes too long",
)
class TestMakeMTH5FDSNInventory(unittest.TestCase):
    """
    test a csv input to get metadata from IRIS

    """

    @classmethod
    def setUpClass(self):

        self.fdsn = FDSN(mth5_version="0.1.0")
        self.make_mth5 = MakeMTH5(
            mth5_version="0.1.0", interact=True, save_path=Path().cwd()
        )

        self.channels = ["LFE", "LFN", "LFZ", "LQE", "LQN"]
        ORF08 = ["4P", "ORF08", "2006-09-04T16:00:00", "2006-09-26T00:00:00"]

        request_list = []
        for entry in [ORF08]:
            for channel in self.channels:
                request_list.append(
                    [entry[0], entry[1], "", channel, entry[2], entry[3]]
                )
        self.logger = logger
        self.csv_fn = Path().cwd().joinpath("test_inventory.csv")
        self.mth5_path = Path().cwd()

        self.stations = ["ORF08"]

        # Turn list into dataframe
        self.metadata_df = pd.DataFrame(
            request_list, columns=self.fdsn.request_columns
        )

        self.metadata_df.to_csv(self.csv_fn, index=False)

        self.metadata_df_fail = pd.DataFrame(
            request_list,
            columns=["net", "sta", "loc", "chn", "startdate", "enddate"],
        )

    def test_client(self):
        self.assertEqual(self.fdsn.client, "IRIS")

    def test_file_version(self):
        self.assertEqual(self.fdsn.mth5_version, "0.1.0")

    def test_validate_dataframe_fail(self):
        with self.subTest("bad value"):
            self.assertRaises(ValueError, self.fdsn._validate_dataframe, [])
        with self.subTest("bad path"):
            self.assertRaises(IOError, self.fdsn._validate_dataframe, "k.fail")

    def test_df_input_inventory(self):
        try:
            inv, streams = self.fdsn.get_inventory_from_df(
                self.metadata_df, data=False
            )

        except FDSNNoDataException as error:
            msg = (
                "The requested data could not be found on the FDSN IRIS server, "
                "check data availability"
            )
            self.logger.warning(msg)
            self.logger.exception(error)

            raise Exception(msg)
        with self.subTest(name="stations"):
            self.assertListEqual(
                sorted(self.stations),
                sorted(list(set([ss.code for ss in inv.networks[0].stations]))),
            )
        with self.subTest(name="channels_ORF08"):
            self.assertListEqual(
                sorted(self.channels),
                sorted(
                    list(
                        set(
                            [
                                ss.code
                                for ss in inv.networks[0].stations[0].channels
                            ]
                        )
                    )
                ),
            )

    def test_csv_input_inventory(self):
        inv, streams = self.fdsn.get_inventory_from_df(self.csv_fn, data=False)
        with self.subTest(name="stations"):
            self.assertListEqual(
                sorted(self.stations),
                sorted([ss.code for ss in inv.networks[0].stations]),
            )
        with self.subTest(name="channels_ORF08"):
            self.assertListEqual(
                sorted(self.channels),
                sorted(
                    list(
                        set(
                            [
                                ss.code
                                for ss in inv.networks[0].stations[0].channels
                            ]
                        )
                    )
                ),
            )

    def test_fail_csv_inventory(self):
        self.assertRaises(
            ValueError,
            self.fdsn.get_inventory_from_df,
            *(self.metadata_df_fail, self.fdsn.client, False),
        )

    def test_fail_wrong_input_type(self):
        self.assertRaises(
            ValueError,
            self.fdsn.get_inventory_from_df,
            *(("bad tuple", "bad_tuple"), self.fdsn.client, False),
        )

    def test_fail_non_existing_file(self):
        self.assertRaises(
            IOError,
            self.fdsn.get_inventory_from_df,
            *("c:\bad\file\name", self.fdsn.client, False),
        )

    def test_h5_parameters(self):
        with self.subTest("compression"):
            self.assertEqual(self.make_mth5.h5_compression, "gzip")
        with self.subTest("compression_options"):
            self.assertEqual(self.make_mth5.h5_compression_opts, 4)
        with self.subTest("shuffle"):
            self.assertEqual(self.make_mth5.h5_shuffle, True)
        with self.subTest("fletcher32"):
            self.assertEqual(self.make_mth5.h5_fletcher32, True)
        with self.subTest("data_level"):
            self.assertEqual(self.make_mth5.h5_data_level, 1)
        with self.subTest("file_version"):
            self.assertEqual(self.make_mth5.mth5_version, "0.1.0")
        with self.subTest("save_path"):
            self.assertEqual(self.make_mth5.save_path, self.mth5_path)
        with self.subTest("interact"):
            self.assertEqual(self.make_mth5.interact, True)

    def test_fdsn_h5_parameters(self):
        with self.subTest("compression"):
            self.assertEqual(self.fdsn.h5_compression, "gzip")
        with self.subTest("compression_options"):
            self.assertEqual(self.fdsn.h5_compression_opts, 4)
        with self.subTest("shuffle"):
            self.assertEqual(self.fdsn.h5_shuffle, True)
        with self.subTest("fletcher32"):
            self.assertEqual(self.fdsn.h5_fletcher32, True)
        with self.subTest("data_level"):
            self.assertEqual(self.fdsn.h5_data_level, 1)
        with self.subTest("file_version"):
            self.assertEqual(self.fdsn.mth5_version, "0.1.0")

    @classmethod
    def tearDownClass(self):
        self.csv_fn.unlink()


@unittest.skipIf(
    "peacock" not in str(Path().cwd().as_posix()),
    "Test is too long, have to download data from IRIS",
)
class TestMakeMTH5(unittest.TestCase):
    """
    test a csv input to get metadata from IRIS

    """

    @classmethod
    def setUpClass(self):

        self.fdsn = FDSN(mth5_version="0.1.0")
        self.fdsn.client = "IRIS"
        self.make_mth5 = MakeMTH5(
            mth5_version="0.1.0", interact=True, save_path=Path().cwd()
        )

        channels = ["LFE", "LFN", "LFZ", "LQE", "LQN"]
        ORF08 = ["4P", "ORF08", "2006-09-04T16:00:00", "2006-09-26T00:00:00"]

        request_list = []
        for entry in [ORF08]:
            for channel in channels:
                request_list.append(
                    [entry[0], entry[1], "", channel, entry[2], entry[3]]
                )
        self.logger = logger
        self.csv_fn = Path().cwd().joinpath("test_inventory.csv")
        self.mth5_path = Path().cwd()

        self.stations = ["ORF08"]
        self.channels = ["MQE", "MQN", "MFE", "MFN", "MFZ"]

        # Turn list into dataframe
        self.metadata_df = pd.DataFrame(
            request_list, columns=self.fdsn.request_columns
        )
        self.metadata_df.to_csv(self.csv_fn, index=False)

        self.metadata_df_fail = pd.DataFrame(
            request_list,
            columns=["net", "sta", "loc", "chn", "startdate", "enddate"],
        )

        try:
            self.m = self.make_mth5.from_fdsn_client(
                self.metadata_df, client="IRIS"
            )
        except FDSNNoDataException as error:
            self.logger.warning(
                "The requested data could not be found on the FDSN IRIS server, check data availability"
            )
            self.logger.error(error)

            raise Exception(
                "The requested data could not be found on the FDSN IRIS server, check data availability"
            )

    def test_stations(self):
        self.assertListEqual(self.stations, self.m.stations_group.groups_list)

    def test_orf08_runs_list(self):
        self.assertListEqual(
            sorted(
                [
                    "Fourier_Coefficients",
                    "Transfer_Functions",
                    "001",
                    "002",
                ]
            ),
            sorted(self.m.get_station("ORF08").groups_list),
        )

    def test_orf08_channels(self):
        for run in ["001", "002"]:
            for ch in ["ex", "ey", "hx", "hy", "hz"]:
                x = self.m.get_channel("ORF08", run, ch)

                with self.subTest(name=f"has data ORF08.{run}.{ch}"):
                    self.assertTrue(abs(x.hdf5_dataset[()].mean()) > 0)
                with self.subTest(name=f"has metadata ORF08.{run}.{ch}"):
                    self.assertEqual(x.metadata.component, ch)
                with self.subTest(name=f"has filters ORF08.{run}.{ch}"):
                    self.assertTrue(len(x.metadata.filter.name) >= 1)

    def test_orf08_channels_to_ts(self):
        for run in ["001", "002"]:
            for ch in ["ex", "ey", "hx", "hy", "hz"]:
                x = self.m.get_channel("ORF08", run, ch).to_channel_ts()
                with self.subTest(name=f"has data ORF08.{run}.{ch}"):
                    self.assertTrue(abs(x.ts.mean()) > 0)
                with self.subTest(name=f"has metadata ORF08.{run}.{ch}"):
                    self.assertEqual(x.component, ch)
                with self.subTest(name=f"has filters ORF08.{run}.{ch}"):
                    self.assertTrue(len(x.channel_response.filters_list) >= 1)

    @classmethod
    def tearDownClass(self):
        self.m.close_mth5()
        self.m.filename.unlink()
        self.csv_fn.unlink()


# =============================================================================
# Run
# =============================================================================
if __name__ == "__main__":
    unittest.main()
