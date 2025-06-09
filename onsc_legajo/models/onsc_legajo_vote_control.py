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

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('restrict_period'):
            ElectoralAct = self.env['onsc.legajo.electoral.act'].suspend_security().with_context(active_test=False)
            electoral_act_ids = ElectoralAct.search([
                ('date_since_consultation_control', '<=', fields.Date.today()),
                ('date_until_consultation_control', '>=', fields.Date.today())])
            domain = expression.AND([[('electoral_act_ids', 'in', electoral_act_ids.ids)], domain])
        return super(ONSCLegajoVoteRegistry, self).read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy
        )

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

    # debe recibir un json.dumps([('id', 'in', employee_ids)])
    default_electoral_act_ids_domain = fields.Char(
        string='Elecciones disponibles',
    )
    any_electoral_act_active = fields.Boolean(
        '¿Alguna Elección activa?',
        search='_search_any_electoral_act_active',
        store=False)

    create_uid = fields.Many2one('res.users', 'Creado por', index=True, readonly=True)

    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')

    @api.constrains("date")
    def _check_date(self):
        for record in self:
            if record.date > fields.Date.today():
                raise ValidationError(_("La Fecha del presentación debe ser menor o igual al día de hoy"))




    @api.onchange('date')
    def onchange_date(self):
        if self.date and self.date > fields.Date.today():
            self.date = False
            return warning_response(_(u"La Fecha de presentación debe ser menor o igual al día de hoy"))

    @api.onchange('date','electoral_act_ids')
    def onchange_date_electoral_act_ids(self):
        if self.date and self.electoral_act_ids:
            ElectoralAct = self.env['onsc.legajo.electoral.act'].suspend_security().with_context(active_test=False)
            electoral_act_ids = ElectoralAct.search([
                ('date_since_consultation_control', '<=', self.date),
                ('date_until_consultation_control', '>=', self.date),
                ('id', 'in', self.electoral_act_ids.ids)])
            if len(electoral_act_ids) < len(self.electoral_act_ids):
                raise ValidationError(_("Acto electoral fuera de fecha de presentación"))


    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self._context.get('is_from_menu', False):
            self.electoral_act_ids = [(5,)]

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
        is_iam_admin = self.user_has_groups('onsc_legajo.group_legajo_vote_control_administrar')
        is_valid_user = self.user_has_groups(
            'onsc_legajo.group_legajo_vote_control_administrar,onsc_legajo.group_legajo_vote_control_recursos_humanos_inciso,onsc_legajo.group_legajo_vote_control_recursos_humanos_ue')
        for record in self:
            if not self._context.get('restrict_user'):
                record.should_disable_form_edit = False
            else:
                is_iam_owner = self.env.user.id == record.create_uid.id
                should_disable_form_edit = not is_valid_user or not is_iam_owner
                record.should_disable_form_edit = not is_iam_admin and should_disable_form_edit

    def _get_domain_employee_ids(self):
        exp = self._get_expression_domain([('legajo_state', '=', 'active')], is_employee_model=True)
        return json.dumps(exp)

    def unlink(self):
        is_iam_superuser = self.user_has_groups('onsc_legajo.group_legajo_vote_control_administrar')
        if self._context.get('restrict_user') and not is_iam_superuser and self.filtered(
                lambda x: x.create_uid.id != self.env.user.id):
            raise ValidationError(_("No puede eliminar registros creados por otros Funcionarios"))
        return super(ONSCLegajoVoteRegistry, self).unlink()

    def action_save(self):
        self._send_notification()
        return True

    def _send_notification(self):
        template = self.env.ref('onsc_legajo.email_template_vote_registry')
        emailto = self.employee_id.partner_id.institutional_email or self.employee_id.partner_id.email
        template.send_mail(self.id, force_send=True, email_values={'email_to': emailto})
