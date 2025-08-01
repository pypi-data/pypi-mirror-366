from dataclasses import dataclass

from ..api.noun_phrase import NounPhrases
from .types import ConceptType


@dataclass
class QuestionDescriptor:
    noun_phrases: NounPhrases
    type: ConceptType
