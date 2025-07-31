from name4py import Gender
from deeplotx.nn import BaseNeuralNetwork

from name2gender.model import load_model, SMALL_MODEL, ENCODER


class Name2Gender:
    def __init__(self, model: BaseNeuralNetwork | None = None):
        super().__init__()
        if model is None:
            model = load_model(SMALL_MODEL)
        self._model = model

    def __call__(self, name: str, return_probability: bool = False, threshold: float = .5) -> tuple[Gender, float] | Gender:
        name = f'{name[0].upper()}{name[1:]}'
        emb = ENCODER.encode(name)
        prob = self._model.predict(emb).item()
        gender = Gender.Male if prob >= threshold else Gender.Female
        if return_probability:
            return gender, prob if gender == Gender.Male else (1. - prob)
        return gender
