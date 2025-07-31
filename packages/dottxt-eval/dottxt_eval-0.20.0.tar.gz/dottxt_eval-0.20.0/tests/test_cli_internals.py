"""Tests for CLI internal functionality to achieve targeted coverage."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from doteval.cli import cli


def create_mock_storage_with_experiments(temp_dir, experiments_data):
    """Helper to create mock storage with experiment data."""
    storage_path = Path(temp_dir)

    # Create experiment directories and files
    for exp_name, evaluations in experiments_data.items():
        exp_path = storage_path / exp_name
        exp_path.mkdir(parents=True, exist_ok=True)

        # Create evaluation files
        for eval_name in evaluations:
            eval_path = exp_path / f"{eval_name}.json"
            eval_path.write_text('{"test": "data"}')

    return f"json://{storage_path}"


class TestListCLI:
    """Test the list CLI command."""

    def test_list_experiments_skip_doteval_directory(self):
        """Test that .doteval directory is skipped (line 37)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = f"json://{temp_dir}"

            with patch("doteval.cli.get_storage") as mock_get_storage:
                mock_storage_backend = MagicMock()
                mock_storage_backend.list_experiments.return_value = [
                    ".doteval",
                    "real_experiment",
                ]
                mock_storage_backend.list_evaluations.return_value = ["eval1", "eval2"]
                mock_get_storage.return_value = mock_storage_backend

                runner = CliRunner()
                result = runner.invoke(cli, ["list", "--storage", storage])

                assert result.exit_code == 0
                # Should have called list_evaluations only for real_experiment, not .doteval
                calls = mock_storage_backend.list_evaluations.call_args_list
                called_experiments = [call[0][0] for call in calls]
                assert "real_experiment" in called_experiments
                assert ".doteval" not in called_experiments

    def test_list_experiments_ephemeral_pattern_matching(self):
        """Test ephemeral experiment pattern matching (line 39)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = f"json://{temp_dir}"

            with patch("doteval.cli.get_storage") as mock_get_storage:
                mock_storage_backend = MagicMock()
                mock_storage_backend.list_experiments.return_value = [
                    "named_experiment",
                    "20231201_120000_abcd1234",  # Ephemeral pattern
                    "another_named",
                ]
                mock_storage_backend.list_evaluations.return_value = ["eval1"]
                mock_get_storage.return_value = mock_storage_backend

                runner = CliRunner()
                result = runner.invoke(cli, ["list", "--storage", storage])

                assert result.exit_code == 0
                # Should have processed both named and ephemeral experiments
                assert (
                    "Named Experiments" in result.output
                    or "Ephemeral Experiments" in result.output
                )

    def test_list_experiments_no_experiments_found(self):
        """Test when no experiments are found (lines 43-45)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = f"json://{temp_dir}"

            with patch("doteval.cli.get_storage") as mock_get_storage:
                mock_storage_backend = MagicMock()
                mock_storage_backend.list_experiments.return_value = []
                mock_get_storage.return_value = mock_storage_backend

                runner = CliRunner()
                result = runner.invoke(cli, ["list", "--storage", storage])

                assert result.exit_code == 0
                assert "No experiments found" in result.output

    def test_list_experiments_name_filtering(self):
        """Test experiment name filtering (line 54, 69)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = f"json://{temp_dir}"

            with patch("doteval.cli.get_storage") as mock_get_storage:
                mock_storage_backend = MagicMock()
                mock_storage_backend.list_experiments.return_value = [
                    "experiment_match",
                    "20231201_120000_match1234",  # Ephemeral with match
                    "20231201_130000_other1234",  # Ephemeral without match
                    "experiment_other",
                ]
                mock_storage_backend.list_evaluations.return_value = ["eval1"]
                mock_get_storage.return_value = mock_storage_backend

                # Filter by name "match"
                runner = CliRunner()
                result = runner.invoke(
                    cli, ["list", "--name", "match", "--storage", storage]
                )

                assert result.exit_code == 0
                # Should have called list_evaluations only for experiments containing "match"
                calls = mock_storage_backend.list_evaluations.call_args_list
                called_experiments = [call[0][0] for call in calls]

                # Should include experiments with "match" in name
                expected_matches = ["experiment_match", "20231201_120000_match1234"]
                for expected in expected_matches:
                    assert expected in called_experiments

    def test_list_experiments_timestamp_extraction(self):
        """Test timestamp extraction from experiment names (lines 74-78)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = f"json://{temp_dir}"

            with patch("doteval.cli.get_storage") as mock_get_storage:
                mock_storage_backend = MagicMock()
                mock_storage_backend.list_experiments.return_value = [
                    "path/to/20231201_120000_abcd1234",  # With path separator
                    "20231201_130000_efgh5678",  # Without path separator
                ]
                mock_storage_backend.list_evaluations.return_value = ["eval1"]
                mock_get_storage.return_value = mock_storage_backend

                runner = CliRunner()
                result = runner.invoke(cli, ["list", "--storage", storage])

                assert result.exit_code == 0
                # Should have processed both experiments
                assert mock_storage_backend.list_evaluations.call_count == 2

    def test_list_experiments_table_spacing(self):
        """Test table spacing when both named and ephemeral exist (lines 81-83)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = f"json://{temp_dir}"

            with patch("doteval.cli.get_storage") as mock_get_storage:
                mock_storage_backend = MagicMock()
                mock_storage_backend.list_experiments.return_value = [
                    "named_experiment",  # Named
                    "20231201_120000_abcd1234",  # Ephemeral
                ]
                mock_storage_backend.list_evaluations.return_value = ["eval1"]
                mock_get_storage.return_value = mock_storage_backend

                runner = CliRunner()
                result = runner.invoke(cli, ["list", "--storage", storage])

                assert result.exit_code == 0
                # Should have both named and ephemeral sections
                assert "Named Experiments" in result.output
                assert "Ephemeral Experiments" in result.output

    @patch("doteval.cli.get_storage")
    def test_list_experiments_storage_backend_error_handling(self, mock_get_storage):
        """Test error handling when storage backend fails."""
        mock_get_storage.side_effect = Exception("Storage connection failed")

        runner = CliRunner()
        result = runner.invoke(cli, ["list", "--storage", "json://invalid_path"])

        # CLI should handle the error gracefully
        assert result.exit_code != 0

    def test_list_experiments_evaluations_count_display(self):
        """Test that evaluation counts are displayed correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = f"json://{temp_dir}"

            with patch("doteval.cli.get_storage") as mock_get_storage:
                mock_storage_backend = MagicMock()
                mock_storage_backend.list_experiments.return_value = [
                    "exp_with_many",
                    "exp_with_few",
                    "20231201_120000_abcd1234",  # Ephemeral
                ]

                def mock_list_evaluations(exp_name):
                    if exp_name == "exp_with_many":
                        return ["eval1", "eval2", "eval3", "eval4", "eval5"]
                    elif exp_name == "exp_with_few":
                        return ["eval1"]
                    else:
                        return ["eval1", "eval2"]

                mock_storage_backend.list_evaluations.side_effect = (
                    mock_list_evaluations
                )
                mock_get_storage.return_value = mock_storage_backend

                runner = CliRunner()
                result = runner.invoke(cli, ["list", "--storage", storage])

                assert result.exit_code == 0
                # Should have called list_evaluations for each experiment
                assert mock_storage_backend.list_evaluations.call_count == 3
                # Should display counts in output
                assert "5" in result.output  # exp_with_many
                assert "1" in result.output  # exp_with_few
                assert "2" in result.output  # ephemeral
