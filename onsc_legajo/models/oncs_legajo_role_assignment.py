# -*- coding:utf-8 -*-
import json

from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


class ONSCLegajoJobRoleAssignment(models.Model):
    _name = 'onsc.legajo.job.role.assignment'
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
    ]

    job_id = fields.Many2one("hr.job", string="Puesto", tracking=True)
    role_assignment_id = fields.Many2one(
        "onsc.legajo.role.assignment",
        string="Asignación de funciones",
        copy=False,
        tracking=True
    )
    date_start = fields.Date(string="Fecha de inicio", required=True, copy=False, tracking=True)
    date_end = fields.Date(string="Fecha de fin", copy=False, tracking=True)
    role_assignment_mecanism = fields.Selection(
        string='Mecanismo de asignación de funciones',
        selection=[('concurso', 'Concurso'), ('direct', 'Asignación directa'), ('other', 'Otros')],
        copy=False,
        tracking=True
    )
    role_assignment_file = fields.Binary(string="Documento digitalizado", tracking=True, copy=False)
    role_assignment_filename = fields.Char('Nombre del documento digitalizado', copy=False)

    def button_show_role_assignment_action(self):
        action = self.env.ref('onsc_legajo.onsc_legajo_show_role_assignment_action').suspend_security()
        action.res_id = self.role_assignment_id.id
        return action.read()[0]


class ONSCLegajoRoleAssignment(models.Model):
    _name = 'onsc.legajo.role.assignment'

    _inherit = [
        'onsc.legajo.abstract.opbase.security',
        'onsc.partner.common.data',
        'onsc.legajo.job.role.assignment'
    ]
    _description = 'Asignación de funciones'
    _rec_name = 'full_name'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ONSCLegajoRoleAssignment, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                                    toolbar=toolbar,
                                                                    submenu=submenu)
        doc = etree.XML(res['arch'])
        is_user_consulta = self.env.user.has_group('onsc_legajo.group_legajo_role_assignment_consulta')
        is_user_administrar = self.env.user.has_group('onsc_legajo.group_legajo_role_assignment_administrar')
        if view_type in ['form', 'tree', 'kanban'] and is_user_consulta and not is_user_administrar:
            for node_form in doc.xpath("//%s" % (view_type)):
                node_form.set('create', '0')
                node_form.set('edit', '0')
                node_form.set('copy', '0')
                node_form.set('delete', '0')
        res['arch'] = etree.tostring(doc)
        return res

    def _is_group_inciso_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_role_assignment_recursos_humanos_inciso')

    def _is_group_ue_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_role_assignment_recursos_humanos_ue')

    def _is_group_consulta_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_role_assignment_consulta')

    def _is_group_responsable_uo_security(self):
        return False

    def _is_group_legajo_role_assignment_administrar(self):
        return self.user_has_groups('onsc_legajo.group_legajo_role_assignment_administrar')

    def _get_domain(self, args):
        args = super(ONSCLegajoRoleAssignment, self)._get_domain(args, use_employee=True)
        return args

    @api.model
    def default_get(self, fields):
        res = super(ONSCLegajoRoleAssignment, self).default_get(fields)
        res['cv_emissor_country_id'] = self.env.ref('base.uy').id
        res['cv_document_type_id'] = self.env['onsc.cv.document.type'].sudo().search([('code', '=', 'ci')], limit=1).id
        return res

    def read(self, fields=None, load="_classic_read"):
        Employee = self.env['hr.employee'].sudo()
        Job = self.env['hr.job'].sudo()
        result = super(ONSCLegajoRoleAssignment, self).read(fields, load)
        for item in result:
            if item.get('employee_id'):
                employee_id = item['employee_id'][0]
                item['employee_id'] = (item['employee_id'][0], Employee.browse(employee_id)._custom_display_name())
            if item.get('job_id'):
                job_id = item['job_id'][0]
                item['job_id'] = (item['job_id'][0], Job.browse(job_id)._custom_display_name())
        return result

    employee_id = fields.Many2one("hr.employee", string="Funcionario", tracking=True, required=True)
    employee_id_domain = fields.Char(string="Dominio Funcionario", compute='_compute_employee_id_domain')

    contract_id = fields.Many2one(
        'hr.contract',
        'Contrato',
        required=True,
        copy=False,
        tracking=True,
    )
    contract_id_domain = fields.Char(string="Dominio Contrato", compute='_compute_contract_id_domain')
    show_contract = fields.Boolean('Mostrar contrato', compute='_compute_contract_id_domain')

    # job_id = fields.Many2one("hr.job", string="Puesto", tracking=True)
    job_id_domain = fields.Char(string="Dominio Puesto", compute='_compute_job_id_domain')
    show_job = fields.Boolean('Mostrar Puestos', compute='_compute_job_id_domain')

    inciso_id = fields.Many2one('onsc.catalog.inciso', related='job_id.inciso_id', store=True)
    operating_unit_id = fields.Many2one("operating.unit", related='job_id.operating_unit_id', store=True)
    department_id = fields.Many2one("hr.department", string="UO", related='job_id.department_id', store=True)

    job_security_job_id = fields.Many2one(
        "onsc.legajo.security.job",
        string="Seguridad de puesto del Puesto",
        related='job_id.security_job_id',
        store=True
    )
    security_job_id = fields.Many2one("onsc.legajo.security.job", string="Seguridad de puesto", tracking=True)
    security_job_id_domain = fields.Char(compute='_compute_security_job_id_domain')

    is_uo_manager = fields.Boolean(string='¿Es responsable de UO?', default=True)

    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')

    state = fields.Selection(
        string='Estado',
        selection=[('draft', 'Borrador'), ('confirm', 'Confirmado'), ('end', 'Finalizado'), ],
        default='draft',
        tracking=True
    )

    job_role_assignment_ids = fields.One2many(
        'onsc.legajo.job.role.assignment',
        'role_assignment_id',
        string='Asignaciones de funciones en el Puesto'
    )

    is_end_notified = fields.Boolean(string='Ya fué notificado el estado finalizado')
    is_other_role_assignment_active = fields.Boolean(
        string='¿Hay otra asignación de roles activa?',
        compute='_compute_is_other_role_assignment_active',
        store=True
    )
    full_name = fields.Char('Nombre', compute='_compute_full_name')

    # ES NECESARIO?
    # department_id_domain = fields.Char(string="Dominio Funcionario", compute='_compute_department_id_domain')
    # state_id = fields.Many2one(
    #     'res.country.state',
    #     string='Departamento donde desempeña funciones',
    #     domain="[('country_id.code','=','UY')]", copy=False)
    # occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación')
    # attached_document_discharge_ids = fields.One2many('onsc.legajo.attached.document', 'cambio_uo_id',
    #                                                   string='Documentos adjuntos')

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
        is_consulta = self.user_has_groups('onsc_legajo.group_legajo_role_assignment_consulta')
        is_superior = self.user_has_groups(
            'onsc_legajo.group_legajo_role_assignment_recursos_humanos_inciso,onsc_legajo.group_legajo_role_assignment_recursos_humanos_ue,onsc_legajo.group_legajo_role_assignment_administrar')
        for record in self:
            is_only_consulta = is_consulta and not is_superior
            record.should_disable_form_edit = record.state in ['end'] or is_only_consulta

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

    @api.depends('job_id', 'date_start', 'date_end')
    def _compute_is_other_role_assignment_active(self):
        for rec in self:
            args = [
                ('state', '!=', 'draft'),
                ('job_id', '=', rec.job_id.id),
                ('date_start', '<=', fields.Date.today()),
                '|', ('date_end', '=', False), ('date_end', '>=', fields.Date.today()),
            ]
            if isinstance(rec.id, int):
                args = expression.AND([[
                    ('id', '!=', rec.id)
                ], args])
            rec.is_other_role_assignment_active = self.search_count(args)

    # @api.depends('contract_id')
    # def _compute_department_id_domain(self):
    #     for rec in self:
    #         rec.department_id_domain = json.dumps([('id', 'in', self.get_uo_tree(rec.contract_id))])

    @api.depends('contract_id')
    def _compute_security_job_id_domain(self):
        user_level = self.env.user.employee_id.job_id.sequence
        for rec in self:
            domain = [('sequence', '>=', user_level)]
            rec.security_job_id_domain = json.dumps(domain)

    @api.constrains("date_start", "contract_id", "job_id", "date_end")
    def _check_date(self):
        if self._context.get('no_check_write'):
            return True
        for record in self:
            if record.job_id and record.date_start < record.job_id.start_date:
                raise ValidationError(_("La fecha desde debe ser mayor o igual a la fecha del puesto actual"))
            if record.date_end and record.date_start > record.date_end:
                raise ValidationError(_("La fecha de inicio debe ser menor o igual a la fecha de fin"))
            if record.date_start > fields.Date.today():
                raise ValidationError(_("La fecha desde debe ser menor o igual a la fecha de registro"))
            yesterdary = fields.Date.today() - relativedelta(days=1)
            if record.date_end and record.date_end < yesterdary:
                raise ValidationError(_("La fecha de fin debe ser mayor o igual a ayer!"))

    @api.constrains("security_job_id", "department_id", "date_start", "legajo_state", "job_id")
    def _check_security_job_id(self):
        if self._context.get('no_check_write'):
            return True
        Job = self.env['hr.job'].sudo()
        for record in self:
            if not record.job_id:
                raise ValidationError(_("No se ha identificado un Puesto para ese Funcionario en ese Contrato"))
            if record.security_job_id and not record.is_uo_manager:
                raise ValidationError(_("La Seguridad de puesto debe ser de Responsable de UO"))
            isnt_same_security = (record.security_job_id != record.job_id.security_job_id or not record.job_id.is_uo_manager)
            if record.security_job_id and isnt_same_security and not Job.is_job_available_for_manager(
                    record.department_id, record.date_start, nro_doc=True):
                raise ValidationError(_("No se puede tener más de un responsable para la misma UO"))

    @api.constrains("security_job_id", "department_id", "date_start", "legajo_state", "job_id")
    def _check_is_other_role_assignment_active(self):
        JobRoleAssignment = self.env['onsc.legajo.job.role.assignment'].sudo()
        for record in self:
            if JobRoleAssignment.search_count([
                ('job_id', '=', record.job_id.id),
                '|', ('date_end', '=', False), ('date_end', '>=', fields.Date.today())
            ]):
                raise ValidationError(
                    _("El funcionario tiene una Asignación de función activa para dicho Vínculo laboral"))
            if JobRoleAssignment.search_count([
                ('job_id', '=', record.job_id.id),
                ('date_start', '<=', record.date_start),
                ('date_end', '>=', record.date_start)
            ]):
                raise ValidationError(
                    _("Fecha de inicio no permitida. "
                      "Ya existe una Asignación de función con un período que la comprende"))

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
        if len(job_ids) == 1:
            self.job_id = job_ids[0].id
            if job_ids[0].is_uo_manager:
                self.security_job_id = job_ids[0].security_job_id.id
        else:
            self.job_id = False
            self.security_job_id = False

    @api.onchange('contract_id')
    def onchange_contract_id(self):
        self.security_job_id = False

    @api.model
    def create(self, values):
        new_record = super().create(values)
        if new_record.date_end and new_record.date_end < fields.Date.today():
            new_record.action_end(send_notification=False)
        return new_record

    def write(self, values):
        result = super().write(values)
        if len(self) and 'date_end' in values:
            ws7_operation = self._context.get('ws7_operation', False)
            if values.get('date_end') and fields.Date.from_string(values.get('date_end')) < fields.Date.today():
                if ws7_operation:
                    self._message_log(body=_('Se finaliza la Asignación de funciones por notificación de %s' % (ws7_operation)))
                self.action_end()
            elif ws7_operation:
                self.write({'state': 'end'})
                self._message_log(body=_('Se finaliza la Asignación de funciones por notificación de %s' % (ws7_operation)))
                self._update_job_role_assignments_date_end()
            else:
                self._update_job_role_assignments_date_end()
        return result

    def unlink(self):
        if self.filtered(lambda x: x.state != 'draft'):
            raise ValidationError(_("Solo se pueden eliminar registros en estado Borrador"))
        return super(ONSCLegajoRoleAssignment, self).unlink()

    def action_confirm(self):
        self.ensure_one()
        self._validate_confirm()
        # TODO MISMO PUESTO ES MISMA SEGURIDAD Y QUE EL PUESTO TENGA LA MARCA DE RESPONSABLE DE UO
        if self.job_security_job_id == self.security_job_id and self.job_id.is_uo_manager:
            self.suspend_security()._create_job_role_assignment(self.job_id)
        else:
            self.suspend_security()._copy_job_and_create_job_role_assignment()
        self.write({'state': 'confirm'})

    def _update_job_role_assignments_date_end(self):
        if len(self.job_role_assignment_ids) > 1:
            last_job_role_assignment = self.job_role_assignment_ids.sorted(key=lambda x: x.date_start, reverse=True)[0]
        else:
            last_job_role_assignment = self.job_role_assignment_ids
        ws7_operation = self._context.get('ws7_operation', False)
        if ws7_operation:
            last_job_role_assignment.job_id._message_log(
                body=_('Se finaliza la Asignación de funciones por notificación de %s' % (ws7_operation)))
        # for job_role_assignment_id in self.job_role_assignment_ids.sorted(key=lambda x: x.date_end, reverse=True):
        cond1 = not last_job_role_assignment.date_end or last_job_role_assignment.date_end != self.date_end
        cond2 = last_job_role_assignment.date_end and not self.date_end
        if cond1 or cond2:
            last_job_role_assignment.with_context(no_check_write=True).write({
                'date_end': self.date_end
            })

    def _copy_job_and_create_job_role_assignment(self):
        Job = self.env['hr.job']
        self.job_id.suspend_security().with_context(no_check_write=True, is_copy_job=True).deactivate(
            self.date_start - relativedelta(days=1))
        new_job = Job.suspend_security().with_context(no_check_write=True, is_copy_job=True).create_job(
            self.contract_id,
            self.department_id,
            self.date_start,
            self.security_job_id,
            is_uo_manager=True,
            source_job=self.job_id
        )
        self._create_job_role_assignment(new_job)
        return new_job

    def _create_job_role_assignment(self, job_id):
        self.ensure_one()
        JobRoleAssignment = self.env['onsc.legajo.job.role.assignment'].suspend_security()
        JobRoleAssignment.create({
            'job_id': job_id.id,
            'role_assignment_id': self.id,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'role_assignment_mecanism': self.role_assignment_mecanism,
            'role_assignment_file': self.role_assignment_file,
            'role_assignment_filename': self.role_assignment_filename,
        })

    def action_end(self, send_notification=True):
        if send_notification:
            email_template_id = self.env.ref('onsc_legajo.email_template_af_end_records')
            for record in self:
                email_template_id.send_mail(record.id)
        self._update_job_role_assignments_date_end()
        self.write({'state': 'end', 'is_end_notified': True})

    def process_end_records(self):
        records = self.search([
            ('state', 'in', ['confirm', 'end']),
            ('is_end_notified', '=', False),
            ('date_end', '<', fields.Date.today()),
        ])
        email_template_id = self.env.ref('onsc_legajo.email_template_af_end_records')
        for record in records:
            email_template_id.send_mail(record.id)
        records.write({'state': 'end', 'is_end_notified': True})

    def _validate_confirm(self):
        message = []
        self._check_date()
        self._check_security_job_id()
        self._check_is_other_role_assignment_active()
        for required_field in ['employee_id', 'contract_id', 'date_start', 'role_assignment_mecanism',
                               'role_assignment_file', 'security_job_id']:
            if not eval('self.%s' % required_field):
                message.append(self._fields[required_field].string)
        if message:
            fields_str = '\n'.join(message)
            message = 'Información faltante o no cumple validación:\n \n%s' % fields_str
            raise ValidationError(_(message))
        if self.job_id.end_date and self.job_id.end_date < fields.Date.today():
            raise ValidationError(_("El Puesto asociado al Vínculo no se encuentra activo"))

    def get_uo_tree(self, contract=False):
        Department = self.env['hr.department'].sudo()
        department_ids = []
        if self.user_has_groups('onsc_legajo.group_legajo_role_assignment_recursos_humanos_inciso') or \
                self.user_has_groups('onsc_legajo.group_legajo_role_assignment_recursos_humanos_ue') or \
                self.user_has_groups('onsc_legajo.group_legajo_role_assignment_administrar'):
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
        return department_ids

    def _get_domain_employee_ids(self):
        if self._is_group_inciso_security() or self._is_group_ue_security() or self._is_group_consulta_security() \
                or self._is_group_legajo_role_assignment_administrar():
            args = self._get_domain([
                ("legajo_state", "in", ('active', 'incoming_commission')), ('regime_id.is_public_employee', '=', True)])
            employee_ids = self.env['hr.contract'].sudo().search(args).mapped('employee_id').ids
        elif self._is_group_responsable_uo_security():
            department_ids = self.get_uo_tree()
            employee_ids = self.env['hr.job'].search([
                ('contract_id.legajo_state', 'in', ('active', 'incoming_commission')),
                ('regime_id.is_public_employee', '=', True),
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
                or self._is_group_legajo_role_assignment_administrar():
            args = [
                ("legajo_state", "in", ("incoming_commission", "active")),
                ('regime_id.is_public_employee', '=', True),
                ('employee_id', '=', self.employee_id.id)
            ]
            return self.env['hr.contract'].search(self._get_domain(args))
        elif self._is_group_responsable_uo_security():
            department_ids = self.get_uo_tree()
            return self.env['hr.job'].search([
                ('employee_id', '=', self.employee_id.id),
                ('regime_id.is_public_employee', '=', True),
                ('contract_id.legajo_state', 'in', ('active', 'incoming_commission')),
                ('department_id', 'in', department_ids)]).mapped('contract_id')
        else:
            return self.env['hr.contract']

    def get_followers_mails(self):
        return self.message_follower_ids.mapped('partner_id').get_onsc_mails()
