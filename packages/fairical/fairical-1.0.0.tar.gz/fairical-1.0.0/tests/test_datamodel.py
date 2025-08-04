# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later


import json
import pathlib

import pydantic
import pytest

from fairical.scores import _CACHE, Scores
from fairical.solutions import Solutions


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear the JSON cache before and after each test."""
    _CACHE.clear()
    yield
    _CACHE.clear()


def test_inline_valid():
    payload = {
        "scores": [[0.0, 1.0, 0.5], [0.2, 0.8, 0.3]],
        "ground-truth": [0, 1, 0],
        "attributes": {
            "race": ["A", "B", "C"],
            "gender": ["F", "M", "F"],
            "age": [20, 30, 40],
        },
    }

    dm = Scores.model_validate(payload)
    assert len(dm.scores) == 2
    assert isinstance(dm.scores, list)
    assert all(isinstance(s, list) for s in dm.scores)
    assert dm.scores[0] == [0.0, 1.0, 0.5]
    assert isinstance(dm.ground_truth, list)
    assert dm.ground_truth == [0, 1, 0]
    assert isinstance(dm.attributes, dict)
    assert dm.attributes["age"] == [20, 30, 40]


def test_file_backed_valid(tmp_path: pathlib.Path):
    # Prepare JSON files
    scores_data = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    gt_data = [0, 1, 0]
    attrs_data = {
        "race": ["X", "Y", "Z"],
        "gender": ["M", "F", "M"],
        "age": [25, 35, 45],
    }

    scores_file0 = tmp_path / "scores0.json"
    scores_file1 = tmp_path / "scores1.json"
    gt_file = tmp_path / "gt.json"
    attrs_file = tmp_path / "attrs.json"

    # dumps data
    scores_file0.write_text(json.dumps(scores_data[0]))
    scores_file1.write_text(json.dumps(scores_data[1]))
    gt_file.write_text(json.dumps(gt_data))
    attrs_file.write_text(json.dumps(attrs_data))

    payload = {
        "scores": [scores_file0, scores_file1],
        "ground-truth": gt_file,
        "attributes": attrs_file,
    }
    dm = Scores.model_validate(payload)

    # Cache should have entries for each path
    assert scores_file0.resolve() in _CACHE
    assert scores_file1.resolve() in _CACHE
    assert gt_file.resolve() in _CACHE
    assert attrs_file.resolve() in _CACHE

    # Scores fields loaded correctly
    assert all(isinstance(s, list) for s in dm.scores)
    assert dm.scores == scores_data
    assert dm.ground_truth == gt_data
    assert dm.attributes == attrs_data

    # Now test relative paths with context
    payload = {
        "scores": [scores_file0.name, scores_file1.name],
        "ground-truth": gt_file.name,
        "attributes": attrs_file.name,
    }
    main_file = tmp_path / "main.json"
    with main_file.open("w") as f:
        f.write(json.dumps(payload))
        f.flush()
    # Validate using model_validate_json and context for base_dir
    dm2 = Scores.load(main_file)

    # The nested files should be loaded correctly via relative paths
    assert all(isinstance(s, list) for s in dm2.scores)
    assert dm2.scores == scores_data
    assert dm2.ground_truth == gt_data
    assert dm2.attributes == attrs_data


def test_score_value_error():
    payload = {
        "scores": [[-0.1, 0.5, 1.1]],  # out-of-range
        "ground-truth": [0, 1, 0],
        "attributes": {
            "race": ["A", "B", "C"],
            "gender": ["F", "M", "F"],
            "age": [20, 30, 40],
        },
    }
    with pytest.raises(pydantic.ValidationError):
        Scores.model_validate(payload)


def test_ground_truth_value_error():
    payload = {
        "scores": [[0.2, 0.4, 0.6]],
        "ground-truth": [0, -1, 1],  # negative label
        "attributes": {
            "race": ["A", "B", "C"],
            "gender": ["F", "M", "F"],
            "age": [20, 30, 40],
        },
    }
    with pytest.raises(pydantic.ValidationError):
        Scores.model_validate(payload)


def test_attribute_type_error():
    payload = {
        "scores": [[0.2, 0.4, 0.6]],
        "ground-truth": [0, 1, 0],
        "attributes": {
            "race": ["A", "B", "C"],
            "gender": ["F", "M", "F"],
            "age": [["twenty"], "thirty", "forty"],
        },
    }
    with pytest.raises(pydantic.ValidationError):
        Scores.model_validate(payload)


def test_inconsistent_scores_length():
    payload = {
        "scores": [
            [0.1, 0.2, 0.3],
            [0.4, 0.5],  # inconsistent length
        ],
        "ground-truth": [0, 1, 0],
        "attributes": {
            "race": ["A", "B", "C"],
            "gender": ["F", "M", "F"],
            "age": [20, 30, 40],
        },
    }
    with pytest.raises(ValueError) as exc:
        Scores.model_validate(payload)
    assert "scores[1] length 2 != 3" in str(exc.value)


def test_inconsistent_ground_truth():
    payload = {
        "scores": [[0.5, 0.6, 0.7]],
        "ground-truth": [0, 1],  # too short
        "attributes": {
            "race": ["A", "B", "C"],
            "gender": ["F", "M", "F"],
            "age": [20, 30, 40],
        },
    }
    with pytest.raises(ValueError) as exc:
        Scores.model_validate(payload)
    assert "ground-truth length 2 != 3" in str(exc.value)


def test_inconsistent_attribute_length():
    payload = {
        "scores": [[0.1, 0.2, 0.3]],
        "ground-truth": [0, 1, 0],
        "attributes": {
            "race": ["A", "B"],
            "gender": ["F", "M", "F"],
            "age": [20, 30, 40],
        },
    }
    with pytest.raises(ValueError) as exc:
        Scores.model_validate(payload)
    assert "attribute 'race' length 2 != 3" in str(exc.value)


def test_getitem_and_empty_lists():
    payload = {
        "scores": [[]],
        "ground-truth": [],
        "attributes": {"race": [], "gender": [], "age": []},
    }
    dm = Scores.model_validate(payload)
    assert isinstance(dm.scores[0], list)

    # Empty lists should work
    assert len(dm.scores[0]) == 0
    # __getitem__ should raise IndexError on empty
    with pytest.raises(IndexError):
        _ = dm.scores[0][0]

    # Test getitem on ground_truth and attributes
    assert isinstance(dm.ground_truth, list)
    with pytest.raises(IndexError):
        _ = dm.ground_truth[0]

    assert isinstance(dm.attributes, dict)
    with pytest.raises(KeyError):
        _ = dm.attributes["nonexistent"]


def test_invalid_solution_single():
    with pytest.raises(ValueError) as exc:
        Solutions.fromarray([[0.1, 0.9], [0.3, 0.3]], ("tpr", "eod+age"))
    assert "cannot use `tpr` as the sole utility metrics" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        Solutions.fromarray([[0.1, 0.9], [0.3, 0.3]], ("tnr", "eod+age"))
    assert "cannot use `tnr` as the sole utility metrics" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        Solutions.fromarray([[0.1, 0.9], [0.3, 0.3]], ("fpr", "eod+age"))
    assert "cannot use `fpr` as the sole utility metrics" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        Solutions.fromarray([[0.1, 0.9], [0.3, 0.3]], ("fnr", "eod+age"))
    assert "cannot use `fnr` as the sole utility metrics" in str(exc.value)


def test_invalid_solution_pair():
    with pytest.raises(ValueError) as exc:
        Solutions.fromarray(
            [[0.1, 0.9, 0.8], [0.3, 0.3, 0.7]], ("fnr", "eod+age", "tpr")
        )
    assert "cannot use the pair `['fnr', 'tpr']` as the sole utility metrics" in str(
        exc.value
    )

    with pytest.raises(ValueError) as exc:
        Solutions.fromarray(
            [[0.1, 0.9, 0.8], [0.3, 0.3, 0.7]], ("tnr", "eod+age", "fpr")
        )
    assert "cannot use the pair `['tnr', 'fpr']` as the sole utility metrics" in str(
        exc.value
    )

    with pytest.raises(ValueError) as exc:
        Solutions.fromarray(
            [[0.1, 0.9, 0.8], [0.3, 0.3, 0.7]], ("rec", "eod+age", "fnr")
        )
    assert "cannot use the pair `['rec', 'fnr']` as the sole utility metrics" in str(
        exc.value
    )
