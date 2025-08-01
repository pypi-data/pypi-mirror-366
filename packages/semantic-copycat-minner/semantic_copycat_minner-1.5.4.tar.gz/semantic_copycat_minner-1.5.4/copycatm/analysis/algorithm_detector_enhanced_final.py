"""
Enhanced Algorithm Detector Final Version - Optimized comprehensive detection.

This final version fixes conflicts and provides the best overall detection.
"""

from typing import Dict, List, Any, Optional, Tuple
import re
from ..analysis.algorithm_detector import AlgorithmDetector
from ..analysis.algorithm_types import AlgorithmType
from ..analysis.false_positive_filter import FalsePositiveFilter


class EnhancedAlgorithmDetectorFinal(AlgorithmDetector):
    """Final enhanced algorithm detector with optimized patterns."""
    
    def __init__(self, config=None):
        """Initialize final enhanced detector."""
        super().__init__(config)
        
        # Initialize false positive filter
        self.fp_filter = FalsePositiveFilter()
        
        # Override pattern priority to check graph algorithms before search
        self.pattern_priority = [
            # Graph algorithms BEFORE search algorithms to avoid conflicts
            AlgorithmType.GRAPH_TRAVERSAL,         # Check graph patterns first
            AlgorithmType.SORTING_ALGORITHM,
            AlgorithmType.SEARCH_ALGORITHM,        # Check search after graph
            AlgorithmType.CRYPTOGRAPHIC_ALGORITHM,
            AlgorithmType.DYNAMIC_PROGRAMMING,
            AlgorithmType.NUMERICAL_ALGORITHM,
            AlgorithmType.COMPRESSION_ALGORITHM,
            AlgorithmType.AUDIO_CODEC,
            AlgorithmType.VIDEO_CODEC,
            AlgorithmType.VIDEO_PROCESSING,
            AlgorithmType.AUDIO_PROCESSING,
            AlgorithmType.IMAGE_PROCESSING,
            AlgorithmType.SIGNAL_PROCESSING,
        ]
        
        # Add all enhanced patterns
        self._add_enhanced_patterns()
    
    def _add_enhanced_patterns(self):
        """Add all enhanced patterns with proper conflict resolution."""
        self._enhance_sorting_patterns()
        self._enhance_search_patterns()
        self._enhance_graph_patterns()
        self._enhance_audio_patterns()
    
    def _enhance_sorting_patterns(self):
        """Enhanced sorting algorithm patterns."""
        if AlgorithmType.SORTING_ALGORITHM in self.patterns:
            sorting = self.patterns[AlgorithmType.SORTING_ALGORITHM]['subtypes']
            
            # Enhanced quicksort
            if 'quicksort' in sorting:
                sorting['quicksort']['required_patterns'] = []
                sorting['quicksort']['flexible_patterns'] = [
                    (r'\[\s*\w+\s+for\s+\w+\s+in\s+\w+\s+if\s+\w+\s*<\s*pivot\s*\]', 0.4),
                    (r'\[\s*\w+\s+for\s+\w+\s+in\s+\w+\s+if\s+\w+\s*>\s*pivot\s*\]', 0.4),
                    (r'pivot\s*=', 0.3),
                    (r'partition\s*\(', 0.3),
                ]
            
            # Enhanced merge sort
            if 'merge_sort' in sorting:
                sorting['merge_sort']['required_patterns'] = []
                sorting['merge_sort']['flexible_patterns'] = [
                    (r'merge\s*\(.*left.*right', 0.5),
                    (r'merge_sort\s*\(.*\[.*:\s*mid', 0.4),
                    (r'merge_sort\s*\(.*\[\s*mid\s*:', 0.4),
                    (r'return\s+merge\s*\(', 0.4),
                ]
    
    def _enhance_search_patterns(self):
        """Enhanced search algorithm patterns with graph conflict avoidance."""
        if AlgorithmType.SEARCH_ALGORITHM in self.patterns:
            search = self.patterns[AlgorithmType.SEARCH_ALGORITHM]['subtypes']
            
            # Linear search - add negative patterns to avoid graph conflicts
            if 'linear_search' in search:
                search['linear_search']['required_patterns'] = []
                search['linear_search']['flexible_patterns'] = [
                    (r'for.*in.*range.*len', 0.4),
                    (r'for.*in.*enumerate', 0.4),
                    (r'if.*==.*target', 0.5),
                    (r'return\s+i(?:\s|$|[^\w])', 0.3),
                    (r'return\s+-1', 0.3),
                ]
                # Add function to check for disqualifying patterns
                search['linear_search']['disqualifiers'] = [
                    r'graph\s*\[',
                    r'visited',
                    r'neighbor',
                    r'queue',
                    r'depth.*first',
                    r'breadth.*first',
                ]
    
    def _enhance_graph_patterns(self):
        """Enhanced graph algorithm patterns with high specificity."""
        if AlgorithmType.GRAPH_TRAVERSAL in self.patterns:
            graph = self.patterns[AlgorithmType.GRAPH_TRAVERSAL]['subtypes']
            
            # DFS with high confidence patterns
            graph['dfs'] = {
                'keywords': ['dfs', 'depth_first_search', 'depth-first'],
                'required_patterns': [],
                'flexible_patterns': [
                    (r'depth_first_search\s*\(', 0.5),
                    (r'visited\.(add|append)', 0.4),
                    (r'for.*neighbor.*in.*graph', 0.4),
                    (r'if.*not.*in.*visited', 0.3),
                    (r'recursive.*graph.*neighbor', 0.3),
                ],
                'confidence_boost': 0.3,
                'min_confidence': 0.5
            }
            
            # BFS with high confidence patterns
            graph['bfs'] = {
                'keywords': ['bfs', 'breadth_first_search', 'breadth-first', 'queue'],
                'required_patterns': [],
                'flexible_patterns': [
                    (r'breadth_first_search\s*\(', 0.5),
                    (r'queue\s*=\s*\[', 0.4),
                    (r'queue\.(append|pop)', 0.4),
                    (r'while.*queue', 0.4),
                    (r'for.*neighbor.*in.*graph', 0.3),
                ],
                'confidence_boost': 0.3,
                'min_confidence': 0.5
            }
            
            # Dijkstra with high confidence patterns
            graph['dijkstra'] = {
                'keywords': ['dijkstra', 'shortest_path', 'distances'],
                'required_patterns': [],
                'flexible_patterns': [
                    (r'dijkstra.*\(', 0.5),
                    (r'distances\s*=\s*\{', 0.4),
                    (r'float\s*\(\s*[\'"]inf', 0.4),
                    (r'min\s*\(.*key\s*=.*distances', 0.4),
                    (r'unvisited\.(remove|discard)', 0.3),
                ],
                'confidence_boost': 0.3,
                'min_confidence': 0.5
            }
            
            # Update generic to have lower confidence
            if 'generic' in graph:
                graph['generic']['confidence_boost'] = -0.2
    
    def _enhance_audio_patterns(self):
        """Enhanced audio codec patterns for C."""
        if AlgorithmType.AUDIO_CODEC in self.patterns:
            audio = self.patterns[AlgorithmType.AUDIO_CODEC]['subtypes']
            
            # Enhanced PCM codec patterns
            if 'pcm_codec' in audio:
                audio['pcm_codec']['keywords'] = [
                    'pcm', 'pcm_encode', 'pcm_decode', 
                    'audio_encode', 'audio_decode', 'audio_codec',
                    'sample_rate', 'channels', 'bits_per_sample',
                    'AudioCodecContext', 'AudioFrame'
                ]
                
                audio['pcm_codec']['flexible_patterns'] = [
                    # Function names
                    (r'audio_(encode|decode)_frame', 0.6),
                    (r'pcm_(encode|decode)', 0.6),
                    (r'audio_codec_(init|cleanup)', 0.4),
                    
                    # PCM format indicators
                    (r'AUDIO_FORMAT_PCM', 0.5),
                    (r'PCM_S(16|24|32)(LE|BE)', 0.5),
                    
                    # Audio data types
                    (r'int16_t\s*\*\s*(samples|output|input)', 0.4),
                    (r'uint8_t\s*\*\s*data', 0.3),
                    (r'AudioCodecContext', 0.4),
                    (r'AudioFrame', 0.4),
                    
                    # Audio parameters
                    (r'sample_rate', 0.3),
                    (r'channels', 0.3),
                    (r'bits_per_sample', 0.3),
                    (r'frame_size', 0.3),
                    
                    # Bit manipulation for endianness
                    (r'<<\s*8\s*\|.*>>\s*8', 0.4),
                    (r'>>\s*8.*&\s*0xFF', 0.4),
                    
                    # Audio processing patterns
                    (r'samples\s*\[.*\].*=', 0.3),
                    (r'memcpy.*samples', 0.3),
                    (r'sample_count\s*\*\s*.*channels', 0.3),
                ]
                
                # Lower threshold for C files
                audio['pcm_codec']['min_confidence'] = 0.35
                audio['pcm_codec']['required_patterns'] = []
    
    def _calculate_specific_confidence(self, func_text: str, func_name: str, 
                                     func_node: Any, pattern: Dict[str, Any], subtype: str,
                                     language: str = None, algo_type: Any = None) -> float:
        """Calculate confidence with better conflict resolution."""
        
        # Check for disqualifying patterns first
        if 'disqualifiers' in pattern:
            for disqualifier in pattern['disqualifiers']:
                if re.search(disqualifier, func_text, re.IGNORECASE):
                    return 0.0  # Disqualified
        
        confidence = 0.0
        
        # 1. Flexible patterns (highest weight for specificity)
        if 'flexible_patterns' in pattern:
            flex_score = self._check_flexible_patterns(func_text, pattern['flexible_patterns'])
            confidence += flex_score * 0.5  # 50% weight
        
        # 2. Function name matching
        name_score = self._calculate_name_match(func_name, subtype, algo_type)
        confidence += name_score * 0.3  # 30% weight
        
        # 3. Keyword matching
        keyword_score = self._calculate_keyword_score(func_text, func_name, pattern.get('keywords', []))
        confidence += keyword_score * 0.2  # 20% weight
        
        # 4. Check minimum confidence
        min_confidence = pattern.get('min_confidence', 0.3)
        if confidence < min_confidence:
            return 0.0
        
        # 5. Apply boosts/penalties
        confidence += pattern.get('confidence_boost', 0)
        
        # 6. Language-specific adjustments
        if language == 'c' and algo_type == AlgorithmType.AUDIO_CODEC:
            if confidence > 0.3:
                confidence += 0.2
        
        # 7. Avoid false positives
        if func_name.lower() in ['for', 'if', 'while', 'main', 'return']:
            if algo_type != AlgorithmType.AUDIO_CODEC:  # Allow main for audio codecs
                confidence *= 0.1
        
        return min(confidence, 1.0)
    
    def _check_flexible_patterns(self, func_text: str, patterns: List[Tuple[str, float]]) -> float:
        """Check flexible patterns with weights."""
        if not patterns:
            return 0.0
        
        total_score = 0.0
        max_possible = sum(weight for _, weight in patterns)
        
        for pattern, weight in patterns:
            if re.search(pattern, func_text, re.IGNORECASE | re.DOTALL):
                total_score += weight
        
        return total_score / max_possible if max_possible > 0 else 0.0
    
    def _calculate_name_match(self, func_name: str, subtype: str, algo_type: Any) -> float:
        """Calculate function name similarity."""
        func_lower = func_name.lower()
        subtype_lower = subtype.lower()
        
        # Exact or partial match
        if subtype_lower in func_lower or func_lower in subtype_lower:
            return 1.0
        
        # Type-specific matches
        if algo_type == AlgorithmType.GRAPH_TRAVERSAL:
            if 'dfs' in func_lower and 'dfs' in subtype_lower:
                return 1.0
            if 'bfs' in func_lower and 'bfs' in subtype_lower:
                return 1.0
            if 'dijkstra' in func_lower and 'dijkstra' in subtype_lower:
                return 1.0
        
        # Common algorithm name patterns
        patterns = {
            'sort': ['bubble', 'merge', 'quick', 'heap'],
            'search': ['linear', 'binary', 'dfs', 'bfs'],
            'graph': ['dijkstra', 'prim', 'kruskal', 'floyd'],
        }
        
        for category, algorithms in patterns.items():
            if category in func_lower:
                for algo in algorithms:
                    if algo in subtype_lower:
                        return 0.7
        
        return 0.0
    
    def detect_algorithms(self, ast_tree: Any, language: str, file_lines: Optional[int] = None) -> List[Dict[str, Any]]:
        """Detect algorithms with false positive filtering."""
        # Call parent method to get initial detections
        detected_algorithms = super().detect_algorithms(ast_tree, language, file_lines)
        
        
        # Apply false positive filtering
        if detected_algorithms:
            # Get file content for context if available
            file_content = None
            if hasattr(ast_tree, 'text'):
                file_content = ast_tree.text.decode('utf-8') if isinstance(ast_tree.text, bytes) else ast_tree.text
            
            
            # Filter results
            filtered_algorithms = self.fp_filter.enhance_detection_results(
                detected_algorithms, 
                file_content
            )
            
            
            return filtered_algorithms
        
        return detected_algorithms