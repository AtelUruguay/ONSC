# -*- coding: utf-8 -*-

import json

from odoo import fields, models, api


class ONSCCVFileValidationConfig(models.Model):
    _name = 'onsc.cv.documentary.validation.config'
    _description = 'Configuración de validación documental'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'model.history']
    _history_model = 'onsc.cv.documentary.validation.config.history'
    _rec_name = 'model_id'

    active = fields.Boolean(string="Activo", default=True)
    model_id = fields.Many2one(comodel_name="ir.model", string="Modelo",
                               ondelete='cascade',
                               history=True,
                               required=True,
                               domain="[('model', 'ilike', '%onsc.cv%')]")
    field_ids = fields.Many2many("ir.model.fields", string="Documentos a excluir", history=True, )

    @api.onchange('model_id')
    def onchange_model_id(self):
        self.field_ids = [(5,)]


class ONSCCVFileValidationConfigHistory(models.Model):
    _inherit = ['model.history.data']
    _name = 'onsc.cv.documentary.validation.config.history'
    _parent_model = 'onsc.cv.documentary.validation.config'
