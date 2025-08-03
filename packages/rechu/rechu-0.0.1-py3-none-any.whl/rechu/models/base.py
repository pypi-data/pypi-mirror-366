"""
Base model for receipt cataloging.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, registry
from ..types.measurable import Quantity, Unit, QuantityType, UnitType
from ..types.quantized import GTIN, Price, GTINType, PriceType


class Base(DeclarativeBase): # pylint: disable=too-few-public-methods
    """
    Base ORM model class for receipt models.
    """

    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })

    registry = registry(type_annotation_map={
        Price: PriceType,
        Quantity: QuantityType,
        Unit: UnitType,
        GTIN: GTINType
    })
