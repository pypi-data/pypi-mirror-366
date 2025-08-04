"""
Test CLI argument parsing and validation for GetAtmos.
DownloadAtmos or MergeAtmos aren't called - we just mock em, boohoo.
"""

import sys
import tempfile
from argparse import ArgumentTypeError
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from tfv_get_tools.cli.atmos_cli import GetAtmos


class TestCLIArgumentParsing:
    """Test argument parsing for both download (A) and merge (B) commands.
    Nothing magical happening here - just straight argparse confirmation of types.
    """

    def setup_method(self):
        """Set up test environment with mock functions."""
        self.mock_download = Mock()
        self.mock_merge = Mock()

        # Create CLI instance with injected mock functions
        self.cli = GetAtmos(
            download_func=self.mock_download, merge_func=self.mock_merge
        )

    def test_download_command_basic_args(self):
        """Test download command with minimal required arguments."""
        test_args = [
            "A",
            "2022-01-01 00:00",
            "2022-01-31 23:00",
            "145",
            "155",
            "-40",
            "-30",
        ]

        with patch.object(sys, "argv", test_args):
            args = self.cli.parser.parse_args(test_args)

            assert args.command == "A"
            assert args.time_start == "2022-01-01 00:00"
            assert args.time_end == "2022-01-31 23:00"
            assert args.bbox == [
                145,
                155,
                -40,
                -30,
            ]  # bbox will be converted to numeric (int or float)
            # TODO: we should probably convert bbox to tuple of floats here
            assert args.source == "ERA5"  # default
            assert args.model == "default"  # default
            assert args.test is False  # default

    def test_download_command_with_optional_args(self):
        """Test download command with optional arguments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_args = [
                "A",
                "2022-01-01 00:00",
                "2022-01-31 23:00",
                "145",
                "155",
                "-40",
                "-30",
                "-p",
                temp_dir,
                "-s",
                "BARRA2",
                "-m",
                "R2",
                "--test",
            ]

            args = self.cli.parser.parse_args(test_args)

            assert args.path == Path(temp_dir)
            assert args.source == "BARRA2"
            assert args.model == "R2"
            assert args.test is True

    def test_download_command_invalid_path(self):
        """Test download command with invalid output path."""
        test_args = [
            "A",
            "2022-01-01 00:00",
            "2022-01-31 23:00",
            "145",
            "155",
            "-40",
            "-30",
            "-p",
            "/nonexistent/path",
        ]

        with pytest.raises(SystemExit):  # argparse exits on error
            self.cli.parser.parse_args(test_args)

    def test_merge_command_basic_args(self):
        """Test merge command with minimal arguments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_args = ["B", "-i", temp_dir, "-o", temp_dir]

            args = self.cli.parser.parse_args(test_args)

            assert args.command == "B"
            assert args.in_path == Path(temp_dir)
            assert args.out_path == Path(temp_dir)
            assert args.source == "ERA5"  # default
            assert args.model == "default"  # default

    def test_merge_command_with_all_options(self):
        """Test merge command with all optional arguments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_args = [
                "B",
                "-f",
                "some_hekkers_merged_named.nc",
                "--time_start",
                "2022-01-01 00:00",
                "--time_end",
                "2022-07-31 23:00",
                "-i",
                temp_dir,
                "-o",
                temp_dir,
                "-s",
                "BARRA2",
                "-m",
                "C2",
                "-fvc",
                "-rp",
                "7856",
                "-tz",
                "10",
                "-ltz",
                "AEST",
                "--wrapto360",
                "--pad_dry",
            ]

            args = self.cli.parser.parse_args(test_args)

            assert args.file_name == "some_hekkers_merged_named.nc"
            assert args.time_start == "2022-01-01 00:00"
            assert args.time_end == "2022-07-31 23:00"
            assert args.source == "BARRA2"
            assert args.model == "C2"
            assert args.write_fvc is True
            assert args.reproject == 7856
            assert args.timezone_offset == 10.0
            assert args.timezone_label == "AEST"
            assert args.wrapto360 is True
            assert args.pad_dry is True

    def test_info_command(self):
        """Test info command parsing."""
        args = self.cli.parser.parse_args(["info"])

        assert args.command == "info"
        assert hasattr(args, "func")


class TestCLIExecution:
    """Test CLI execution with mocked functions."""

    def setup_method(self):
        """Set up test environment with mock functions."""
        self.mock_download = Mock()
        self.mock_merge = Mock()

        self.cli = GetAtmos(
            download_func=self.mock_download, merge_func=self.mock_merge
        )

    def test_download_execution(self):
        """Test that download function is called with correct arguments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_args = [
                "A",
                "2022-01-01 00:00",
                "2022-07-31 23:00",
                "145",
                "155",
                "-40",
                "-30",
                "-p",
                temp_dir,
                "-s",
                "BARRA2",
                "--test",
            ]

            args = self.cli.parser.parse_args(test_args)
            self.cli.run_download(args)

            # Verify mock was called with correct arguments
            self.mock_download.assert_called_once_with(
                "2022-01-01 00:00",
                "2022-07-31 23:00",
                (145.0, 155.0),  # xlims as tuple of floats
                (-40.0, -30.0),  # ylims as tuple of floats
                source="BARRA2",
                out_path=Path(temp_dir),
                TEST_MODE=True,
            )

    def test_merge_execution_basic(self):
        """Test that merge function is called with basic arguments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_args = ["B", "-i", temp_dir, "-o", temp_dir]

            args = self.cli.parser.parse_args(test_args)
            self.cli.run_merge(args)

            # Verify mock was called
            self.mock_merge.assert_called_once()
            call_args = self.mock_merge.call_args

            assert call_args.kwargs["in_path"] == Path(temp_dir)
            assert call_args.kwargs["out_path"] == Path(temp_dir)
            assert call_args.kwargs["source"] == "ERA5"
            assert call_args.kwargs["model"] == "default"
            assert call_args.kwargs["local_tz"] is None

    def test_merge_execution_with_timezone(self):
        """Test merge execution with timezone arguments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_args = [
                "B",
                "-i",
                temp_dir,
                "-o",
                temp_dir,
                "-tz",
                "10",
                "-ltz",
                "AEST",
            ]

            args = self.cli.parser.parse_args(test_args)
            self.cli.run_merge(args)

            call_args = self.mock_merge.call_args
            assert call_args.kwargs["local_tz"] == (10.0, "AEST")

    def test_merge_execution_timezone_offset_only(self):
        """Test merge execution with only timezone offset."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_args = ["B", "-i", temp_dir, "-o", temp_dir, "-tz", "-8"]

            args = self.cli.parser.parse_args(test_args)
            self.cli.run_merge(args)

            call_args = self.mock_merge.call_args
            assert call_args.kwargs["local_tz"] == (-8.0, "UTC-8.0")

    def test_merge_execution_timezone_label_without_offset_error(self):
        """Test that timezone label without offset raises error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_args = ["B", "-i", temp_dir, "-o", temp_dir, "-ltz", "AEST"]

            args = self.cli.parser.parse_args(test_args)

            with pytest.raises(ValueError, match="Need to supply a timezone_offset"):
                self.cli.run_merge(args)

    def test_info_execution(self):
        """Test info command execution."""
        args = self.cli.parser.parse_args(["info"])

        # Capture stdout to verify info is printed
        import io
        from contextlib import redirect_stdout

        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            self.cli.print_detailed_info(args)

        output = captured_output.getvalue()
        assert "GetAtmos" in output
        assert "ERA5" in output
        assert "BARRA2" in output


class TestCLIPathValidation:
    """Test path validation functionality."""

    def setup_method(self):
        """Set up CLI instance."""
        self.cli = GetAtmos()

    def test_valid_directory_path(self):
        """Test that valid directory paths are accepted."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.cli.dir_path(temp_dir)
            assert result == Path(temp_dir)
            assert isinstance(result, Path)

    def test_invalid_directory_path(self):
        """Test that invalid directory paths raise ArgumentTypeError."""
        with pytest.raises(ArgumentTypeError, match="is not a valid path"):
            self.cli.dir_path("/this/path/does/not/exist")

    def test_file_instead_of_directory(self):
        """Test that file paths (not directories) raise ArgumentTypeError."""
        with tempfile.NamedTemporaryFile() as temp_file:
            with pytest.raises(ArgumentTypeError, match="is not a valid path"):
                self.cli.dir_path(temp_file.name)


class TestBboxParsing:
    """Test bounding box coordinate parsing."""

    def setup_method(self):
        """Set up CLI instance."""
        self.cli = GetAtmos()

    def test_bbox_parsing_integers(self):
        """Test bbox parsing with integer coordinates."""
        test_args = [
            "A",
            "2022-01-01 00:00",
            "2022-01-31 23:00",
            "145",
            "155",
            "-40",
            "-30",
        ]

        args = self.cli.parser.parse_args(test_args)
        assert args.bbox == [145, 155, -40, -30]

        # Test conversion in run_download
        xlims = tuple([float(x) for x in args.bbox[:2]])
        ylims = tuple([float(x) for x in args.bbox[2:]])

        assert xlims == (145.0, 155.0)
        assert ylims == (-40.0, -30.0)

    def test_bbox_parsing_floats(self):
        """Test bbox parsing with float coordinates."""
        test_args = [
            "A",
            "2022-01-01 00:00",
            "2022-01-31 23:00",
            "145.5",
            "155.25",
            "-40.75",
            "-30.1",
        ]

        args = self.cli.parser.parse_args(test_args)

        xlims = tuple([float(x) for x in args.bbox[:2]])
        ylims = tuple([float(x) for x in args.bbox[2:]])

        assert xlims == (145.5, 155.25)
        assert ylims == (-40.75, -30.1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
