# -*- coding:utf-8 -*-
import json
import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name

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
    _rec_name = 'full_name'

    def _get_domain(self, args):
        if self._context.get('is_from_menu') and self.user_has_groups(
                'onsc_legajo.group_legajo_alta_vl_recursos_humanos_inciso'):
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
            if inciso_id:
                args = expression.AND([[
                    ('inciso_id', '=', inciso_id.id)
                ], args])
        if self._context.get('is_from_menu') and self.user_has_groups(
                'onsc_legajo.group_legajo_alta_vl_recursos_humanos_ue'):
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
        args = self._get_domain(args)
        return super(ONSCLegajoAltaVL, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                     access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        domain = self._get_domain(domain)
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.model
    def _get_default_inciso_id(self):
        if self.user_has_groups('onsc_legajo.group_legajo_alta_vl_recursos_humanos_inciso') or \
                self.user_has_groups('onsc_legajo.group_legajo_alta_vl_recursos_humanos_ue'):
            return self.env.user.employee_id.job_id.contract_id.inciso_id
        return False

    @api.model
    def _get_default_ue_id(self):
        if self.user_has_groups('onsc_legajo.group_legajo_alta_vl_recursos_humanos_ue'):
            return self.env.user.employee_id.job_id.contract_id.operating_unit_id
        return False

    full_name = fields.Char('Nombre', compute='_compute_full_name', store=True)
    partner_id = fields.Many2one("res.partner", string="Contacto")
    date_start = fields.Date(string="Fecha de alta", default=fields.Date.today(), copy=False)
    income_mechanism_id = fields.Many2one('onsc.legajo.income.mechanism', string='Mecanismo de ingreso', copy=False)
    call_number = fields.Char(string='Número de llamado', copy=False)
    is_call_number_required = fields.Boolean(string="¿Requiere número de llamado?",
                                             related="income_mechanism_id.is_call_number_required", store=True)
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso',
                                default=lambda self: self._get_default_inciso_id(), copy=False)
    is_inciso_readonly = fields.Boolean(compute="_compute_is_readonly")
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora",
                                        default=lambda self: self._get_default_ue_id(), copy=False)
    is_operating_unit_readonly = fields.Boolean(compute="_compute_is_readonly")
    operating_unit_id_domain = fields.Char(compute='_compute_operating_unit_id_domain')
    department_id = fields.Many2one("hr.department", string="Unidad organizativa", copy=False)
    department_id_domain = fields.Char(compute='_compute_department_id_domain')
    is_responsable_uo = fields.Boolean(string="¿Responsable de UO?", related="security_job_id.is_uo_manager",
                                       store=True)
    programa = fields.Char(string='Programa', copy=False)
    proyecto = fields.Char(string='Proyecto', copy=False)
    office_id = fields.Many2one("onsc.legajo.office", string="Oficina", compute="_compute_office_id", store=True)
    retributive_day_id = fields.Many2one('onsc.legajo.jornada.retributiva', string='Jornada retributiva',
                                         domain="[('office_id', '=', office_id)]", copy=False)
    is_reserva_sgh = fields.Boolean(string="¿Tiene reserva en SGH?", copy=False)
    regime_id = fields.Many2one('onsc.legajo.regime', string='Régimen', copy=False)
    is_presupuestado = fields.Boolean(related="regime_id.presupuesto", store=True)
    is_indVencimiento = fields.Boolean(related="regime_id.indVencimiento", store=True)
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor 1', copy=False)
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor 2', copy=False)
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor 3', copy=False)
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor 4', copy=False)
    partida_id = fields.Many2one('onsc.legajo.budget.item', compute="_compute_partida", store=True)
    nroPuesto = fields.Char(string='Puesto', copy=False)
    nroPlaza = fields.Char(string='Plaza', copy=False)
    security_job_id = fields.Many2one("onsc.legajo.security.job", string="Seguridad de puesto", copy=False)
    occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación', copy=False)
    date_income_public_administration = fields.Date(string="Fecha de ingreso a la administración pública", copy=False)
    inactivity_years = fields.Integer(string="Años de inactividad", copy=False)
    is_graduation_date_required = fields.Boolean(string=u"¿Fecha de graduación requerida?",
                                                 related="descriptor1_id.is_graduation_date_required")
    graduation_date = fields.Date(string='Fecha de graduación', copy=False)
    contract_expiration_date = fields.Date(string='Vencimiento del contrato', copy=False)
    reason_discharge = fields.Char(string='Descripción del motivo', copy=True)
    norm_code_discharge_id = fields.Many2one('onsc.legajo.norm', string='Tipo de norma', copy=True)
    norm_number_discharge = fields.Integer(string='Número de norma', related="norm_code_discharge_id.numeroNorma",
                                           store=True, readonly=True)
    norm_year_discharge = fields.Integer(string='Año de norma', related="norm_code_discharge_id.anioNorma", store=True,
                                         readonly=True)
    norm_article_discharge = fields.Integer(string='Artículo de norma', related="norm_code_discharge_id.articuloNorma",
                                            store=True, readonly=True)
    resolution_description_discharge = fields.Char(string='Descripción de la resolución', copy=True)
    resolution_date_discharge = fields.Date(string='Fecha de la resolución', copy=True)
    resolution_type_discharge = fields.Selection(
        [
            ('m', 'Inciso'),
            ('p', 'Presidencia o Poder ejecutivo'),
            ('u', 'Unidad ejecutora')
        ],
        copy=True,
        string='Tipo de resolución'
    )
    emergency_service_id = fields.Many2one("onsc.legajo.health.provider", u"Cobertura de salud", copy=False)
    additional_information_discharge = fields.Text(string='Información adicional', copy=False)
    attached_document_discharge_ids = fields.One2many('onsc.legajo.alta.vl.attached.document', 'alta_vl_id',
                                                      string='Documentos adjuntos')
    state = fields.Selection(STATES, string='Estado', default='borrador', copy=False)
    id_alta = fields.Char(string="Id Alta")

    @api.constrains("attached_document_discharge_ids")
    def _check_attached_document_discharge(self):
        for record in self:
            if not record.attached_document_discharge_ids:
                raise ValidationError(_("Debe haber al menos un documento adjunto"))

    # @api.constrains("office_id")
    # def _check_office(self):
    #     for record in self:
    #         if not record.office_id:
    #             raise ValidationError(_("Para esta combinación de Inciso-UE-Programa-Proyecto no hay oficinas"))

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
            if record.date_start > fields.Date.today():
                raise ValidationError(_("La fecha debe ser menor o igual al día de alta"))

    @api.constrains("graduation_date", "date_start")
    def _check_graduation_date(self):
        for record in self:
            if record.date_start and record.graduation_date and record.graduation_date > record.date_start:
                raise ValidationError(_("La fecha de graduación debe ser menor o igual al día de alta"))

    @api.onchange('regime_id')
    def onchange_regimen(self):
        for rec in self:
            rec.descriptor1_id = False
            rec.descriptor2_id = False
            rec.descriptor3_id = False
            rec.descriptor4_id = False
            rec.contract_expiration_date = False
            rec.vacante_ids = False

    @api.onchange('descriptor1_id', 'descriptor2_id', 'regime_id', 'is_reserva_sgh', 'programa', 'proyecto',
                  'nroPuesto', 'nroPlaza')
    def onchange_clear_vacante_id(self):
        for rec in self:
            rec.vacante_ids = False

    @api.onchange('inciso_id')
    def onchange_inciso(self):
        # TODO: terminar los demas campos a setear
        self.operating_unit_id = False
        self.department_id = False
        self.programa = False
        self.proyecto = False
        self.office_id = False
        self.retributive_day_id = False

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

    @api.depends('cv_first_name', 'cv_second_name', 'cv_last_name_1', 'cv_last_name_2')
    def _compute_full_name(self):
        for record in self:
            full_name = calc_full_name(record.cv_first_name, record.cv_second_name,
                                       record.cv_last_name_1, record.cv_last_name_2)
            if full_name:
                record.full_name = full_name
            else:
                record.full_name = 'New'

    def _compute_is_readonly(self):
        for rec in self:
            rec.is_inciso_readonly = self.user_has_groups('onsc_legajo.group_legajo_alta_vl_recursos_humanos_inciso') or \
                                     self.user_has_groups('onsc_legajo.group_legajo_alta_vl_recursos_humanos_ue')
            rec.is_operating_unit_readonly = self.user_has_groups(
                'onsc_legajo.group_legajo_alta_vl_recursos_humanos_ue')

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
            self.department_id_domain = json.dumps(domain)

    @api.depends('inciso_id', 'operating_unit_id', 'programa', 'proyecto')
    def _compute_office_id(self):
        for rec in self:
            Office = self.env['onsc.legajo.office'].sudo()
            if rec.inciso_id and rec.operating_unit_id and rec.programa and rec.proyecto:
                domain = [
                    ('inciso', '=', rec.inciso_id.id),
                    ('unidadEjecutora', '=', rec.operating_unit_id.id),
                    ('programa', '=', rec.programa),
                    ('proyecto', '=', rec.proyecto),
                ]
                rec.office_id = Office.search(domain, limit=1)
            else:
                rec.office_id = False

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
            raise ValidationError(_("No se pueden eliminar Altas VL en este estado"))
        return super(ONSCLegajoAltaVL, self).unlink()

    @api.model
    def syncronize(self, log_info=False):
        self.vacante_ids = self.env['onsc.legajo.abstract.alta.vl.ws1'].with_context(
            log_info=log_info).suspend_security().syncronize(self)
        return True
