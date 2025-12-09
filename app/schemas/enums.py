from enum import Enum


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"


class TagNames(str, Enum):
    FRAGILE = "fragile"
    PERISHABLE = "perishable"
    HEAVY = "heavy"
    GIFT = "gifts   "
    electronics = "electronics"
    DOCUMENTS = "documents"
    RETURN = "return"
    EXPRESS = "express"
    INTERNATIONAL = "international"
    TEMPERATURE_CONTROLLED = "temperature_controlled"
    STANDARD = "standard"
