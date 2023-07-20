# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class ONSCDesempenoDegree(models.Model):
    _name = 'onsc.desempeno.degree'
    _description = 'Grados de desarrollo'

    name = fields.Char(string="Nombre grados de desarrollo", compute="_compute_name", store=True)
    description = fields.Char(string="Grados de desarrollo", required=True)
    frecuency = fields.Char(string="Frecuencia", required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ('description_uniq', 'unique(description)', u'El nombre del grado de desarrollo debe ser único'),
    ]

    @api.depends('description', 'frecuency')
    def _compute_name(self):
        for record in self:
            if record.description and record.frecuency:
                record.name = '%s - %s' % (record.description, record.frecuency)
            else:
                record.name = ''

    def toggle_active(self):
        return super(ONSCDesempenoDegree, self.with_context(no_check_write=True)).toggle_active()
