# -*- coding:utf-8 -*-
import json

from lxml import etree

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name


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
        is_responsable= self.env.user.has_group('onsc_legajo.group_legajo_cambio_uo_responsable_uo')
        if view_type in ['search'] and not is_responsable:

            for node_form in doc.xpath("//filter[@name='mis_subordinados']"):
                node_form.getparent().remove(node_form)
        res['arch'] = etree.tostring(doc)
        return res

    def _get_domain(self, args):
        args = expression.AND([[
            ('employee_id', '!=', self.env.user.employee_id.id)
        ], args])

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
            # contract_id = self.env.user.employee_id.job_id.contract_id
            # department_id = contract_id.job_ids.filtered(lambda x: x.end_date is False)
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
        res['cv_document_type_id'] = self.env['onsc.cv.document.type'].sudo().search([('code', '=', 'ci')],
                                                                                     limit=1).id or False
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

    subordinados_directos = fields.Boolean('Busqueda por subordinados directos', search='_search_subordinados_directos',
                                           store=False)
    hr_departmen_ids = []


    def _search_subordinados_directos(self, operator, operand):
        subordinados_result = self.env.user.employee_id.obtener_subordinados()
        subordinados_ids = subordinados_result['subordinados_directos_ids']
        if not subordinados_ids:
            return [('id', '=', '0')]
        return [('employee_id', 'in', subordinados_ids)]


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
            rec.department_id_domain = self._domain_uo_ids()

    @api.depends('employee_id')
    def _compute_full_name(self):
        for record in self:
            record.full_name = record.employee_id.cv_nro_doc + ' - ' + calc_full_name(
                record.employee_id.cv_first_name, record.employee_id.cv_second_name,
                record.employee_id.cv_last_name_1,
                record.employee_id.cv_last_name_2) + ' - ' + record.date_start.strftime('%Y%m%d')

    @api.model
    def _domain_uo_ids(self):
        self.get_uo_hijas( self.env.user.employee_id.department_id)
        self.department_ids = []
        ids = []
        uo_hijas = self.env['hr.department'].search([('id', 'in', self.hr_departmen_ids)])
        for uo in uo_hijas:
            ids.append(uo.id)
        return ids

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        for record in self.sudo():
            if record.employee_id:
                record.cv_birthdate = record.employee_id.cv_birthdate
                record.cv_sex =record.employee_id.cv_sex

    def get_uo_hijas(self, department):
        hijas = self.env['hr.department'].search([('parent_id', '=', department.id)])
        if hijas:
            self.hr_departmen_ids.append(department.id)
            for hija in hijas:
                self.get_uo_hijas(hija)
        else:
            self.hr_departmen_ids.append(department.id)

    def _get_domain_employee_ids(self):
        args = [("legajo_state", "=", 'active')]
        args = self._get_domain(args)

        employees = self.env['hr.contract'].search(args).mapped('employee_id')
        if employees:
            return json.dumps([('id', 'in', employees.ids)])
        else:
            return json.dumps([('id', '=', False)])


    def action_confirm(self):
        self.write({'state': 'confirmado'})

    def unlink(self):
        if self.filtered(lambda x: x.state != 'borrador'):
            raise ValidationError(_("Solo se pueden eliminar registros en estado borrador"))
        return super(ONSCLegajoCambioUO, self).unlink()
