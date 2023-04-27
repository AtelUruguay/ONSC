# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    legajo_employee_ids = fields.One2many("hr.employee", inverse_name="user_partner_id", string="Empleados de legajos")
