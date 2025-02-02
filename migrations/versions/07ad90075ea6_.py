"""empty message

Revision ID: 07ad90075ea6
Revises: 3dfdcfd93d0b
Create Date: 2024-12-04 21:38:28.742979

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '07ad90075ea6'
down_revision = '3dfdcfd93d0b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.alter_column('servings',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=255),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.alter_column('servings',
               existing_type=sa.String(length=255),
               type_=sa.INTEGER(),
               existing_nullable=True)

    # ### end Alembic commands ###
