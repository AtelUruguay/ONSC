# -*- coding: utf-8 -*-
import json
import logging

from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as warning_response

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class HrJob(models.Model):
    _inherit = 'hr.job'
    _order = 'start_date desc'

    def init(self):
        self._cr.execute("""CREATE INDEX IF NOT EXISTS hr_job_employee_id ON hr_job (employee_id)""")
        self._cr.execute("""CREATE INDEX IF NOT EXISTS hr_job_contract_id ON hr_job (contract_id)""")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        result = super(HrJob, self).name_search(name, args=args, operator=operator, limit=limit)
        if self._context.get('show_employee_as_display_name', False):
            by_employee_domain = [('employee_id.name', operator, name)]
            by_employee_domain += args
            by_employee = self.search(by_employee_domain, limit=limit)
            result = list(set(result + by_employee.name_get()))
        return result

    def name_get(self):
        res = []
        for record in self:
            if self._context.get('custom_display_name', False):
                _custom_name = record._custom_display_name()
            elif self._context.get('show_employee_as_display_name', False):
                _custom_name = record.employee_id.display_name
            else:
                _custom_name = record.name
            res.append((record.id, _custom_name))
        return res

    def _custom_display_name(self):
        return 'UO Origen: %s, Seg de puesto: %s ' % (
            self.department_id.display_name,
            self.security_job_id.display_name)

    security_job_id = fields.Many2one(
        "onsc.legajo.security.job",
        string="Seguridad de puesto",
        ondelete='restrict',
        tracking=True
    )
    legajo_id = fields.Many2one(
        'onsc.legajo',
        string='Legajo',
        related='contract_id.legajo_id',
        store=True,
        index=True
    )
    inciso_id = fields.Many2one(
        'onsc.catalog.inciso',
        string='Inciso',
        related='contract_id.inciso_id',
        store=True,
        index=True
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Unidad ejecutora",
        related='contract_id.operating_unit_id',
        store=True,
        index=True
    )
    is_readonly = fields.Boolean(string="Solo lectura", compute="_compute_is_readonly")
    role_extra_is_readonly = fields.Boolean(string="Solo lectura", compute="_compute_is_readonly")
    department_id_domain = fields.Char(compute='_compute_department_domain')
    legajo_state = fields.Selection(
        [('active', 'Activo'), ('egresed', 'Egresado')],
        string='Estado del funcionario',
        related='contract_id.legajo_id.legajo_state',
        store=True
    )
    # ASIGNACION DE FUNCIONES
    role_assignment_ids = fields.One2many(
        'onsc.legajo.job.role.assignment',
        'job_id',
        string='Asignaciones de funciones'
    )
    is_uo_manager = fields.Boolean(string='¿Es responsable de UO?')
    sequence = fields.Integer(string="Nivel", compute='_compute_sequence', store=True)

    _sql_constraints = [
        ('name_company_uniq', 'unique(1=1)',
         'The name of the job position must be unique per department in company!'),
    ]

    @api.depends('contract_id')
    def _compute_department_domain(self):
        UOs = self.env['hr.department']
        for rec in self:
            uos = UOs.search([('operating_unit_id', '=', rec.contract_id.operating_unit_id.id)])
            rec.department_id_domain = json.dumps([('id', 'in', uos.ids)])

    def _compute_is_readonly(self):
        for record in self:
            # readonly si la fecha end_date es menor a la fecha actual
            record.is_readonly = not self.user_has_groups('onsc_legajo.group_legajo_configurador_puesto')
            record.role_extra_is_readonly = not self.user_has_groups(
                'onsc_legajo.group_legajo_configurador_puesto') and record.end_date and record.end_date <= fields.Date.today()

    #
    # def _compute_is_role_assignment_admin(self):
    #     for record in self:
    #         record.is_role_assignment_admin = self.user_has_groups('onsc_legajo.group_legajo_role_assignment_administrar')
    @api.depends('role_ids', 'role_ids.user_role_id.sequence', 'role_extra_ids', 'role_extra_ids.user_role_id.sequence')
    def _compute_sequence(self):
        today = fields.Date.today()
        for rec in self:
            role_list = rec.role_ids.filtered(
                lambda r: r.active and r.start_date <= today and (r.end_date is False or r.end_date >= today)) | rec.role_extra_ids.filtered(
                lambda r: r.active and r.start_date <= today and (r.end_date is False or r.end_date >= today))
            rec.sequence = role_list and role_list.sorted(key=lambda line: line.user_role_id.sequence)[0].user_role_id.sequence

    @api.constrains("contract_id", "start_date", "end_date")
    def _check_date_range_into_contract(self):
        if self._context.get('no_check_date_range'):
            return True
        for record in self:
            if record.start_date < record.contract_id.date_start:
                raise ValidationError(_("La fecha desde está fuera del rango de fechas del contrato"))
            if record.contract_id.active and record.end_date and record.contract_id.date_end and record.end_date > record.contract_id.date_end:
                raise ValidationError(_("La fecha hasta está fuera del rango de fechas del contrato"))

    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.start_date = False
            return warning_response(_(u"La fecha desde no puede ser mayor que la fecha hasta"))
        self.role_ids.start_date = self.start_date
        self.role_extra_ids.filtered(
            lambda x: x.start_date is False or x.start_date < self.start_date).start_date = self.start_date

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            self.end_date = False
            return warning_response(_(u"La fecha hasta no puede ser menor que la fecha desde"))
        self.role_ids.end_date = self.end_date
        if self.end_date:
            self.role_extra_ids.filtered(
                lambda x: x.end_date is False or x.end_date > self.end_date).end_date = self.end_date

    @api.onchange('security_job_id')
    def onchange_security_job_id(self):
        _role_ids = [(5, 0)]
        manager_roles_ids = []
        if self.is_uo_manager:
            manager_roles = self.env['res.users.role'].sudo().search([('is_uo_manager', '=', True)])
            manager_roles_ids = manager_roles.ids
            _role_ids.extend([
                (0, 0, {
                    'user_role_id': role.id,
                    'type': 'system',
                    'start_date': self.start_date if self.start_date else fields.Date.today(),
                    'end_date': self.end_date
                })
                for role in
                manager_roles])
        if self.security_job_id:
            for role in self.security_job_id.user_role_ids:
                if role.id not in manager_roles_ids:
                    _role_ids.append((0, 0, {
                        'user_role_id': role.id,
                        'type': 'system',
                        'start_date': self.start_date if self.start_date else fields.Date.today(),
                        'end_date': self.end_date
                    }))
        self.role_ids = _role_ids

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.contract_id = False
        self.department_id = False

    @api.onchange('contract_id')
    def onchange_contract_id(self):
        self.department_id = False

    def write(self, values):
        for modified_field in ['department_id', 'security_job_id']:
            if modified_field in values:
                self.contract_id.notify_sgh = True
        return super(HrJob, self.suspend_security()).write(values)

    def get_available_jobs(self, user=False):
        """
        Devuelve los puestos activos del funcionario asociado el usuario logueado
        :param user: Recordser de res.users
        :return: Recordset de hr.job
        """
        today = fields.Date.today()
        user = user or self.env.user
        employee_ids = user.employee_ids.ids
        return self.search([
            '&', ('employee_id', 'in', employee_ids.ids),
            '&', ('start_date', '<=', today), '|', ('end_date', '>=', today), ('end_date', '=', False)])

    def get_active_jobs_in_hierarchy(self, user=False, force_same_uo=False):
        """
        Devuelve los puestos activos de la estructura asociada el usuario logueado
        :param user: Recordser de res.users
        :param force_same_uo: Boolean. Si es True busca hasta el tercer nivel (UO), si es False busca hasta el segundo nivel (UE)
        :return: Recordset de hr.job
        """
        today = fields.Date.today()
        user = user or self.env.user
        job_id = user.employee_id.job_id
        if force_same_uo:
            base_args = [('department_id', '=', job_id.department_id.id)]
        else:
            base_args = [('contract_id.operating_unit_id', '=', job_id.contract_id.operating_unit_id.id)]
        args = expression.AND([base_args, ['&', ('start_date', '<=', today),
                                           '|', ('end_date', '>=', today), ('end_date', '=', False)]])
        return self.sudo().search(args)

    def button_open_current_job(self):
        ctx = self.env.context.copy()
        ctx.update({'edit': True})
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': self._name,
            'name': 'Editar puesto',
            'context': ctx,
            "target": "current",
            "res_id": self.id,
        }

    # INTELIGENCIA DE ENTIDAD
    def create_job(self,
                   contract,
                   department,
                   start_date,
                   security_job,
                   is_uo_manager=False,
                   extra_security_roles=False,
                   end_date=False,
                   source_job=False):
        """
        CREA NUEVO PUESTO A PARTIR DE LA DATA DE ENTRADA
        :param contract: Recordset a hr.contract
        :param department: Recordset a hr.department
        :param start_date: Date
        :param security_job: Recordset a onsc.legajo.security.job
        :param is_responsable_uo: Si el Puesto es de Responsable de UO
        :param extra_security_roles: Extra security to apply
        :param end_date: Pasar en caso que el puesto tenga definida una fecha de fin. Debe ser a futuro
        :return: nuevo recordet de hr.job
        """
        role_extra_ids = [(5,)]
        if extra_security_roles:
            for extra_security_role in extra_security_roles:
                role_extra_vals = {
                    'user_role_id': extra_security_role.user_role_id.id,
                    'type': 'manual',
                    'start_date': start_date,
                    'end_date': False,
                    'active': extra_security_role.active
                }
                if end_date:
                    role_extra_vals['end_date'] = end_date
                role_extra_ids.append((0, 0, role_extra_vals))
        job = self.suspend_security().create({
            'name': '%s - %s' % (contract.display_name, str(start_date)),
            'employee_id': contract.employee_id.id,
            'contract_id': contract.id,
            'department_id': department.id,
            'start_date': start_date,
            'end_date': end_date,
            'security_job_id': security_job.id,
            'is_uo_manager': is_uo_manager,
            'role_extra_ids': role_extra_ids
        })
        job.onchange_security_job_id()
        if job.is_uo_manager and job.start_date <= fields.Date.today():
            job.department_id.suspend_security().write({
                'manager_id': job.employee_id.id,
                'is_manager_reserved': False
            })
        return job

    def deactivate(self, date_end):
        for job in self.suspend_security():
            if job.end_date and job.end_date <= date_end:
                continue
            job.role_assignment_ids.filtered(lambda x: x.date_end is False or x.date_end > date_end).write({
                'date_end': date_end
            })
            if job.start_date > date_end:
                job_end_date = job.start_date
            else:
                job_end_date = date_end
            job.end_date = job_end_date
            job.suspend_security().onchange_end_date()
            if date_end < fields.Date.today() and job.is_uo_manager:
                job.suspend_security().mapped('department_id').filtered(
                    lambda x: x.manager_id.id or x.is_manager_reserved).write(
                    {'manager_id': False, 'is_manager_reserved': False
                     })

    def update_start_date(self, start_date):
        self.suspend_security().write({'start_date': start_date})
        self.suspend_security().onchange_start_date()

    def is_job_available_for_manager(self, department, date, nro_doc=False):
        """

        :param department: Record of hr.department
        :param date: Fecha a chequear
        :param nro_doc: Si se pasa es para chequear si no es el mismo funcionario
        :return:
        """
        # TODO no se precisa por ahora definir para periodos cerrados
        if nro_doc:
            args = [
                ('contract_id.nro_doc', '!=', nro_doc),
                ('department_id', '=', department.id),
                ('is_uo_manager', '=', True),
                '|',
                '|',
                ('start_date', '>=', date),
                '&', ('start_date', '<=', date), '|', ('end_date', '=', False), ('end_date', '>=', date),
                ('department_id.is_manager_reserved', '=', True)
            ]
        else:
            args = [
                ('department_id', '=', department.id),
                ('is_uo_manager', '=', True),
                '|',
                '|',
                ('start_date', '>=', date),
                '&', ('start_date', '<=', date), '|', ('end_date', '=', False), ('end_date', '>=', date),
                ('department_id.is_manager_reserved', '=', True)
            ]
        return self.search_count(args) == 0

    def is_this_job_available_for_manager(self, job, department, date):
        """

        :param job: Record of hr.job
        :param date: Fecha a chequear
        :param nro_doc: Si se pasa es para chequear si no es el mismo funcionario
        :return:
        """
        # TODO no se precisa por ahora definir para periodos cerrados
        args = [
            ('id', '!=', job.id),
            ('department_id', '=', department.id),
            ('is_uo_manager', '=', True),
            '|',
            '|',
            ('start_date', '>=', date),
            '&', ('start_date', '<=', date), '|', ('end_date', '=', False), ('end_date', '>=', date),
            ('department_id.is_manager_reserved', '=', True)
        ]
        return self.search_count(args) == 0

    def update_managers(self):
        self.env['hr.department'].search([('manager_id', '!=', False)]).write({'manager_id': False})
        date = fields.Date.today()
        for record in self.search([
            ('is_uo_manager', '=', True),
            ('contract_id.legajo_state', '!=', 'baja'),
            ('start_date', '<=', date),
            '|', ('end_date', '=', False), ('end_date', '>=', date)
        ]):
            if record.department_id.manager_id.id != record.employee_id.id:
                record.department_id.suspend_security().write({'manager_id': record.employee_id.id})

    def get_management_job_from_department(self, department, date=fields.Date.today()):
        return self.search([
            ('department_id', '=', department.id),
            ('is_uo_manager', '=', True),
            '|',
            ('start_date', '>=', date),
            '&', ('start_date', '<=', date), '|', ('end_date', '=', False), ('end_date', '>=', date)
        ], limit=1)


class HrJobRoleLine(models.Model):
    _inherit = 'hr.job.role.line'

    user_role_id_domain = fields.Char(default=lambda self: self._user_role_id_domain(),
                                      compute='_compute_user_role_id_domain')
    file = fields.Binary("Agregar adjunto")
    filename = fields.Char('Nombre del documento adjunto')

    @api.constrains("start_date", "end_date", "job_id", "active", "user_role_id")
    def _check_roles_duplicated(self):
        if self._context.get('bulked_creation'):
            return True
        for record in self.filtered(lambda x: x.type != 'system'):
            # Se comenta porque no debe controlar contra roles del Tipo de Seguridad
            # job_roles = record.job_id.role_ids
            # job_roles = record.job_id.role_extra_ids
            job_roles = record.job_id.role_extra_ids.filtered(
                lambda x: x.id != record.id and x.active and x.user_role_id == record.user_role_id)
            if job_roles.filtered(lambda x: (x.start_date >= record.start_date and (record.end_date is False or record.end_date >= x.start_date)) or (x.end_date and x.end_date >= record.start_date and (record.end_date is False or record.end_date >= x.start_date))):
                raise ValidationError(_("El rol configurado no puede repetirse para el mismo puesto en el mismo "
                                        "periodo de vigencia. Revisar la pestaña de Roles y Roles adicionales"))

    @api.constrains("end_date")
    def _check_end_date(self):
        if self._context.get('bulked_creation'):
            return True
        for record in self:
            if record.job_id.end_date and (record.end_date is False or record.end_date > record.job_id.end_date):
                raise ValidationError(
                    _("El periodo de vigencia del rol adicional %s debe estar dentro del periodo de vigencia del puesto") % record.user_role_id.name)

    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.start_date = False
            return warning_response(_(u"La fecha desde no puede ser mayor que la fecha hasta"))
        if self.job_id.end_date and self.start_date and self.job_id.end_date < self.start_date:
            self.start_date = False
            return warning_response(_(u"La fecha desde no puede ser mayor que la fecha hasta del puesto"))
        if self.job_id.start_date and self.start_date and self.job_id.start_date > self.start_date:
            self.start_date = False
            return warning_response(_(u"La fecha desde no puede ser menor que la fecha desde del puesto"))

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date and self.end_date < fields.Date.today():
            self.end_date = False
            return warning_response(_(u"La fecha hasta no puede ser menor a la fecha actual"))
        if self.end_date and self.start_date and self.end_date < self.start_date:
            self.end_date = False
            return warning_response(_(u"La fecha hasta no puede ser menor que la fecha desde"))
        if self.job_id.start_date and self.end_date and self.job_id.start_date > self.end_date:
            self.end_date = False
            return warning_response(_(u"La fecha hasta no puede ser menor que la fecha desde del puesto"))
        if self.job_id.end_date and self.end_date and self.job_id.end_date < self.end_date:
            self.end_date = False
            return warning_response(_(u"La fecha hasta no puede ser mayor que la fecha hasta del puesto"))

    def _compute_user_role_id_domain(self):
        for rec in self:
            rec.user_role_id_domain = self._user_role_id_domain()

    def _user_role_id_domain(self):
        user_level = self.env.user.employee_id.job_id.sequence
        if self._context.get('bulked_creation'):
            return json.dumps([('id', '!=', False)])
        if self.user_has_groups(
                'onsc_legajo.group_legajo_configurador_puesto_ajuste_seguridad_manual_informatica_onsc'):
            args = [('sequence', '>=', user_level)]
        else:
            args = [('sequence', '>=', user_level), ('is_byinciso', '=', True)]
        roles = self.env['res.users.role'].search(args)
        return json.dumps([('id', 'in', roles.ids)])

    def _check_write(self):
        list_users = self.env.ref('base.user_admin')
        list_users |= self.env.ref('base.user_root')
        if self._context.get('no_check_write') or self.env.user.id in list_users.ids:
            return True
        is_informatica_onsc = self.user_has_groups(
            'onsc_legajo.group_legajo_configurador_puesto_ajuste_seguridad_manual_informatica_onsc')
        if not is_informatica_onsc and self.filtered(
                lambda x: x.user_role_id.is_byinciso is False and x.type == 'manual'):
            raise ValidationError(
                _("Solo puede modificar las lineas de roles adicionales para las que está habilitado por inciso"))

    @api.model
    def create(self, values):
        record = super(HrJobRoleLine, self).create(values)
        _logger.info('ACTUALIZANDO SEGURIDAD PUESTO: LINEA CREADA')
        if not self._context.get('bulked_creation'):
            line_name = record.user_role_id.name or ''
            record.job_id._message_log(body=_('Línea del rol adicional %s creada') % (line_name))
        return record

    def write(self, vals):
        self._check_write()
        _fields = ['start_date', 'end_date', 'user_role_id', 'active']
        ref_tracked_fields = self.fields_get(_fields)
        initial_values = {}
        for rec in self:
            line_name = rec.user_role_id.name or ''
            for field in _fields:
                initial_values[field] = eval('rec.%s' % (field))
            super(HrJobRoleLine, rec).write(vals)
            dummy, tracking_value_ids = rec._mail_track(ref_tracked_fields, initial_values)
            rec.job_id._message_log(body=_('Línea del rol adicional %s actualizada') % (line_name),
                                    tracking_value_ids=tracking_value_ids)
        return True
