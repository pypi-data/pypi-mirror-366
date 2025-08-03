"""
Add product metadata range

Revision ID: 5a5bf02e8988
Revises: 8ef12eb24650
Create Date: 2025-06-29 22:58:47.923160
"""
# pylint: disable=invalid-name

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# Revision identifiers, used by Alembic.
revision: str = '5a5bf02e8988'
down_revision: Union[str, None] = '8ef12eb24650'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Perform the upgrade.
    """

    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('generic_id', sa.Integer(),
                                      nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_product_generic_id_product'),
                                    'product', ['generic_id'], ['id'],
                                    ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade() -> None:
    """
    Perform the downgrade.
    """

    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_product_generic_id_product'),
                                 type_='foreignkey')
        product = table('product', column('id', sa.Integer()),
                        column('generic_id', sa.Integer()))
        batch_op.execute(product.delete()
                         .where(product.c.generic_id.is_not(None)))
        batch_op.drop_column('generic_id')

    # ### end Alembic commands ###
