from enum import StrEnum


class Provider(StrEnum):
    OPENAI = "openai"
    AZURE = "aoai"
    OASIS = "oasis"


class ClientType(StrEnum):
    SDK = "sdk"
    LANGCHAIN = "langchain"
    API = "api"