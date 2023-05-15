# -*- coding: utf-8 -*-
import json
import logging

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
    _inherit = ['onsc.partner.common.data', 'mail.thread', 'mail.activity.mixin']
    _description = 'Alta de vínculo laboral'

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(ONSCLegajoAltaVL, self).fields_get(allfields, attributes)
        hide = ['document_identity_file', 'document_identity_filename', 'civical_credential_file',
                'civical_credential_filename','is_cv_race_public','cv_gender_record_filename',
                'cjppu_affiliate_number', 'professional_resume', 'user_linkedIn', 'is_driver_license', 'cv_gender2',
                'cv_gender_id', 'is_afro_descendants', 'is_occupational_health_card', 'occupational_health_card_date',
                'is_medical_aptitude_certificate_status', 'medical_aptitude_certificate_date', 'is_victim_violent',
                'is_public_information_victim_violent', 'allow_content_public', 'situation_disability',
                'people_disabilitie', 'certificate_date', 'to_date', 'see', 'hear', 'walk', 'speak', 'realize', 'lear',
                'interaction', 'need_other_support', 'afro_descendants_file', 'occupational_health_card_file',
                'occupational_health_card_filename','relationship_victim_violent_filename','is_cv_gender_public',
                'medical_aptitude_certificate_file', 'relationship_victim_violent_file', 'document_certificate_file',
                'document_certificate_filename','afro_descendants_filename']
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
        if self.user_has_groups('onsc_legajo.group_legajo_alta_vl_recursos_humanos_inciso') or self.user_has_groups(
                'onsc_legajo.group_legajo_alta_vl_recursos_humanos_ue'):
            res['inciso_id'] = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        if self.user_has_groups('onsc_legajo.group_legajo_alta_vl_recursos_humanos_ue'):
            res['operating_unit_id'] = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        return res

    partner_id = fields.Many2one("res.partner", string="Contacto")
    date_start = fields.Date(string="Fecha de alta", default=fields.Date.today(), copy=False, readonly=True,
                             states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    income_mechanism_id = fields.Many2one('onsc.legajo.income.mechanism', string='Mecanismo de ingreso', copy=False,
                                          readonly=True,
                                          states={'borrador': [('readonly', False)],
                                                  'error_sgh': [('readonly', False)]})
    call_number = fields.Char(string='Número de llamado', copy=False, readonly=True,
                              states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    is_call_number_required = fields.Boolean(string="¿Requiere número de llamado?",
                                             related="income_mechanism_id.is_call_number_required", store=True)
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', copy=False, readonly=True,
                                states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    is_inciso_readonly = fields.Boolean(compute="_compute_is_readonly", readonly=True,
                                        states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora", copy=False)
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
    reason_description = fields.Char(string='Descripción del motivo', copy=True,
                                     readonly=True,
                                     states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})

    # Datos de la Norma
    norm_id = fields.Many2one('onsc.legajo.norm', string='Norma', copy=True,
                              readonly=True,
                              states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    norm_type = fields.Char(string="Tipo norma", related="norm_id.tipoNorma", store=True, readonly=True)
    norm_number = fields.Integer(string='Número de norma', related="norm_id.numeroNorma",
                                 store=True, readonly=True)
    norm_year = fields.Integer(string='Año de norma', related="norm_id.anioNorma", store=True,
                               readonly=True)
    norm_article = fields.Integer(string='Artículo de norma', related="norm_id.articuloNorma",
                                  store=True, readonly=True)
    resolution_description = fields.Char(string='Descripción de la resolución', copy=True,
                                         readonly=True,
                                         states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    resolution_date = fields.Date(string='Fecha de la resolución', copy=True,
                                  readonly=True,
                                  states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    resolution_type = fields.Selection(
        [
            ('M', 'Inciso'),
            ('P', 'Presidencia o Poder ejecutivo'),
            ('U', 'Unidad ejecutora')
        ],
        copy=True,
        string='Tipo de resolución'
        , readonly=True, states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    health_provider_id = fields.Many2one("onsc.legajo.health.provider", u"Cobertura de salud", copy=False,
                                         readonly=True,
                                         states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    additional_information = fields.Text(string='Información adicional', copy=False,
                                         readonly=True,
                                         states={'borrador': [('readonly', False)], 'error_sgh': [('readonly', False)]})
    attached_document_ids = fields.One2many('onsc.legajo.alta.vl.attached.document', 'alta_vl_id',
                                            string='Documentos adjuntos',
                                            readonly=True, states={'borrador': [('readonly', False)],
                                                                   'error_sgh': [('readonly', False)]})
    state = fields.Selection(STATES, string='Estado', default='borrador', copy=False)
    id_alta = fields.Char(string="Id Alta")

    @api.constrains("attached_document_ids")
    def _check_attached_document_ids(self):
        for record in self:
            if not record.attached_document_ids and record.state != 'borrador':
                raise ValidationError(_("Debe haber al menos un documento adjunto"))

    @api.constrains("is_responsable_uo", "date_start", "department_id")
    def _check_responsable_uo(self):
        for rec in self:
            if rec.is_responsable_uo and rec.date_start and rec.department_id:
                domain = [
                    '&', '&', ('start_date', '<=', rec.date_start),
                    '|', ('end_date', '>=', rec.date_start), ('end_date', '=', False),
                    ('department_id', '=', False)]
                jobs = self.env['hr.job'].search(domain).filtered(lambda x: x.security_job_id.is_uo_manager)
                domain_alta = [
                    ('state', '=', 'pendiente_auditoria_cgn'),
                    ('date_start', '=', rec.date_start),
                    ('department_id', '=', rec.department_id.id),
                ]
                altas = self.search(domain_alta)
                if jobs or altas:
                    raise ValidationError("Ya existe un puesto responsable de UO")

    @api.constrains("date_start")
    def _check_date(self):
        for record in self:
            if record.date_start > fields.Date.today():
                raise ValidationError(_("La fecha debe ser menor o igual al día de alta"))

    @api.constrains("date_start")
    def _check_date(self):
        for record in self:
            if record.date_start and record.date_start > fields.Date.today():
                raise ValidationError(_("La fecha debe ser menor o igual al día de alta"))

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
                'onsc_legajo.group_legajo_alta_vl_recursos_humanos_inciso') or
                                      self.user_has_groups('onsc_legajo.group_legajo_alta_vl_recursos_humanos_ue')) \
                                     and not self.user_has_groups(
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

    def action_aprobado_cgn(self):
        for rec in self:
            rec.state = 'aprobado_cgn'

    def action_rechazado_cgn(self):
        for rec in self:
            rec.state = 'rechazado_cgn'

    def action_gafi_ok(self):
        for rec in self:
            rec.state = 'gafi_ok'

    def action_gafi_error(self):
        for rec in self:
            rec.state = 'gafi_error'

    def unlink(self):
        if self.filtered(lambda x: x.state != 'borrador'):
            raise ValidationError(_("Solo se pueden eliminar una transacción en estado borrador"))
        return super(ONSCLegajoAltaVL, self).unlink()
