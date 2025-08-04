# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib
import re

from click.testing import CliRunner

from fairical.scripts.cli import cli


def str_counter(substr: str, s: str) -> int:
    """Count number of occurences of regular expression ``str`` on ``s``.

    Parameters
    ----------
    substr
        String or regular expression to search for in ``s``.
    s
        String where to search for ``substr``, that may include new-line characters.

    Returns
    -------
        The count on the number of occurences of ``substr`` on ``s``.
    """

    return sum(1 for _ in re.finditer(substr, s, re.MULTILINE))


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert result.output.startswith("Usage:")


def test_cli_solve_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["solve", "--help"])
    assert result.exit_code == 0
    assert result.output.startswith("Usage:")


def test_cli_evaluate_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["evaluate", "--help"])
    assert result.exit_code == 0
    assert result.output.startswith("Usage:")


def test_cli_plot_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["plot", "--help"])
    assert result.exit_code == 0
    assert result.output.startswith("Usage:")


def test_cli_solve(datadir: pathlib.Path, tmp_path: pathlib.Path, caplog):
    runner = CliRunner()

    with caplog.at_level("INFO", logger="fairical"):
        result = runner.invoke(
            cli,
            [
                "solve",
                "-vv",
                "--metric=acc",
                "--metric=eod+race",
                "--metric=eod+gender",
                str(datadir / "data" / "empirical" / "system_1.json"),
                str(datadir / "data" / "empirical" / "system_2.json"),
                "--output-path",
                str(tmp_path),
                "--thresholds=3",
            ],
        )

    assert result.exit_code == 0

    assert str_counter("Calculating solutions for system", caplog.text) == 2
    assert str_counter("Evaluating subsystem", caplog.text) == 50
    assert str_counter("Deduplication reduced solutions", caplog.text) == 2
    assert str_counter(f"Saved `{str(tmp_path)}.*`$", caplog.text) == 2


def test_cli_evaluate(datadir: pathlib.Path, tmp_path: pathlib.Path, caplog):
    runner = CliRunner()

    radar_pdf = tmp_path / "radar.pdf"

    with caplog.at_level("INFO", logger="fairical"):
        result = runner.invoke(
            cli,
            [
                "evaluate",
                "-vv",
                str(datadir / "data" / "uc-2" / "system_1.json"),
                str(datadir / "data" / "uc-2" / "system_2.json"),
                "--deduplicate",
                "--radar",
                str(radar_pdf),
            ],
        )

    assert result.exit_code == 0
    assert radar_pdf.exists()

    assert (
        str_counter(
            r"^\s*system_1\s*0.12\s*0.50\s*1.00\s*0.00\s*0.24\s*0.12$", result.output
        )
        == 1
    )
    assert (
        str_counter(
            r"^\s*system_2\s*1.00\s*0.89\s*1.00\s*0.26\s*0.09\s*0.43$", result.output
        )
        == 1
    )

    assert str_counter("Loading solutions for system", caplog.text) == 2
    assert str_counter("Deduplication reduced solutions", caplog.text) == 2
    assert str_counter("Non-dominated/Dominated solutions", caplog.text) == 2


def test_cli_evaluate_nodedup(datadir: pathlib.Path, tmp_path: pathlib.Path, caplog):
    runner = CliRunner()

    radar_pdf = tmp_path / "radar.pdf"

    with caplog.at_level("INFO", logger="fairical"):
        result = runner.invoke(
            cli,
            [
                "evaluate",
                "-vv",
                str(datadir / "data" / "uc-2" / "system_1.json"),
                str(datadir / "data" / "uc-2" / "system_2.json"),
                "--no-deduplicate",
            ],
        )

    assert result.exit_code == 0
    assert not radar_pdf.exists()  # should not exist, as no opt given

    assert (
        str_counter(
            r"^\s*system_1\s*0.12\s*0.04\s*1.00\s*0.00\s*0.24\s*0.02$", result.output
        )
        == 1
    )
    assert (
        str_counter(
            r"^\s*system_2\s*1.00\s*0.32\s*1.00\s*0.26\s*0.09\s*0.20$", result.output
        )
        == 1
    )

    assert str_counter("Loading solutions for system.*", caplog.text) == 2
    assert str_counter("Non-dominated/Dominated solutions", caplog.text) == 2


def test_cli_plot_3d(datadir: pathlib.Path, tmp_path: pathlib.Path, caplog):
    runner = CliRunner()

    pareto_pdf = tmp_path / "plot.pdf"

    with caplog.at_level("INFO", logger="fairical"):
        result = runner.invoke(
            cli,
            [
                "plot",
                "-vv",
                str(datadir / "data" / "uc-3" / "system_1.json"),
                str(datadir / "data" / "uc-3" / "system_2.json"),
                "--pareto",
                str(pareto_pdf),
            ],
        )

    assert result.exit_code == 0
    assert pareto_pdf.exists()

    assert str_counter("Loading solutions for system", caplog.text) == 2
    assert str_counter("Deduplication reduced solutions", caplog.text) == 2
    assert str_counter("Non-dominated/Dominated solutions", caplog.text) == 2
    assert str_counter(f"Saving plot at `{str(pareto_pdf)}`", caplog.text) == 1
