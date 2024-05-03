# -*- coding: utf-8 -*-

import json

from odoo import fields, models, api


class ONSCCVFileValidationConfig(models.Model):
    _name = 'onsc.cv.documentary.validation.config'
    _description = 'Configuración de validación documental'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'model.history']
    _history_model = 'onsc.cv.documentary.validation.config.history'
    _rec_name = 'model_id'

    def _default_model_id_domain(self):
        fields = self.env['ir.model.fields'].search([
            ('model_id.model', 'ilike', '%onsc.cv%'),
            ('model_id.model', 'not ilike', '%onsc.cv.abstract%'),
            ('model_id.model', '!=', 'onsc.cv.information.contact'),
            ('model_id.model', '!=', 'onsc.cv.academic.program.subject'),
            ('model_id.model', '!=', 'onsc.cv.digital.call'),
            ('model_id.model', '!=', 'onsc.cv.other.relevant.information'),
            ('name', '=', 'cv_digital_id')])
        return json.dumps([('id', 'in', fields.mapped('model_id').ids)])

    active = fields.Boolean(string="Activo", default=True)
    model_id = fields.Many2one("ir.model", string="Modelo",
                               ondelete='cascade',
                               history=True,
                               required=True)
    field_id = fields.Many2one("ir.model.fields", string="Enlace en el CV")
    model_id_domain = fields.Char(compute='_compute_model_id_domain', default=_default_model_id_domain)

    field_ids = fields.Many2many("ir.model.fields", string="Campos a excluir", history=True, )

    _sql_constraints = [
        ("model_id_uniq", "unique (model_id)", "El modelo debe ser único",)
    ]

    @api.onchange('model_id')
    def onchange_model_id(self):
        self.field_id = self.env['ir.model.fields'].search([
            ('ttype', 'in', ['one2many', 'many2many']),
            ('relation', '=', self.model_id.model),
            ('model_id.model', '=', 'onsc.cv.digital')], limit=1)
        self.field_ids = [(5,)]

    def _compute_model_id_domain(self):
        model_id_domain = self._default_model_id_domain()
        for rec in self:
            rec.model_id_domain = model_id_domain

    def write(self, vals):
        return super(ONSCCVFileValidationConfig, self.suspend_security()).write(vals)

    def get_config(self, name=False):
        if name is False:
            return self.search([])
        return self.search([('model_id.model', '=', self._name)], limit=1)


class ONSCCVFileValidationConfigHistory(models.Model):
    _inherit = ['model.history.data']
    _name = 'onsc.cv.documentary.validation.config.history'
    _parent_model = 'onsc.cv.documentary.validation.config'
