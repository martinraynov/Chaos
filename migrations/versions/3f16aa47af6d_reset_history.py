"""reset history

Revision ID: 3f16aa47af6d
Revises: 2b51c35f9879
Create Date: 2019-05-14 18:01:46.447246

"""

# revision identifiers, used by Alembic.
revision = '3f16aa47af6d'
down_revision = '2b51c35f9879'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


def upgrade():
    op.execute('DROP TRIGGER IF EXISTS last_disruption_changes ON public.disruption')
    op.execute('DROP TRIGGER IF EXISTS handle_impact_change_for_associate_impact_pt_object ON public.impact')

    op.execute('DROP FUNCTION IF EXISTS public.log_disruption_update()')
    op.execute('DROP FUNCTION IF EXISTS public.handle_impact_change_for_associate_impact_pt_object()')

    op.execute('DROP SCHEMA history CASCADE')
    create_history_schema()


def downgrade():
    create_history_schema()

    # create tables
    op.create_table('disruption',
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
                    sa.Column('disruption_id', UUID(), nullable=False),
                    sa.Column('reference', sa.Text(), nullable=True),
                    sa.Column('note', sa.Text(), nullable=True),
                    sa.Column('start_publication_date', sa.DateTime(), nullable=True),
                    sa.Column('end_publication_date', sa.DateTime(), nullable=True),
                    sa.Column('version', sa.Integer(), nullable=False),
                    sa.Column('client_id', UUID(), nullable=False),
                    sa.Column('contributor_id', UUID(), nullable=False),
                    sa.Column('cause_id', UUID(), nullable=False),
                    sa.Column('status', sa.Text(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    schema='history'
                    )
    op.create_table('associate_disruption_tag',
                    sa.Column('tag_id', UUID(), nullable=False),
                    sa.Column('disruption_id', UUID(), nullable=False),
                    sa.Column('version', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('tag_id', 'disruption_id', 'version'),
                    schema='history'
                    )

    op.create_table('associate_disruption_pt_object',
                    sa.Column('disruption_id', UUID(), nullable=False),
                    sa.Column('pt_object_id', UUID(), nullable=False),
                    sa.Column('version', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('disruption_id', 'pt_object_id', 'version'),
                    schema='history'
                    )

    op.create_table('associate_disruption_property',
                    sa.Column('value', sa.Text(), nullable=False),
                    sa.Column('disruption_id', UUID(), nullable=False),
                    sa.Column('property_id', UUID(), nullable=False),
                    sa.Column('version', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('disruption_id', 'property_id', 'value', 'version'),
                    schema='history'
                    )

    op.create_table('impact',
                    sa.Column('created_at', sa.DateTime(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
                    sa.Column('disruption_id', sa.Integer(), nullable=False),
                    sa.Column('public_created_at', sa.DateTime(), nullable=False),
                    sa.Column('public_updated_at', sa.DateTime(), nullable=True),
                    sa.Column('public_id', UUID(), nullable=False),
                    sa.Column('public_disruption_id', UUID(), nullable=False),
                    sa.Column('public_status', sa.Text(), nullable=False),
                    sa.Column('public_severity_id', UUID(), nullable=True),
                    sa.Column('public_send_notifications', sa.Boolean(), nullable=False),
                    sa.Column('public_version', sa.Integer(), nullable=False),
                    sa.Column('public_notification_date', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.ForeignKeyConstraint(['disruption_id'], ['history.disruption.id']),
                    schema='history'
                    )

    op.create_table('associate_impact_pt_object',
                    sa.Column('public_impact_id', UUID(), nullable=True),
                    sa.Column('public_pt_object_id', UUID(), nullable=True),
                    sa.Column('public_impact_version', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('public_impact_id', 'public_pt_object_id', 'public_impact_version'),
                    schema='history'
                    )

    # create functions
    log_disruption_history_function = (
        'CREATE OR REPLACE FUNCTION log_disruption_update()'
        ' RETURNS trigger AS '
        '$BODY$ '
        'BEGIN '
        ' INSERT INTO history.disruption(created_at,updated_at,disruption_id,reference,note,start_publication_date,end_publication_date,version,client_id,contributor_id,cause_id,status)'
        ' VALUES(OLD.created_at,OLD.updated_at,OLD.id,OLD.reference,OLD.note,OLD.start_publication_date,OLD.end_publication_date,OLD.version,OLD.client_id,OLD.contributor_id,OLD.cause_id,OLD.status);'
        ' INSERT INTO history.associate_disruption_tag(tag_id,disruption_id,version)'
        ' SELECT tag_id,disruption_id,OLD.version FROM public.associate_disruption_tag WHERE disruption_id = OLD.id;'
        ' INSERT INTO history.associate_disruption_pt_object(disruption_id,pt_object_id,version)'
        ' SELECT disruption_id,pt_object_id,OLD.version FROM public.associate_disruption_pt_object WHERE disruption_id = OLD.id;'
        ' INSERT INTO history.associate_disruption_property(value,disruption_id,property_id,version)'
        ' SELECT value,disruption_id,property_id,OLD.version FROM public.associate_disruption_property WHERE disruption_id = OLD.id;'
        ' RETURN NEW;'
        'END; '
        '$BODY$ '
        'LANGUAGE plpgsql VOLATILE'
    )

    create_disruption_history_function = (
        'CREATE OR REPLACE FUNCTION history.handle_disruption_history_change_for_impacts() RETURNS TRIGGER '
        'AS $data$ '
        '   DECLARE '
        '       public_disruption_id uuid; '
        '   BEGIN '
        '   public_disruption_id = new.disruption_id; '
        '   INSERT INTO history.impact ('
        '            created_at,'
        '            disruption_id,'
        '            public_created_at,'
        '            public_updated_at,'
        '            public_id,'
        '            public_disruption_id,'
        '            public_status,'
        '            public_severity_id,'
        '            public_send_notifications,'
        '            public_version,'
        '            public_notification_date'
        '        ) '
        '            SELECT '
        '                NOW(),'
        '                NEW.id,'
        '                created_at,'
        '                updated_at,'
        '                id,'
        '                disruption_id,'
        '                status,'
        '                severity_id,'
        '                send_notifications,'
        '                version,'
        '                notification_date'
        '            FROM'
        '                public.impact'
        '            WHERE'
        '                public.impact.disruption_id = public_disruption_id'
        '        ;'
        '   RETURN NULL;'
        ' END;'
        ' $data$ LANGUAGE plpgsql;'
    )

    create_impact_function = (
        'CREATE OR REPLACE FUNCTION handle_impact_change_for_associate_impact_pt_object() RETURNS TRIGGER '
        'AS $BODY$ '
        '   BEGIN '
        '   INSERT INTO history.associate_impact_pt_object ('
        '            public_impact_id,'
        '            public_pt_object_id,'
        '            public_impact_version'
        '        ) '
        '            SELECT '
        '                impact_id,'
        '                pt_object_id,'
        '                OLD.version'
        '            FROM'
        '                public.associate_impact_pt_object'
        '            WHERE'
        '                public.associate_impact_pt_object.impact_id = OLD.id'
        '        ;'
        '   RETURN NULL;'
        ' END;'
        ' $BODY$ LANGUAGE plpgsql;'
    )

    op.execute(log_disruption_history_function)
    op.execute(create_disruption_history_function)
    op.execute(create_impact_function)

    # create triggers
    create_disruption_trigger = (
        'CREATE TRIGGER last_disruption_changes '
        '   AFTER UPDATE ON public.disruption '
        '       FOR EACH ROW EXECUTE PROCEDURE log_disruption_update()'
    )

    create_disruption_history_trigger = (
        'CREATE TRIGGER handle_disruption_history_change_for_impacts '
        '   AFTER INSERT OR UPDATE ON history.disruption '
        '       FOR EACH ROW EXECUTE PROCEDURE history.handle_disruption_history_change_for_impacts()'
    )

    create_impact_trigger = (
        'CREATE TRIGGER handle_impact_change_for_associate_impact_pt_object '
        '   AFTER UPDATE ON public.impact '
        '       FOR EACH ROW EXECUTE PROCEDURE handle_impact_change_for_associate_impact_pt_object()'
    )

    op.execute(create_disruption_trigger)
    op.execute(create_disruption_history_trigger)
    op.execute(create_impact_trigger)


def create_history_schema():
    """
    Creates schema "history" if not exist
    :return:
    """
    connection = op.get_bind()
    result = connection.execute(
        'SELECT COUNT(*) as nb FROM information_schema.schemata WHERE schema_name = \'history\'')
    for row in result:
        if row['nb'] == 0:
            op.execute('CREATE SCHEMA history')
