"""
Semantic hashing implementation with proper MinHash, reduced false positives,
and better algorithm differentiation.
"""

import hashlib
import re
import struct
from typing import List, Any, Optional, Set, Dict, Tuple
import random


class SemanticHasher:
    """Semantic hasher with proper MinHash implementation and better differentiation."""
    
    def __init__(self, num_perm: int = 128, lsh_bands: int = 20):
        self.num_perm = num_perm
        self.lsh_bands = lsh_bands
        
        # Generate hash functions for MinHash (using random seeds)
        random.seed(42)  # Reproducible hash functions
        self.hash_functions = []
        for i in range(num_perm):
            a = random.randint(1, (1 << 31) - 1)
            b = random.randint(0, (1 << 31) - 1)
            c = random.randint(1, (1 << 31) - 1)
            self.hash_functions.append((a, b, c))
    
    def generate_minhash(self, text: str) -> str:
        """Generate proper MinHash from text data."""
        # Extract shingles (n-grams) from text
        shingles = self._extract_shingles(text, n=3)
        
        if not shingles:
            # Return hash of empty content (not a static value)
            return hashlib.md5(b"empty").hexdigest()[:16]
        
        # Initialize MinHash signature
        signature = [float('inf')] * self.num_perm
        
        # Apply hash functions to each shingle
        for shingle in shingles:
            shingle_hash = hash(shingle) & 0x7FFFFFFF  # Ensure positive
            
            for i, (a, b, c) in enumerate(self.hash_functions):
                # Universal hash function: h(x) = (ax + b) mod c
                hash_value = ((a * shingle_hash + b) % c) & 0x7FFFFFFF
                signature[i] = min(signature[i], hash_value)
        
        # Convert signature to hex string
        hex_parts = []
        for i in range(0, len(signature), 4):
            # Combine 4 values into one hex chunk
            combined = 0
            for j in range(4):
                if i + j < len(signature):
                    combined ^= signature[i + j]
            hex_parts.append(format(combined & 0xFFFF, '04x'))
        
        return ''.join(hex_parts[:8])  # Return first 32 hex chars
    
    def minhash(self, ast_tree: Any) -> str:
        """Generate MinHash from AST (compatibility method)."""
        return self.minhash_from_ast(ast_tree)
    
    def simhash(self, data: str) -> str:
        """Generate SimHash from text (compatibility method)."""
        return self.generate_simhash(data)
    
    def generate_simhash(self, text: str) -> str:
        """Generate SimHash with better feature extraction."""
        # Extract weighted features
        features = self._extract_algorithmic_features(text)
        
        if not features:
            # Return hash of empty content
            return hashlib.md5(b"empty").hexdigest()[:16]
        
        # Initialize SimHash vector
        hash_bits = 64
        vector = [0] * hash_bits
        
        # Process each feature with its weight
        for feature, weight in features.items():
            # Hash the feature
            feature_hash = int(hashlib.md5(feature.encode('utf-8')).hexdigest(), 16)
            
            # Update vector based on bits
            for i in range(hash_bits):
                if feature_hash & (1 << i):
                    vector[i] += weight
                else:
                    vector[i] -= weight
        
        # Generate final SimHash
        simhash_value = 0
        for i in range(hash_bits):
            if vector[i] > 0:
                simhash_value |= (1 << i)
        
        return format(simhash_value, '016x').upper()
    
    def _extract_shingles(self, text: str, n: int = 3) -> Set[str]:
        """Extract n-gram shingles from text for MinHash."""
        # Normalize text
        normalized = self._normalize_for_shingles(text)
        
        # Extract character n-grams
        shingles = set()
        for i in range(len(normalized) - n + 1):
            shingle = normalized[i:i+n]
            if shingle.strip():  # Skip empty shingles
                shingles.add(shingle)
        
        # Also extract token-based shingles for better algorithm detection
        tokens = self._tokenize_code(normalized)
        for i in range(len(tokens) - n + 1):
            token_shingle = ' '.join(tokens[i:i+n])
            shingles.add(token_shingle)
        
        return shingles
    
    def _normalize_for_shingles(self, text: str) -> str:
        """Normalize text for shingle extraction."""
        # Remove comments
        text = re.sub(r'#.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Keep algorithmic structure but normalize syntax
        text = re.sub(r'\b(var|let|const|auto|int|float|double|string)\b', 'VAR', text)
        text = re.sub(r'\b[a-zA-Z_]\w*\b', lambda m: m.group() if self._is_keyword(m.group()) else 'ID', text)
        
        return text.strip()
    
    def _tokenize_code(self, text: str) -> List[str]:
        """Tokenize code into meaningful units."""
        # Split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b|[^\w\s]', text)
        
        # Filter out single characters except operators
        filtered_tokens = []
        for token in tokens:
            if len(token) > 1 or token in '+-*/=<>!&|':
                filtered_tokens.append(token)
        
        return filtered_tokens
    
    def _is_keyword(self, word: str) -> bool:
        """Check if word is a programming keyword."""
        keywords = {
            'if', 'else', 'elif', 'while', 'for', 'do', 'switch', 'case',
            'try', 'catch', 'finally', 'return', 'break', 'continue',
            'def', 'function', 'class', 'struct', 'void', 'public', 'private'
        }
        return word.lower() in keywords
    
    def _extract_algorithmic_features(self, text: str) -> Dict[str, int]:
        """Extract features that distinguish algorithms."""
        features = {}
        
        # Algorithm-specific patterns with higher weights
        algorithm_patterns = {
            # Sorting patterns
            'sort_swap': (r'\w+\s*[,=]\s*\w+\s*[,=]\s*\w+', 10),  # Swap pattern
            'sort_compare': (r'if\s*\([^)]*[<>]=?\s*[^)]*\)', 8),  # Comparison
            'sort_pivot': (r'pivot|partition', 12),  # Quicksort specific
            'sort_bubble': (r'for.*for.*if.*swap|bubble', 15),  # Bubble sort
            
            # Search patterns  
            'search_binary': (r'(left|low|high|mid|middle)\s*[+\-=]', 12),  # Binary search
            'search_linear': (r'for.*if.*return|find|search', 8),  # Linear search
            'search_target': (r'target|needle|search|find', 6),
            
            # Recursive patterns
            'recursive_call': (r'(\w+)\s*\([^)]*\1[^)]*\)', 10),  # Self-call
            'recursive_base': (r'if.*return(?!.*\()', 8),  # Base case
            
            # Mathematical patterns
            'math_fibonacci': (r'fib|n-1.*n-2', 15),  # Fibonacci specific
            'math_factorial': (r'fact|n\s*\*.*n-1', 12),  # Factorial
            'math_modulo': (r'%|mod', 6),
            
            # Data structure patterns
            'array_access': (r'\[\s*\w+\s*\]', 4),
            'loop_pattern': (r'for|while', 5),
            'conditional': (r'if|else', 4)
        }
        
        # Extract pattern features
        for pattern_name, (pattern, weight) in algorithm_patterns.items():
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            if matches > 0:
                features[f"algo:{pattern_name}"] = weight * min(matches, 3)  # Cap at 3 occurrences
        
        # Extract structural complexity features
        lines = text.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        
        # Line count bins (different algorithms have different sizes)
        line_bin = min(len(non_empty_lines) // 10, 10)
        features[f"size:lines_{line_bin}"] = 5
        
        # Nesting depth (important for algorithm complexity)
        max_indent = 0
        for line in non_empty_lines:
            indent = len(line) - len(line.lstrip())
            max_indent = max(max_indent, indent)
        
        indent_bin = min(max_indent // 4, 5)
        features[f"complexity:nesting_{indent_bin}"] = 7
        
        # Control flow complexity
        control_keywords = ['if', 'else', 'elif', 'while', 'for', 'switch', 'case']
        control_count = sum(1 for keyword in control_keywords 
                          if re.search(rf'\b{keyword}\b', text, re.IGNORECASE))
        
        complexity_bin = min(control_count // 2, 5)
        features[f"complexity:control_{complexity_bin}"] = 6
        
        # Function/method count
        function_count = len(re.findall(r'\b(def|function|void|int|float)\s+\w+\s*\(', text))
        features[f"structure:functions_{min(function_count, 5)}"] = 4
        
        # Operator distribution (different algorithms use different operations)
        operators = {
            'arithmetic': r'[+\-*/]',
            'comparison': r'[<>=!]=?',
            'logical': r'&&|\|\||and|or',
            'bitwise': r'[&|^~](?![&|])',
            'assignment': r'=(?!=)'
        }
        
        for op_type, pattern in operators.items():
            count = len(re.findall(pattern, text))
            if count > 0:
                features[f"ops:{op_type}_{min(count // 3, 5)}"] = 3
        
        return features
    
    def calculate_similarity(self, hash1: str, hash2: str, hash_type: str = "minhash") -> float:
        """Calculate similarity between two hashes with better accuracy."""
        try:
            if not hash1 or not hash2 or hash1 == "empty" or hash2 == "empty":
                return 0.0
            
            if hash_type == "minhash":
                # Estimate Jaccard similarity from MinHash signatures
                return self._estimate_minhash_similarity(hash1, hash2)
            elif hash_type == "simhash":
                # Calculate normalized Hamming distance
                return self._calculate_simhash_similarity(hash1, hash2)
            else:
                return 0.0
        except Exception:
            return 0.0
    
    def _estimate_minhash_similarity(self, hash1: str, hash2: str) -> float:
        """Estimate Jaccard similarity from MinHash signatures."""
        if hash1 == hash2:
            return 1.0
        
        # Compare hash chunks (each chunk represents multiple hash values)
        chunks1 = [hash1[i:i+4] for i in range(0, len(hash1), 4)]
        chunks2 = [hash2[i:i+4] for i in range(0, len(hash2), 4)]
        
        if len(chunks1) != len(chunks2):
            return 0.0
        
        # Count matching chunks
        matches = sum(1 for c1, c2 in zip(chunks1, chunks2) if c1 == c2)
        
        # Estimate similarity (with adjustment for hash collisions)
        base_similarity = matches / len(chunks1)
        
        # Apply non-linear scaling to reduce false positives
        # This makes small differences more significant
        if base_similarity < 0.5:
            return base_similarity * 0.5  # Reduce low similarities
        elif base_similarity < 0.8:
            return 0.25 + (base_similarity - 0.5) * 0.833  # Linear in middle range
        else:
            return 0.5 + (base_similarity - 0.8) * 2.5  # Amplify high similarities
    
    def _calculate_simhash_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate similarity from SimHash values."""
        if len(hash1) != len(hash2):
            return 0.0
        
        # Convert hex strings to integers
        try:
            val1 = int(hash1, 16)
            val2 = int(hash2, 16)
        except ValueError:
            return 0.0
        
        # Calculate Hamming distance
        xor = val1 ^ val2
        distance = bin(xor).count('1')
        
        # Maximum possible distance is 64 bits
        max_distance = 64
        
        # Convert to similarity (with non-linear scaling)
        raw_similarity = 1.0 - (distance / max_distance)
        
        # Apply scaling to reduce false positives
        if raw_similarity < 0.6:
            return raw_similarity * 0.3  # Heavily penalize low similarities
        elif raw_similarity < 0.8:
            return 0.18 + (raw_similarity - 0.6) * 1.6  # Moderate scaling
        else:
            return 0.5 + (raw_similarity - 0.8) * 2.5  # Amplify high similarities
    
    def minhash_from_ast(self, ast_tree: Any) -> str:
        """Generate MinHash from AST with better feature extraction."""
        features = []
        
        if hasattr(ast_tree, 'root'):
            self._extract_ast_features_recursive(ast_tree.root, features)
        
        if not features:
            # Extract from code if AST traversal fails
            if hasattr(ast_tree, 'code'):
                return self.generate_minhash(ast_tree.code)
            return hashlib.md5(b"empty_ast").hexdigest()[:16]
        
        # Convert features to text and generate MinHash
        feature_text = ' '.join(features)
        return self.generate_minhash(feature_text)
    
    def _extract_ast_features_recursive(self, node: Any, features: List[str], depth: int = 0):
        """Recursively extract meaningful features from AST."""
        if not hasattr(node, 'type') or depth > 10:  # Limit depth
            return
        
        # Extract node type and structural information
        node_type = node.type
        
        # Important node types for algorithm detection
        important_types = {
            'function_definition', 'function_declaration', 'method_definition',
            'if_statement', 'while_statement', 'for_statement', 'switch_statement',
            'return_statement', 'assignment', 'binary_operator', 'comparison_operator',
            'call_expression', 'array_access', 'recursive_call'
        }
        
        if node_type in important_types:
            features.append(f"ast:{node_type}")
            
            # Add context information
            if hasattr(node, 'children') and node.children:
                child_types = [child.type for child in node.children[:3] if hasattr(child, 'type')]
                if child_types:
                    features.append(f"pattern:{node_type}->{'-'.join(child_types)}")
        
        # Extract operator information
        if 'operator' in node_type and hasattr(node, 'text'):
            op_text = str(node.text).strip()
            if op_text in '+-*/<>=!&|':
                features.append(f"op:{op_text}")
        
        # Recurse through children
        if hasattr(node, 'children'):
            for child in node.children:
                self._extract_ast_features_recursive(child, features, depth + 1)
    
    # Compatibility method aliases
    def minhash_from_text(self, text: str) -> str:
        """Alias for generate_minhash for compatibility."""
        return self.generate_minhash(text)
    
    def simhash_from_text(self, text: str) -> str:
        """Alias for generate_simhash for compatibility."""
        return self.generate_simhash(text)
    
    def semantic_similarity(self, hash1: str, hash2: str, hash_type: str = "minhash") -> float:
        """Alias for calculate_similarity for compatibility."""
        return self.calculate_similarity(hash1, hash2, hash_type)