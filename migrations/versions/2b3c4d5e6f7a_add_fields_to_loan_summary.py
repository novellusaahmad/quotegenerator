"""add extra summary fields to loan_summary

Revision ID: 2b3c4d5e6f7a
Revises: 1a2b3c4d5e6f
Create Date: 2024-07-30 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2b3c4d5e6f7a'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('loan_summary', sa.Column('currency_symbol', sa.String(length=5), nullable=True))
    op.add_column('loan_summary', sa.Column('gross_amount_percentage', sa.Numeric(15, 4), nullable=True))
    op.add_column('loan_summary', sa.Column('ltv_target', sa.Numeric(15, 4), nullable=True))
    op.add_column('loan_summary', sa.Column('monthly_interest_payment', sa.Numeric(15, 2), nullable=True))
    op.add_column('loan_summary', sa.Column('quarterly_interest_payment', sa.Numeric(15, 2), nullable=True))
    op.add_column('loan_data', sa.Column('currency_symbol', sa.String(), nullable=True))
    op.add_column('loan_data', sa.Column('gross_amount_percentage', sa.String(), nullable=True))
    op.add_column('loan_data', sa.Column('ltv_target', sa.String(), nullable=True))
    op.add_column('loan_data', sa.Column('monthly_interest_payment', sa.String(), nullable=True))
    op.add_column('loan_data', sa.Column('quarterly_interest_payment', sa.String(), nullable=True))


def downgrade():
    op.drop_column('loan_summary', 'quarterly_interest_payment')
    op.drop_column('loan_summary', 'monthly_interest_payment')
    op.drop_column('loan_summary', 'ltv_target')
    op.drop_column('loan_summary', 'gross_amount_percentage')
    op.drop_column('loan_summary', 'currency_symbol')
    op.drop_column('loan_data', 'quarterly_interest_payment')
    op.drop_column('loan_data', 'monthly_interest_payment')
    op.drop_column('loan_data', 'ltv_target')
    op.drop_column('loan_data', 'gross_amount_percentage')
    op.drop_column('loan_data', 'currency_symbol')
