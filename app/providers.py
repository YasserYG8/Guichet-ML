from app.config import HF_TOKEN, MODEL_ID
from app.schemas import Prediction


class MockProvider:
    name = "mock"

    def detect_language(self, text: str) -> list[Prediction]:
        # Ceci n'est PAS un modele : ce sont des regles simples,
        # qui produisent le meme type de reponse qu'un vrai modele.
        if any("\u0600" <= c <= "\u06ff" for c in text):
            return [Prediction(label="ar", score=0.97)]
        mots_fr = {"je", "mon", "ma", "compte", "bonjour", "pas", "plus"}
        if set(text.lower().replace(".", "").split()) & mots_fr:
            return [
                Prediction(label="fr", score=0.95),
                Prediction(label="it", score=0.03),
            ]
        return [
            Prediction(label="en", score=0.93),
            Prediction(label="de", score=0.04),
        ]


class HfProvider:
    name = "huggingface"

    def __init__(self):
        from huggingface_hub import InferenceClient

        if not HF_TOKEN:
            raise RuntimeError("HF_TOKEN absent")
        self.client = InferenceClient(provider="hf-inference", api_key=HF_TOKEN)

    def detect_language(self, text: str) -> list[Prediction]:
        brut = self.client.text_classification(text, model=MODEL_ID, top_k=3)
        return [Prediction(label=i.label, score=i.score) for i in brut]


def get_provider(mode: str):
    if mode == "real":
        try:
            return HfProvider()
        except Exception:
            return MockProvider()  # repli automatique
    return MockProvider()