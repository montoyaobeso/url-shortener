from pydantic import BaseModel


class URLBase(BaseModel):
    url: str


class URL(URLBase):
    code: str
    clicks: int
    is_active: int = 1


class URLInfo(URL):
    short_url: str
