# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = "res.users"

    operating_unit_ids = fields.One2many(
        comodel_name="operating.unit",
        context={'active_test': False},
        compute="_compute_operating_unit_ids",
        inverse="_inverse_operating_unit_ids",
    )
    assigned_operating_unit_ids = fields.Many2many(
        comodel_name="operating.unit",
        relation="operating_unit_users_rel",
        column1="user_id",
        column2="operating_unit_id",
        string="Operating Units",
        context={'active_test': False},
        default=lambda self: self._default_operating_units(),
    )

    @api.depends("groups_id", "assigned_operating_unit_ids")
    def _compute_operating_unit_ids(self):
        super(ResUsers, self.with_context(active_test=False))._compute_operating_unit_ids()
