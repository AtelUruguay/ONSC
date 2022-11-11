# -*- coding: utf-8 -*-

from odoo import fields, models


class Users(models.Model):
    _inherit = "res.users"

    def _default_accion_id(self):
        default_user_id = self.env['ir.model.data']._xmlid_to_res_id('base.default_user', raise_if_not_found=False)
        return self.env['res.users'].browse(default_user_id).sudo().action_id if default_user_id else False

    action_id = fields.Many2one(
        'ir.actions.actions',
        string='Home Action',
        default=_default_accion_id,
        help="If specified, this action will be opened at log on for this user, in addition to the standard menu.")
