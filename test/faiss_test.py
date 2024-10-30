import os
import ast
import faiss
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity

class FaissEmbedder:
    def __init__(self, model_name='microsoft/codebert-base', embedding_dim=768):
        # Load the tokenizer and model for embeddings
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.function_embeddings = []  # To store embedding vectors
        self.function_names = []  # To store function names for easy reference
    
    def ingest_project(self, directory):
        """Recursively walk through directory to find Python files and extract function embeddings."""
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.extract_functions_and_embed(file_path)

    def extract_functions_and_embed(self, file_path):
        """Extract function definitions from Python file and add embeddings to FAISS index."""
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()
            try:
                parsed = ast.parse(code)
                for node in ast.walk(parsed):
                    if isinstance(node, ast.FunctionDef):
                        function_name = node.name
                        function_code = ast.unparse(node)
                        embedding = self.calculate_embedding(function_code)
                        self.add_to_index(embedding, function_name)
            except Exception as e:
                print(f"Error parsing file {file_path}: {e}")

    def calculate_embedding(self, code_snippet):
        """Generate a CodeBERT embedding for a given code snippet."""
        inputs = self.tokenizer(code_snippet, return_tensors='pt', truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy().astype('float32')
    
    def add_to_index(self, embedding, function_name):
        """Add a function's embedding to the FAISS index."""
        self.index.add(np.array([embedding]))
        self.function_embeddings.append(embedding)
        self.function_names.append(function_name)
    
    def compare_function_similarity(self, function_code, top_k=5):
        """Compare the new function embedding against all stored embeddings and return similar functions with scores."""
        new_embedding = self.calculate_embedding(function_code)
        distances, indices = self.index.search(np.array([new_embedding]), top_k)
        similarity_scores = [(self.function_names[idx], 100 - (dist * 100)) for dist, idx in zip(distances[0], indices[0])]
        return similarity_scores

# Example Usage
faiss_embedder = FaissEmbedder()
faiss_embedder.ingest_project('/path/to/your/python/project')

# Compare a new function to existing ones
new_function_code = """
def example_function(x):
    return x * 2
"""

similar_functions = faiss_embedder.compare_function_similarity(new_function_code)
for func_name, score in similar_functions:
    print(f"Function: {func_name}, Similarity Score: {score:.2f}")
