"""feat: admin boundaries

Revision ID: 50fd789492b2
Revises: 68cbf0444c24
Create Date: 2025-02-11 16:44:43.289213

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "50fd789492b2"
down_revision: Union[str, None] = "68cbf0444c24"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_geospatial_table(
        "admin_boundaries",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("osm_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("admin_level", sa.Integer(), nullable=True),
        sa.Column(
            "geometry",
            Geometry(
                geometry_type="POLYGON",
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                nullable=False,
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("osm_id"),
    )
    op.create_geospatial_index(
        "idx_admin_boundaries_geometry",
        "admin_boundaries",
        ["geometry"],
        unique=False,
        postgresql_using="gist",
        postgresql_ops={},
    )
    op.drop_geospatial_table("all_buildings_hala")
    op.drop_geospatial_table("buildings_hala")
    op.drop_geospatial_table("amenities_hala")
    op.drop_geospatial_table("buildings_centroids_hala")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_geospatial_table(
        "buildings_centroids_hala",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=True),
        sa.Column("osm_id", sa.BIGINT(), autoincrement=False, nullable=True),
        sa.Column(
            "information",
            postgresql.JSON(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "centroid_geom",
            Geometry(
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                _spatial_index_reflected=True,
            ),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.create_geospatial_table(
        "amenities_hala",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=True),
        sa.Column("osm_id", sa.BIGINT(), autoincrement=False, nullable=True),
        sa.Column(
            "information",
            postgresql.JSON(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "geometry",
            Geometry(
                geometry_type="POLYGON",
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                _spatial_index_reflected=True,
            ),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "categories", sa.VARCHAR(length=255), autoincrement=False, nullable=True
        ),
        sa.Column("name", sa.VARCHAR(length=255), autoincrement=False, nullable=True),
        sa.Column("historical", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("wikipedia", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("image_url", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("website", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column(
            "sub_categories", sa.VARCHAR(length=255), autoincrement=False, nullable=True
        ),
    )
    op.create_geospatial_table(
        "buildings_hala",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=True),
        sa.Column("osm_id", sa.BIGINT(), autoincrement=False, nullable=True),
        sa.Column(
            "information",
            postgresql.JSON(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "geometry",
            Geometry(
                geometry_type="POLYGON",
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                _spatial_index_reflected=True,
            ),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "Category", sa.VARCHAR(length=255), autoincrement=False, nullable=True
        ),
    )
    op.create_geospatial_table(
        "all_buildings_hala",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=True),
        sa.Column("osm_id", sa.BIGINT(), autoincrement=False, nullable=True),
        sa.Column(
            "information",
            postgresql.JSON(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "geometry",
            Geometry(
                geometry_type="POLYGON",
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                _spatial_index_reflected=True,
            ),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "Category",
            sa.VARCHAR(length=255),
            server_default=sa.text("'Unknown'::character varying"),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_geospatial_index(
        "idx_admin_boundaries_geometry",
        table_name="admin_boundaries",
        postgresql_using="gist",
        column_name="geometry",
    )
    op.drop_geospatial_table("admin_boundaries")
    # ### end Alembic commands ###
