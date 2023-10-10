# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCatalogDescriptor1(models.Model):
    _inherit = 'onsc.catalog.descriptor1'

    is_occupation_required = fields.Boolean(string=u"Ocupación")
