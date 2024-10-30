import torch
from transformers import BertTokenizer, BertModel, TFBertModel
import tensorflow as tf
import inspect
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def get_function_code(func):
    """Extract source code from the function."""
    return inspect.getsource(func)

def get_embeddings_pytorch(text):
    """Generate embeddings using BERT model in PyTorch."""
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).numpy()

def get_embeddings_tensorflow(text):
    """Generate embeddings using BERT model in TensorFlow."""
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = TFBertModel.from_pretrained('bert-base-uncased')
    inputs = tokenizer(text, return_tensors='tf', padding=True, truncation=True)
    outputs = model(**inputs)
    return tf.reduce_mean(outputs.last_hidden_state, axis=1).numpy()

def calculate_similarity(embedding1, embedding2):
    """Calculate cosine similarity between two embeddings."""
    return cosine_similarity(embedding1, embedding2)[0][0]

def are_functions_similar(func1, func2, threshold=0.95):
    """Determine if two functions are similar based on cosine similarity."""
    # Extract code
    code1 = get_function_code(func1)
    code2 = get_function_code(func2)
    
    # Get embeddings
    emb_pytorch_1 = get_embeddings_pytorch(code1)
    emb_pytorch_2 = get_embeddings_pytorch(code2)
    emb_tensorflow_1 = get_embeddings_tensorflow(code1)
    emb_tensorflow_2 = get_embeddings_tensorflow(code2)
    
    # Calculate similarities
    similarity_pytorch = calculate_similarity(emb_pytorch_1, emb_pytorch_2)
    similarity_tensorflow = calculate_similarity(emb_tensorflow_1, emb_tensorflow_2)
    
    print(f"Similarity (PyTorch): {similarity_pytorch}")
    print(f"Similarity (TensorFlow): {similarity_tensorflow}")
    
    return similarity_pytorch >= threshold and similarity_tensorflow >= threshold


def example_func1(host, database, user, password, port=5432):
    """
    Connect to PostgreSQL using psycopg2.

    Args:
        host (str): Database host address.
        database (str): Database name.
        user (str): Username.
        password (str): Password.
        port (int, optional): Port number. Defaults to 5432.

    Returns:
        connection: psycopg2 connection object or None if connection fails.
    """
    try:
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )
        print("Connected to PostgreSQL database with psycopg2.")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return None

def example_func2(host, database, user, password, port=5432):
    """
    Connect to PostgreSQL using pg8000.

    Args:
        host (str): Database host address.
        database (str): Database name.
        user (str): Username.
        password (str): Password.
        port (int, optional): Port number. Defaults to 5432.

    Returns:
        connection: pg8000 connection object or None if connection fails.
    """
    try:
        conn = pg8000.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )
        print("Connected to PostgreSQL database with pg8000.")
        return conn
    except pg8000.dbapi.InterfaceError as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return None

# Determine similarity
is_similar = are_functions_similar(example_func1, example_func2)
print("Are the functions similar?", is_similar)
