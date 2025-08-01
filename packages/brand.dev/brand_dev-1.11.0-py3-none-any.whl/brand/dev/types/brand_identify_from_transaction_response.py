# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = [
    "BrandIdentifyFromTransactionResponse",
    "Brand",
    "BrandAddress",
    "BrandBackdrop",
    "BrandBackdropColor",
    "BrandBackdropResolution",
    "BrandColor",
    "BrandLogo",
    "BrandLogoColor",
    "BrandLogoResolution",
    "BrandSocial",
    "BrandStock",
]


class BrandAddress(BaseModel):
    city: Optional[str] = None
    """City name"""

    country: Optional[str] = None
    """Country name"""

    country_code: Optional[str] = None
    """Country code"""

    postal_code: Optional[str] = None
    """Postal or ZIP code"""

    state_code: Optional[str] = None
    """State or province code"""

    state_province: Optional[str] = None
    """State or province name"""

    street: Optional[str] = None
    """Street address"""


class BrandBackdropColor(BaseModel):
    hex: Optional[str] = None
    """Color in hexadecimal format"""

    name: Optional[str] = None
    """Name of the color"""


class BrandBackdropResolution(BaseModel):
    aspect_ratio: Optional[float] = None
    """Aspect ratio of the image (width/height)"""

    height: Optional[int] = None
    """Height of the image in pixels"""

    width: Optional[int] = None
    """Width of the image in pixels"""


class BrandBackdrop(BaseModel):
    colors: Optional[List[BrandBackdropColor]] = None
    """Array of colors in the backdrop image"""

    resolution: Optional[BrandBackdropResolution] = None
    """Resolution of the backdrop image"""

    url: Optional[str] = None
    """URL of the backdrop image"""


class BrandColor(BaseModel):
    hex: Optional[str] = None
    """Color in hexadecimal format"""

    name: Optional[str] = None
    """Name of the color"""


class BrandLogoColor(BaseModel):
    hex: Optional[str] = None
    """Color in hexadecimal format"""

    name: Optional[str] = None
    """Name of the color"""


class BrandLogoResolution(BaseModel):
    aspect_ratio: Optional[float] = None
    """Aspect ratio of the image (width/height)"""

    height: Optional[int] = None
    """Height of the image in pixels"""

    width: Optional[int] = None
    """Width of the image in pixels"""


class BrandLogo(BaseModel):
    colors: Optional[List[BrandLogoColor]] = None
    """Array of colors in the logo"""

    mode: Optional[Literal["light", "dark", "has_opaque_background"]] = None
    """
    Indicates when this logo is best used: 'light' = best for light mode, 'dark' =
    best for dark mode, 'has_opaque_background' = can be used for either as image
    has its own background
    """

    resolution: Optional[BrandLogoResolution] = None
    """Resolution of the logo image"""

    type: Optional[Literal["icon", "logo"]] = None
    """Type of the logo based on resolution (e.g., 'icon', 'logo')"""

    url: Optional[str] = None
    """CDN hosted url of the logo (ready for display)"""


class BrandSocial(BaseModel):
    type: Optional[str] = None
    """Type of social media, e.g., 'facebook', 'twitter'"""

    url: Optional[str] = None
    """URL of the social media page"""


class BrandStock(BaseModel):
    exchange: Optional[str] = None
    """Stock exchange name"""

    ticker: Optional[str] = None
    """Stock ticker symbol"""


class Brand(BaseModel):
    address: Optional[BrandAddress] = None
    """Physical address of the brand"""

    backdrops: Optional[List[BrandBackdrop]] = None
    """An array of backdrop images for the brand"""

    colors: Optional[List[BrandColor]] = None
    """An array of brand colors"""

    description: Optional[str] = None
    """A brief description of the brand"""

    domain: Optional[str] = None
    """The domain name of the brand"""

    email: Optional[str] = None
    """Company email address"""

    is_nsfw: Optional[bool] = None
    """Indicates whether the brand content is not safe for work (NSFW)"""

    logos: Optional[List[BrandLogo]] = None
    """An array of logos associated with the brand"""

    phone: Optional[str] = None
    """Company phone number"""

    slogan: Optional[str] = None
    """The brand's slogan"""

    socials: Optional[List[BrandSocial]] = None
    """An array of social media links for the brand"""

    stock: Optional[BrandStock] = None
    """
    Stock market information for this brand (will be null if not a publicly traded
    company)
    """

    title: Optional[str] = None
    """The title or name of the brand"""


class BrandIdentifyFromTransactionResponse(BaseModel):
    brand: Optional[Brand] = None
    """Detailed brand information"""

    code: Optional[int] = None
    """HTTP status code"""

    status: Optional[str] = None
    """Status of the response, e.g., 'ok'"""
