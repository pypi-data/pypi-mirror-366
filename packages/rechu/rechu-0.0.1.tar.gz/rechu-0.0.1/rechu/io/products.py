"""
Products matching metadata file handling.
"""

from datetime import datetime
from pathlib import Path
from typing import get_args, Collection, Iterable, Iterator, IO, Literal, \
    Optional, TypeVar, Union
from typing_extensions import TypedDict
from .base import YAMLReader, YAMLWriter
from ..models.base import GTIN, Price, Quantity
from ..models.product import Product, LabelMatch, PriceMatch, DiscountMatch

class _Product(TypedDict, total=False):
    """
    Serialized product metadata.
    """

    shop: str
    labels: list[str]
    prices: Union[list[Price], dict[str, Price]]
    bonuses: list[str]
    brand: Optional[str]
    description: Optional[str]
    category: Optional[str]
    type: Optional[str]
    portions: Optional[int]
    weight: Optional[Quantity]
    volume: Optional[Quantity]
    alcohol: Optional[str]
    sku: str
    gtin: int

class _GenericProduct(_Product, total=False):
    range: list["_Product"]

class _InventoryGroup(TypedDict, total=False):
    shop: str
    brand: str
    category: str
    type: str
    products: list[_GenericProduct]

PrimaryField = Literal["shop"]
OptionalShareableField = Literal["brand", "category", "type"]
ShareableField = Literal[PrimaryField, OptionalShareableField]
SharedFields = Iterable[ShareableField]
PropertyField = Literal[
    OptionalShareableField,
    "description", "portions", "weight", "volume", "alcohol"
]
IdentifierField = Literal["sku", "gtin"]
Field = Literal[PrimaryField, PropertyField, IdentifierField]
OptionalField = Literal[PropertyField, IdentifierField]
_Input = Union[str, int, Quantity]
_FieldT = TypeVar("_FieldT", bound=_Input)
SHARED_FIELDS: tuple[ShareableField, ...] = get_args(ShareableField)
PROPERTY_FIELDS: tuple[PropertyField, ...] = get_args(PropertyField)
IDENTIFIER_FIELDS: tuple[IdentifierField, ...] = get_args(IdentifierField)
OPTIONAL_FIELDS: tuple[OptionalField, ...] = get_args(OptionalField)

class ProductsReader(YAMLReader[Product]):
    """
    File reader for products metadata.
    """

    def parse(self, file: IO) -> Iterator[Product]:
        data: _InventoryGroup = self.load(file)
        if not isinstance(data, dict):
            raise TypeError(f"File '{self._path}' does not contain a mapping")
        if not isinstance(data.get('products'), list):
            raise TypeError(f"File '{self._path}' is missing 'products' list")

        for meta in data['products']:
            product = self._product(data, {}, meta)
            product.range = [
                self._product(data, meta, sub_meta)
                for sub_meta in meta.get('range', [])
            ]
            yield product

    @staticmethod
    def _get(input_type: type[_FieldT],
             value: Optional[_Input]) -> Optional[_FieldT]:
        if value is not None:
            value = input_type(value)
            if not isinstance(value, input_type): # pragma: no cover
                value = None

        return value

    def _product(self, data: _InventoryGroup, generic: _GenericProduct,
                 meta: _Product) -> Product:
        if not isinstance(meta, dict):
            raise TypeError(f"Product is not a mapping: {meta!r}")
        product = Product(shop=data.get('shop', generic.get('shop')),
                          brand=meta.get('brand', generic.get('brand')),
                          description=meta.get('description',
                                               generic.get('description')),
                          category=meta.get('category',
                                            generic.get('category',
                                                        data.get('category'))),
                          type=meta.get('type', generic.get('type',
                                                            data.get('type'))),
                          portions=self._get(int,
                                             meta.get('portions',
                                                      generic.get('portions'))),
                          weight=self._get(Quantity,
                                           meta.get('weight',
                                                    generic.get('weight'))),
                          volume=self._get(Quantity,
                                           meta.get('volume',
                                                    generic.get('volume'))),
                          alcohol=meta.get('alcohol', generic.get('alcohol')),
                          sku=meta.get('sku'),
                          gtin=GTIN(meta['gtin']) if 'gtin' in meta else None)

        product.labels = [
            LabelMatch(name=name)
            for name in meta.get('labels', generic.get('labels', []))
        ]
        prices = meta.get('prices', generic.get('prices', []))
        if isinstance(prices, list):
            product.prices = [
                PriceMatch(value=Price(price)) for price in prices
            ]
        else:
            product.prices = [
                PriceMatch(value=Price(price), indicator=key)
                for key, price in prices.items()
            ]
        product.discounts = [
            DiscountMatch(label=label)
            for label in meta.get('bonuses', generic.get('bonuses', []))
        ]

        return product

class ProductsWriter(YAMLWriter[Product]):
    """
    File writer for products metadata.
    """

    def __init__(self, path: Path, models: Collection[Product],
                 updated: Optional[datetime] = None,
                 shared_fields: SharedFields = ('shop', 'category', 'type')):
        super().__init__(path, models, updated=updated)
        self._shared_fields = set(shared_fields)

    @staticmethod
    def _get_prices(product: Product) -> Union[list[Price], dict[str, Price]]:
        prices: list[Price] = []
        indicator_prices: dict[str, Price] = {}

        for price in product.prices:
            if price.indicator is not None:
                indicator_prices[price.indicator] = price.value
            else:
                prices.append(price.value)

        if indicator_prices:
            if prices:
                raise ValueError('Not all price matchers have indicators')
            return indicator_prices

        return prices

    def _get_product(self, product: Product, skip_fields: set[Field],
                     generic: _GenericProduct) \
            -> Union[_Product, _GenericProduct]:
        data: Union[_Product, _GenericProduct] = {}
        if 'shop' not in skip_fields:
            data['shop'] = product.shop

        labels = [label.name for label in product.labels]
        if labels != generic.get('labels', []):
            data['labels'] = labels

        prices = self._get_prices(product)
        if prices != generic.get('prices', []):
            data['prices'] = prices

        discounts = [discount.label for discount in product.discounts]
        if discounts != generic.get('bonuses', []):
            data['bonuses'] = discounts

        for field in PROPERTY_FIELDS:
            if field not in skip_fields:
                value = getattr(product, field, None)
                if value != generic.get(field):
                    data[field] = value
        for id_field in IDENTIFIER_FIELDS:
            identifier = getattr(product, id_field, None)
            if identifier is not None:
                data[id_field] = identifier

        return data

    def _get_generic_product(self, product: Product, skip_fields: set[Field]) \
            -> _GenericProduct:
        data: _GenericProduct = {**self._get_product(product, skip_fields, {})}

        if product.range:
            data['range'] = [
                self._get_product(sub_product, skip_fields | {'shop'}, data)
                for sub_product in product.range
            ]

        return data

    def serialize(self, file: IO) -> None:
        group: _InventoryGroup = {}
        skip_fields: set[Field] = set()
        for shared in self._shared_fields:
            values = {getattr(product, shared) for product in self._models}
            try:
                common = values.pop()
            except KeyError:
                common = None
            if not values and common is not None:
                group[shared] = str(common)
                skip_fields.add(shared)
            elif shared == 'shop':
                raise ValueError('Not all products are from the same shop')

        group['products'] = [
            self._get_generic_product(product, skip_fields)
            for product in self._models
        ]
        self.save(group, file)
