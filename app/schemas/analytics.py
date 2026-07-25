from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class AnalyticsDailyPoint(BaseModel):
    date: date
    orders: int
    revenue: Decimal


class AnalyticsSummary(BaseModel):
    total_revenue: Decimal
    total_orders: int
    average_order_value: Decimal
    total_products: int
    total_customers: int
    pending_orders: int
    processing_orders: int
    cancelled_orders: int
    daily: list[AnalyticsDailyPoint]
