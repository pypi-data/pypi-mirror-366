from typing import Optional, Dict, Any, Literal, Union
from pydantic import BaseModel, Field
from datetime import datetime
from .base import BaseToolCallModel
import json


class Brand(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    name_ru: Optional[str] = None
    name_uz: Optional[str] = None
    default_lang: Optional[str] = None


class MainCategoryParent(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    depth: Optional[int] = None
    parent: Optional[Dict[str, Any]] = None


class MainCategory(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    depth: Optional[int] = None
    parent: Optional[MainCategoryParent] = None
    exist_children: Optional[bool] = None
    product_count: Optional[int] = None
    order: Optional[int] = None
    status: Optional[int] = None
    created_at: Optional[Union[datetime, str]] = None
    updated_at: Optional[Union[datetime, str]] = None


class Merchant(BaseModel):
    id: Optional[Union[int, str]] = None
    name: Optional[str] = None
    logo: Optional[str] = None
    type: Optional[Dict[str, Any]] = None
    status: Optional[Dict[str, Any]] = None
    created_at: Optional[Union[datetime, str]] = None
    updated_at: Optional[Union[datetime, str]] = None


class Offer(BaseModel):
    id: Optional[Union[int, str]] = None
    original_price: Optional[Union[str, int, float]] = None
    price: Optional[Union[str, int, float]] = None
    three_month_price: Optional[Union[str, int, float]] = Field(
        default=None, alias="3_month_price"
    )
    six_month_price: Optional[Union[str, int, float]] = Field(
        default=None, alias="6_month_price"
    )
    nine_month_price: Optional[Union[str, int, float]] = Field(
        default=None, alias="9_month_price"
    )
    twelve_month_price: Optional[Union[str, int, float]] = Field(
        default=None, alias="12_month_price"
    )
    eighteen_month_price: Optional[Union[str, int, float]] = Field(
        default=None, alias="18_month_price"
    )
    discount: Optional[bool] = None
    discount_percent: Optional[Union[str, int, float]] = None
    discount_start_at: Optional[Union[datetime, str]] = None
    discount_expire_at: Optional[Union[datetime, str]] = None

    merchant: Optional[Merchant] = None
    status: Optional[Dict[str, Any]] = None
    market_type: Optional[str] = Literal[
        "b2c",
        "b2b",
        "B2B",
        "B2C",
        "G2B",
        "G2C",
        "C2C",
        "C2B",
        "B2G",
        "G2G",
        "G2C",
        "g2b",
        "g2c",
        "c2c",
        "c2b",
        "b2g",
        "g2g",
        "g2c",
    ]

    def filter_for_llm(self):
        return {
            "price": self.price if self.price else None,
            "merchant": self.merchant.name if self.merchant else None,
            "status": self.status if self.status else None,
            "six_month_price": self.six_month_price if self.six_month_price else None,
            "twelve_month_price": self.twelve_month_price
            if self.twelve_month_price
            else None,
        }


class Meta(BaseModel):
    current_page: Optional[int] = Field(default=1, alias="current_page")
    from_: Optional[int] = Field(default=1, alias="from")
    last_page: Optional[int] = Field(default=1, alias="last_page")
    path: Optional[str] = Field(default=None, alias="path")
    per_page: Optional[int] = Field(default=1, alias="per_page")
    to: Optional[int] = Field(default=1, alias="to")
    total: Optional[int] = Field(default=1, alias="total")


class ProductItem(BaseModel):
    id: Optional[Union[int, str]] = None
    remote_id: Optional[str] = None
    name_ru: Optional[str] = None
    name_uz: Optional[str] = None
    slug: Optional[str] = None
    brand: Optional[Brand] = None
    main_categories: Optional[list[MainCategory]] = None
    short_name_uz: Optional[str] = None
    short_name_ru: Optional[str] = None
    main_image: Optional[Dict[str, str]] = None
    created_at: Optional[Union[datetime, str]] = None
    updated_at: Optional[Union[datetime, str]] = None
    count: Optional[int] = None
    tracking: Optional[bool] = None
    offers: Optional[list[Offer]] = None
    status: Optional[Dict[str, Any]] = None
    view_count: Optional[int] = None
    order_count: Optional[int] = None
    like_count: Optional[int] = None
    rate: Optional[int] = None
    cancelled_count: Optional[int] = None

    def filter_for_llm(self):
        return {
            "name_uz": self.name_uz if self.name_uz else None,
            "name_ru": self.name_ru if self.name_ru else None,
            "offers": [x.filter_for_llm() for x in self.offers],
            "brand": self.brand.name if self.brand else None,
        }


class SearchProductsResponse(BaseToolCallModel, BaseModel):
    items: Optional[list[ProductItem]] = None
    meta: Optional[Meta] = None

    def filter_for_llm(self):
        data = [x.filter_for_llm() for x in self.items if self.items]
        return json.dumps(data, ensure_ascii=False, indent=2)
