# -*- coding:utf-8 -*-
import json

from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as warning_response

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


class ONSCLegajoCambioUO(models.Model):
    _name = 'onsc.legajo.cambio.uo'
    _inherit = [
        'onsc.legajo.actions.common.data',
        'onsc.partner.common.data',
        'mail.thread',
        'mail.activity.mixin',
        'onsc.legajo.abstract.opbase.security'
    ]
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

    def _is_group_inciso_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_cambio_uo_recursos_humanos_inciso')

    def _is_group_ue_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_cambio_uo_recursos_humanos_ue')

    def _is_group_responsable_uo_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_cambio_uo_recursos_humanos_ue')

    def _get_domain(self, args):
        args = super(ONSCLegajoCambioUO, self)._get_domain(args)
        if not self._is_group_inciso_security() and not self._is_group_ue_security() and self._is_group_responsable_uo_security():
            Department = self.env['hr.department'].sudo()
            department_id = self.env.user.employee_id.job_id.department_id.id
            department_ids = Department.search(['|', ('id', 'child_of', department_id),
                                                ('id', '=', department_id)])
            employees = department_ids.jobs_ids.mapped('employee_id')
            args = expression.AND([[
                ('employee_id', '=', employees.ids)
            ], args])
        return args

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
    show_contract = fields.Boolean('Show Contract', compute='_compute_contract_id_domain')

    @api.constrains("date_start", "contract_id")
    def _check_date(self):
        for record in self:
            if record.date_start > fields.Date.today():
                raise ValidationError(_("La fecha desde debe ser menor o igual a la fecha de registro"))
            if record.date_start and record.contract_id and record.date_start < record.contract_id.date_start:
                raise ValidationError(_("La fecha desde debe ser mayor o igual a la fecha de inicio del contrato"))
            if len(record.contract_id.job_ids) > 1:
                last_job = record.contract_id.job_ids.sorted(key=lambda x: x.date_end, reverse=True)[0]
                if record.job_ids and record.date_start < last_job.start_date:
                    raise ValidationError(
                        _("La fecha desde debe ser mayor o igual a la fecha de inicio del último puesto"))

    @api.constrains("department_id", "contract_id")
    def _check_department_id(self):
        for record in self:
            if record.department_id.id == record.contract_id.job_ids.filtered(
                    lambda x: x.end_date is False).department_id.id:
                raise ValidationError(_("La UO destino tiene que ser distinta a la actual"))

    @api.constrains("security_job_id", "department_id", "date_start", "legajo_state")
    def _check_security_job_id(self):
        Job = self.env['hr.job'].sudo()
        for record in self:
            if not Job.is_job_available_for_manager(record.department_id,
                                                    record.security_job_id,
                                                    record.date_start):
                raise ValidationError(_("No se puede tener mas de un responsable para la misma UO "))

    @api.depends('state')
    def _compute_should_disable_form_edit(self):
        for record in self:
            record.should_disable_form_edit = record.state not in ['borrador'] or self.user_has_groups(
                'onsc_legajo.group_legajo_cambio_uo_consulta')

    @api.depends('cv_emissor_country_id')
    def _compute_employee_id_domain(self):
        for rec in self:
            rec.employee_id_domain = self._get_domain_employee_ids()

    @api.depends('contract_id')
    def _compute_department_id_domain(self):
        for rec in self:
            rec.department_id_domain = json.dumps([('id', 'in', self.get_uo_tree(rec.contract_id))])

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
                contracts = rec._get_contracts()
                rec.show_contract = len(contracts) > 1
                rec.contract_id_domain = json.dumps([('id', 'in', contracts.ids)])
            else:
                rec.show_contract = False
                rec.contract_id_domain = json.dumps([('id', 'in', [])])

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        for record in self.sudo():
            if record.employee_id:
                contracts = record._get_contracts()
                record.cv_birthdate = record.employee_id.cv_birthdate
                record.cv_sex = record.employee_id.cv_sex
                record.contract_id = contracts and contracts[0].id or False
            else:
                record.cv_birthdate = False
                record.cv_sex = False
                record.contract_id = False

    @api.onchange('department_id')
    def onchange_department_id(self):
        self.operating_unit_id = self.department_id.operating_unit_id.id
        self.inciso_id = self.department_id.inciso_id.id

    def get_uo_tree(self, contract=False):
        Department = self.env['hr.department'].sudo()
        department_ids = []
        if self.user_has_groups('onsc_legajo.group_legajo_cambio_uo_recursos_humanos_inciso') or \
                self.user_has_groups('onsc_legajo.group_legajo_cambio_uo_recursos_humanos_ue') or \
                self.user_has_groups('onsc_legajo.group_legajo_cambio_uo_administrar'):
            contract_id = contract or self.env.user.employee_id.job_id.contract_id
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
            department_ids = Department.search(args).ids
        elif self.user_has_groups('onsc_legajo.group_legajo_cambio_uo_responsable_uo'):
            department_id = self.env.user.employee_id.job_id.department_id.id
            # if contract and contract.job_ids.filtered(lambda x: x.end_date is False):
            #     id_department = contract.job_ids.filtered(lambda x: x.end_date is False).department_id.id
            # _department_id = id_department and id_department or self.env.user.employee_id.job_id.contract_id.job_ids.filtered(
            #     lambda x: x.end_date is False).department_id.id
            department_ids = Department.search(['|', ('id', 'child_of', department_id),
                                                ('id', '=', department_id)]).ids
        return department_ids

    def _get_domain_employee_ids(self):
        args = self._get_domain([("legajo_state", "in", ('active', 'incoming_commission'))])
        employees = self.env['hr.contract'].sudo().search(args).mapped('employee_id')
        return json.dumps([('id', 'in', employees.ids)])

    def _get_contracts(self):
        Contract = self.env['hr.contract']
        args = [("legajo_state", "in", ("incoming_commission", "active")),
                ('employee_id', '=', self.employee_id.id)]
        return Contract.search(self._get_domain(args))

    def action_confirm(self):
        self.ensure_one()
        Job = self.env['hr.job']
        self._validate_confirm()
        self.contract_id.suspend_security().write({'eff_date': self.date_start, 'occupation_id': self.occupation_id.id})
        job = self.contract_id.suspend_security().job_ids.filtered(lambda x: x.end_date is False)
        notify = False
        if job.start_date == self.date_start:
            job.deactivate({'end_date': self.date_start})
            notify = True
        else:
            job.deactivate({'end_date': self.date_start - relativedelta(days=1)})
        Job.suspend_security().create_job(self.contract_id,
                                          self.department_id,
                                          self.date_start,
                                          self.security_job_id)
        self.write({'state': 'confirmado'})
        if notify:
            return warning_response(
                _(u"No pueden existir dos puestos activos para el mismo contrato, se inactivará el puesto anterior"))

    def action_show_organigram(self):
        return {
            'type': 'ir.actions.client',
            'target': 'current',
            'tag': 'organization_dashboard',
            'params': {
                'title': 'Organigrama',
                'operating_unit_id': self.department_id.operating_unit_id.id,
                'department_id': self.department_id.id,
                'short_name': False,
                'responsible': True,
                'end_date': fields.Date.today(),
                'inciso': self.department_id.operating_unit_id.inciso_id.display_name,
                'ue': self.department_id.operating_unit_id.display_name,
            },
        }

    def _validate_confirm(self):
        message = []
        self._check_date()
        if self.env.user.employee_id.id == self.employee_id.id:
            raise ValidationError(_("No se puede confirmar un traslado a si mismo"))

        for required_field in ['department_id', 'security_job_id', 'occupation_id']:
            if not eval('self.%s' % required_field):
                message.append(self._fields[required_field].string)

        if message:
            fields_str = '\n'.join(message)
            message = 'Información faltante o no cumple validación:\n \n%s' % fields_str
            raise ValidationError(_(message))

    def unlink(self):
        if self.filtered(lambda x: x.state != 'borrador'):
            raise ValidationError(_("Solo se pueden eliminar registros en estado borrador"))
        return super(ONSCLegajoCambioUO, self).unlink()
