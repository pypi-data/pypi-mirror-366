"""
Graph Neural Network model for code similarity detection.

This module implements a GNN model for analyzing code structure
similarity using PyTorch and torch-geometric.
"""

import logging
import networkx as nx
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch_geometric.nn import GCNConv, global_mean_pool
    from torch_geometric.data import Data, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.debug("PyTorch and torch-geometric not available. GNN features will be disabled.")


class CodeGNNModel(nn.Module):
    """Graph Neural Network model for code similarity detection."""
    
    def __init__(self, 
                 node_features: int = 64,
                 hidden_channels: int = 128,
                 num_layers: int = 3,
                 dropout: float = 0.2):
        """
        Initialize the GNN model.
        
        Args:
            node_features: Number of input node features
            hidden_channels: Number of hidden channels
            num_layers: Number of GNN layers
            dropout: Dropout rate
        """
        super(CodeGNNModel, self).__init__()
        
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch and torch-geometric are required for GNN features")
        
        self.node_features = node_features
        self.hidden_channels = hidden_channels
        self.num_layers = num_layers
        self.dropout = dropout
        
        # Node feature encoder
        self.node_encoder = nn.Linear(node_features, hidden_channels)
        
        # GNN layers
        self.convs = nn.ModuleList()
        for _ in range(num_layers):
            self.convs.append(GCNConv(hidden_channels, hidden_channels))
        
        # Graph-level classifier
        self.classifier = nn.Sequential(
            nn.Linear(hidden_channels, hidden_channels),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_channels, hidden_channels // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_channels // 2, 1)
        )
        
        # Similarity projection
        self.similarity_projection = nn.Sequential(
            nn.Linear(hidden_channels * 2, hidden_channels),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_channels, hidden_channels // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_channels // 2, 1),
            nn.Sigmoid()
        )
    
    def forward(self, data: Data) -> torch.Tensor:
        """
        Forward pass through the GNN.
        
        Args:
            data: PyTorch Geometric Data object
            
        Returns:
            Graph embeddings
        """
        x, edge_index = data.x, data.edge_index
        
        # Node feature encoding
        x = self.node_encoder(x)
        
        # GNN layers
        for conv in self.convs:
            x = conv(x, edge_index)
            x = F.relu(x)
            x = F.dropout(x, p=self.dropout, training=self.training)
        
        # Global pooling
        x = global_mean_pool(x, data.batch)
        
        return x
    
    def encode_graph(self, data: Data) -> torch.Tensor:
        """
        Encode a graph into a fixed-size representation.
        
        Args:
            data: PyTorch Geometric Data object
            
        Returns:
            Graph embedding
        """
        return self.forward(data)
    
    def compute_similarity(self, graph1_embedding: torch.Tensor, 
                          graph2_embedding: torch.Tensor) -> torch.Tensor:
        """
        Compute similarity between two graph embeddings.
        
        Args:
            graph1_embedding: Embedding of first graph
            graph2_embedding: Embedding of second graph
            
        Returns:
            Similarity score between 0 and 1
        """
        # Concatenate embeddings
        combined = torch.cat([graph1_embedding, graph2_embedding], dim=1)
        
        # Compute similarity
        similarity = self.similarity_projection(combined)
        
        return similarity
    
    def predict_similarity(self, graph1: nx.Graph, graph2: nx.Graph) -> float:
        """
        Predict similarity between two NetworkX graphs.
        
        Args:
            graph1: First graph
            graph2: Second graph
            
        Returns:
            Similarity score between 0 and 1
        """
        # Convert graphs to PyTorch Geometric format
        data1 = self._graph_to_data(graph1)
        data2 = self._graph_to_data(graph2)
        
        # Get embeddings
        with torch.no_grad():
            embedding1 = self.encode_graph(data1)
            embedding2 = self.encode_graph(data2)
            
            # Compute similarity
            similarity = self.compute_similarity(embedding1, embedding2)
        
        return similarity.item()
    
    def _graph_to_data(self, graph: nx.Graph) -> Data:
        """
        Convert NetworkX graph to PyTorch Geometric Data object.
        
        Args:
            graph: NetworkX graph
            
        Returns:
            PyTorch Geometric Data object
        """
        # Create node features
        node_features = []
        node_mapping = {}
        
        for i, (node, data) in enumerate(graph.nodes(data=True)):
            node_mapping[node] = i
            
            # Create feature vector
            features = self._extract_node_features(data)
            node_features.append(features)
        
        # Create edge index
        edge_index = []
        for u, v in graph.edges():
            if u in node_mapping and v in node_mapping:
                edge_index.append([node_mapping[u], node_mapping[v]])
                edge_index.append([node_mapping[v], node_mapping[u]])  # Undirected
        
        if not edge_index:
            # Add self-loops if no edges
            for i in range(len(node_features)):
                edge_index.append([i, i])
        
        # Convert to tensors
        x = torch.tensor(node_features, dtype=torch.float)
        edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
        
        return Data(x=x, edge_index=edge_index)
    
    def _extract_node_features(self, node_data: Dict[str, Any]) -> List[float]:
        """
        Extract numerical features from node data.
        
        Args:
            node_data: Node attributes
            
        Returns:
            List of numerical features
        """
        features = []
        
        # Node type one-hot encoding
        node_types = ['function', 'class', 'control', 'assignment', 'call', 
                     'variable', 'literal', 'operator', 'import', 'return', 'node']
        node_type = node_data.get('type', 'node')
        for nt in node_types:
            features.append(1.0 if node_type == nt else 0.0)
        
        # Text features
        text = node_data.get('text', '')
        features.append(len(text))  # Text length
        features.append(len(text.split()))  # Word count
        
        # Line information
        features.append(node_data.get('line_start', 0))
        features.append(node_data.get('line_end', 0))
        
        # Language features
        languages = ['python', 'javascript', 'typescript', 'java', 'c', 'cpp', 'go', 'rust']
        language = node_data.get('language', 'python')
        for lang in languages:
            features.append(1.0 if language == lang else 0.0)
        
        # Boolean features
        features.append(1.0 if node_data.get('has_children', False) else 0.0)
        features.append(1.0 if node_data.get('is_leaf', False) else 0.0)
        
        # Language-specific features
        if language == 'python':
            features.append(1.0 if node_data.get('is_function', False) else 0.0)
            features.append(1.0 if node_data.get('is_class', False) else 0.0)
            features.append(1.0 if node_data.get('is_control_flow', False) else 0.0)
            features.append(1.0 if node_data.get('is_function_call', False) else 0.0)
            features.append(1.0 if node_data.get('is_assignment', False) else 0.0)
        else:
            # Default values for other languages
            features.extend([0.0, 0.0, 0.0, 0.0, 0.0])
        
        # Pad to fixed size
        target_size = 64
        while len(features) < target_size:
            features.append(0.0)
        
        return features[:target_size]


class SimpleGNNModel:
    """Simple GNN model that doesn't require PyTorch for basic similarity."""
    
    def __init__(self):
        """Initialize simple GNN model."""
        pass
    
    def compute_graph_similarity(self, graph1: nx.Graph, graph2: nx.Graph) -> float:
        """
        Compute similarity between two graphs using graph metrics.
        
        Args:
            graph1: First graph
            graph2: Second graph
            
        Returns:
            Similarity score between 0 and 1
        """
        if graph1.number_of_nodes() == 0 or graph2.number_of_nodes() == 0:
            return 0.0
        
        # Extract graph features
        features1 = self._extract_graph_features(graph1)
        features2 = self._extract_graph_features(graph2)
        
        # Compute similarity based on features
        similarity = self._compute_feature_similarity(features1, features2)
        
        return similarity
    
    def _extract_graph_features(self, graph: nx.Graph) -> Dict[str, float]:
        """Extract features from graph."""
        features = {
            'num_nodes': graph.number_of_nodes(),
            'num_edges': graph.number_of_edges(),
            'avg_degree': sum(dict(graph.degree()).values()) / graph.number_of_nodes(),
            'density': nx.density(graph),
            'avg_clustering': nx.average_clustering(graph) if graph.number_of_nodes() > 1 else 0.0
        }
        
        # Add node type distribution
        node_types = {}
        for node, data in graph.nodes(data=True):
            node_type = data.get('type', 'unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        # Normalize node type counts
        total_nodes = graph.number_of_nodes()
        for node_type in ['function', 'class', 'control', 'assignment', 'call', 'variable']:
            features[f'pct_{node_type}'] = node_types.get(node_type, 0) / total_nodes
        
        return features
    
    def _compute_feature_similarity(self, features1: Dict[str, float], 
                                  features2: Dict[str, float]) -> float:
        """Compute similarity between feature vectors."""
        # Normalize features
        max_values = {}
        for key in features1.keys():
            max_values[key] = max(features1[key], features2[key])
        
        # Compute normalized differences
        total_diff = 0.0
        for key in features1.keys():
            if max_values[key] > 0:
                diff = abs(features1[key] - features2[key]) / max_values[key]
                total_diff += diff
        
        # Convert to similarity (1 - average difference)
        avg_diff = total_diff / len(features1)
        similarity = 1.0 - avg_diff
        
        return max(0.0, min(1.0, similarity)) 