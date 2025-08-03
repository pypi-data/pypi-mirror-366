# -*- coding: utf-8 -*-
"""
Created on Thu May 13 13:45:27 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""
# =============================================================================
# Imports
# =============================================================================

import unittest
from pathlib import Path
import numpy as np

from mth5 import CHANNEL_DTYPE
from mth5.mth5 import MTH5
from mth5 import helpers
from mth5.helpers import validate_name
from mt_metadata.timeseries import Experiment
from mt_metadata import MT_EXPERIMENT_SINGLE_STATION

fn_path = Path(__file__).parent
# =============================================================================
#
# =============================================================================
helpers.close_open_files()


class TestMTH5(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.maxDiff = None
        self.fn = fn_path.joinpath("test.mth5")
        self.mth5_obj = MTH5(file_version="0.2.0")
        self.mth5_obj.open_mth5(self.fn, mode="w")
        self.experiment = Experiment()
        self.experiment.from_xml(fn=MT_EXPERIMENT_SINGLE_STATION)
        self.survey_name = validate_name(self.experiment.surveys[0].id)
        self.mth5_obj.from_experiment(self.experiment)

    def test_surveys(self):
        survey = self.experiment.surveys[0]
        sg = self.mth5_obj.get_survey(self.survey_name)

        sd_md = survey.to_dict(single=True)
        sd_md.pop("hdf5_reference")
        sd_md.pop("mth5_type")

        h5_md = sg.metadata.to_dict(single=True)
        h5_md.pop("hdf5_reference")
        h5_md.pop("mth5_type")

        self.assertDictEqual(sd_md, h5_md)

    def test_stations(self):
        stations = self.experiment.surveys[0].stations
        for station in stations:
            with self.subTest(name=station.id):
                h5_station = self.mth5_obj.get_station(
                    station.id, self.survey_name
                )
                sd = station.to_dict(single=True)
                sd.pop("hdf5_reference")
                sd.pop("mth5_type")

                h5_sd = h5_station.metadata.to_dict(single=True)
                h5_sd.pop("hdf5_reference")
                h5_sd.pop("mth5_type")

                self.assertDictEqual(h5_sd, sd)

    def test_runs(self):
        runs = self.experiment.surveys[0].stations[0].runs
        for run in runs:
            with self.subTest(name=run.id):
                h5_run = self.mth5_obj.get_run(
                    self.experiment.surveys[0].stations[0].id,
                    run.id,
                    survey=self.survey_name,
                )
                sd = run.to_dict(single=True)
                sd.pop("hdf5_reference")
                sd.pop("mth5_type")

                h5_sd = h5_run.metadata.to_dict(single=True)
                h5_sd.pop("hdf5_reference")
                h5_sd.pop("mth5_type")

                self.assertDictEqual(h5_sd, sd)

    def test_to_run_ts(self):
        run_group = self.mth5_obj.get_run(
            self.experiment.surveys[0].stations[0].id,
            self.experiment.surveys[0].stations[0].runs[0].id,
            self.experiment.surveys[0].id,
        )
        run_ts = run_group.to_runts()

        for key in self.experiment.surveys[0].to_dict(single=True).keys():
            if key in ["hdf5_reference", "mth5_type"]:
                continue
            with self.subTest(f"survey.{key}"):
                self.assertEqual(
                    self.experiment.surveys[0].get_attr_from_name(key),
                    run_ts.survey_metadata.get_attr_from_name(key),
                )

        for key in (
            self.experiment.surveys[0].stations[0].to_dict(single=True).keys()
        ):
            if key in ["hdf5_reference", "mth5_type"]:
                continue

            with self.subTest(f"station.{key}"):
                if key in ["run_list"]:
                    self.assertListEqual(
                        ["a"],
                        run_ts.station_metadata.run_list,
                    )
                else:
                    self.assertEqual(
                        self.experiment.surveys[0]
                        .stations[0]
                        .get_attr_from_name(key),
                        run_ts.station_metadata.get_attr_from_name(key),
                    )

        for key in (
            self.experiment.surveys[0]
            .stations[0]
            .runs[0]
            .to_dict(single=True)
            .keys()
        ):
            if key in ["hdf5_reference", "mth5_type"]:
                continue
            with self.subTest(f"run.{key}"):
                if key in ["time_period.end"]:
                    self.assertNotEqual(
                        self.experiment.surveys[0]
                        .stations[0]
                        .runs[0]
                        .get_attr_from_name(key),
                        run_ts.run_metadata.get_attr_from_name(key),
                    )
                else:
                    self.assertEqual(
                        self.experiment.surveys[0]
                        .stations[0]
                        .runs[0]
                        .get_attr_from_name(key),
                        run_ts.run_metadata.get_attr_from_name(key),
                    )

    def test_to_channel_ts(self):
        channel_group = self.mth5_obj.get_channel(
            self.experiment.surveys[0].stations[0].id,
            self.experiment.surveys[0].stations[0].runs[0].id,
            self.experiment.surveys[0]
            .stations[0]
            .runs[0]
            .channels[0]
            .component,
            self.experiment.surveys[0].id,
        )
        ch_ts = channel_group.to_channel_ts()

        for key in self.experiment.surveys[0].to_dict(single=True).keys():
            if key in ["hdf5_reference", "mth5_type"]:
                continue
            with self.subTest(f"survey.{key}"):
                self.assertEqual(
                    self.experiment.surveys[0].get_attr_from_name(key),
                    ch_ts.survey_metadata.get_attr_from_name(key),
                )

        for key in (
            self.experiment.surveys[0].stations[0].to_dict(single=True).keys()
        ):
            if key in ["hdf5_reference", "mth5_type"]:
                continue

            with self.subTest(f"station.{key}"):
                if key in ["run_list", "channels_recorded"]:
                    self.assertListEqual(
                        ["a", "b", "c", "d", "e"],
                        ch_ts.station_metadata.run_list,
                    )
                else:
                    self.assertEqual(
                        self.experiment.surveys[0]
                        .stations[0]
                        .get_attr_from_name(key),
                        ch_ts.station_metadata.get_attr_from_name(key),
                    )

        for key in (
            self.experiment.surveys[0]
            .stations[0]
            .runs[0]
            .to_dict(single=True)
            .keys()
        ):
            if key in [
                "hdf5_reference",
                "mth5_type",
                "channels_recorded_magnetic",
                "channels_recorded_electric",
                "channels_recorded_auxiliary",
            ]:
                continue
            with self.subTest(f"run.{key}"):
                self.assertEqual(
                    self.experiment.surveys[0]
                    .stations[0]
                    .runs[0]
                    .get_attr_from_name(key),
                    ch_ts.run_metadata.get_attr_from_name(key),
                )

        for key in (
            self.experiment.surveys[0]
            .stations[0]
            .runs[0]
            .channels[0]
            .to_dict(single=True)
            .keys()
        ):
            if key in [
                "hdf5_reference",
                "mth5_type",
                "filter.name",
                "filter.applied",
            ]:
                continue
            with self.subTest(f"channel.{key}"):
                if key in ["time_period.end"]:
                    self.assertNotEqual(
                        self.experiment.surveys[0]
                        .stations[0]
                        .runs[0]
                        .channels[0]
                        .get_attr_from_name(key),
                        ch_ts.station_metadata.get_attr_from_name(key),
                    )
                else:
                    self.assertEqual(
                        self.experiment.surveys[0]
                        .stations[0]
                        .runs[0]
                        .channels[0]
                        .get_attr_from_name(key),
                        ch_ts.channel_metadata.get_attr_from_name(key),
                    )

        def test_channels(self):
            runs = self.experiment.surveys[0].stations[0].runs
            for run in runs:
                with self.subTest(name=run.id):
                    h5_run = self.mth5_obj.get_run(
                        self.experiment.surveys[0].stations[0].id,
                        run.id,
                        self.survey_name,
                    )
                    for channel in run.channels:
                        h5_channel = h5_run.get_channel(channel.component)

                        sd = channel.to_dict(single=True)
                        sd.pop("hdf5_reference")
                        sd.pop("mth5_type")

                        h5_sd = h5_channel.metadata.to_dict(single=True)
                        h5_sd.pop("hdf5_reference")
                        h5_sd.pop("mth5_type")

                        self.assertDictEqual(h5_sd, sd)

        def test_filters(self):
            exp_filters = self.experiment.surveys[0].filters
            sg = self.mth5_obj.get_survey(self.survey_name)

            for key, value in exp_filters.items():
                with self.subTest(name=key):
                    key = key.replace("/", " per ").lower()
                    sd = value.to_dict(single=True, required=False)
                    h5_sd = sg.filters_group.to_filter_object(key)
                    h5_sd = h5_sd.to_dict(single=True, required=False)
                    for k in sd.keys():
                        with self.subTest(f"{key}_{k}"):
                            v1 = sd[k]
                            v2 = h5_sd[k]
                            if isinstance(v1, (float, int)):
                                self.assertAlmostEqual(v1, float(v2), 5)
                            elif isinstance(v1, np.ndarray):
                                self.assertEqual(v1.dtype, v2.dtype)
                                self.assertTrue((v1 == v2).all())
                            else:
                                self.assertEqual(v1, v2)
                # self.assertDictEqual(h5_sd, sd)

    def test_channel_summary(self):
        self.mth5_obj.channel_summary.summarize()

        with self.subTest("test shape"):
            self.assertEqual(self.mth5_obj.channel_summary.shape, (25,))
        with self.subTest("test nrows"):
            self.assertEqual(self.mth5_obj.channel_summary.nrows, 25)
        with self.subTest(("test dtype")):
            self.assertEqual(self.mth5_obj.channel_summary.dtype, CHANNEL_DTYPE)
        with self.subTest("test station"):
            self.assertTrue(
                (
                    self.mth5_obj.channel_summary.array["station"] == b"REW09"
                ).all()
            )

    @classmethod
    def tearDownClass(self):
        self.mth5_obj.close_mth5()
        self.fn.unlink()


class TestUpdateFromExperiment(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.maxDiff = None
        self.fn = fn_path.joinpath("test.h5")
        self.mth5_obj = MTH5(file_version="0.1.0")
        self.mth5_obj.open_mth5(self.fn, mode="w")
        self.experiment = Experiment()
        self.experiment.from_xml(fn=MT_EXPERIMENT_SINGLE_STATION)
        self.mth5_obj.from_experiment(self.experiment)

        self.experiment_02 = Experiment()
        self.experiment_02.from_xml(fn=MT_EXPERIMENT_SINGLE_STATION)
        self.experiment_02.surveys[0].id = "different_survey_name"
        self.experiment_02.surveys[0].stations[0].location.latitude = 10

    def test_update_from_new_experiment(self):
        self.mth5_obj.from_experiment(self.experiment_02, update=True)

        with self.subTest("new_survey"):
            self.assertEqual(
                self.mth5_obj.survey_group.metadata.id,
                self.experiment_02.surveys[0].id,
            )
        with self.subTest("new_location"):
            st = self.mth5_obj.get_station("REW09")
            self.assertEqual(
                st.metadata.location.latitude,
                self.experiment_02.surveys[0].stations[0].location.latitude,
            )

    @classmethod
    def tearDownClass(self):
        self.mth5_obj.close_mth5()
        self.fn.unlink()


# =============================================================================
# run
# =============================================================================
if __name__ == "__main__":
    unittest.main()
