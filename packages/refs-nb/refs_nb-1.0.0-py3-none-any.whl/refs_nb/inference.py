import joblib
import importlib.resources

_model = None

def _initialize():
    """Load the model into memory if not already loaded."""
    global _model
    with importlib.resources.path("refs_nb", "text_classifier_pipeline_hashed.joblib") as model_path:
        _model = joblib.load(model_path)

def predict(texts):
    """
    Predict the class of each text in the input.
    
    Args:
        texts (str or list of str): Text(s) to classify.
        
    Returns:
        tuple: (preds, probs) where preds is a list of predicted classes ['main_text', 'reference'],
               and probs is a list of probability arrays [p_main_text, p_reference].
    """
    if isinstance(texts, str):
        texts = [texts]

    if _model is None:
        _initialize()

    preds = _model.predict(texts)
    probs = _model.predict_proba(texts)
    return preds, probs