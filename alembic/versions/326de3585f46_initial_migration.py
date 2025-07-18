"""initial migration

Revision ID: 326de3585f46
Revises: 
Create Date: 2025-03-18 22:19:03.134260

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa # type: ignore


# revision identifiers, used by Alembic.
revision: str = '326de3585f46'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('prompt_history', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'prompt_history')
    # ### end Alembic commands ###
