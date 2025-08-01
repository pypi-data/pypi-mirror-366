"""Tests for the intra-class rarity random forest models."""

# Authors: Janne Wernecken
# License: BSD 3 clause

import numpy as np
import pytest

from icrlearn.rarity._cb_loop import calculate_cb_loop


@pytest.fixture
def data():
    # First class, last sample is rare
    X_0 = np.asarray(
        [
            [-2, -1],
            [-1, -1],
            [-1, -2],
            [1, 1],
            [1, 2],
            [2, 1],
            [-2, -1],
            [-1, -1],
            [-1, -2],
            [1, 1],
            [1, 2],
            [2, 1],
            [-2, -1],
            [-1, -1],
            [-1, -2],
            [1, 1],
            [1, 2],
            [2, 1],
            [-2, -1],
            [-1, -1],
            [-1, -2],
            [1, 1],
            [1, 2],
            [2, 1],
            [3, 6],
        ]
    )
    y_0 = np.zeros(len(X_0))

    # Second class, last sample is rare
    X_1 = np.asarray(
        [
            [6, 7],
            [7, 7],
            [7, 6],
            [8, 8],
            [8, 9],
            [9, 8],
            [6, 7],
            [7, 7],
            [7, 6],
            [8, 8],
            [8, 9],
            [9, 8],
            [6, 7],
            [7, 7],
            [7, 6],
            [8, 8],
            [8, 9],
            [9, 8],
            [6, 7],
            [7, 7],
            [7, 6],
            [8, 8],
            [8, 9],
            [9, 8],
            [3, 1],
        ]
    )
    y_1 = np.ones(len(X_1))

    X = np.vstack((X_0, X_1))
    y = np.hstack((y_0, y_1))
    return X, y


def test_cb_loop(data):
    X, y = data

    actual_rarity_scores = calculate_cb_loop(X, y)
    assert len(actual_rarity_scores) == len(X)
    assert len(actual_rarity_scores) == len(y)
    assert np.all(np.isfinite(actual_rarity_scores))
    assert np.all(actual_rarity_scores >= 0)

    # Rare samples have a rarity score close to 1
    # For the test case the threshold is set to 0.8
    index_first_rare_sample = int(len(X) / 2 - 1)
    index_second_rare_sample = len(X) - 1
    assert actual_rarity_scores[index_first_rare_sample] > 0.8
    assert actual_rarity_scores[index_second_rare_sample] > 0.8

    # All other samples should have a rarity score < 0.8
    non_rare_samples = np.delete(
        np.arange(len(X)), [index_first_rare_sample, index_second_rare_sample]
    )
    assert np.all(actual_rarity_scores[non_rare_samples] < 0.8)
