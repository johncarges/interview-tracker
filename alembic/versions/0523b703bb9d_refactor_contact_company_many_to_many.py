"""refactor contact company many-to-many

Revision ID: 0523b703bb9d
Revises: db3bd3223260
Create Date: 2026-03-02 14:54:25.924308

"""
from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '0523b703bb9d'
down_revision: str | Sequence[str] | None = 'db3bd3223260'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'contactcompany',
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['company.id']),
        sa.ForeignKeyConstraint(['contact_id'], ['contact.id']),
        sa.PrimaryKeyConstraint('contact_id', 'company_id'),
    )
    # SQLite requires batch mode to drop columns
    with op.batch_alter_table('contact') as batch_op:
        batch_op.drop_column('company_id')


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('contact') as batch_op:
        batch_op.add_column(sa.Column('company_id', sa.INTEGER(), nullable=True))
    op.drop_table('contactcompany')
