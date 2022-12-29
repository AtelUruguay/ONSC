# -*- coding: utf-8 -*-


def migrate(cr, version):
    #DROP TABLE many2many  - Asociada a una columna que ya deja de existir en Docencia->Materias
    cr.execute("DROP TABLE IF EXISTS academic_program_teaching_rel")
