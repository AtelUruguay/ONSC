# -*- coding: utf-8 -*-

from odoo import fields, models, tools, api
from odoo.osv import expression


class ONSCLegajoDepartment(models.Model):
    _name = "onsc.legajo.job.hierarchy"
    _description = "Legajo - Jerarquía de puestos"
    _auto = False
    _order = "job_id"

    job_id = fields.Many2one('hr.job', string="Puesto")
    level_0 = fields.Many2one('hr.department', string='Nivel 0')
    level_1 = fields.Many2one('hr.department', string='Nivel 1')
    level_2 = fields.Many2one('hr.department', string='Nivel 2')
    level_3 = fields.Many2one('hr.department', string='Nivel 3')
    level_4 = fields.Many2one('hr.department', string='Nivel 4')
    level_4 = fields.Many2one('hr.department', string='Nivel 5')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''CREATE OR REPLACE VIEW %s AS
WITH RECURSIVE department_hierarchy AS (
    -- Caso base: obtener el departamento inicial de cada job
    SELECT
        j.id AS job_id,
        d.id AS department_id,
        d.parent_id,
        ARRAY[d.id] AS hierarchy_array -- Iniciamos el array con el primer departamento
    FROM hr_job j
    JOIN hr_department d ON j.department_id = d.id

    UNION ALL

    -- Paso recursivo: agregar el departamento padre al inicio del array
    SELECT
        dh.job_id,
        d.id AS department_id,
        d.parent_id,
        ARRAY[d.id] || dh.hierarchy_array -- Se agrega el padre al inicio del array
    FROM hr_department d
    JOIN department_hierarchy dh ON d.id = dh.parent_id
)
SELECT
    job_id,
    hierarchy_array[1] AS level_0, -- Padre más alto
    hierarchy_array[2] AS level_1,
    hierarchy_array[3] AS level_2,
    hierarchy_array[4] AS level_3,
    hierarchy_array[5] AS level_4,
    hierarchy_array[6] AS level_5
FROM department_hierarchy
WHERE parent_id IS NULL; -- Se filtra para obtener la jerarquía completa
''' % (self._table,))
