# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ONSCDesempenoDegreeProgress(models.Model):
    _name = 'onsc.desempeno.degree.progress'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Grados de avance'

    name = fields.Char(string="Nombre-Porcentaje de avance", compute="_compute_name", store=True)
    description = fields.Char(string="Nombre del grado de avance", tracking=True, required=True)
    create_date = fields.Date(string=u'Fecha de creación', tracking=True, readonly=True)
    porcent = fields.Float(string="Grado de avance", tracking=True, required=True)
    active = fields.Boolean(string="Activo", tracking=True, default=True)
    is_cancel_flow = fields.Boolean(string='Es el Cancelar (Mejorar label)')

    _sql_constraints = [
        ('description_uniq', 'unique(description)', u'El nombre de grados de avance debe ser único'),
    ]

    @api.depends('description', 'porcent')
    def _compute_name(self):
        for record in self:
            if record.description:
                record.name = '%s (%s' % (record.description, record.porcent * 100) + '%)'
            else:
                record.name = ''

    @api.constrains('is_cancel_flow')
    def _compute_is_cancel_flow(self):
        for record in self:
            if record.is_cancel_flow and self.search_count([('is_cancel_flow','=',True), ('id', '!=', record.id)]) > 1:
                raise ValidationError(_("No puede existir más de un Grado de Avance de Cancelación"))

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['description'] = _("%s (Copia)") % self.description
        return super(ONSCDesempenoDegreeProgress, self).copy(default=default)
