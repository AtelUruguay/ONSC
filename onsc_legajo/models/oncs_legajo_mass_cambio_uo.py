# -*- coding:utf-8 -*-
import json

from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name

from odoo import fields, models, api, _, Command
from odoo.exceptions import ValidationError
from odoo import tools
from odoo.osv import expression


class ONSCLegajoMassCambioUO(models.Model):
    _name = 'onsc.legajo.mass.cambio.uo'
    _inherit = [
        # 'onsc.legajo.actions.common.data',
        # 'onsc.partner.common.data',
        'mail.thread',
        'mail.activity.mixin',
        'onsc.legajo.abstract.opbase.security'
    ]
    _description = 'Cambio Masivo de UO'
    _rec_name = 'name'

    @api.model
    def default_get(self, fields):
        res = super(ONSCLegajoMassCambioUO, self).default_get(fields)
        # is_group_administrator = self.user_has_groups('onsc_legajo.group_legajo_alta_vl_administrar_altas_vl')
        is_group_inciso = self._is_group_inciso_security()
        is_group_ue = self._is_group_ue_security()
        if is_group_inciso or is_group_ue:
            employee_contract = self.env.user.employee_id.job_id.contract_id
            res['inciso_id'] = employee_contract.inciso_id.id
            res['operating_unit_id'] = employee_contract.operating_unit_id.id
        return res

    def _is_group_inciso_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_mass_cambio_uo_recursos_humanos_inciso')

    def _is_group_ue_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_mass_cambio_uo_recursos_humanos_ue')

    def _get_domain(self, args):
        return super(ONSCLegajoMassCambioUO, self)._get_domain(args, user_partner=False)

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

    name = fields.Char(string='Nombre', compute='_compute_name', store=True)

    @api.constrains('start_date')
    def _check_start_date(self):
        for rec in self:
            if rec.start_date > fields.Date.today():
                raise ValidationError(
                    _("La fecha desde no puede ser mayor a la fecha actual"))

    @api.onchange('inciso_id')
    def _onchange_inciso_id(self):
        if self.operating_unit_id and self.operating_unit_id.inciso_id != self.inciso_id:
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

    @api.depends('inciso_id', 'operating_unit_id', 'state')
    def _compute_name(self):
        for rec in self:
            state_display = dict(self.fields_get(allfields=['state'])['state']['selection']).get(rec.state)
            rec.name = '%s-%s-%s' % (rec.inciso_id.name, rec.operating_unit_id.name, state_display)

    def unlink(self):
        if self.filtered(lambda x: x.state != 'draft'):
            raise ValidationError(
                _("Solo se pueden eliminar registros en estado borrador"))
        return super(ONSCLegajoMassCambioUO, self).unlink()

    def button_confirm(self):
        for rec in self:
            rec.line_ids.action_confirm()
        self.write({'state': 'confirm'})

    def button_clean(self):
        self.ensure_one()
        self.employee_id = False
        self.is_not_uo = False
        self.department_id = False
        self.line_ids.filtered(lambda x: not x.is_included).unlink()

    def button_search(self):
        self.ensure_one()
        self.line_ids.filtered(lambda x: not x.is_included).unlink()
        self._search_contracts()

    def button_select_all(self):
        self.line_ids.write({'is_included': True})

    def button_unselect_all(self):
        self.line_ids.write({'is_included': False})


    def _search_contracts(self):
        Line = self.env['onsc.legajo.mass.cambio.uo.line']
        default_security_job = self.env['onsc.legajo.security.job'].sudo().search([
            ('is_default_mass_change_uo', '=', True)
        ], limit=1)
        if self.employee_id:
            contracts = self._get_contracts(employee_id=self.employee_id.id)
        elif self.department_id:
            contracts = self._get_contracts(department_id=self.department_id.id)
        elif self.is_not_uo:
            contracts = self._get_contracts_sin_uo()
        else:
            contracts = self.env['hr.contract'].sudo()
        employee_in_line_ids = self.line_ids.mapped('employee_id').ids
        bulked_vals = []
        buked_vals_dict = {}
        for contract in contracts:
            if not isinstance(contract, dict):
                contract_id = contract.id
                employee_id = contract.employee_id.id
                legajo_state_id = contract.legajo_state_id.id
            else:
                contract_id = contract['contract_id']
                employee_id = contract['employee_id']
                legajo_state_id = contract['legajo_state_id']
            if employee_id not in employee_in_line_ids:
                if not buked_vals_dict.get(employee_id):
                    buked_vals_dict[employee_id] = {
                        'cambio_uo_id': self.id,
                        'employee_id': employee_id,
                        'department_id': self.department_id.id,
                        'target_department_id': self.target_department_id.id,
                        'start_date': self.start_date,
                        'security_job_id': default_security_job.id,
                        'contract_ids': [contract_id],
                        'legajo_state_id': legajo_state_id
                    }
                else:
                    buked_vals_dict[employee_id]['contract_ids'].append(contract_id)
        for vals in buked_vals_dict.values():
            if len(vals.get('contract_ids')) == 1:
                vals['contract_id'] = vals.get('contract_ids')[0]
            del vals['contract_ids']
            bulked_vals.append(vals)
        Line.create(bulked_vals)

    def _get_contracts(self, employee_id=None, department_id=None):
        args = [
            ("legajo_state", "in", ("incoming_commission", "active")),
            ('operating_unit_id', '=', self.operating_unit_id.id),
            ('employee_id', '!=', self.env.user.employee_id.id)
        ]
        if employee_id and not department_id:
            args.append(('employee_id', '=', employee_id))
            return self.env['hr.contract'].sudo().search(args)
        elif department_id:
            args = [
                ('contract_id.legajo_state', 'in', ('active', 'incoming_commission')),
                ('department_id', '=', department_id)
            ]
            if employee_id:
                args.append(('employee_id', '=', employee_id))
            return self.env['hr.job'].sudo().search(args).mapped('contract_id')
        else:
            return self.env['hr.contract'].sudo().search(args)

    def _get_contracts_sin_uo(self):
        _sql = """SELECT
    id, employee_id, legajo_state_id
FROM
    hr_contract
WHERE
    legajo_state in ('active', 'incoming_commission') AND
    operating_unit_id = %s AND
    id NOT IN (SELECT contract_id FROM hr_job WHERE operating_unit_id = %s AND (end_date IS NULL OR end_date >= CURRENT_DATE))""" % (
        self.operating_unit_id.id, self.operating_unit_id.id)
        self.env.cr.execute(_sql)
        results = self.env.cr.fetchall()
        contract_ids = []
        for result in results:
            contract_ids.append({'contract_id': result[0], 'employee_id': result[1], 'legajo_state_id': result[2]})
        return contract_ids

class ONSCLegajoMassCambioUOLine(models.Model):
    _name = 'onsc.legajo.mass.cambio.uo.line'

    cambio_uo_id = fields.Many2one(
        'onsc.legajo.mass.cambio.uo', 'Cambio de UO masivo')
    is_included = fields.Boolean(string='¿Incluido?')
    employee_id = fields.Many2one('hr.employee', 'C.I.')
    contract_id = fields.Many2one('hr.contract', 'Contrato')
    job_id = fields.Many2one('hr.job', 'Puesto', compute='_compute_job_info', store=True)
    department_id = fields.Many2one('hr.department', 'UO origen', compute='_compute_job_info', store=True)
    target_department_id = fields.Many2one('hr.department', 'UO destino')
    start_date = fields.Date(string='Fecha desde')
    security_job_id = fields.Many2one(
        "onsc.legajo.security.job", string="Seguridad de puesto")
    is_responsable_uo = fields.Boolean(string="¿Responsable de UO?")
    legajo_state_id = fields.Many2one(
        'onsc.legajo.res.country.department',
        string='Departamento donde desempeña funciones')
    op_cambio_uo_id = fields.Many2one(
        'onsc.legajo.cambio.uo',
        string='Cambio de UO')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirm', 'Confirmado'),
        ('error', 'Error')
    ], string='Estado', default='draft')
    error_message = fields.Char(string='Mensaje de error')

    is_contract_readonly = fields.Boolean(
        string='Contrats no editable', compute='_compute_contract_info')
    contract_id_domain = fields.Char(
        string="Dominio Contrato (interno)", compute='_compute_contract_info')

    @api.constrains('employee_id', 'target_department_id', 'is_responsable_uo', 'cambio_uo_id')
    def _constrains_is_responsable_uo(self):
        for rec in self:
            if rec.is_responsable_uo and self.search_count([
                ('is_responsable_uo', '=', True),
                ('target_department_id', '=', rec.target_department_id.id),
                ('employee_id', '=', rec.employee_id.id),
                ('cambio_uo_id', '=', rec.cambio_uo_id.id)
            ]) > 1:
                raise ValidationError('Solo puede haber un responsable de UO por cada UO destino')

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

    @api.depends('contract_id')
    def _compute_job_info(self):
        for rec in self:
            if rec.contract_id:
                jobs = rec.contract_id.job_ids.filtered(lambda x: x.end_date is False or x.end_date >= fields.Date.today())
                if len(jobs) >= 1:
                    rec.job_id = jobs[0].id
                    rec.department_id = jobs[0].department_id.id
                else:
                    rec.job_id = False
                    rec.department_id = False

    def action_confirm(self):
        CambioUO = self.env['onsc.legajo.cambio.uo'].suspend_security()
        for rec in self.filtered(lambda x: x.is_included and x.state == 'draft'):
            try:
                # Usamos un savepoint para aislar la operación completa
                with self._cr.savepoint():
                    vals = {
                        'inciso_id': rec.cambio_uo_id.inciso_id.id,
                        'operating_unit_id': rec.cambio_uo_id.operating_unit_id.id,
                        'employee_id': rec.employee_id.id,
                        'contract_id': rec.contract_id.id,
                        'department_id': rec.target_department_id.id,
                        'date_start': rec.start_date,
                        'security_job_id': rec.security_job_id.id,
                        'is_responsable_uo': rec.is_responsable_uo,
                        'legajo_state_id': rec.legajo_state_id.id,
                        'cv_birthdate': rec.employee_id.cv_birthdate,
                        'cv_sex': rec.employee_id.cv_sex,
                        'job_id': rec.job_id.id
                    }
                    if rec.cambio_uo_id.document_file:
                        vals['attached_document_discharge_ids'] = [(0, 0, {
                            'document_type_id': rec.cambio_uo_id.document_type_id.id,
                            'document_file': rec.cambio_uo_id.document_file,
                            'document_file_name': rec.cambio_uo_id.document_file_name,
                            'name': rec.cambio_uo_id.description
                        })]

                    # Crear el registro del cambio de unidad operativa
                    cambio_uo = CambioUO.create(vals)

                    try:
                        # Intentar confirmar el cambio de unidad operativa
                        cambio_uo.action_confirm()
                    except Exception as inner_e:
                        # Si falla, registramos el error pero mantenemos el registro creado
                        rec.write({
                            'state': 'error',
                            'error_message': f"Error en confirmación: {tools.ustr(inner_e)}",
                            'op_cambio_uo_id': cambio_uo.id  # Asociar el registro creado
                        })
                        continue  # Ir al siguiente registro

                    # Si todo funciona, marcamos el estado como confirmado
                    rec.write({'state': 'confirm', 'op_cambio_uo_id': cambio_uo.id, 'error_message': False})
            except Exception as outer_e:
                # Manejo de errores generales para el registro
                rec.write({'state': 'error', 'error_message': f"Error general: {tools.ustr(outer_e)}"})


    def button_open_cambio_uo(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'onsc.legajo.cambio.uo',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.op_cambio_uo_id.id,
            'target': 'current',
            'context': {'show_descriptors':True, 'is_from_menu': False},
            'views': [
                [self.env.ref('onsc_legajo.onsc_legajo_cambio_uo_form').id, 'form'],
            ]
        }
