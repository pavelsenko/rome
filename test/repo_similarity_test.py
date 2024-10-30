import os
import ast
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

class FunctionSimilarityModel:
    def __init__(self, repo_paths):
        """
        Initialize the model with paths to the repositories.
        
        :param repo_paths: List of paths to the repositories.
        """
        self.repo_paths = repo_paths
        self.code_files = []
        self.functions = []
        self.function_embeddings = []
    
    def collect_code(self):
        """
        Collect code files from the repositories.
        """
        self.code_files = []
        for repo_path in self.repo_paths:
            for root, dirs, files in os.walk(repo_path):
                for file in files:
                    if file.endswith('.py'):
                        self.code_files.append(os.path.join(root, file))
    
    def extract_functions(self):
        """
        Extract functions from the code files using AST parsing.
        """
        self.functions = []
        for file_path in self.code_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                try:
                    tree = ast.parse(code)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            function_code = ast.get_source_segment(code, node)
                            self.functions.append({
                                'name': node.name,
                                'code': function_code,
                                'file': file_path
                            })
                except SyntaxError:
                    continue  # Skip files with syntax errors
    
    def generate_embeddings(self):
        """
        Generate embeddings for the extracted functions using CodeBERT.
        """
        tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        model = AutoModel.from_pretrained("microsoft/codebert-base")
        
        self.function_embeddings = []
        for func in self.functions:
            code_tokens = tokenizer.tokenize(func['code'])
            code_ids = tokenizer.convert_tokens_to_ids(code_tokens)
            tokens_tensor = torch.tensor([code_ids])
            
            with torch.no_grad():
                outputs = model(tokens_tensor)
                embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
                self.function_embeddings.append(embeddings)
    
    def find_similar_functions(self, function_code, top_n=5):
        """
        Find similar functions to the given function code.
        
        :param function_code: The code of the function to find similar functions to.
        :param top_n: The number of similar functions to return.
        :return: List of similar functions with their similarity scores.
        """
        tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        model = AutoModel.from_pretrained("microsoft/codebert-base")
        
        code_tokens = tokenizer.tokenize(function_code)
        code_ids = tokenizer.convert_tokens_to_ids(code_tokens)
        tokens_tensor = torch.tensor([code_ids])
        
        with torch.no_grad():
            outputs = model(tokens_tensor)
            query_embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        
        # Compute cosine similarities
        similarities = cosine_similarity(
            [query_embedding],
            self.function_embeddings
        )[0]
        
        # Get top_n similar functions
        similar_indices = similarities.argsort()[-top_n:][::-1]
        similar_functions = []
        for idx in similar_indices:
            similar_functions.append({
                'name': self.functions[idx]['name'],
                'code': self.functions[idx]['code'],
                'file': self.functions[idx]['file'],
                'similarity': similarities[idx]
            })
        return similar_functions
