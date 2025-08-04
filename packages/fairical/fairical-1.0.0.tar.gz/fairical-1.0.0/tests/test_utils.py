# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later


from fairical import utils


def test_make_table_basic() -> None:
    indicators: dict[str, dict[utils.IndicatorType, float]] = {
        "System A": {
            "hv": 0.8,
            "ud": 0.2,
            "os": 0.3,
            "as": 0.75,
            "onvg": 12,
            "onvgr": 0.6,
            "relative-onvg": 5,
            "area": 0.55,
        },
        "System B": {
            "hv": 0.6,
            "ud": 0.1,
            "os": 0.5,
            "as": 0.95,
            "onvg": 11,
            "onvgr": 0.5,
            "relative-onvg": 4,
            "area": 0.45,
        },
    }
    table = utils.make_table(indicators, fmt="simple")
    assert "System" in table
    assert "System A" in table
    assert "System B" in table
    assert "HV" in table
    assert "Area" in table
    # Check numeric formatting
    assert ".80" in table or "0.80" in table  # may vary by tabulate version


def test_make_table_dict_input() -> None:
    indicators: dict[str, dict[utils.IndicatorType, float]] = {
        "Sys1": {
            "hv": 0.7,
            "ud": 0.25,
            "os": 0.4,
            "as": 0.72,
            "onvg": 10,
            "onvgr": 0.55,
            "relative-onvg": 4,
            "area": 0.35,
        }
    }
    table = utils.make_table(indicators, fmt="github")
    assert "Sys1" in table
    assert (
        "|   Area |" in table or "| Area |" in table
    )  # allow for tabulate header formatting


def test_make_table_with_custom_keys() -> None:
    indicators: dict[str, dict[utils.IndicatorType, float]] = {
        "SysX": {
            "hv": 0.8,
            "ud": 0.2,
            "os": 0.3,
            "as": 0.9,
            "onvg": 12,
            "onvgr": 0.6,
            "relative-onvg": 5,
        },
        "SysY": {
            "hv": 0.6,
            "ud": 0.1,
            "os": 0.5,
            "as": 0.85,
            "onvg": 11,
            "onvgr": 0.5,
            "relative-onvg": 4,
        },
    }
    # Only use a subset of keys
    keys = ["hv", "ud", "os"]
    table = utils.make_table(indicators, fmt="simple", table_keys=keys)

    assert "HV" in table
    assert "UD" in table
    assert "OS" in table
    assert "Area" in table

    assert "ONVG" not in table
    assert "ONVGR" not in table
    assert "RELATIVE-ONVG" not in table
