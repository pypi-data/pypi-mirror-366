"""
Tests for CLI functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from click.testing import CliRunner

from copycatm.cli.commands import cli


class TestCLI:
    """Test CLI commands."""
    
    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()
        
        # Create temporary test files
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.py")
        
        with open(self.test_file, "w") as f:
            f.write("""
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
""")
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_analyze_command(self):
        """Test analyze command."""
        result = self.runner.invoke(cli, ["analyze", self.test_file])
        assert result.exit_code == 0
        assert "copycatm_version" in result.output
    
    def test_batch_command(self):
        """Test batch command."""
        result = self.runner.invoke(cli, ["batch", self.temp_dir])
        assert result.exit_code == 0
        assert "results" in result.output
    
    def test_single_command(self):
        """Test single command (alias for analyze)."""
        result = self.runner.invoke(cli, ["single", self.test_file])
        assert result.exit_code == 0
        assert "copycatm_version" in result.output
    
    def test_verbose_output(self):
        """Test verbose output."""
        result = self.runner.invoke(cli, ["-v", "analyze", self.test_file])
        assert result.exit_code == 0
    
    def test_quiet_output(self):
        """Test quiet output."""
        result = self.runner.invoke(cli, ["-q", "analyze", self.test_file])
        assert result.exit_code == 0
    
    def test_debug_output(self):
        """Test debug output."""
        result = self.runner.invoke(cli, ["--debug", "analyze", self.test_file])
        assert result.exit_code == 0
    
    def test_output_file(self):
        """Test output to file."""
        output_file = os.path.join(self.temp_dir, "output.json")
        result = self.runner.invoke(cli, ["-o", output_file, "analyze", self.test_file])
        assert result.exit_code == 0
        assert os.path.exists(output_file)
    
    def test_complexity_threshold(self):
        """Test complexity threshold option."""
        result = self.runner.invoke(cli, ["analyze", self.test_file, "-c", "5"])
        assert result.exit_code == 0
    
    def test_min_lines(self):
        """Test min lines option."""
        result = self.runner.invoke(cli, ["analyze", self.test_file, "--min-lines", "10"])
        assert result.exit_code == 0
    
    def test_include_intermediates(self):
        """Test include intermediates option."""
        result = self.runner.invoke(cli, ["analyze", self.test_file, "--include-intermediates"])
        assert result.exit_code == 0
    
    def test_hash_algorithms(self):
        """Test hash algorithms option."""
        result = self.runner.invoke(cli, ["analyze", self.test_file, "--hash-algorithms", "sha256,tlsh"])
        assert result.exit_code == 0
    
    def test_confidence_threshold(self):
        """Test confidence threshold option."""
        result = self.runner.invoke(cli, ["analyze", self.test_file, "--confidence-threshold", "0.8"])
        assert result.exit_code == 0
    
    def test_only_algorithms(self):
        """Test only algorithms option."""
        result = self.runner.invoke(cli, ["analyze", self.test_file, "--only-algorithms"])
        assert result.exit_code == 0
    
    def test_only_metadata(self):
        """Test only metadata option."""
        result = self.runner.invoke(cli, ["analyze", self.test_file, "--only-metadata"])
        assert result.exit_code == 0
    
    def test_invalid_file(self):
        """Test error handling for invalid file."""
        result = self.runner.invoke(cli, ["analyze", "nonexistent.py"])
        assert result.exit_code != 0
    
    def test_invalid_directory(self):
        """Test error handling for invalid directory."""
        result = self.runner.invoke(cli, ["batch", "nonexistent_dir"])
        assert result.exit_code != 0 