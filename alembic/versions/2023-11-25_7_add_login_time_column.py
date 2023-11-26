"""Add login time column

Revision ID: 76f2a2c3a433
Revises: ddf3cca3f83e
Create Date: 2023-11-25 22:42:51.964959

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "76f2a2c3a433"
down_revision: Union[str, None] = "ddf3cca3f83e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users_logins",
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users_logins", "time")
    # ### end Alembic commands ###
