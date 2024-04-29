# -*- coding: utf-8 -*-
import json
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as warning_response

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ONSCLegajoVoteRegistry(models.Model):
    _name = "onsc.legajo.vote.registry"
    _description = 'Registro de control de votos'
    _inherit = [
        'onsc.legajo.abstract.opbase.security'
    ]

    def _get_domain(self, args):
        return super(ONSCLegajoVoteRegistry, self)._get_domain(args, use_employee=True)

    def _is_group_inciso_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_vote_control_recursos_humanos_inciso')

    def _is_group_ue_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_vote_control_recursos_humanos_ue')

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Funcionario",
        index=True)
    legajo_id = fields.Many2one(
        comodel_name="onsc.legajo",
        string="Legajo",
        compute='_compute_legajo_id',
        store=True
    )
    date = fields.Date(
        string='Fecha de presentación',
        default = lambda s: fields.Date.today(),
        required=True)
    electoral_act_ids = fields.Many2many(
        comodel_name='onsc.legajo.electoral.act',
        required=True,
        relation="onsc_legajo_vote_registry_electoral_act",
        string='Elecciones')
    electoral_act_ids_domain = fields.Char(
        string='Elecciones disponibles',
        related='legajo_id.electoral_act_ids_domain')

    any_electoral_act_active = fields.Boolean(
        '¿Alguna Elección activa?',
        search='_search_any_electoral_act_active',
        store=False)

    @api.constrains("date")
    def _check_date(self):
        for record in self:
            if record.date > fields.Date.today():
                raise ValidationError("La Fecha del presentación debe ser menor o igual al día de hoy")

    @api.onchange('date')
    def onchange_date(self):
        if self.date and self.date > fields.Date.today():
            self.date = False
            return warning_response(_(u"La Fecha de presentación debe ser menor o igual al día de hoy"))

    def _search_any_electoral_act_active(self, operator, operand):
        ElectoralAct = self.env['onsc.legajo.electoral.act'].suspend_security().with_context(active_test=False)
        electoral_act_ids = ElectoralAct.search([
                ('date_since_entry_control', '<=', fields.Date.today()),
                ('date_until_entry_control', '>=', fields.Date.today())])
        return [('electoral_act_ids', 'in', electoral_act_ids.ids)]

    @api.depends('employee_id')
    def _compute_legajo_id(self):
        for rec in self:
            rec.legajo_id = self.env['onsc.legajo'].sudo().search([('employee_id', '=', rec.employee_id.id)], limit=1)
