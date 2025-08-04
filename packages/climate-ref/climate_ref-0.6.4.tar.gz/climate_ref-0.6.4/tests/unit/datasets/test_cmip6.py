import datetime

import numpy as np
import pandas as pd

from climate_ref.datasets.cmip6 import (
    CMIP6DatasetAdapter,
    _apply_fixes,
    _clean_branch_time,
    _parse_datetime,
    parse_cmip6,
)


def test_parse_datetime():
    pd.testing.assert_series_equal(
        _parse_datetime(pd.Series(["2021-01-01 00:00:00", "1850-01-17 00:29:59.999993", None])),
        pd.Series(
            [datetime.datetime(2021, 1, 1, 0, 0), datetime.datetime(1850, 1, 17, 0, 29, 59, 999993), None],
            dtype="object",
        ),
    )


def test_parse_exception():
    result = parse_cmip6("missing_file")

    assert result["INVALID_ASSET"] == "missing_file"
    assert "TRACEBACK" in result


def test_clean_branch_time():
    inp = pd.Series(["0D", "12", "12.0", "12.000", "12.0000", "12.00000", None, np.nan])
    exp = pd.Series([0.0, 12.0, 12.0, 12.0, 12.0, 12.0, np.nan, np.nan])

    pd.testing.assert_series_equal(_clean_branch_time(inp), exp)


class TestCMIP6Adapter:
    def test_catalog_empty(self, db):
        adapter = CMIP6DatasetAdapter()
        df = adapter.load_catalog(db)
        assert df.empty

    def test_load_catalog(self, db_seeded, catalog_regression, sample_data_dir):
        adapter = CMIP6DatasetAdapter()
        df = adapter.load_catalog(db_seeded)

        for k in adapter.dataset_specific_metadata + adapter.file_specific_metadata:
            assert k in df.columns

        # The order of the rows may be flakey due to sqlite ordering and the created time resolution
        catalog_regression(df.sort_values(["instance_id", "start_time"]), basename="cmip6_catalog_db")

    def test_load_catalog_multiple_versions(self, config, db_seeded, catalog_regression, sample_data_dir):
        adapter = CMIP6DatasetAdapter()
        data_catalog = adapter.load_catalog(db_seeded)
        target_ds = "CMIP6.CMIP.CSIRO.ACCESS-ESM1-5.historical.r1i1p1f1.Amon.tas.gn.v20191115"
        target_metadata = data_catalog[data_catalog["instance_id"] == target_ds]

        # Make an old version
        target_metadata.version = "v20000101"
        target_metadata.instance_id = target_ds.replace("v20191115", "v20000101")
        with db_seeded.session.begin():
            adapter.register_dataset(config, db_seeded, target_metadata)

        # An older version should not be in the catalog
        pd.testing.assert_frame_equal(
            data_catalog.sort_values(["instance_id", "start_time"]),
            adapter.load_catalog(db_seeded).sort_values(["instance_id", "start_time"]),
        )

        # Make a new version
        target_metadata.version = "v20230101"
        new_instance_id = target_ds.replace("v20191115", "v20230101")
        target_metadata.instance_id = new_instance_id
        with db_seeded.session.begin():
            adapter.register_dataset(config, db_seeded, target_metadata)

        # The new version should be in the catalog
        latest_data_catalog = adapter.load_catalog(db_seeded)
        latest_instance_ids = latest_data_catalog.instance_id.unique().tolist()
        assert target_ds not in latest_instance_ids
        assert new_instance_id in latest_instance_ids

    def test_round_trip(self, db_seeded, sample_data_dir):
        # Indexes and ordering may be different
        adapter = CMIP6DatasetAdapter()
        local_data_catalog = (
            adapter.find_local_datasets(sample_data_dir / "CMIP6")
            .drop(columns=["time_range"])
            .sort_values(["instance_id", "start_time"])
            .reset_index(drop=True)
        )

        db_data_catalog = (
            adapter.load_catalog(db_seeded).sort_values(["instance_id", "start_time"]).reset_index(drop=True)
        )

        # TODO: start_time has a different dtype from the database due to pandas dt coercion
        db_data_catalog["start_time"] = db_data_catalog["start_time"].astype(object)
        pd.testing.assert_frame_equal(local_data_catalog, db_data_catalog, check_like=True)

    def test_load_local_datasets(self, sample_data_dir, catalog_regression):
        adapter = CMIP6DatasetAdapter()
        data_catalog = adapter.find_local_datasets(sample_data_dir / "CMIP6")

        # TODO: add time_range to the db?
        assert sorted(data_catalog.columns.tolist()) == sorted(
            [*adapter.dataset_specific_metadata, *adapter.file_specific_metadata, "time_range"]
        )

        catalog_regression(
            data_catalog.sort_values(["instance_id", "start_time"]), basename="cmip6_catalog_local"
        )


def test_apply_fixes():
    df = pd.DataFrame(
        {
            "instance_id": ["dataset_001", "dataset_001", "dataset_002"],
            "parent_variant_label": ["r1i1p1f1", "r1i1p1f2", "r1i1p1f2"],
            "variant_label": ["r1i1p1f1", "r1i1p1f1", "r1i1p1f2"],
            "branch_time_in_child": ["0D", "12", "12.0"],
            "branch_time_in_parent": [None, np.nan, "12.0"],
        }
    )

    res = _apply_fixes(df)

    exp = pd.DataFrame(
        {
            "instance_id": ["dataset_001", "dataset_001", "dataset_002"],
            "parent_variant_label": ["r1i1p1f1", "r1i1p1f1", "r1i1p1f2"],
            "variant_label": ["r1i1p1f1", "r1i1p1f1", "r1i1p1f2"],
            "branch_time_in_child": [0.0, 12.0, 12.0],
            "branch_time_in_parent": [np.nan, np.nan, 12.0],
        }
    )
    pd.testing.assert_frame_equal(res, exp)
