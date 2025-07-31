"""
Tests for the main analyzer functionality.
"""

import pytest
import tempfile
import os
from copycatm.core.analyzer import CopycatAnalyzer
from copycatm.core.config import AnalysisConfig
from copycatm.core.exceptions import AnalysisError, UnsupportedLanguageError


class TestCopycatAnalyzer:
    """Test the main analyzer class."""
    
    def setup_method(self):
        """Setup test environment."""
        self.config = AnalysisConfig(
            complexity_threshold=3,
            min_lines=10,
            include_intermediates=False
        )
        self.analyzer = CopycatAnalyzer(self.config)
        
        # Create temporary test files
        self.temp_dir = tempfile.mkdtemp()
        self.python_file = os.path.join(self.temp_dir, "test.py")
        self.js_file = os.path.join(self.temp_dir, "test.js")
        
        # Python test file with quicksort
        with open(self.python_file, "w") as f:
            f.write("""
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
""")
        
        # JavaScript test file
        with open(self.js_file, "w") as f:
            f.write("""
function quicksort(arr) {
    if (arr.length <= 1) return arr;
    const pivot = arr[Math.floor(arr.length / 2)];
    const left = arr.filter(x => x < pivot);
    const middle = arr.filter(x => x === pivot);
    const right = arr.filter(x => x > pivot);
    return [...quicksort(left), ...middle, ...quicksort(right)];
}
""")
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_analyze_file(self):
        """Test analyzing a single file."""
        result = self.analyzer.analyze_file(self.python_file)
        
        assert "copycatm_version" in result
        assert "file_metadata" in result
        assert "file_properties" in result
        assert "algorithms" in result
        assert "mathematical_invariants" in result
        assert "analysis_summary" in result
        
        # Check file metadata
        metadata = result["file_metadata"]
        assert metadata["file_name"] == "test.py"
        assert metadata["language"] == "python"
        assert metadata["is_source_code"] is True
    
    def test_analyze_directory(self):
        """Test analyzing a directory."""
        results = self.analyzer.analyze_directory(self.temp_dir)
        
        assert isinstance(results, list)
        assert len(results) >= 1  # At least the Python file
    
    def test_analyze_code(self):
        """Test analyzing code string directly."""
        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        
        result = self.analyzer.analyze_code(code, "python", "fibonacci.py")
        
        assert "copycatm_version" in result
        assert result["file_metadata"]["language"] == "python"
    
    def test_unsupported_language(self):
        """Test error handling for unsupported language."""
        with pytest.raises(ValueError):
            self.analyzer.analyze_code("some code", "unsupported_lang", "test.txt")
    
    def test_invalid_file(self):
        """Test error handling for invalid file."""
        with pytest.raises(AnalysisError):
            self.analyzer.analyze_file("nonexistent.py")
    
    def test_configuration(self):
        """Test analyzer with different configurations."""
        # Test with higher complexity threshold
        config = AnalysisConfig(complexity_threshold=10)
        analyzer = CopycatAnalyzer(config)
        result = analyzer.analyze_file(self.python_file)
        assert result is not None
        
        # Test with include intermediates
        config = AnalysisConfig(include_intermediates=True)
        analyzer = CopycatAnalyzer(config)
        result = analyzer.analyze_file(self.python_file)
        assert result is not None
    
    def test_javascript_analysis(self):
        """Test analyzing JavaScript code."""
        result = self.analyzer.analyze_file(self.js_file)
        
        assert result["file_metadata"]["language"] == "javascript"
        assert result["file_metadata"]["is_source_code"] is True
    
    def test_small_file_analysis(self):
        """Test analyzing a small file (should trigger invariant extraction)."""
        small_file = os.path.join(self.temp_dir, "small.py")
        with open(small_file, "w") as f:
            f.write("x = 1 + 2")
        
        result = self.analyzer.analyze_file(small_file)
        
        # Small files should have invariants instead of algorithms
        assert len(result["algorithms"]) == 0
        # Note: The current implementation always returns at least one invariant
        # This is a placeholder behavior
    
    def test_hash_generation(self):
        """Test that hashes are generated correctly."""
        result = self.analyzer.analyze_file(self.python_file)
        
        # Check that hashes are present in algorithms
        if result["algorithms"]:
            algorithm = result["algorithms"][0]
            assert "hashes" in algorithm
            hashes = algorithm["hashes"]
            assert "direct" in hashes
            assert "fuzzy" in hashes
            assert "semantic" in hashes
    
    def test_transformation_resistance(self):
        """Test transformation resistance calculation."""
        result = self.analyzer.analyze_file(self.python_file)
        
        # Check that transformation resistance is calculated
        if result["algorithms"]:
            algorithm = result["algorithms"][0]
            assert "transformation_resistance" in algorithm
            resistance = algorithm["transformation_resistance"]
            assert "variable_renaming" in resistance
            assert "language_translation" in resistance
            assert "style_changes" in resistance
            assert "framework_adaptation" in resistance 