# -*- coding: utf-8 -*-
import json

from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as warning_response

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


class ONSCLegajoVoteRegistry(models.Model):
    _name = "onsc.legajo.vote.registry"
    _description = 'Registro de control de votos'
    _rec_name = "employee_id"
    _inherit = [
        'onsc.legajo.abstract.legajo.security'
    ]

    def read(self, fields=None, load="_classic_read"):
        Employee = self.env['hr.employee'].sudo()
        result = super(ONSCLegajoVoteRegistry, self).read(fields, load)
        for item in result:
            if item.get('employee_id'):
                employee_id = item['employee_id'][0]
                item['employee_id'] = (item['employee_id'][0], Employee.browse(employee_id)._custom_display_name())
        return result

    def _get_abstract_config_security(self):
        return self.user_has_groups(
            'onsc_legajo.group_legajo_vote_control_consulta,onsc_legajo.group_legajo_vote_control_administrar')

    def _get_abstract_inciso_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_vote_control_recursos_humanos_inciso')

    def _get_abstract_ue_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_vote_control_recursos_humanos_ue')

    def _get_abstract_responsable_uo(self):
        return self.user_has_groups('onsc_legajo.group_legajo_vote_control_responsable_uo')

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('restrict_period'):
            ElectoralAct = self.env['onsc.legajo.electoral.act'].suspend_security().with_context(active_test=False)
            electoral_act_ids = ElectoralAct.search([
                ('date_since_consultation_control', '<=', fields.Date.today()),
                ('date_until_consultation_control', '>=', fields.Date.today())])
            args = expression.AND([[('electoral_act_ids', 'in', electoral_act_ids.ids)], args])
        return super(ONSCLegajoVoteRegistry, self)._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid)

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Funcionario",
        required=True,
        index=True)
    employee_id_domain = fields.Char(string="Dominio Funcionario", compute='_compute_employee_id_domain',
                                     default=lambda self: self._get_domain_employee_ids())
    legajo_id = fields.Many2one(
        comodel_name="onsc.legajo",
        string="Legajo",
        compute='_compute_legajo_id',
        store=True
    )
    date = fields.Date(
        string='Fecha de presentación',
        default=lambda s: fields.Date.today(),
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
    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')

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

    def _compute_employee_id_domain(self):
        for rec in self:
            rec.employee_id_domain = self._get_domain_employee_ids()

    def _compute_should_disable_form_edit(self):
        is_valid_user = self.user_has_groups(
            'onsc_legajo.group_legajo_vote_control_administrar,onsc_legajo.group_legajo_vote_control_recursos_humanos_inciso,onsc_legajo.group_legajo_vote_control_recursos_humanos_ue')
        for record in self:
            record.should_disable_form_edit = self._context.get('is_from_menu') and not is_valid_user

    def _get_domain_employee_ids(self):
        available_contracts = self._get_user_available_contract()
        if not available_contracts:
            return json.dumps([('id', '=', False)])
        else:
            sql_query = """SELECT DISTINCT employee_id FROM hr_contract WHERE id IN %s AND employee_id IS NOT NULL"""
            self.env.cr.execute(sql_query, [tuple(available_contracts.ids)])
            results = self.env.cr.fetchall()
            employee_ids = [item[0] for item in results]
            return json.dumps([('id', 'in', employee_ids)])
