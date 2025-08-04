from pydantic import BaseModel, Field


class GundemResponse(BaseModel):
    title: str = Field(..., description="The title of the topic.")
    url: str = Field(..., description="The URL of the topic.")
    count: str = Field(..., description="The number of entries for the topic.")


class TopicBaseResponse(BaseModel):
    topic: str = Field(..., description="The topic of the entry.")
    content: str = Field(..., description="The content of the entry.")
    author: str = Field(..., description="The author of the entry.")
    date: str = Field(...,
                      description="The date of the entry in 'DD.MM.YYYY HH:MM' format.")


class DebeResponse(BaseModel):
    title: str = Field(..., description="The title of the debe entry.")
    url: str = Field(..., description="The URL of the debe entry.")
