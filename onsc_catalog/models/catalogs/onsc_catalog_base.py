# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ONSCCatalogHierarchicalLevel(models.Model):
    _name = 'onsc.catalog.hierarchical.level'
    _description = 'Nivel jerárquico'
    _order = 'order ASC'

    code = fields.Char(string=u"Código", required=True)
    name = fields.Char(string='Nombre del nivel jerárquico', required=True)
    description = fields.Text(string='Descripción')
    order = fields.Integer(string="Orden", required=True)
    is_central_administration = fields.Boolean(string="¿Es administración central?", default=True)
    active = fields.Boolean(default=True, tracking=True, history=True)

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

    _sql_constraints = [
        ("short_name_uniq", "unique (short_name)", "La sigla debe ser única"),
    ]

    def toggle_active(self):
        return super(ONSCCatalogOccupationalFamily, self.with_context(no_check_active=True)).toggle_active()


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

    def toggle_active(self):
        return super(ONSCCatalogManagementProcess, self.with_context(no_check_active=True)).toggle_active()


class ONSCCatalogManagementProcessHistory(models.Model):
    _name = 'onsc.catalog.management.process.history'
    _description = u'Proceso de gestión: Historial'
    _inherit = ['model.history.data']
    _parent_model = 'onsc.catalog.management.process'


class ONSCCatalogTypeOrganization(models.Model):
    _name = 'onsc.catalog.type.organization'
    _description = u'Tipo de organismo'
    _inherit = ['onsc.cv.catalog.abstract']


class ONSCCatalogTopicAddressed(models.Model):
    _name = 'onsc.catalog.topic.addressed'
    _description = u'Temática abordada'
    _inherit = ['onsc.cv.catalog.abstract']


class ONSCCatalogDescriptor1(models.Model):
    _name = 'onsc.catalog.descriptor1'
    _description = u'Descriptor 1'
    _inherit = ['onsc.cv.catalog.abstract']

    occupational_family_id = fields.Many2one("onsc.catalog.occupational.family", string="Mapeo familia ocupacional",
                                             ondelete='restrict')
    is_graduation_date_required = fields.Boolean(string=u"¿Fecha de graduación requerida?")


class ONSCCatalogDescriptor2(models.Model):
    _name = 'onsc.catalog.descriptor2'
    _description = u'Descriptor 2'
    _inherit = ['onsc.cv.catalog.abstract']


class ONSCCatalogDescriptor3(models.Model):
    _name = 'onsc.catalog.descriptor3'
    _description = u'Descriptor 3'
    _inherit = ['onsc.cv.catalog.abstract']


class ONSCCatalogDescriptor4(models.Model):
    _name = 'onsc.catalog.descriptor4'
    _description = u'Descriptor 4'
    _inherit = ['onsc.cv.catalog.abstract']
