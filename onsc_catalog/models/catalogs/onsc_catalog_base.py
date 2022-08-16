# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ONSCCatalogHierarchicalLevel(models.Model):
    _name = 'onsc.catalog.hierarchical.level'
    _description = 'Nivel jerárquico'

    code = fields.Char(string=u"Código", required=True)
    name = fields.Char(string='Nombre del nivel jerárquico', required=True)
    description = fields.Text(string='Descripción')
    order = fields.Integer(string="Orden", required=True)
    is_central_administration = fields.Boolean(string="¿Es administración central?", default=True)

    @api.constrains("order")
    def _check_order(self):
        if any(record.order == 0 for record in self):
            raise ValidationError(_(u"El orden debe ser mayor a 0"))

    _sql_constraints = [
        ('is_central_name_uniq',
         'unique(is_central_administration,name)',
         u'El nombre del nivel jerárquico debe ser único'),
        ('is_central_code_uniq', 'unique(is_central_administration,code)',
         u'El código del nivel jerárquico debe ser único'),
        ('is_central_order_uniq', 'unique(is_central_administration,order)',
         u'El orden del nivel jerárquico debe ser único'),
    ]


# FAMILIA OCUPACIONAL
class ONSCCatalogOccupationalFamily(models.Model):
    _name = 'onsc.catalog.occupational.family'
    _description = 'Familia ocupacional'
    _inherit = ['onsc.catalog.abstract.base', 'model.history', 'mail.thread', 'mail.activity.mixin']
    _history_model = 'onsc.catalog.occupational.family.history'

    short_name = fields.Char(string="Sigla", required=True, tracking=True, history=True)


class ONSCCatalogOccupationalFamilyHistory(models.Model):
    _name = 'onsc.catalog.occupational.family.history'
    _description = 'Familia ocupacional: Historial'
    _inherit = ['model.history.data']
    _parent_model = 'onsc.catalog.occupational.family'


# PROCESO DE GESTION
class ONSCCatalogManagementProcess(models.Model):
    _name = 'onsc.catalog.management.process'
    _description = u'Proceso de gestión'
    _inherit = ['onsc.catalog.abstract.base', 'model.history', 'mail.thread', 'mail.activity.mixin']
    _history_model = 'onsc.catalog.management.process.history'


class ONSCCatalogManagementProcessHistory(models.Model):
    _name = 'onsc.catalog.management.process.history'
    _description = u'Proceso de gestión: Historial'
    _inherit = ['model.history.data']
    _parent_model = 'onsc.catalog.management.process'
