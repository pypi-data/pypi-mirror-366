import os

__ROOT__ = os.path.dirname(os.path.abspath(__file__))
__CACHE_DIR__ = os.path.join(__ROOT__, '.cache')

from .model import download_model, load_model, SMALL_MODEL, BASE_MODEL
from .__main__ import Gender, Name2Gender
