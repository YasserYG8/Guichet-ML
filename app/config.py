import os
from dotenv import load_dotenv
load_dotenv()
MODE = os.getenv("INFERENCE_MODE", "mock").lower()
HF_TOKEN = os.getenv("HF_TOKEN", "")
MODEL_ID = os.getenv("MODEL_ID", "papluca/xlm-roberta-base-language-detection")
REVIEW_THRESHOLD = float(os.getenv("REVIEW_THRESHOLD", "0.60"))
