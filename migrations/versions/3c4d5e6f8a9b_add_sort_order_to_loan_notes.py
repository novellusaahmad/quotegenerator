"""add sort order to loan notes

Revision ID: 3c4d5e6f8a9b
Revises: 2b3c4d5e6f7a
Create Date: 2024-08-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3c4d5e6f8a9b'
down_revision = '2b3c4d5e6f7a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'loan_notes',
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
    )

    op.execute(
        sa.text(
            """
            UPDATE loan_notes AS ln
            SET sort_order = ordered.row_number - 1
            FROM (
                SELECT id, ROW_NUMBER() OVER (PARTITION BY "group" ORDER BY id) AS row_number
                FROM loan_notes
            ) AS ordered
            WHERE ln.id = ordered.id
            """
        )
    )

    op.alter_column(
        'loan_notes',
        'sort_order',
        existing_type=sa.Integer(),
        nullable=False,
    )


def downgrade():
    op.drop_column('loan_notes', 'sort_order')
