# -*- coding: utf-8 -*-
import json
import logging

from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as warning_response

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

_logger = logging.getLogger(__name__)

STATES = [
    ('borrador', 'Borrador'),
    ('error_sgh', 'Error SGH'),
    ('pendiente_auditoria_cgn', 'Pendiente Auditoría CGN'),
    ('aprobado_cgn', 'Aprobado CGN'),
    ('rechazado_cgn', 'Rechazado CGN'),
    ('gafi_ok', 'GAFI OK'),
    ('gafi_error', 'GAFI Error'),
]


class ONSCLegajoAltaVL(models.Model):
    _name = 'onsc.legajo.alta.vl'
    _inherit = ['onsc.partner.common.data', 'mail.thread', 'mail.activity.mixin', 'onsc.legajo.actions.common.data']
    _description = 'Alta de vínculo laboral'
    _order = 'create_date DESC'

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(ONSCLegajoAltaVL, self).fields_get(allfields, attributes)
        hide = ['document_identity_file', 'document_identity_filename', 'civical_credential_file',
                'civical_credential_filename', 'is_cv_race_public', 'cv_gender_record_filename',
                'cjppu_affiliate_number', 'professional_resume', 'user_linkedIn', 'is_driver_license', 'cv_gender2',
                'cv_gender_id', 'is_afro_descendants', 'is_occupational_health_card', 'occupational_health_card_date',
                'is_medical_aptitude_certificate_status', 'medical_aptitude_certificate_date', 'is_victim_violent',
                'is_public_information_victim_violent', 'allow_content_public', 'situation_disability',
                'people_disabilitie', 'certificate_date', 'to_date', 'see', 'hear', 'walk', 'speak', 'realize', 'lear',
                'interaction', 'need_other_support', 'afro_descendants_file', 'occupational_health_card_file',
                'occupational_health_card_filename', 'relationship_victim_violent_filename', 'is_cv_gender_public',
                'medical_aptitude_certificate_file', 'relationship_victim_violent_file', 'document_certificate_file',
                'document_certificate_filename', 'afro_descendants_filename']
        for field in hide:
            if field in res:
                res[field]['selectable'] = False
                res[field]['searchable'] = False
                res[field]['sortable'] = False
        return res

    def _get_domain(self, args):
        args = expression.AND([[
            ('partner_id', '!=', self.env.user.partner_id.id)
        ], args])
        if self.user_has_groups('onsc_legajo.group_legajo_alta_vl_recursos_humanos_inciso'):
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
            if inciso_id:
                args = expression.AND([[
                    ('inciso_id', '=', inciso_id.id)
                ], args])
        elif self.user_has_groups('onsc_legajo.group_legajo_alta_vl_recursos_humanos_ue'):
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
        return args

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_menu'):
            args = self._get_domain(args)
        return super(ONSCLegajoAltaVL, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                     access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu'):
            domain = self._get_domain(domain)
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.model
    def default_get(self, fields):
        res = super(ONSCLegajoAltaVL, self).default_get(fields)
        res['cv_emissor_country_id'] = self.env.ref('base.uy').id
        res['cv_document_type_id'] = self.env['onsc.cv.document.type'].sudo().search([('code', '=', 'ci')],
                                                                                     limit=1).id or False
        is_group_administrator = self.user_has_groups('onsc_legajo.group_legajo_alta_vl_administrar_altas_vl')
        is_group_inciso = self.user_has_groups('onsc_legajo.group_legajo_alta_vl_recursos_humanos_inciso')
        is_group_ue = self.user_has_groups('onsc_legajo.group_legajo_alta_vl_recursos_humanos_ue')
        if is_group_administrator or is_group_inciso or is_group_ue:
            res['inciso_id'] = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        if is_group_administrator or is_group_ue:
            res['operating_unit_id'] = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        return res

    partner_id = fields.Many2one("res.partner", string="Contacto", readonly=True,
                                 states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    date_start = fields.Date(string="Fecha de alta", default=lambda *a: fields.Date.today(), copy=False, readonly=True,
                             states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    income_mechanism_id = fields.Many2one('onsc.legajo.income.mechanism', string='Mecanismo de ingreso', copy=False,
                                          readonly=True,
                                          states={'borrador': [('readonly', False)],
                                                  'error_sgh': [('readonly', False)]})
    call_number = fields.Char(string='Número de llamado', copy=False, readonly=True,
                              states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    is_call_number_required = fields.Boolean(string="¿Requiere número de llamado?",
                                             related="income_mechanism_id.is_call_number_required", store=True)
    # inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', copy=False, readonly=True,
    #                             states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    is_inciso_readonly = fields.Boolean(compute="_compute_is_readonly", readonly=True,
                                        states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    # operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora", copy=False)
    is_operating_unit_readonly = fields.Boolean(compute="_compute_is_readonly")
    operating_unit_id_domain = fields.Char(compute='_compute_operating_unit_id_domain')
    department_id = fields.Many2one("hr.department", string="Unidad organizativa", copy=False, readonly=True,
                                    states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    department_id_domain = fields.Char(compute='_compute_department_id_domain')
    is_responsable_uo = fields.Boolean(string="¿Responsable de UO?", related="security_job_id.is_uo_manager",
                                       store=True)
    program_project_id = fields.Many2one('onsc.legajo.office', string='Programa - Proyecto', copy=False,
                                         domain="[('inciso', '=', inciso_id),('unidadEjecutora', '=', operating_unit_id)]",
                                         readonly=True,
                                         states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    retributive_day_id = fields.Many2one('onsc.legajo.jornada.retributiva', string='Jornada retributiva',
                                         domain="[('office_id', '=', program_project_id)]", copy=False,
                                         readonly=True,
                                         states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    is_reserva_sgh = fields.Boolean(string="¿Tiene reserva en SGH?", copy=False,
                                    readonly=True,
                                    states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    regime_id = fields.Many2one('onsc.legajo.regime', string='Régimen', copy=False,
                                readonly=True,
                                states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    is_presupuestado = fields.Boolean(related="regime_id.presupuesto", store=True)
    is_indVencimiento = fields.Boolean(related="regime_id.indVencimiento", store=True)

    # Datos para los Descriptores
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor 1', copy=False,
                                     readonly=True,
                                     states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    descriptor1_domain_id = fields.Char(compute='_compute_descriptor1_domain_id')
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor 2', copy=False,
                                     readonly=True,
                                     states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})

    descriptor2_domain_id = fields.Char(compute='_compute_descriptor2_domain_id')
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor 3', copy=False,
                                     readonly=True,
                                     states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})

    descriptor3_domain_id = fields.Char(compute='_compute_descriptor3_domain_id')
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor 4', copy=False,
                                     readonly=True,
                                     states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    descriptor4_domain_id = fields.Char(compute='_compute_descriptor4_domain_id')

    # Datos para el puesto
    partida_id = fields.Many2one('onsc.legajo.budget.item', compute="_compute_partida", store=True)
    nroPuesto = fields.Char(string='Puesto', copy=False,
                            readonly=True,
                            states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    nroPlaza = fields.Char(string='Plaza', copy=False,
                           readonly=True,
                           states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    security_job_id = fields.Many2one("onsc.legajo.security.job", string="Seguridad de puesto", copy=False,
                                      readonly=True,
                                      states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación', copy=False,
                                    readonly=True,
                                    states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    date_income_public_administration = fields.Date(string="Fecha de ingreso a la administración pública", copy=False,
                                                    readonly=True, states={'borrador': [('readonly', False)],
                                                                           'error_sgh': [('readonly', False)]})
    inactivity_years = fields.Integer(string="Años de inactividad", copy=False,
                                      readonly=True,
                                      states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    is_graduation_date_required = fields.Boolean(string=u"¿Fecha de graduación requerida?",
                                                 related="descriptor1_id.is_graduation_date_required")
    graduation_date = fields.Date(string='Fecha de graduación', copy=False,
                                  readonly=True,
                                  states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    contract_expiration_date = fields.Date(string='Vencimiento del contrato', copy=False,
                                           readonly=True, states={'borrador': [('readonly', False)],
                                                                  'error_sgh': [('readonly', False)]})
    health_provider_id = fields.Many2one("onsc.legajo.health.provider", u"Cobertura de salud", copy=False,
                                         readonly=True,
                                         states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    attached_document_ids = fields.One2many('onsc.legajo.attached.document', 'alta_vl_id',
                                            string='Documentos adjuntos',
                                            readonly=True, states={'borrador': [('readonly', False)],
                                                                   'error_sgh': [('readonly', False)]})
    state = fields.Selection(STATES, string='Estado', default='borrador', copy=False)
    # Response WS4
    id_alta = fields.Char(string="Id Alta")
    secPlaza = fields.Char(string="Sec Plaza")
    codigoJornadaFormal = fields.Char(string="Código Jornada Formal")
    descripcionJornadaFormal = fields.Char(string="Descripción Jornada Formal")
    ws4_user_id = fields.Many2one("res.users", string="Usuario que manda aprobación a CGN")

    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')

    @api.depends('mass_upload_id')
    def _compute_origin_type(self):
        for record in self:
            if record.mass_upload_id:
                record.origin_type = 'P'
            else:
                record.origin_type = 'M'

    @api.depends('state')
    def _compute_should_disable_form_edit(self):
        for record in self:
            record.should_disable_form_edit = record.state not in ['borrador', 'error_sgh']

    @api.constrains("attached_document_ids")
    def _check_attached_document_ids(self):
        for record in self:
            if not record.attached_document_ids and record.state != 'borrador':
                raise ValidationError(_("Debe haber al menos un documento adjunto"))

    @api.constrains("date_start")
    def _check_date(self):
        for record in self:
            if record.date_start and record.date_start > fields.Date.today():
                raise ValidationError(_("La fecha debe ser menor o igual al día de alta"))

    @api.constrains("date_start", "contract_expiration_date")
    def _check_contract_expiration_date(self):
        for record in self:
            if record.contract_expiration_date and record.date_start and record.date_start > record.contract_expiration_date:
                raise ValidationError(
                    _("La fecha de Vencimiento del contrato no puede ser anterior a la Fecha de alta"))

    @api.constrains("graduation_date", "date_start")
    def _check_graduation_date(self):
        for record in self:
            if record.date_start and record.graduation_date and record.graduation_date > record.date_start:
                raise ValidationError(_("La fecha de graduación debe ser menor o igual al día de alta"))

    @api.onchange('inciso_id')
    def onchange_inciso(self):
        # TODO: terminar los demas campos a setear
        if self.operating_unit_id and self.operating_unit_id.inciso_id.id != self.inciso_id.id:
            self.operating_unit_id = False
            self.department_id = False
            self.program_project_id = False
            self.retributive_day_id = False

    @api.onchange('operating_unit_id')
    def onchange_operating_unit(self):
        self.department_id = False
        self.program_project_id = False
        self.retributive_day_id = False

    @api.onchange('descriptor1_id')
    def onchange_descriptor1(self):
        self.descriptor2_id = False
        self.descriptor3_id = False
        self.descriptor4_id = False

    @api.onchange('descriptor2_id')
    def onchange_descriptor2(self):
        self.descriptor3_id = False
        self.descriptor4_id = False

    @api.onchange('descriptor3_id')
    def onchange_descriptor3(self):
        self.descriptor4_id = False

    @api.onchange('nroPuesto')
    def onchange_nroPuesto(self):
        if self.nroPuesto and not self.nroPuesto.isnumeric():
            self.nroPuesto = ''
            return warning_response(_("El campo Puesto debe ser numérico"))

    @api.onchange('nroPlaza')
    def onchange_nroPlaza(self):
        if self.nroPlaza and not self.nroPlaza.isnumeric():
            self.nroPlaza = ''
            return warning_response(_("El campo Plaza debe ser numérico"))

    @api.depends('descriptor1_id', 'descriptor2_id', 'descriptor3_id', 'descriptor4_id')
    def _compute_partida(self):
        for rec in self:
            domain = []
            if rec.descriptor1_id:
                domain = expression.AND([domain, [("dsc1Id", "=", rec.descriptor1_id.id)]])
            if rec.descriptor2_id:
                domain = expression.AND([domain, [("dsc2Id", "=", rec.descriptor2_id.id)]])
            if rec.descriptor3_id:
                domain = expression.AND([domain, [("dsc3Id", "=", rec.descriptor3_id.id)]])
            if rec.descriptor4_id:
                domain = expression.AND([domain, [("dsc4Id", "=", rec.descriptor4_id.id)]])
            rec.partida_id = self.env['onsc.legajo.budget.item'].search(domain, limit=1) if domain else False

    @api.depends('inciso_id')
    def _compute_is_readonly(self):
        for rec in self:
            rec.is_inciso_readonly = (self.user_has_groups(
                'onsc_legajo.group_legajo_alta_vl_recursos_humanos_inciso') or self.user_has_groups(
                'onsc_legajo.group_legajo_alta_vl_recursos_humanos_ue')) and not self.user_has_groups(
                'onsc_legajo.group_legajo_alta_vl_administrar_altas_vl')
            rec.is_operating_unit_readonly = self.user_has_groups(
                'onsc_legajo.group_legajo_alta_vl_recursos_humanos_ue') and not self.user_has_groups(
                'onsc_legajo.group_legajo_alta_vl_administrar_altas_vl')

    @api.depends('inciso_id')
    def _compute_operating_unit_id_domain(self):
        for rec in self:
            domain = [('id', 'in', [])]
            if rec.inciso_id.id:
                domain = [('inciso_id', '=', rec.inciso_id.id)]
            self.operating_unit_id_domain = json.dumps(domain)

    @api.depends('inciso_id', 'operating_unit_id')
    def _compute_department_id_domain(self):
        for rec in self:
            domain = []
            if not rec.inciso_id and not rec.operating_unit_id:
                domain = [('id', 'in', [])]
            if rec.inciso_id.id:
                domain = [('inciso_id', '=', rec.inciso_id.id)]
            if rec.operating_unit_id:
                domain = expression.AND([[
                    ('operating_unit_id', '=', rec.operating_unit_id.id)
                ], domain])
            rec.department_id_domain = json.dumps(domain)

    @api.depends('inciso_id', 'operating_unit_id', 'is_reserva_sgh')
    def _compute_descriptor1_domain_id(self):
        domain = [('id', 'in', [])]
        for rec in self:
            if not rec.is_reserva_sgh:
                dsc1Id = self.env['onsc.legajo.budget.item'].search([]).mapped(
                    'dsc1Id')
                if dsc1Id:
                    domain = [('id', 'in', dsc1Id.ids)]
            rec.descriptor1_domain_id = json.dumps(domain)

    @api.depends('descriptor1_id')
    def _compute_descriptor2_domain_id(self):
        for rec in self:
            args = []
            domain = [('id', 'in', [])]
            if rec.descriptor1_id:
                args = [('dsc1Id', '=', rec.descriptor1_id.id)]
            dsc2Id = self.env['onsc.legajo.budget.item'].search(args).mapped('dsc2Id')
            if dsc2Id:
                domain = [('id', 'in', dsc2Id.ids)]
            rec.descriptor2_domain_id = json.dumps(domain)

    @api.depends('descriptor2_id')
    def _compute_descriptor3_domain_id(self):
        for rec in self:
            args = []
            domain = [('id', 'in', [])]
            if rec.descriptor1_id:
                args = [('dsc1Id', '=', rec.descriptor1_id.id)]
            if rec.descriptor2_id:
                args = expression.AND([[('dsc2Id', '=', rec.descriptor2_id.id)], args])
            dsc3Id = self.env['onsc.legajo.budget.item'].search(args).mapped('dsc3Id')
            if dsc3Id:
                domain = [('id', 'in', dsc3Id.ids)]
            rec.descriptor3_domain_id = json.dumps(domain)

    @api.depends('descriptor3_id')
    def _compute_descriptor4_domain_id(self):
        for rec in self:
            args = []
            domain = [('id', 'in', [])]
            if rec.descriptor1_id:
                args = [('dsc1Id', '=', rec.descriptor1_id.id)]
            if rec.descriptor2_id:
                args = expression.AND([[('dsc2Id', '=', rec.descriptor2_id.id)], args])

            if rec.descriptor3_id:
                args = expression.AND([[('dsc3Id', '=', rec.descriptor3_id.id)], args])
            dsc4Id = self.env['onsc.legajo.budget.item'].search(args).mapped('dsc4Id')
            if dsc4Id:
                domain = [('id', 'in', dsc4Id.ids)]
            rec.descriptor4_domain_id = json.dumps(domain)

    def action_error_sgh(self):
        for rec in self:
            rec.state = 'error_sgh'

    def action_pendiente_auditoria_cgn(self):
        for rec in self:
            rec.state = 'pendiente_auditoria_cgn'

    def action_gafi_ok(self):
        for rec in self:
            rec.state = 'gafi_ok'

    def action_gafi_error(self):
        for rec in self:
            rec.state = 'gafi_error'

    def action_aprobado_cgn(self):
        legajo = self._create_legajo()
        self.write({'state': 'aprobado_cgn'})
        self._send_aprobado_notification()
        return legajo

    def action_rechazado_cgn(self):
        self.write({'state': 'rechazado_cgn'})
        self._send_rechazado_notification()
        return True

    def _send_aprobado_notification(self):
        validation_email_template_id = self.env.ref('onsc_legajo.email_template_altavl_aprobada')
        validation_email_template_id.send_mail(self.id, force_send=True)

    def _send_rechazado_notification(self):
        validation_email_template_id = self.env.ref('onsc_legajo.email_template_altavl_rechazada')
        validation_email_template_id.send_mail(self.id, force_send=True)

    # ALTAVL WS5
    def _create_legajo(self):
        employee = self._get_legajo_employee()
        contract = self._get_legajo_contract(employee)
        self._get_legajo_job(contract)
        legajo = self._get_legajo(employee)
        return legajo

    def _get_legajo(self, employee):
        return self.env['onsc.legajo']._get_legajo(
            employee,
            self.date_income_public_administration,
            self.inactivity_years)

    def _get_legajo_employee(self):
        return self.env['hr.employee']._get_legajo_employee(
            self.cv_emissor_country_id,
            self.cv_document_type_id,
            self.partner_id)

    def _get_legajo_contract(self, employee):
        Contract = self.env['hr.contract']
        vals = {
            'employee_id': employee.id,
            'name': employee.name,
            'date_start': self.date_start or fields.Date.today(),
            'inciso_id': self.inciso_id.id,
            'operating_unit_id': self.operating_unit_id.id,
            'income_mechanism_id': self.income_mechanism_id.id,
            'program': self.program_project_id.programa,
            'project': self.program_project_id.proyecto,
            'regime_id': self.regime_id.id,
            'occupation_id': self.occupation_id.id,
            'descriptor1_id': self.descriptor1_id.id,
            'descriptor2_id': self.descriptor2_id.id,
            'descriptor3_id': self.descriptor3_id.id,
            'descriptor4_id': self.descriptor4_id.id,
            'position': self.nroPuesto,
            'workplace': self.nroPlaza,
            'sec_position': self.secPlaza,
            'graduation_date': self.graduation_date,
            'reason_description': self.reason_description,
            'norm_code_id': self.norm_id.id,
            'resolution_description': self.resolution_description,
            'resolution_date': self.resolution_date,
            'resolution_type': self.resolution_type,
            'call_number': self.call_number,
            'contract_expiration_date': self.contract_expiration_date,
            'additional_information': self.additional_information,
            'code_day': self.retributive_day_id.codigoJornada,
            'description_day': self.retributive_day_id.descripcionJornada,
            'retributive_day_id': self.retributive_day_id.id,
            'id_alta': self.id_alta,
            #
            'wage': 1
        }

        contract = Contract.suspend_security().create(vals)

        for document_record in self.attached_document_ids:
            document_record.write({
                'contract_id': contract.id,
                'type': 'discharge'})

        contract.activate_legajo_contract()
        return contract

    def _get_legajo_job(self, contract):
        return self.env['hr.job'].create_job(contract, self.department_id, self.date_start, self.security_job_id)

    def unlink(self):
        if self.filtered(lambda x: x.state != 'borrador'):
            raise ValidationError(_("Solo se pueden eliminar transacciones en estado borrador"))
        return super(ONSCLegajoAltaVL, self).unlink()

    # MAIL TEMPLATE UTILS
    def get_followers_mails(self):
        return ','.join(self.message_follower_ids.mapped('partner_id.email'))

    def get_altavl_name(self):
        return self.partner_id.display_name
