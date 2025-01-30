# -*- coding:utf-8 -*-
import json

from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name

from odoo import fields, models, api, _, Command
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
    date_start = fields.Date(
        string="Fecha desde",
        required=True,
        copy=False)
    department_id = fields.Many2one("hr.department", string="UO")
    department_id_domain = fields.Char(string="Dominio Funcionario", compute='_compute_department_id_domain')
    job_id = fields.Many2one("hr.job", string="Puesto origen")
    job_id_domain = fields.Char(string="Dominio Puesto", compute='_compute_job_id_domain')
    show_job = fields.Boolean('Mostrar Puestos', compute='_compute_job_id_domain')

    security_job_id = fields.Many2one("onsc.legajo.security.job", string="Seguridad de puesto")
    security_job_id_domain = fields.Char(compute='_compute_security_job_id_domain')
    is_responsable_uo = fields.Boolean(string="¿Responsable de UO?")
    legajo_state_id = fields.Many2one(
        'onsc.legajo.res.country.department',
        string='Departamento donde desempeña funciones', copy=False)
    occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación')

    attached_document_discharge_ids = fields.One2many('onsc.legajo.attached.document', 'cambio_uo_id',
                                                      string='Documentos adjuntos')
    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')
    full_name = fields.Char('Nombre', compute='_compute_full_name')
    contract_id = fields.Many2one('hr.contract', 'Contrato', required=True, copy=False)
    contract_id_domain = fields.Char(string="Dominio Contrato (interno)", compute='_compute_contract_id_domain')
    is_regime_manager = fields.Boolean(string="¿Régimen tiene la marca 'Responsable UO'?", compute='_compute_is_regime_manager', store=True)
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
        user_level = self.env.user.employee_id.job_id.sequence
        for rec in self:
            domain = [('sequence', '>=', user_level)]
            rec.security_job_id_domain = json.dumps(domain)

    @api.depends('contract_id')
    def _compute_is_regime_manager(self):
        for rec in self:
            rec.is_regime_manager = rec.contract_id.regime_id.is_manager

    @api.constrains("date_start", "contract_id", "job_id")
    def _check_date(self):
        for record in self:
            if record.date_start > fields.Date.today():
                raise ValidationError(_("La fecha desde debe ser menor o igual a la fecha de registro"))
            if record.date_start and record.contract_id and record.date_start < record.contract_id.date_start:
                raise ValidationError(_("La fecha desde debe ser mayor o igual a la fecha de inicio del contrato"))
            if record.job_id and record.date_start < record.job_id.start_date:
                raise ValidationError(_("La fecha desde debe ser mayor o igual a la fecha del puesto actual"))

    @api.constrains("department_id", "job_id", "security_job_id", "legajo_state_id", "is_responsable_uo")
    def _check_department_id(self):
        for record in self:
            is_same_state_id = record.contract_id.legajo_state_id == record.legajo_state_id
            is_same_department = record.job_id.department_id == record.department_id
            is_same_manager = record.job_id.is_uo_manager == record.is_responsable_uo
            is_same_security = record.job_id.security_job_id == record.security_job_id and is_same_manager
            if is_same_state_id and is_same_department and is_same_security:
                raise ValidationError(_("Debe modificar la UO, la Seguridad o el Departamento donde desempeña funciones"))

    @api.constrains("security_job_id", "department_id", "date_start", "legajo_state", "is_responsable_uo")
    def _check_security_job_id(self):
        Job = self.env['hr.job'].sudo()
        for record in self:
            # SI ESTOY QUERIENDO MARCAR COMO RESPONSABLE Y YA EXISTE OTRO PUESTO CUMPLIENDO ESA FUNCION EN ESE DEPARTAMENTO TRANCAR
            # CHEQUEAR SOLAMENTE SI ESTOY HACIENDO MOVIMIENTO DE UO O SEGURIDAD()
            is_same_department = record.job_id.department_id == record.department_id
            is_same_manager = record.job_id.is_uo_manager == record.is_responsable_uo
            is_same_managersecurity = record.job_id.security_job_id == record.security_job_id and is_same_manager
            if (not is_same_department or not is_same_managersecurity) and record.is_responsable_uo and not Job.is_this_job_available_for_manager(
                    record.job_id,
                    record.department_id,
                    record.date_start):
                raise ValidationError(_("No se puede tener más de un responsable para la misma UO"))

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
        self.operating_unit_id = self.contract_id.operating_unit_id.id
        self.inciso_id = self.contract_id.inciso_id.id
        if len(job_ids) == 1:
            self.job_id = job_ids[0].id
            if job_ids[0].security_job_id.active:
                self.security_job_id = job_ids[0].security_job_id.id
            else:
                self.security_job_id = False
            self.department_id = job_ids[0].department_id.id
        else:
            self.job_id = False
            self.security_job_id = False
            self.department_id = False

    @api.onchange('contract_id')
    def onchange_contract_id(self):
        self.occupation_id = False
        self.security_job_id = False
        self.legajo_state_id = self.contract_id.legajo_state_id.id
        if not self.contract_id.regime_id.is_manager:
            self.is_responsable_uo = False

    @api.onchange('job_id')
    def onchange_job_id(self):
        self.is_responsable_uo = self.job_id.is_uo_manager

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
        self._validate_confirm()
        self.with_context(no_check_write=True)._action_confirm()

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
        self._check_date()
        if self.env.user.employee_id.id == self.employee_id.id:
            raise ValidationError(_("No se puede confirmar un traslado a si mismo"))

        if (self.department_id.id and not self.security_job_id.id) or (self.security_job_id.id and not self.department_id.id):
            raise ValidationError(_("Los valores de UO y Seguridad de puesto deben estar ambos vacíos o definidos. "
                                    "No se permite esa combinación con uno de los dos sin definir."))
        if not self.department_id and not self.security_job_id and not self.legajo_state_id:
            raise ValidationError(_("Si los valores de UO y Seguridad de puesto no están definidos "
                                    "al menos el Departamento donde desempeña funciones debe estar establecido."))
        self._check_security_job_id()
        self._check_role_assignment()

    def _check_role_assignment(self):
        JobRoleAssignment = self.env['onsc.legajo.job.role.assignment'].with_context(is_from_menu=False)
        # TODO solo debo chequear si estoy cambiando de UO o estoy cambiando el flag de Responsable
        for record in self:
            is_same_department = record.job_id.department_id == record.department_id
            is_same_manager = record.job_id.is_uo_manager == record.is_responsable_uo
            if (not is_same_manager or not is_same_department) and JobRoleAssignment.search_count([
                ('job_id', '=', record.job_id.id),
                '|', ('date_end', '=', False), ('date_end', '>=', fields.Date.today())
            ]):
                raise ValidationError(
                    _("El funcionario tiene una asignación de funciones vigente que no le permite realizar el cambio."
                      "Debe actualizar la situación de la asignación de función previo a esta acción."))

    def _action_confirm(self):
        self.ensure_one()
        Job = self.env['hr.job']
        warning_message = False
        show_warning = False
        is_change_department_id = self.job_id.department_id != self.department_id
        is_same_manager = self.job_id.is_uo_manager == self.is_responsable_uo
        is_change_security_job_id = self.job_id.security_job_id != self.security_job_id or not is_same_manager
        is_change_state_id = self.contract_id.legajo_state_id != self.legajo_state_id

        if is_change_department_id or is_change_security_job_id:
            job_role_assignment_values = self._get_job_role_assignment_values(
                self.job_id,
                self.date_start)
            if self.job_id.start_date == self.date_start:
                self.suspend_security().job_id.with_context(is_copy_job=True).deactivate(self.date_start)
                self.suspend_security().job_id.write({'active': False})
                show_warning = True
                warning_message = u"No pueden existir dos puestos activos para el mismo contrato, " \
                                  u"se inactivará el puesto anterior"
            else:
                self.suspend_security().job_id.with_context(is_copy_job=True).deactivate(
                    self.date_start - relativedelta(days=1))

            new_job = Job.suspend_security().with_context(is_copy_job=True).create_job(
                self.contract_id,
                self.department_id,
                self.date_start,
                self.security_job_id,
                is_uo_manager=self.is_responsable_uo,
                source_job=self.job_id,
            )
            if len(job_role_assignment_values):
                new_job.write({'role_assignment_ids': job_role_assignment_values})
        else:
            new_job = Job
        if is_change_state_id:
            self.contract_id.write({
                'legajo_state_id': self.legajo_state_id.id,
                'eff_date': fields.Date.today()
            })
        self.write({'state': 'confirmado', 'is_error_synchronization': show_warning,
                    'error_message_synchronization': warning_message})
        return new_job

    def _get_job_role_assignment_values(self, job, date_start):
        job_role_assignment_values = []
        for role_assignment_id in job.role_assignment_ids:
            if role_assignment_id.date_end is False or role_assignment_id.date_end > date_start:
                job_role_assignment_values.append(
                    Command.create({
                        'role_assignment_id': role_assignment_id.role_assignment_id.id,
                        'date_start': date_start,
                        'date_end': role_assignment_id.date_end,
                        'role_assignment_file': role_assignment_id.role_assignment_file,
                        'role_assignment_filename': role_assignment_id.role_assignment_filename
                    })
                )
        return job_role_assignment_values
