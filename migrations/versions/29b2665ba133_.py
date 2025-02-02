"""empty message

Revision ID: 29b2665ba133
Revises:
Create Date: 2024-11-23 14:36:52.112735

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29b2665ba133'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('anonymous_user',
    sa.Column('id', sa.String(length=255), nullable=False),
    sa.Column('identifier', sa.String(length=50), nullable=False),
    sa.Column('request_count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('identifier')
    )
    op.create_table('nutritions',
    sa.Column('id', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('quantity', sa.Float(), nullable=False),
    sa.Column('unit', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('recipes',
    sa.Column('id', sa.String(length=255), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('origin', sa.String(length=255), nullable=False),
    sa.Column('servings', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('preparation_time', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('image_url', sa.String(length=255), nullable=True),
    sa.Column('ingredients', sa.JSON(), nullable=True),
    sa.Column('processes', sa.JSON(), nullable=True),
    sa.Column('nutritions', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('activate', sa.Boolean(), nullable=True),
    sa.Column('google_token', sa.String(length=255), nullable=True),
    sa.Column('google_id', sa.String(length=255), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('google_id'),
    sa.UniqueConstraint('google_token'),
    sa.UniqueConstraint('password')
    )
    op.create_table('anonymous_user_recipe',
    sa.Column('anonymous_user_id', sa.String(length=255), nullable=False),
    sa.Column('recipe_id', sa.String(length=255), nullable=False),
    sa.Column('flag', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['anonymous_user_id'], ['anonymous_user.id'], ),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ),
    sa.PrimaryKeyConstraint('anonymous_user_id', 'recipe_id')
    )
    op.create_table('ingredients',
    sa.Column('id', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('quantity', sa.Float(), nullable=False),
    sa.Column('unit', sa.String(length=50), nullable=False),
    sa.Column('recipe_id', sa.String(length=255), nullable=False),
    sa.Column('nutrition_id', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['nutrition_id'], ['nutritions.id'], ),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payment',
    sa.Column('id', sa.String(length=255), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('payment_type', sa.String(length=50), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('user_id', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('processes',
    sa.Column('id', sa.String(length=255), nullable=False),
    sa.Column('step_number', sa.Integer(), nullable=False),
    sa.Column('instructions', sa.Text(), nullable=False),
    sa.Column('recipe_id', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_recipe',
    sa.Column('user_id', sa.String(length=255), nullable=False),
    sa.Column('recipe_id', sa.String(length=255), nullable=False),
    sa.Column('flag', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'recipe_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_recipe')
    op.drop_table('processes')
    op.drop_table('payment')
    op.drop_table('ingredients')
    op.drop_table('anonymous_user_recipe')
    op.drop_table('user')
    op.drop_table('recipes')
    op.drop_table('nutritions')
    op.drop_table('anonymous_user')
    # ### end Alembic commands ###
