from enum import Enum


class NestedPropertyTokenization(str, Enum):
    FIELD = "field"
    GSE = "gse"
    GSE_CH = "gse_ch"
    KAGOME_JA = "kagome_ja"
    KAGOME_KR = "kagome_kr"
    LOWERCASE = "lowercase"
    TRIGRAM = "trigram"
    WHITESPACE = "whitespace"
    WORD = "word"

    def __str__(self) -> str:
        return str(self.value)
