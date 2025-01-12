# -*- coding:utf-8 -*-
import json

from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name

from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError
from odoo.osv import expression


class ONSCLegajoMassCambioUO(models.Model):
    _name = 'onsc.legajo.mass.cambio.uo'
    _inherit = [
        # 'onsc.legajo.actions.common.data',
        # 'onsc.partner.common.data',
        'mail.thread',
        'mail.activity.mixin',
        # 'onsc.legajo.abstract.opbase.security'
    ]
    _description = 'Cambio Masivo de UO'

    @api.model
    def _get_default_inciso_id(self):
        if self.user_has_groups('onsc_legajo.group_legajo_mass_cambio_uo_recursos_humanos_ue') or \
                self.user_has_groups('onsc_legajo.group_legajo_mass_cambio_uo_recursos_humanos_inciso'):
            return self.env.user.employee_id.job_id.contract_id.inciso_id
        return False

    @api.model
    def _get_default_ue_id(self):
        if self.user_has_groups('onsc_legajo.group_legajo_mass_cambio_uo_recursos_humanos_ue'):
            return self.env.user.employee_id.job_id.contract_id.operating_unit_id
        return False

    inciso_id = fields.Many2one(
        'onsc.catalog.inciso',
        string='Inciso',
        required=True,
        default=lambda self: self._get_default_inciso_id(),
        copy=False)
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Unidad ejecutora origen",
        required=True,
        default=lambda self: self._get_default_ue_id(),
        copy=False)
    employee_id = fields.Many2one('hr.employee', 'C.I.', copy=False)
    department_id = fields.Many2one(
        "hr.department", string="UO de origen", copy=False)
    is_not_uo = fields.Boolean(string='Sin UO')

    target_department_id = fields.Many2one(
        "hr.department", string="UO destino", required=True, copy=False)
    start_date = fields.Date(string='Fecha desde',
                             required=True, default=fields.Date.today)
    state = fields.Selection(
        string='Estado',
        selection=[('draft', 'Borrador'), ('confirm', 'Confirmado')],
        default='draft',
    )
    description = fields.Char(string='Descripción')
    document_type_id = fields.Many2one(
        'onsc.legajo.document.type', 'Tipo de documento')
    document_file = fields.Binary('Archivo')
    document_file_name = fields.Char('Nombre del archivo')

    line_ids = fields.One2many(
        'onsc.legajo.mass.cambio.uo.line', 'cambio_uo_id', string='Líneas')

    is_inciso_readonly = fields.Boolean(compute="_compute_is_readonly")
    is_operating_unit_readonly = fields.Boolean(compute="_compute_is_readonly")
    employee_id_domain = fields.Char(
        string="Dominio Funcionario (interno)", compute='_compute_employee_id_domain')
    operating_unit_id_domain = fields.Char(
        compute='_compute_operating_unit_id_domain')
    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')

    @api.constrains('start_date')
    def _check_start_date(self):
        for rec in self:
            if rec.start_date > fields.Date.today():
                raise ValidationError(
                    _("La fecha desde no puede ser mayor a la fecha actual"))

    @api.onchange('inciso_id')
    def _onchange_inciso_id(self):
        self.operating_unit_id = False

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        self.department_id = False
        self.employee_id = False

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.department_id = False
        if self.employee_id and self.is_not_uo:
            self.is_not_uo = False

    @api.onchange('department_id')
    def _onchange_department_id(self):
        if self.department_id:
            self.is_not_uo = False
            self.employee_id = False

    @api.onchange('is_not_uo')
    def _onchange_is_not_uo(self):
        if self.is_not_uo:
            self.department_id = False
            self.employee_id = False

    @api.depends('state')
    def _compute_should_disable_form_edit(self):
        is_consulta = self.user_has_groups(
            'onsc_legajo.group_legajo_mass_cambio_uo_consulta')
        is_superior = self.user_has_groups(
            'onsc_legajo.group_legajo_mass_cambio_uo_recursos_humanos_inciso,onsc_legajo.group_legajo_mass_cambio_uo_recursos_humanos_ue')
        for record in self:
            is_only_consulta = is_consulta and not is_superior
            record.should_disable_form_edit = record.state not in [
                'draft'] or is_only_consulta

    @api.depends('inciso_id')
    def _compute_operating_unit_id_domain(self):
        # contract = self.env.user.employee_id.job_id.contract_id
        for rec in self:
            domain = [('inciso_id', '=', rec.inciso_id.id)]
            rec.operating_unit_id_domain = json.dumps(domain)

    @api.depends('inciso_id')
    def _compute_is_readonly(self):
        is_inciso_readonly = True
        is_operating_unit_readonly = self.user_has_groups(
            'onsc_legajo.group_legajo_mass_cambio_uo_recursos_humanos_ue') and not self.user_has_groups(
            'onsc_legajo.group_legajo_mass_cambio_uo_recursos_humanos_inciso')
        for rec in self:
            rec.is_inciso_readonly = is_inciso_readonly
            rec.is_operating_unit_readonly = is_operating_unit_readonly

    @api.depends('operating_unit_id')
    def _compute_employee_id_domain(self):
        for rec in self:
            if rec.operating_unit_id:
                contracts = rec._get_contracts()
                rec.employee_id_domain = json.dumps(
                    [('id', 'in', contracts.mapped('employee_id').ids)])
            else:
                rec.employee_id_domain = json.dumps([('id', 'in', [])])

    def unlink(self):
        if self.filtered(lambda x: x.state != 'draft'):
            raise ValidationError(
                _("Solo se pueden eliminar registros en estado borrador"))
        return super(ONSCLegajoMassCambioUO, self).unlink()

    def button_confirm(self):
        self.write({'state': 'confirm'})

    def button_search(self):
        self.ensure_one()
        self.line_ids.filtered(lambda x: not x.is_included).unlink()
        self._search_contracts()

    def _search_contracts(self):
        Line = self.env['onsc.legajo.mass.cambio.uo.line']
        default_security_job = self.env['onsc.legajo.security.job'].sudo().search([
            ('is_default_mass_change_uo', '=', True)
        ], limit=1)
        if self.employee_id:
            contracts = self._get_contracts(employee_id=self.employee_id.id)
        elif self.department_id:
            contracts = self._get_contracts(department_id=self.department_id.id)
        for contract in contracts:
            vals = {
                'cambio_uo_id': self.id,
                'employee_id': self.employee_id.id,
                'department_id': self.department_id.id,
                'target_department_id': self.target_department_id.id,
                'start_date': self.start_date,
                'security_job_id': default_security_job.id,
                'contract_id': contract.id,
            }
            Line.create(vals)

    def button_clean(self):
        self.ensure_one()
        self.employee_id = False
        self.is_not_uo = False
        self.department_id = False

    def _get_contracts(self, employee_id=None, department_id=None):
        # if self._is_group_inciso_security() or self._is_group_ue_security() or self._is_group_consulta_security() \
        #         or self._is_group_legajo_cambio_uo_administrar():
        args = [
            ("legajo_state", "in", ("incoming_commission", "active")),
            ('operating_unit_id', '=', self.operating_unit_id.id)
        ]
        if employee_id:
            args.append(('employee_id', '=', employee_id))
        if department_id:
            args.append(('department_id', '=', department_id))
        return self.env['hr.contract'].search(args)
        # elif self._is_group_responsable_uo_security():
        #     department_ids = self.get_uo_tree()
        #     return self.env['hr.job'].search([
        #         ('employee_id', '=', self.employee_id.id),
        #         ('contract_id.legajo_state', 'in', ('active', 'incoming_commission')),
        #         ('department_id', 'in', department_ids)]).mapped('contract_id')
        # else:
        #     return self.env['hr.contract']


class ONSCLegajoMassCambioUOLine(models.Model):
    _name = 'onsc.legajo.mass.cambio.uo.line'

    cambio_uo_id = fields.Many2one(
        'onsc.legajo.mass.cambio.uo', 'Cambio de UO masivo')
    is_included = fields.Boolean(string='¿Incluido en el cambio?')
    employee_id = fields.Many2one('hr.employee', 'C.I.')
    contract_id = fields.Many2one('hr.contract', 'Contrato')
    department_id = fields.Many2one('hr.department', 'UO origen')
    target_department_id = fields.Many2one('hr.department', 'UO destino')
    start_date = fields.Date(string='Fecha desde')
    security_job_id = fields.Many2one(
        "onsc.legajo.security.job", string="Seguridad de puesto")
    is_responsable_uo = fields.Boolean(string="¿Responsable de UO?")
    legajo_state_id = fields.Many2one(
        'onsc.legajo.res.country.department',
        string='Departamento donde desempeña funciones')

    is_contract_readonly = fields.Boolean(
        string='Contrats no editable', compute='_compute_contract_info')
    contract_id_domain = fields.Char(
        string="Dominio Contrato (interno)", compute='_compute_contract_info')

    @api.constrains('employee_id', 'target_department_id', 'is_responsable_uo')
    def _constrains_is_responsable_uo(self):
        for rec in self:
            if rec.is_responsable_uo and self.search_count([
                ('is_responsable_uo', '=', True),
                ('target_department_id', '=', rec.target_department_id.id),
                ('employee_id', '=', rec.employee_id.id)
                ]) > 1:
                raise ValidationError(
                    'Solo puede haber un responsable de UO por cada UO destino')

    @api.depends('employee_id', 'cambio_uo_id')
    def _compute_contract_info(self):
        for rec in self:
            if rec.employee_id and rec.cambio_uo_id:
                contracts = rec.cambio_uo_id._get_contracts(employee_id=rec.employee_id.id)
                rec.is_contract_readonly = len(contracts) == 1
                rec.contract_id_domain = json.dumps(
                    [('id', 'in', contracts.ids)])
            else:
                rec.is_contract_readonly = False
                rec.contract_id_domain = json.dumps([('id', 'in', [])])
