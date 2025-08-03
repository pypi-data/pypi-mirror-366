"""
Subcommand to create a new receipt YAML file and import it.
"""

from datetime import datetime, date, time, timedelta
import os
from pathlib import Path
import sys
from typing import Optional, Sequence, TextIO, TypeVar, Union, TYPE_CHECKING
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import min as min_, max as max_
from .input import InputSource, Prompt
from .step import Menu, ProductsMeta, ResultMeta, ReturnToMenu, Step, \
    Read, Products, Discounts, ProductMeta, View, Write, Edit, Quit, Help
from ..base import Base
from ...database import Database
from ...io.products import OPTIONAL_FIELDS
from ...matcher.product import ProductMatcher
from ...models.product import Product
from ...models.receipt import Discount, ProductItem, Receipt
from ...models.shop import Shop

@Base.register("new")
class New(Base):
    """
    Create a YAML file for a receipt and import it to the database.
    """

    subparser_keywords = {
        'help': 'Create receipt file and import',
        'description': 'Interactively fill in a YAML file for a receipt and '
                       'import it to the database.'
    }
    subparser_arguments = [
        (('-c', '--confirm'), {
            'action': 'store_true',
            'default': False,
            'help': 'Confirm before updating database files or exiting'
        })
    ]

    def __init__(self) -> None:
        super().__init__()
        self.confirm = False

    def _get_menu_step(self, menu: Menu, input_source: InputSource) -> Step:
        choice: Optional[str] = None
        while choice not in menu:
            choice = input_source.get_input('Menu (help or ? for usage)', str,
                                            options='menu')
            if choice != '' and choice not in menu:
                # Autocomplete
                choice = input_source.get_completion(choice, 0)

        return menu[choice]

    def _show_menu_step(self, menu: Menu, step: Step,
                        reason: ReturnToMenu) -> Step:
        if reason.msg:
            self.logger.warning('%s', reason.msg)
        if step.final:
            step = menu['view']
            step.run()
        return step

    def _confirm_final(self, step: Step, input_source: InputSource) -> None:
        if self.confirm and step.final:
            prompt = f'Confirm that you want to {step.description.lower()} (y)'
            if input_source.get_input(prompt, str) != 'y':
                raise ReturnToMenu('Confirmation canceled')

    def _get_path(self, receipt_date: datetime, shop: str) -> Path:
        data_path = Path(self.settings.get('data', 'path'))
        data_format = self.settings.get('data', 'format')
        filename = data_format.format(date=receipt_date, shop=shop)
        return Path(data_path) / filename

    def _load_date_suggestions(self, session: Session,
                               input_source: InputSource) -> None:
        indicators = [ProductMatcher.IND_MINIMUM, ProductMatcher.IND_MAXIMUM]
        dates = session.execute(select(min_(Receipt.date).label("min"),
                                       max_(Receipt.date).label("max"))).first()
        if dates is None or dates.min is None:
            input_source.update_suggestions({'indicators': indicators})
            return

        today = date.today()
        years = range(dates.min.year, today.year + 1)
        input_source.update_suggestions({
            'days': [
                str(dates.max + timedelta(days=day))
                for day in range(max(0, (today - dates.max).days) + 1)
            ],
            'indicators': [str(year) for year in years] + indicators
        })

    def _load_suggestions(self, session: Session,
                          input_source: InputSource) -> None:
        self._load_date_suggestions(session, input_source)
        input_source.update_suggestions({
            'shops': list(session.scalars(select(Shop.key)
                                          .order_by(Shop.key))),
            'products': list(session.scalars(select(ProductItem.label)
                                             .distinct()
                                             .order_by(ProductItem.label))),
            'discounts': list(session.scalars(select(Discount.label)
                                              .distinct()
                                              .order_by(Discount.label))),
            'meta': ['label', 'price', 'discount'] + list(OPTIONAL_FIELDS) + [
                'range', 'view'
            ]
        })

    def run(self) -> None:
        input_source: InputSource = Prompt()
        matcher = ProductMatcher()
        matcher.discounts = False

        with Database() as session:
            self._load_suggestions(session, input_source)

        receipt_date = input_source.get_date(datetime.combine(date.today(),
                                                              time.min))
        shop = input_source.get_input('Shop', str, options='shops')
        path = self._get_path(receipt_date, shop)
        receipt = Receipt(filename=path.name, updated=datetime.now(),
                          date=receipt_date.date(), shop=shop)
        products: ProductsMeta = set()
        write = Write(receipt, input_source, matcher=matcher, products=products)
        write.path = path
        usage = Help(receipt, input_source)
        menu: Menu = {
            'read': Read(receipt, input_source, matcher=matcher),
            'products': Products(receipt, input_source, matcher=matcher,
                                 products=products),
            'discounts': Discounts(receipt, input_source, matcher=matcher),
            'meta': ProductMeta(receipt, input_source, matcher=matcher,
                                products=products),
            'view': View(receipt, input_source, products=products),
            'write': write,
            'edit': Edit(receipt, input_source,
                         editor=self.settings.get('data', 'editor')),
            'quit': Quit(receipt, input_source),
            'help': usage,
            '?': usage
        }
        usage.menu = menu
        step = self._run_sequential(menu, input_source)
        if step.final:
            return

        # Sequential run did not lead to a final step, so ask for menu choice
        input_source.update_suggestions({'menu': list(menu.keys())})
        while not step.final:
            step = self._get_menu_step(menu, input_source)
            try:
                self._confirm_final(step, input_source)
                result = step.run()
                # Edit might change receipt metadata
                if result.get('receipt_path', False):
                    if receipt.date != receipt_date.date():
                        receipt_date = datetime.combine(receipt.date, time.min)
                    write.path = self._get_path(receipt_date, receipt.shop)
                    receipt.filename = write.path.name
            except ReturnToMenu as reason:
                step = self._show_menu_step(menu, step, reason)

    def _run_sequential(self, menu: Menu, input_source: InputSource) -> Step:
        if not menu: # pragma: no cover
            raise ValueError('Menu must have defined steps')
        step: Step
        for step in menu.values(): # pragma: no branch
            try:
                self._confirm_final(step, input_source)
                step.run()
                if step.final:
                    return step
            except ReturnToMenu as reason:
                step = self._show_menu_step(menu, step, reason)
                break

        return step
