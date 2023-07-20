# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class ONSCDesempenoDegreeProgress(models.Model):
    _name = 'onsc.desempeno.degree_progress'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Grados de avance'

    name = fields.Char(string="Nombre grado de avance", compute="_compute_name", store=True)
    description = fields.Char(string="Grados de avance", tracking=True, required=True)
    create_date = fields.Date(string=u'Fecha de creación', tracking=True, readonly=True)
    porcent = fields.Float(string="Porcentaje", tracking=True, required=True)
    active = fields.Boolean(string="Activo", tracking=True, default=True)

    _sql_constraints = [
        ('description_uniq', 'unique(description)', u'El nombre de grados de avance debe ser único'),
    ]

    @api.depends('description', 'porcent')
    def _compute_name(self):
        for record in self:
            if record.description and record.porcent:
                record.name = '%s ( %s )' % (record.description, record.porcent)
            else:
                record.name = ''

    def toggle_active(self):
        return super(ONSCDesempenoDegreeProgress, self.with_context(no_check_write=True)).toggle_active()
