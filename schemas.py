from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional

class Design(BaseModel):
    """
    Designs collection schema
    Collection name: "design"
    """
    title: str = Field(..., description="Design name")
    description: Optional[str] = Field(None, description="Short description")
    image_url: HttpUrl = Field(..., description="Preview mockup image URL")
    marketplace_url: Optional[HttpUrl] = Field(None, description="Link to Merch by Amazon listing or store")
    tags: List[str] = Field(default_factory=list, description="Keywords/tags")
    colors: List[str] = Field(default_factory=list, description="Available shirt colors")
    price: Optional[float] = Field(None, ge=0)


class ContactMessage(BaseModel):
    """
    Contact messages collection schema
    Collection name: "contactmessage"
    """
    name: str
    email: str
    message: str
