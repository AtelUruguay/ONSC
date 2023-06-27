# -*- coding:utf-8 -*-
import json

from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


class ONSCLegajoCambioUO(models.Model):
    _name = 'onsc.legajo.cambio.uo'
    _inherit = ['onsc.legajo.actions.common.data', 'onsc.partner.common.data', 'mail.thread', 'mail.activity.mixin']
    _description = 'Cambio UO'
    _rec_name = 'full_name'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ONSCLegajoCambioUO, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                              submenu=submenu)
        doc = etree.XML(res['arch'])
        is_user_consulta = self.env.user.has_group('onsc_legajo.group_legajo__cambio_uo_consulta')
        is_user_administrar = self.env.user.has_group('onsc_legajo.group_legajo_baja_vl_administrar_bajas')
        is_responsable = self.env.user.has_group('onsc_legajo.group_legajo_cambio_uo_responsable_uo')
        if view_type in ['form', 'tree', 'kanban'] and is_user_consulta and not is_user_administrar:
            for node_form in doc.xpath("//%s" % (view_type)):
                node_form.set('create', '0')
                node_form.set('edit', '0')
                node_form.set('copy', '0')
                node_form.set('delete', '0')
        if view_type in ['search'] and not is_responsable:
            for node_form in doc.xpath("//filter[@name='mi_uo']"):
                node_form.getparent().remove(node_form)
        res['arch'] = etree.tostring(doc)
        return res

    def _get_domain(self, args):
        if self.user_has_groups('onsc_legajo.group_legajo_cambio_uo_recursos_humanos_inciso'):
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
            if inciso_id:
                args = expression.AND([[
                    ('inciso_id', '=', inciso_id.id)
                ], args])
        elif self.user_has_groups('onsc_legajo.group_legajo_cambio_uo_recursos_humanos_ue'):
            contract_id = self.env.user.employee_id.job_id.contract_id
            inciso_id = contract_id.inciso_id
            operating_unit_id = contract_id.operating_unit_id
            if inciso_id:
                args = expression.AND([[
                    ('inciso_id', '=', inciso_id.id)
                ], args])
            if operating_unit_id:
                args = expression.AND([[
                    ('operating_unit_id', '=', operating_unit_id.id)
                ], args])
        elif self.user_has_groups('onsc_legajo.group_legajo_cambio_uo_responsable_uo'):
            Employees = self.env.user.employee_id.obtener_subordinados()
            if Employees:
                args = expression.AND([[
                    ('employee_id', '=', Employees.ids)
                ], args])
        return args

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_menu'):
            args = self._get_domain(args)
        return super(ONSCLegajoCambioUO, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                       access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu'):
            domain = self._get_domain(domain)
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.model
    def default_get(self, fields):
        res = super(ONSCLegajoCambioUO, self).default_get(fields)
        res['cv_emissor_country_id'] = self.env.ref('base.uy').id
        res['cv_document_type_id'] = self.env['onsc.cv.document.type'].sudo().search([('code', '=', 'ci')], limit=1).id
        return res

    def read(self, fields=None, load="_classic_read"):
        Employee = self.env['hr.employee'].sudo()
        result = super(ONSCLegajoCambioUO, self).read(fields, load)
        for item in result:
            if item.get('employee_id'):
                employee_id = item['employee_id'][0]
                item['employee_id'] = (item['employee_id'][0], Employee.browse(employee_id)._custom_display_name())
        return result

    employee_id = fields.Many2one("hr.employee", string="Funcionario")
    employee_id_domain = fields.Char(string="Dominio Funcionario", compute='_compute_employee_id_domain')
    date_start = fields.Date(string="Fecha desde", default=lambda *a: fields.Date.today(), required=True, copy=False)

    department_id = fields.Many2one("hr.department", string="UO")
    department_id_domain = fields.Char(string="Dominio Funcionario", compute='_compute_department_id_domain')
    security_job_id = fields.Many2one("onsc.legajo.security.job", string="Seguridad de puesto")
    occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación')

    attached_document_discharge_ids = fields.One2many('onsc.legajo.attached.document', 'cambio_uo_id',
                                                      string='Documentos adjuntos')
    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')
    full_name = fields.Char('Nombre', compute='_compute_full_name')
    contract_id = fields.Many2one('hr.contract', 'Contrato', required=True, copy=False)
    contract_id_domain = fields.Char(string="Dominio Contrato", compute='_compute_contract_id_domain')
    show_contract = fields.Boolean('Show Contract')
    department_ids = []

    @api.constrains("date_start")
    def _check_date(self):
        for record in self:
            if record.date_start > fields.Date.today():
                raise ValidationError(_("La fecha desde debe ser menor o igual a la fecha de registro"))

    @api.depends('state')
    def _compute_should_disable_form_edit(self):
        for record in self:
            record.should_disable_form_edit = record.state not in ['borrador']

    @api.depends('cv_emissor_country_id')
    def _compute_employee_id_domain(self):
        for rec in self:
            rec.employee_id_domain = self._get_domain_employee_ids()

    @api.depends('employee_id')
    def _compute_department_id_domain(self):
        for rec in self:
            rec.department_id_domain = self._get_domain_uo_ids()

    @api.depends('employee_id')
    def _compute_full_name(self):
        for record in self:
            record.full_name = '%s-%s-%s' % (
                record.employee_id.cv_nro_doc,
                calc_full_name(
                    record.employee_id.cv_first_name, record.employee_id.cv_second_name,
                    record.employee_id.cv_last_name_1,
                    record.employee_id.cv_last_name_2),
                record.date_start.strftime('%Y%m%d'))

    @api.depends('employee_id')
    def _compute_contract_id_domain(self):
        Contract = self.env['hr.contract']
        for rec in self:
            if rec.employee_id:
                args = self._get_domain([
                    ("legajo_state", "in", ("incoming_commission", "active")),
                    ('employee_id', '=', rec.employee_id.id)
                ])
                contract = Contract.search(args)
                rec.show_contract = len(contract) > 1
                rec.contract_id_domain = json.dumps([('id', 'in', contract.ids)])
            else:
                rec.show_contract = False
                rec.contract_id_domain = json.dumps([('id', 'in', [])])

    @api.model
    def _get_domain_uo_ids(self):
        self.department_ids.clear()
        self.get_uo_hijas()
        ids = []
        uo_hijas = self.env['hr.department'].search([('id', 'in', self.department_ids)])
        for uo in uo_hijas:
            ids.append(uo.id)
        return json.dumps([('id', 'in', ids)])

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        for record in self.sudo():
            if record.employee_id:
                record.cv_birthdate = record.employee_id.cv_birthdate
                record.cv_sex = record.employee_id.cv_sex

    @api.onchange('department_id')
    def onchange_department_id(self):
        self.operating_unit_id = self.department_id.operating_unit_id.id
        self.inciso_id = self.department_id.inciso_id.id

    def get_uo_hijas(self, department=False):
        if self.user_has_groups('onsc_legajo.group_legajo_cambio_uo_recursos_humanos_inciso'):
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
            if inciso_id:
                Uos = self.env['hr.department'].sudo().search([('inciso_id', '=', inciso_id.id)])
                if Uos:
                    self.department_ids.append(department.id)
                    for uo in Uos:
                        self.department_ids.append(uo.id)

        elif self.user_has_groups('onsc_legajo.group_legajo_cambio_uo_recursos_humanos_ue'):
            contract_id = self.env.user.employee_id.job_id.contract_id
            inciso_id = contract_id.inciso_id
            operating_unit_id = contract_id.operating_unit_id
            args = []
            if inciso_id:
                args = expression.AND([[
                    ('inciso_id', '=', inciso_id.id)
                ], args])
            if operating_unit_id:
                args = expression.AND([[
                    ('operating_unit_id', '=', operating_unit_id.id)
                ], args])

            UOs = self.env['hr.department'].sudo().search(args)
            if UOs:
                for uo in UOs:
                    self.department_ids.append(uo.id)

        elif self.user_has_groups('onsc_legajo.group_legajo_cambio_uo_responsable_uo'):
            if not department:
                hijas = self.env['hr.department'].sudo().search(
                    [('parent_id', '=', self.env.user.employee_id.job_id.department_id.id)])
                self.department_ids.append(self.env.user.employee_id.job_id.department_id.id)
            else:
                hijas = self.env['hr.department'].sudo().search(
                    [('parent_id', '=', department.id)])
                self.department_ids.append(department.id)

            if hijas:
                for hija in hijas:
                    self.get_uo_hijas(hija)
            else:
                self.department_ids.append(department.id)

    def _get_domain_employee_ids(self):
        args = self._get_domain([("legajo_state", "in", ('active', 'incoming_commission'))])
        employees = self.env['hr.contract'].sudo().search(args).mapped('employee_id')
        return json.dumps([('id', 'in', employees.ids)])

    def action_confirm(self):
        self.ensure_one()
        Job = self.env['hr.job']

        if self.env.user.employee_id.id == self.employee_id.id:
            raise ValidationError(_("No se puede confirmar un traslado a si mismo"))
        if self.security_job_id.is_uo_manager:
            if self.env['hr.job'].sudo().search_count([
                ('department_id', '=', self.department_id.id),
                ('security_job_id', '=', self.security_job_id.id)
            ]) > 1:
                raise ValidationError(_("No se puede tener mas de un responsable para la misma UO "))
        self.contract_id.suspend_security().write({'eff_date': self.date_start, 'occupation_id': self.occupation_id.id})
        self.contract_id.suspend_security().job_ids.filtered(lambda x: x.end_date is False).write(
            {'end_date': self.date_start - relativedelta(days=1)})
        Job.suspend_security().create_job(self.contract_id, self.department_id,
                                          self.date_start, self.security_job_id)

        self.write({'state': 'confirmado'})

    def unlink(self):
        if self.filtered(lambda x: x.state != 'borrador'):
            raise ValidationError(_("Solo se pueden eliminar registros en estado borrador"))
        return super(ONSCLegajoCambioUO, self).unlink()
