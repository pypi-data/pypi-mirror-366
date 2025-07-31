from pydantic import BaseModel


class Config(BaseModel):
    mountpoint: str