"""
Tests for GNN functionality.
"""

import pytest
import networkx as nx
from copycatm.gnn.graph_builder import CodeGraphBuilder
from copycatm.gnn.gnn_model import SimpleGNNModel
from copycatm.gnn.similarity_detector import GNNSimilarityDetector


class TestGNN:
    """Test GNN functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.graph_builder = CodeGraphBuilder()
        self.simple_model = SimpleGNNModel()
        self.similarity_detector = GNNSimilarityDetector(use_pytorch=False)
    
    def test_graph_builder_creation(self):
        """Test graph builder initialization."""
        assert self.graph_builder is not None
        assert hasattr(self.graph_builder, 'node_types')
        assert len(self.graph_builder.node_types) > 0
    
    def test_simple_gnn_model(self):
        """Test simple GNN model."""
        # Create test graphs
        graph1 = nx.Graph()
        graph1.add_node("node1", type="function", text="def test()")
        graph1.add_node("node2", type="call", text="print()")
        graph1.add_edge("node1", "node2")
        
        graph2 = nx.Graph()
        graph2.add_node("node1", type="function", text="def test()")
        graph2.add_node("node2", type="call", text="print()")
        graph2.add_edge("node1", "node2")
        
        # Test similarity computation
        similarity = self.simple_model.compute_graph_similarity(graph1, graph2)
        assert 0.0 <= similarity <= 1.0
    
    def test_similarity_detector(self):
        """Test similarity detector."""
        assert self.similarity_detector is not None
        assert hasattr(self.similarity_detector, 'graph_builder')
        assert hasattr(self.similarity_detector, 'gnn_model')
    
    def test_graph_features_extraction(self):
        """Test graph features extraction."""
        # Create a test graph
        graph = nx.Graph()
        graph.add_node("func1", type="function", text="def quicksort()")
        graph.add_node("func2", type="function", text="def binary_search()")
        graph.add_node("call1", type="call", text="print()")
        graph.add_edge("func1", "call1")
        graph.add_edge("func2", "call1")
        
        # Extract features
        features = self.graph_builder.get_graph_features(graph)
        
        assert "num_nodes" in features
        assert "num_edges" in features
        assert "avg_degree" in features
        assert "density" in features
        assert "node_types" in features
        
        assert features["num_nodes"] == 3
        assert features["num_edges"] == 2
    
    def test_similarity_hash_generation(self):
        """Test similarity hash generation."""
        # Create test graph
        graph = nx.Graph()
        graph.add_node("node1", type="function", text="def test()")
        graph.add_node("node2", type="call", text="print()")
        graph.add_edge("node1", "node2")
        
        # Generate hash
        hash_value = self.similarity_detector.get_similarity_hash(graph)
        
        assert isinstance(hash_value, str)
        assert len(hash_value) > 0
    
    def test_multiple_graph_comparison(self):
        """Test comparison of multiple graphs."""
        # Create test graphs
        graphs = []
        
        # Graph 1: Simple function
        graph1 = nx.Graph()
        graph1.add_node("func1", type="function", text="def test()")
        graph1.add_node("call1", type="call", text="print()")
        graph1.add_edge("func1", "call1")
        graphs.append(graph1)
        
        # Graph 2: Similar structure
        graph2 = nx.Graph()
        graph2.add_node("func1", type="function", text="def other()")
        graph2.add_node("call1", type="call", text="print()")
        graph2.add_edge("func1", "call1")
        graphs.append(graph2)
        
        # Graph 3: Different structure
        graph3 = nx.Graph()
        graph3.add_node("class1", type="class", text="class Test")
        graph3.add_node("method1", type="function", text="def method()")
        graph3.add_edge("class1", "method1")
        graphs.append(graph3)
        
        # Compare graphs
        similarities = self.similarity_detector.compare_multiple_graphs(graphs)
        
        assert len(similarities) == 3  # 3 pairs: 0-1, 0-2, 1-2
        for similarity in similarities.values():
            assert 0.0 <= similarity <= 1.0
    
    def test_structural_analysis(self):
        """Test structural analysis."""
        # Create test graphs
        graph1 = nx.Graph()
        graph1.add_node("func1", type="function", text="def test()")
        graph1.add_node("call1", type="call", text="print()")
        graph1.add_edge("func1", "call1")
        
        graph2 = nx.Graph()
        graph2.add_node("func1", type="function", text="def other()")
        graph2.add_node("call1", type="call", text="print()")
        graph2.add_edge("func1", "call1")
        
        # Analyze structural differences
        analysis = self.similarity_detector._analyze_structural_differences(graph1, graph2)
        
        assert "node_type_distribution_1" in analysis
        assert "node_type_distribution_2" in analysis
        assert "structural_metrics" in analysis
        assert "common_patterns" in analysis
        assert "unique_patterns_1" in analysis
        assert "unique_patterns_2" in analysis
    
    def test_pattern_extraction(self):
        """Test pattern extraction from graphs."""
        # Create test graph with various patterns
        graph = nx.Graph()
        graph.add_node("func1", type="function", text="def quicksort()")
        graph.add_node("func2", type="function", text="def binary_search()")
        graph.add_node("class1", type="class", text="class Sorter")
        graph.add_node("if1", type="control", text="if condition")
        graph.add_node("call1", type="call", text="print()")
        graph.add_node("call2", type="call", text="sort()")
        
        # Extract patterns
        patterns = self.similarity_detector._extract_patterns(graph)
        
        assert "functions_2" in patterns
        assert "classes_1" in patterns
        assert "control_flow_1" in patterns
        assert "function_calls_2" in patterns
    
    def test_error_handling(self):
        """Test error handling in GNN components."""
        # Test with empty graph
        empty_graph = nx.Graph()
        
        # Should not raise exception
        similarity = self.simple_model.compute_graph_similarity(empty_graph, empty_graph)
        assert similarity == 0.0
        
        # Test with None graph (should handle gracefully)
        try:
            self.similarity_detector.get_similarity_hash(None)
        except Exception:
            # Should handle None gracefully or raise appropriate exception
            pass 