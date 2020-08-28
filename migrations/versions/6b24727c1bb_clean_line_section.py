"""clean line_section
Revision ID: 6b24727c1bb
Revises: 4e3c651ba4be
Create Date: 2020-08-24 11:31:23
"""

# revision identifiers, used by Alembic.
revision = '6b24727c1bb'
down_revision = '4e3c651ba4be'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('line_section', 'sens')
    op.drop_table('associate_line_section_via_object')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('associate_line_section_via_object',
        sa.Column('line_section_id', postgresql.UUID(), nullable=True),
        sa.Column('stop_area_object_id', postgresql.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['line_section_id'], ['line_section.id'], ),
        sa.ForeignKeyConstraint(['stop_area_object_id'], ['pt_object.id'], ),
        sa.PrimaryKeyConstraint('line_section_id', 'stop_area_object_id', name='line_section_stop_area_object_pk')
    )
    op.add_column('line_section', sa.Column('sens', sa.Integer(), nullable=True))
    ### end Alembic commands ###