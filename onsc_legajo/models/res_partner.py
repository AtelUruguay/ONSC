# -*- coding: utf-8 -*-
from lxml import etree

from odoo import models, fields, api
from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name


class ResPartner(models.Model):
    _inherit = "res.partner"

    legajo_employee_ids = fields.One2many("hr.employee", inverse_name="user_partner_id", string="Empleados de legajos")