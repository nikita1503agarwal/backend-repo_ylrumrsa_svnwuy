"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List


class Perfume(BaseModel):
    """
    Elanor luxury perfume collection
    Collection name: "perfume" (lowercase of class name)
    """
    slug: str = Field(..., description="URL-friendly identifier, e.g., 'wrath'")
    name: str = Field(..., description="Display name of the fragrance")
    sin: str = Field(..., description="One of the seven deadly sins")
    color: str = Field(..., description="Hex/RGB/Tailwind color keyword for theming")
    price: float = Field(..., ge=0, description="Price in USD")
    short: str = Field(..., description="Short two-line essence description")
    story_nature: str = Field(..., description="I. The Nature of [Sin]")
    story_interpretation: str = Field(..., description="II. The Scent Interpretation")
    story_who: str = Field(..., description="III. Who Wears [Sin]")
    story_ritual: str = Field(..., description="IV. The Ritual")
    notes_top: List[str] = Field(default_factory=list, description="Top notes")
    notes_heart: List[str] = Field(default_factory=list, description="Heart notes")
    notes_base: List[str] = Field(default_factory=list, description="Base notes")
    bottle_image: Optional[HttpUrl] = Field(None, description="Primary bottle image URL")
    symbol: Optional[str] = Field(None, description="Symbol description or emoji placeholder")


# Example schemas kept for reference
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True


class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
