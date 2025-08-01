from sentence_transformers import SentenceTransformer
import os

_MODEL = None

def load_model():
    """Load and return the pristine-sbert model"""
    global _MODEL
    if _MODEL is None:
        # Get absolute path to included model files
        model_path = os.path.join(os.path.dirname(__file__), "model_files")
        _MODEL = SentenceTransformer(model_path)
    return _MODEL

def calculate_similarity(job_description, resume):
    """
    Calculate similarity score between job description and resume
    
    Args:
        job_description (str): Job description text
        resume (str): Resume text
        
    Returns:
        float: Similarity score (0-1)
    """
    model = load_model()
    job_embedding = model.encode(job_description)
    resume_embedding = model.encode(resume)
    
    from sklearn.metrics.pairwise import cosine_similarity
    return cosine_similarity([job_embedding], [resume_embedding])[0][0]

def batch_similarity(job_description, resumes):
    """
    Calculate similarity scores between job description and multiple resumes
    
    Args:
        job_description (str): Job description text
        resumes (list): List of resume texts
        
    Returns:
        list: Similarity scores for each resume
    """
    model = load_model()
    job_embedding = model.encode(job_description)
    resume_embeddings = model.encode(resumes)
    
    from sklearn.metrics.pairwise import cosine_similarity
    return cosine_similarity([job_embedding], resume_embeddings)[0]