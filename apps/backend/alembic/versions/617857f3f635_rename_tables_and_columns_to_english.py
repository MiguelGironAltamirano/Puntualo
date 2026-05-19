"""Rename Spanish table and column names to English

Revision ID: 617857f3f635
Revises: e417c40fa6cf
Create Date: 2026-05-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '617857f3f635'
down_revision: Union[str, Sequence[str], None] = 'e417c40fa6cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - rename tables and columns to English."""
    
    # Rename tables
    op.rename_table('grados_academicos', 'academic_degrees')
    op.rename_table('universidades', 'universities')
    op.rename_table('materias', 'subjects')
    op.rename_table('categorias_puntuacion', 'rating_categories')
    op.rename_table('profesores', 'teachers')
    op.rename_table('clases', 'classes')
    op.rename_table('resenas', 'reviews')
    op.rename_table('detalle_puntuaciones', 'rating_details')
    
    # Rename columns in academic_degrees
    op.alter_column('academic_degrees', 'nombre', new_column_name='name')
    op.alter_column('academic_degrees', 'nivel', new_column_name='level')
    
    # Rename columns in universities
    op.alter_column('universities', 'nombre', new_column_name='name')
    op.alter_column('universities', 'ciudad', new_column_name='city')
    op.alter_column('universities', 'pais', new_column_name='country')
    
    # Rename columns in subjects
    op.alter_column('subjects', 'nombre', new_column_name='name')
    # area stays the same
    
    # Rename columns in rating_categories
    op.alter_column('rating_categories', 'nombre', new_column_name='name')
    op.alter_column('rating_categories', 'descripcion', new_column_name='description')
    
    # Rename columns in teachers
    op.alter_column('teachers', 'grado_id', new_column_name='degree_id')
    op.alter_column('teachers', 'nombre', new_column_name='name')
    op.alter_column('teachers', 'departamento', new_column_name='department')
    
    # Rename columns in classes
    op.alter_column('classes', 'profesor_id', new_column_name='teacher_id')
    op.alter_column('classes', 'universidad_id', new_column_name='university_id')
    op.alter_column('classes', 'materia_id', new_column_name='subject_id')
    op.alter_column('classes', 'codigo', new_column_name='code')
    op.alter_column('classes', 'horario', new_column_name='schedule')
    op.alter_column('classes', 'semestre', new_column_name='semester')
    op.alter_column('classes', 'año', new_column_name='year')
    
    # Rename columns in reviews
    op.alter_column('reviews', 'usuario_id', new_column_name='user_id')
    op.alter_column('reviews', 'clase_id', new_column_name='class_id')
    op.alter_column('reviews', 'comentario', new_column_name='comment')
    op.alter_column('reviews', 'es_anonima', new_column_name='is_anonymous')
    op.alter_column('reviews', 'estado', new_column_name='status')
    
    # Rename columns in rating_details
    op.alter_column('rating_details', 'resena_id', new_column_name='review_id')
    op.alter_column('rating_details', 'categoria_id', new_column_name='category_id')
    op.alter_column('rating_details', 'valor', new_column_name='score')
    
    # Rename columns in likes
    op.alter_column('likes', 'usuario_id', new_column_name='user_id')
    op.alter_column('likes', 'resena_id', new_column_name='review_id')


def downgrade() -> None:
    """Downgrade schema - revert to Spanish names."""
    
    # Revert column renames in likes
    op.alter_column('likes', 'user_id', new_column_name='usuario_id')
    op.alter_column('likes', 'review_id', new_column_name='resena_id')
    
    # Revert column renames in rating_details
    op.alter_column('rating_details', 'review_id', new_column_name='resena_id')
    op.alter_column('rating_details', 'category_id', new_column_name='categoria_id')
    op.alter_column('rating_details', 'score', new_column_name='valor')
    
    # Revert column renames in reviews
    op.alter_column('reviews', 'user_id', new_column_name='usuario_id')
    op.alter_column('reviews', 'class_id', new_column_name='clase_id')
    op.alter_column('reviews', 'comment', new_column_name='comentario')
    op.alter_column('reviews', 'is_anonymous', new_column_name='es_anonima')
    op.alter_column('reviews', 'status', new_column_name='estado')
    
    # Revert column renames in classes
    op.alter_column('classes', 'teacher_id', new_column_name='profesor_id')
    op.alter_column('classes', 'university_id', new_column_name='universidad_id')
    op.alter_column('classes', 'subject_id', new_column_name='materia_id')
    op.alter_column('classes', 'code', new_column_name='codigo')
    op.alter_column('classes', 'schedule', new_column_name='horario')
    op.alter_column('classes', 'semester', new_column_name='semestre')
    op.alter_column('classes', 'year', new_column_name='año')
    
    # Revert column renames in teachers
    op.alter_column('teachers', 'degree_id', new_column_name='grado_id')
    op.alter_column('teachers', 'name', new_column_name='nombre')
    op.alter_column('teachers', 'department', new_column_name='departamento')
    
    # Revert column renames in rating_categories
    op.alter_column('rating_categories', 'name', new_column_name='nombre')
    op.alter_column('rating_categories', 'description', new_column_name='descripcion')
    
    # Revert column renames in subjects
    op.alter_column('subjects', 'name', new_column_name='nombre')
    
    # Revert column renames in universities
    op.alter_column('universities', 'name', new_column_name='nombre')
    op.alter_column('universities', 'city', new_column_name='ciudad')
    op.alter_column('universities', 'country', new_column_name='pais')
    
    # Revert column renames in academic_degrees
    op.alter_column('academic_degrees', 'name', new_column_name='nombre')
    op.alter_column('academic_degrees', 'level', new_column_name='nivel')
    
    # Revert table renames
    op.rename_table('rating_details', 'detalle_puntuaciones')
    op.rename_table('reviews', 'resenas')
    op.rename_table('classes', 'clases')
    op.rename_table('teachers', 'profesores')
    op.rename_table('rating_categories', 'categorias_puntuacion')
    op.rename_table('subjects', 'materias')
    op.rename_table('universities', 'universidades')
    op.rename_table('academic_degrees', 'grados_academicos')
