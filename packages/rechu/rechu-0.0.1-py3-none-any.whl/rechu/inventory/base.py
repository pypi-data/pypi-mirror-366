"""
Bag of files containing multiple grouped models that share common properties.
"""

from collections.abc import Iterable, Iterator, Sequence
from pathlib import Path
from typing import Mapping, Optional, TypeVar
from sqlalchemy.orm import Session
from ..io.base import Writer
from ..models.base import Base as ModelBase

T = TypeVar('T', bound=ModelBase)

Selectors = list[dict[str, Optional[str]]]

class Inventory(Mapping[Path, Sequence[T]]):
    """
    An inventory of a type of model grouped by one or more characteristics,
    which are concretized in file names.
    """

    @classmethod
    def spread(cls, models: Iterable[T]) -> "Inventory[T]":
        """
        Create an inventory based on provided models by assigning them to groups
        that each belongs to.
        """

        raise NotImplementedError('Spreading must be implemented by subclass')

    @classmethod
    def select(cls, session: Session,
               selectors: Optional[Selectors] = None) -> "Inventory[T]":
        """
        Create an inventory based on models stored in the database.
        """

        raise NotImplementedError('Selection must be implemented by subclass')

    @classmethod
    def read(cls) -> "Inventory[T]":
        """
        Create an inventory based on models stored in files.
        """

        raise NotImplementedError('Reading must be implemented by subclass')

    def get_writers(self) -> Iterator[Writer[T]]:
        """
        Obtain writers for each inventory file.
        """

        raise NotImplementedError('Writers must be implemented by subclass')

    def write(self) -> None:
        """
        Write an inventory to files.
        """

        for writer in self.get_writers():
            writer.write()

    def merge_update(self, other: "Inventory[T]", update: bool = True,
                     only_new: bool = False) -> "Inventory[T]":
        """
        Find groups with models that are added or updated in the other inventory
        compared to the current inventory. The returned inventory contains the
        new, existing and merged models grouped by path; only paths with changes
        are included. The products in the current inventory are updated as well.
        If `update` is enabled, then new models are added to and changed models
        updated in the current inventory; this is the default. If `update` is
        disabled, then only the updated models are provided in the return value
        and the current object also remains immutable. If `only_new` is enabled,
        then models that existed but had changes are not considered, just like
        unchanged models; `only_new` inherently disables `update`.
        """

        raise NotImplementedError('Merging must be implemented by subclass')
