"""seed 40 test teachers for frontend testing

Revision ID: d7e8f9a0b1c2
Revises: c1d2e3f4a5b6
Create Date: 2026-05-26 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "d7e8f9a0b1c2"
down_revision: Union[str, Sequence[str], None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 40 Test teachers distributed across 10 faculties (4 per faculty)
# Data structure: {name, faculty_id, status, score, evaluations}
TEACHERS_DATA = [
    # Faculty 11: Facultad de Ingeniería de Sistemas e Informática
    {"name": "Dr. Carlos Mendoza Rodriguez", "faculty": 11, "status": "validated", "score": 4.8, "evals": 125},
    {"name": "Prof. María López García", "faculty": 11, "status": "validated", "score": 3.9, "evals": 87},
    {"name": "Ing. Juan Peña Castro", "faculty": 11, "status": "pending_validation", "score": 3.2, "evals": 42},
    {"name": "Dr. Ana María Gutierrez Morales", "faculty": 11, "status": "validated", "score": 4.5, "evals": 156},
    
    # Faculty 12: Facultad de Ingeniería Electrónica y Eléctrica
    {"name": "Prof. Luis Alberto Flores Quispe", "faculty": 12, "status": "validated", "score": 4.2, "evals": 98},
    {"name": "Lic. Patricia Reyes Morales", "faculty": 12, "status": "validated", "score": 3.8, "evals": 73},
    {"name": "Ing. Diego Vargas Santos", "faculty": 12, "status": "pending_validation", "score": 2.9, "evals": 28},
    {"name": "Dr. Elena Castillo Romero", "faculty": 12, "status": "validated", "score": 4.7, "evals": 142},
    
    # Faculty 13: Facultad de Ingeniería Industrial
    {"name": "Dr. Roberto Medina Quispe", "faculty": 13, "status": "validated", "score": 4.6, "evals": 119},
    {"name": "Prof. Claudia Fernández Rojas", "faculty": 13, "status": "validated", "score": 3.7, "evals": 81},
    {"name": "Ing. Fernando Romero Gutierrez", "faculty": 13, "status": "pending_validation", "score": 3.1, "evals": 39},
    {"name": "Lic. Gabriela Herrera López", "faculty": 13, "status": "validated", "score": 4.3, "evals": 107},
    
    # Faculty 5: Facultad de Ciencias Físicas
    {"name": "Dr. Hector Jiménez Soto", "faculty": 5, "status": "validated", "score": 4.4, "evals": 95},
    {"name": "Prof. Isabella Moreno Delgado", "faculty": 5, "status": "validated", "score": 3.6, "evals": 68},
    {"name": "Ing. Javier Ruiz Castillo", "faculty": 5, "status": "pending_validation", "score": 2.8, "evals": 24},
    {"name": "Dr. Karina Sánchez Flores", "faculty": 5, "status": "validated", "score": 4.9, "evals": 168},
    
    # Faculty 6: Facultad de Ciencias Matemáticas
    {"name": "Prof. Luis Martínez Perez", "faculty": 6, "status": "validated", "score": 4.1, "evals": 89},
    {"name": "Lic. Marcela García Vega", "faculty": 6, "status": "validated", "score": 3.5, "evals": 76},
    {"name": "Dr. Nicolás Ramírez Silva", "faculty": 6, "status": "pending_validation", "score": 3.0, "evals": 35},
    {"name": "Prof. Olivia Campos Rodríguez", "faculty": 6, "status": "validated", "score": 4.6, "evals": 134},
    
    # Faculty 8: Facultad de Derecho y Ciencia Política
    {"name": "Dr. Pablo Esquivel Montoya", "faculty": 8, "status": "validated", "score": 4.3, "evals": 101},
    {"name": "Prof. Quilliana Ibáñez Reyes", "faculty": 8, "status": "validated", "score": 3.4, "evals": 62},
    {"name": "Lic. Rodrigo Vásquez Aguirre", "faculty": 8, "status": "pending_validation", "score": 2.7, "evals": 18},
    {"name": "Dr. Sonia Palacios Mendez", "faculty": 8, "status": "validated", "score": 4.8, "evals": 151},
    
    # Faculty 9: Facultad de Educación
    {"name": "Prof. Teófilo Ramos López", "faculty": 9, "status": "validated", "score": 4.0, "evals": 84},
    {"name": "Lic. Úrsula Navarro García", "faculty": 9, "status": "validated", "score": 3.3, "evals": 55},
    {"name": "Dr. Valentina Ortiz Soto", "faculty": 9, "status": "pending_validation", "score": 2.6, "evals": 15},
    {"name": "Prof. Wagner Salinas Mora", "faculty": 9, "status": "validated", "score": 4.5, "evals": 128},
    
    # Faculty 16: Facultad de Medicina
    {"name": "Dr. Xavier Benavides Campos", "faculty": 16, "status": "validated", "score": 4.7, "evals": 145},
    {"name": "Prof. Yadira Toledo Fuentes", "faculty": 16, "status": "validated", "score": 3.9, "evals": 91},
    {"name": "Lic. Zacarías Contreras Ruiz", "faculty": 16, "status": "pending_validation", "score": 3.1, "evals": 44},
    {"name": "Dr. Amparo Díaz Vargas", "faculty": 16, "status": "validated", "score": 4.4, "evals": 113},
    
    # Faculty 19: Facultad de Psicología
    {"name": "Prof. Benjamín Flores Acosta", "faculty": 19, "status": "validated", "score": 4.2, "evals": 96},
    {"name": "Lic. Cristina Morales Bravo", "faculty": 19, "status": "validated", "score": 3.2, "evals": 49},
    {"name": "Dr. Domingo Rosales Jiménez", "faculty": 19, "status": "pending_validation", "score": 2.9, "evals": 21},
    {"name": "Prof. Esperanza Salazar López", "faculty": 19, "status": "validated", "score": 4.6, "evals": 138},
    
    # Faculty 20: Facultad de Ingeniería Química e Ingeniería Química
    {"name": "Dr. Fabian Guerrero Núñez", "faculty": 20, "status": "validated", "score": 4.3, "evals": 104},
    {"name": "Prof. Gilberta Estrada Moreno", "faculty": 20, "status": "validated", "score": 3.6, "evals": 72},
    {"name": "Ing. Héctor Pacheco Vega", "faculty": 20, "status": "pending_validation", "score": 2.8, "evals": 30},
    {"name": "Dr. Irene Vargas Salinas", "faculty": 20, "status": "validated", "score": 4.7, "evals": 147},
]


def upgrade() -> None:
    """Insert 40 test teachers across 10 faculties"""
    # Build individual value tuples for the INSERT statement
    rows = [
        f"(gen_random_uuid(), '{t['name']}', 1, {t['faculty']}, '{t['status']}', {t['score']}, {t['evals']}, true, now(), now())"
        for t in TEACHERS_DATA
    ]
    
    # Create the bulk INSERT statement
    insert_sql = (
        "INSERT INTO professors "
        "(id, full_name, university_id, faculty_id, validation_status, global_score, total_evaluations, is_active, created_at, updated_at) "
        "VALUES " + ", ".join(rows) + " ON CONFLICT DO NOTHING"
    )
    
    op.execute(sa.text(insert_sql))


def downgrade() -> None:
    """Remove all 40 test teachers by name"""
    teacher_names = [t["name"] for t in TEACHERS_DATA]
    names_list = ", ".join(f"'{name}'" for name in teacher_names)
    op.execute(sa.text(f"DELETE FROM professors WHERE full_name IN ({names_list})"))
