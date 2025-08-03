
from pydantic import BaseModel

class MetaReactionContent(BaseModel):
    emoji: str
    message_id: str

    @property
    def emoji(self) -> str:
        return self.emoji

    @property
    def message_id(self) -> str:
        return self.message_id