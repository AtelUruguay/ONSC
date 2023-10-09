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
        is_user_consulta = self.env.user.has_group('onsc_legajo.group_legajo_cambio_uo_consulta')
        is_user_administrar = self.env.user.has_group('onsc_legajo.group_legajo_cambio_uo_administrar')
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

    def _is_group_consulta_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_cambio_uo_consulta')

    def _is_group_responsable_uo_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_cambio_uo_responsable_uo')

    def _is_group_legajo_cambio_uo_administrar(self):
        return self.user_has_groups('onsc_legajo.group_legajo_cambio_uo_administrar')

    def _get_domain(self, args, filter_by_departments=False):
        args = super(ONSCLegajoCambioUO, self)._get_domain(args, use_employee=True)
        not_abstract_security = not self._is_group_inciso_security() and not self._is_group_ue_security() and not self._is_group_legajo_cambio_uo_administrar()
        if not_abstract_security and self._is_group_responsable_uo_security():
            Job = self.env['hr.job'].sudo()
            department_ids = self.get_uo_tree()
            if filter_by_departments:
                args = expression.AND([[
                    ('department_id', 'in', department_ids)
                ], args])
            else:
                job_ids = Job.with_context(active_test=False).search([('department_id', 'in', department_ids)]).ids
                args = expression.AND([[
                    ('job_id', 'in', job_ids)
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
        Job = self.env['hr.job'].sudo()
        result = super(ONSCLegajoCambioUO, self).read(fields, load)
        for item in result:
            if item.get('employee_id'):
                employee_id = item['employee_id'][0]
                item['employee_id'] = (item['employee_id'][0], Employee.browse(employee_id)._custom_display_name())
            if item.get('job_id'):
                job_id = item['job_id'][0]
                item['job_id'] = (item['job_id'][0], Job.browse(job_id)._custom_display_name())
        return result

    employee_id = fields.Many2one("hr.employee", string="Funcionario")
    employee_id_domain = fields.Char(string="Dominio Funcionario", compute='_compute_employee_id_domain')
    date_start = fields.Date(string="Fecha desde", default=lambda *a: fields.Date.today(), required=True, copy=False)

    department_id = fields.Many2one("hr.department", string="UO")
    department_id_domain = fields.Char(string="Dominio Funcionario", compute='_compute_department_id_domain')
    job_id = fields.Many2one("hr.job", string="Puesto origen")
    job_id_domain = fields.Char(string="Dominio Puesto", compute='_compute_job_id_domain')
    show_job = fields.Boolean('Mostrar Puestos', compute='_compute_job_id_domain')

    security_job_id = fields.Many2one("onsc.legajo.security.job", string="Seguridad de puesto")
    security_job_id_domain = fields.Char(compute='_compute_security_job_id_domain')
    occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación')

    attached_document_discharge_ids = fields.One2many('onsc.legajo.attached.document', 'cambio_uo_id',
                                                      string='Documentos adjuntos')
    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')
    full_name = fields.Char('Nombre', compute='_compute_full_name')
    contract_id = fields.Many2one('hr.contract', 'Contrato', required=True, copy=False)
    contract_id_domain = fields.Char(string="Dominio Contrato", compute='_compute_contract_id_domain')
    show_contract = fields.Boolean('Mostrar contrato', compute='_compute_contract_id_domain')

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

    @api.depends('state')
    def _compute_should_disable_form_edit(self):
        is_consulta = self.user_has_groups('onsc_legajo.group_legajo_cambio_uo_consulta')
        is_superior = self.user_has_groups(
            'onsc_legajo.group_legajo_cambio_uo_recursos_humanos_inciso,onsc_legajo.group_legajo_cambio_uo_recursos_humanos_ue,onsc_legajo.group_legajo_cambio_uo_responsable_uo,onsc_legajo.group_legajo_cambio_uo_administrar')
        for record in self:
            is_only_consulta = is_consulta and not is_superior
            record.should_disable_form_edit = record.state not in ['borrador'] or is_only_consulta

    @api.depends('cv_emissor_country_id')
    def _compute_employee_id_domain(self):
        for rec in self:
            rec.employee_id_domain = self._get_domain_employee_ids()

    @api.depends('employee_id')
    def _compute_contract_id_domain(self):
        for rec in self:
            if rec.employee_id:
                contracts = rec._get_contracts()
                rec.show_contract = len(contracts) > 1
                rec.contract_id_domain = json.dumps([('id', 'in', contracts.ids)])
            else:
                rec.show_contract = False
                rec.contract_id_domain = json.dumps([('id', 'in', [])])

    @api.depends('contract_id')
    def _compute_job_id_domain(self):
        is_responsable_uo = self._is_group_responsable_uo_security()
        department_ids = self.get_uo_tree()
        for rec in self:
            if is_responsable_uo:
                job_ids = rec.contract_id.job_ids.filtered(lambda x:
                                                           x.end_date is False
                                                           or x.end_date >= fields.Date.today()
                                                           and x.department_id.id in department_ids)
            else:
                job_ids = rec.contract_id.job_ids.filtered(
                    lambda x: x.end_date is False or x.end_date >= fields.Date.today())
            rec.job_id_domain = json.dumps([('id', 'in', job_ids.ids)])
            rec.show_job = len(job_ids) > 1

    @api.depends('contract_id')
    def _compute_department_id_domain(self):
        for rec in self:
            rec.department_id_domain = json.dumps([('id', 'in', self.get_uo_tree(rec.contract_id))])

    @api.depends('contract_id')
    def _compute_security_job_id_domain(self):
        for rec in self:
            if not rec.contract_id.regime_id.is_manager:
                domain = [('is_uo_manager', '=', False)]
            else:
                domain = [('is_uo_manager', 'in', [True, False])]
            rec.security_job_id_domain = json.dumps(domain)

    @api.constrains("date_start", "contract_id", "job_id")
    def _check_date(self):
        for record in self:
            if record.date_start > fields.Date.today():
                raise ValidationError(_("La fecha desde debe ser menor o igual a la fecha de registro"))
            if record.date_start and record.contract_id and record.date_start < record.contract_id.date_start:
                raise ValidationError(_("La fecha desde debe ser mayor o igual a la fecha de inicio del contrato"))
            if record.job_id and record.date_start < record.job_id.start_date:
                raise ValidationError(_("La fecha desde debe ser mayor o igual a la fecha del puesto actual"))

    @api.constrains("department_id", "job_id", "security_job_id")
    def _check_department_id(self):
        for record in self:
            is_same_department = record.job_id and record.job_id.department_id == record.department_id
            if record.job_id and is_same_department and record.job_id.security_job_id == record.security_job_id:
                raise ValidationError(_("Si el cambio es dentro de la misma UO no debería ser con "
                                        "la misma Seguridad de puesto"))

    @api.constrains("security_job_id", "department_id", "date_start", "legajo_state")
    def _check_security_job_id(self):
        Job = self.env['hr.job'].sudo()
        for record in self:
            if not Job.is_job_available_for_manager(record.department_id,
                                                    record.security_job_id,
                                                    record.date_start):
                raise ValidationError(_("No se puede tener mas de un responsable para la misma UO "))

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

    @api.onchange('contract_id')
    def onchange_department_id_contract_id(self):
        if self._is_group_responsable_uo_security():
            department_ids = self.get_uo_tree()
            job_ids = self.contract_id.job_ids.filtered(lambda x:
                                                        x.end_date is False
                                                        or x.end_date >= fields.Date.today()
                                                        and x.department_id.id in department_ids)
        else:
            job_ids = self.contract_id.job_ids.filtered(
                lambda x: x.end_date is False or x.end_date >= fields.Date.today())
        if len(job_ids) == 1:
            self.job_id = job_ids[0].id
        else:
            self.job_id = False

    @api.onchange('contract_id')
    def onchange_contract_id(self):
        self.occupation_id = False
        self.security_job_id = False

    def unlink(self):
        if self.filtered(lambda x: x.state != 'borrador'):
            raise ValidationError(_("Solo se pueden eliminar registros en estado borrador"))
        return super(ONSCLegajoCambioUO, self).unlink()

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
            department_ids = Department.search(['|', ('id', 'child_of', department_id),
                                                ('id', '=', department_id)]).ids
        return department_ids

    def _get_domain_employee_ids(self):
        if self._is_group_inciso_security() or self._is_group_ue_security() or self._is_group_consulta_security() \
                or self._is_group_legajo_cambio_uo_administrar():
            args = self._get_domain([("legajo_state", "in", ('active', 'incoming_commission'))],
                                    filter_by_departments=True)
            employee_ids = self.env['hr.contract'].sudo().search(args).mapped('employee_id').ids
        elif self._is_group_responsable_uo_security():
            department_ids = self.get_uo_tree()
            employee_ids = self.env['hr.job'].search([
                ('contract_id.legajo_state', 'in', ('active', 'incoming_commission')),
                ('department_id', 'in', department_ids),
                '|',
                ('end_date', '=', False),
                ('end_date', '>=', fields.Date.today()),
            ]).mapped('employee_id').ids
        else:
            employee_ids = []
        return json.dumps([('id', 'in', employee_ids), ('id', '!=', self.env.user.employee_id.id)])

    def _get_contracts(self):
        if self._is_group_inciso_security() or self._is_group_ue_security() or self._is_group_consulta_security() \
                or self._is_group_legajo_cambio_uo_administrar():
            args = [
                ("legajo_state", "in", ("incoming_commission", "active")),
                ('employee_id', '=', self.employee_id.id)
            ]
            return self.env['hr.contract'].search(self._get_domain(args))
        elif self._is_group_responsable_uo_security():
            department_ids = self.get_uo_tree()
            return self.env['hr.job'].search([
                ('employee_id', '=', self.employee_id.id),
                ('contract_id.legajo_state', 'in', ('active', 'incoming_commission')),
                ('department_id', 'in', department_ids)]).mapped('contract_id')
        else:
            return self.env['hr.contract']

    def action_confirm(self):
        self.ensure_one()
        Job = self.env['hr.job']
        self._validate_confirm()
        self.contract_id.suspend_security().write({'eff_date': self.date_start, 'occupation_id': self.occupation_id.id})
        warning_message = False
        show_warning = False
        if self.job_id.start_date == self.date_start:
            self.suspend_security().job_id.deactivate(self.date_start)
            self.suspend_security().job_id.write({'active': False})
            show_warning = True
            warning_message = u"No pueden existir dos puestos activos para el mismo contrato, " \
                              u"se inactivará el puesto anterior"
        else:
            self.suspend_security().job_id.deactivate(self.date_start - relativedelta(days=1))
        Job.suspend_security().create_job(self.contract_id,
                                          self.department_id,
                                          self.date_start,
                                          self.security_job_id)
        self.write({'state': 'confirmado', 'is_error_synchronization': show_warning,
                    'error_message_synchronization': warning_message})

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
        self._check_security_job_id()
        if self.env.user.employee_id.id == self.employee_id.id:
            raise ValidationError(_("No se puede confirmar un traslado a si mismo"))

        for required_field in ['department_id', 'security_job_id', 'occupation_id']:
            if not eval('self.%s' % required_field):
                message.append(self._fields[required_field].string)

        if message:
            fields_str = '\n'.join(message)
            message = 'Información faltante o no cumple validación:\n \n%s' % fields_str
            raise ValidationError(_(message))
