# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from lxml import etree
from lxml.html import builder as html

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Invite(models.TransientModel):
    _inherit = 'mail.wizard.invite'

    @api.depends('res_model', 'res_id')
    def _get_domain_partner_ids(self):
        context = self.env.context.copy()
        model = context.get('default_res_model', '')
        res_id = context.get('default_res_id', False)
        if model == 'onsc.legajo.alta.vl' and res_id:
            alta_id = self.env[model].browse(res_id)
            partner_ids = self.env['hr.contract'].search(
                [
                    ('operating_unit_id', '=', alta_id.operating_unit_id.id)
                ]).mapped('employee_id.user_id.partner_id')
            return [('id', 'in', partner_ids.ids)]
        return [('type', '!=', 'private')]

    partner_ids = fields.Many2many('res.partner', string='Recipients', help="List of partners that will be added as follower of the current document.",
                                   domain=_get_domain_partner_ids)

