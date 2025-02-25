from typing import List
from typing import Tuple

import numpy as np
import pandas as pd
import pytest

from etna.analysis.outliers.sequence_outliers import get_segment_sequence_anomalies
from etna.analysis.outliers.sequence_outliers import get_sequence_anomalies
from etna.datasets.tsdataset import TSDataset


@pytest.fixture
def test_sequence_anomalies_interface(outliers_tsds: TSDataset):
    length = 5
    anomaly_seq_dict = get_sequence_anomalies(ts=outliers_tsds, num_anomalies=1, anomaly_length=length)

    for segment in ["1", "2"]:
        assert segment in anomaly_seq_dict
        assert isinstance(anomaly_seq_dict[segment], list)
        assert len(anomaly_seq_dict[segment]) == length
        for timestamp in anomaly_seq_dict[segment]:
            assert isinstance(timestamp, np.datetime64)


@pytest.mark.parametrize(
    "arr, expected",
    (
        ([1, 1, 10, -7, 1, 1, 1, 1], [(1, 4)]),
        ([1, 1, 12, 15, 1, 1, 1], [(0, 3)]),
        ([1, 1, -12, -15, 1, 1, 1, 12, 15], [(5, 8), (0, 3)]),
    ),
)
def test_segment_sequence_anomalies(arr: List[int], expected: List[Tuple[int, int]]):
    arr = np.array(arr)
    anomaly_length = 3
    num_anomalies = len(expected)
    expected = sorted(expected)

    result = get_segment_sequence_anomalies(series=arr, num_anomalies=num_anomalies, anomaly_length=3)
    result = sorted(result)
    for idx in range(num_anomalies):
        assert (result[idx][0] == expected[idx][0]) and (result[idx][1] == expected[idx][1])


def test_sequence_anomalies(outliers_tsds: TSDataset):
    bounds_dict = {
        "1": [np.datetime64("2021-01-01"), np.datetime64("2021-01-16")],
        "2": [np.datetime64("2021-01-17"), np.datetime64("2021-02-01")],
    }
    delta = pd.to_timedelta(outliers_tsds.index.freq)
    expected = dict([(seg, np.arange(bounds[0], bounds[1], delta)) for seg, bounds in bounds_dict.items()])
    anomaly_seq_dict = get_sequence_anomalies(outliers_tsds, num_anomalies=1, anomaly_length=15)

    for segment in expected:
        assert (anomaly_seq_dict[segment] == expected[segment]).all()


def test_in_column(outliers_df_with_two_columns):
    outliers = get_sequence_anomalies(
        ts=outliers_df_with_two_columns, num_anomalies=1, anomaly_length=4, in_column="feature"
    )
    delta = pd.to_timedelta(outliers_df_with_two_columns.index.freq)

    expected = {
        "1": np.arange(np.datetime64("2021-01-06"), np.datetime64("2021-01-10"), delta),
        "2": np.arange(np.datetime64("2021-01-25"), np.datetime64("2021-01-29"), delta),
    }

    for key in expected:
        assert key in outliers
        np.testing.assert_array_equal(outliers[key], expected[key])
