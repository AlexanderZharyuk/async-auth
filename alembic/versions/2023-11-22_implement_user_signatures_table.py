"""Implement user signatures table

Revision ID: c3c718bfc512
Revises: 024d67eaf3e3
Create Date: 2023-11-22 15:43:55.535900

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3c718bfc512"
down_revision: Union[str, None] = "024d67eaf3e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users_signatures",
        sa.Column("signature", sa.String(length=120), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("users_signatures_user_id_fkey"),
        ),
        sa.PrimaryKeyConstraint(
            "signature", name=op.f("users_signatures_pkey")
        ),
        sa.UniqueConstraint(
            "signature", name=op.f("users_signatures_signature_key")
        ),
        sa.UniqueConstraint(
            "user_id", name=op.f("users_signatures_user_id_key")
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("users_signatures")
    # ### end Alembic commands ###