from enum import Enum


class PropertyTokenization(str, Enum):
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
