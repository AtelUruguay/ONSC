# -*- coding: utf-8 -*-
import json
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as warning_response

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ONSCLegajoVoteRegistry(models.Model):
    _name = "onsc.legajo.vote.registry"
    _description = 'Registro de control de votos'

    legajo_id = fields.Many2one(
        comodel_name="onsc.legajo",
        string="Legajo",
        required=True)
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Funcionario",
        related='legajo_id.employee_id',
        store=True)
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
        compute="_compute_electoral_act_ids_domain")

    @api.constrains("date")
    def _check_date(self):
        for record in self:
            if record.date > fields.Date.today():
                raise ValidationError("La Fecha del presentación debe ser menor o igual al día de hoy")

    @api.depends('legajo_id')
    def _compute_electoral_act_ids_domain(self):
        for rec in self:
            if rec.legajo_id:
                electoral_act_ids = rec.legajo_id.vote_registry_ids.mapped('electoral_act_ids').ids
                rec.electoral_act_ids_domain = json.dumps([("id", "not in", electoral_act_ids)])
            else:
                rec.electoral_act_ids_domain = json.dumps([("id", "in", [])])

    @api.onchange('date')
    def onchange_date(self):
        if self.date and self.date > fields.Date.today():
            self.date = False
            return warning_response(_(u"La Fecha de presentación debe ser menor o igual al día de hoy"))