# -*- coding:utf-8 -*-
import json

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

STATES = [
    ('borrador', 'Borrador'),
    ('error_sgh', 'Error SGH'),
    ('pendiente_auditoria_cgn', 'Pendiente Auditoría CGN'),
    ('aprobado_cgn', 'Aprobado CGN'),
    ('rechazado_cgn', 'Rechazado CGN'),
    ('gafi_ok', 'GAFI OK'),
    ('gafi_error', 'GAFI Error'),
]


class ONSCEmploymentRelationship(models.Model):
    _name = 'onsc.legajo.employment.relationship'
    _description = 'Vínculo laboral'

    programa = fields.Char(string='Programa', copy=False)
    proyecto = fields.Char(string='Proyecto', copy=False)
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor 1', copy=False)
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor 2', copy=False)
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor 3', copy=False)
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor 4', copy=False)
    nroPuesto = fields.Char(string='Puesto', copy=False)
    nroPlaza = fields.Char(string='Plaza', copy=False)
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', copy=False)
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora", copy=False)
    baja_vl_id = fields.Many2one("onsc.legajo.baja.vl", string="Baja de vínculo laboral", copy=False)
    regime_id = fields.Many2one('onsc.legajo.regime', string='Régimen', copy=False)


class ONSCLegajoBajaVL(models.Model):
    _name = 'onsc.legajo.baja.vl'
    _inherit = ['onsc.legajo.actions.common.data', 'mail.thread', 'mail.activity.mixin']
    _description = 'Baja de vínculo laboral'


    end_date = fields.Date(string="Fecha de Baja", default=fields.Date.today(), required=True, copy=False)
    res_partner_id = fields.Many2one('res.partner', string='Contacto',  copy=False)
    full_name = fields.Char("Nombre", related="res_partner_id.cv_full_name")

    causes_discharge_id = fields.Many2one('onsc.legajo.causes.discharge', string='Causal de Egreso', copy=False)
    causes_discharge_line_ids = fields.One2many('onsc.legajo.causes.discharge.line',
                                                related='causes_discharge_id.causes_discharge_line_ids',
                                                string="Motivos de causal de egreso extendido")
    employment_relationship_ids = fields.One2many('onsc.legajo.employment.relationship', 'baja_vl_id',
                                                  string="Vínculo laboral")
    attached_document_discharge_ids = fields.One2many('onsc.legajo.alta.vl.attached.document', 'baja_vl_id',
                                                      string='Documentos adjuntos')
    integration_error_id = fields.Many2one('onsc.legajo.integration.error', string=u'Error reportado integración',
                                           copy=False)
    contract_id = fields.Many2one('hr.contract', 'Contrato')
    id_baja = fields.Char(string="Id Baja")
    is_require_extended = fields.Boolean("¿Requiere extendido?", related="causes_discharge_id.is_require_extended")
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso',
                                default=lambda self: self._get_default_inciso_id(), copy=False)
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora",
                                        default=lambda self: self._get_default_ue_id(), copy=False)
    partner_ids_domain = fields.Char(compute='_compute_partner_ids')
    @api.depends('state')
    def _compute_partner_ids(self):
        for rec in self:
            rec.partner_ids_domain = self._get_domain_partner_ids()

    def _get_domain_partner_ids(self):
        contract_id = self.env['hr.contract'].search(
            [('legajo_state', '=', 'active'), ('employee_id', '=', self.env.user.employee_id.id)])
        if contract_id:
            iniciso_id = contract_id.inciso_id.id
            operating_unit_id = contract_id.operating_unit_id.id
            partner_ids = self.env['hr.contract'].search([('legajo_state', '=', 'active'),
                                                          ('inciso_id', '=', iniciso_id),
                                                          ('operating_unit_id', '=', operating_unit_id),
                                                          ('employee_id', '!=',
                                                           self.env.user.employee_id.id)]).mapped(
                'employee_id.user_id.partner_id').filtered(lambda x: x.is_partner_cv)
            return json.dumps([('id', 'in', partner_ids.ids)])
        else:
            return False

    @api.constrains("end_date")
    def _check_date(self):
        for record in self:
            if record.end_date > fields.Date.today():
                raise ValidationError(_("La fecha baja debe ser menor o igual a la fecha de registro"))

    @api.constrains("attached_document_discharge_ids")
    def _check_attached_document_discharge(self):
        for record in self:
            if not record.attached_document_discharge_ids:
                raise ValidationError(_("Debe haber al menos un documento adjunto"))

    @api.model
    def _get_default_inciso_id(self):
        if self.user_has_groups('onsc_legajo.group_legajo_baja_vl_recursos_humanos_inciso') or \
                self.user_has_groups('onsc_legajo.group_legajo_baja_vl_recursos_humanos_ue'):
            return self.env.user.employee_id.job_id.contract_id.inciso_id
        return False

    @api.model
    def _get_default_ue_id(self):
        if self.user_has_groups('onsc_legajo.group_legajo_baja_vl_recursos_humanos_ue'):
            return self.env.user.employee_id.job_id.contract_id.operating_unit_id
        return False

    def button_get_contract(self):
        employee_id = self.env['hr.employee'].sudo().search([('cv_emissor_country_id.code', '=', "UY"),
                                                             ('cv_document_type_id.code', '=', 'ci'),
                                                             ('cv_nro_doc', '=', self.cv_nro_doc)])

        contract_ids = self.env['hr.contract'].sudo().search([('employee_id', '=', employee_id.id)])

        self.cv_birthdate = employee_id.cv_birthdate
        # for  contract_id in contract_ids:
        #      nroPuesto
        #      nroPlaza
        #      descriptor1_id
        #      descriptor2_id
        #      descriptor3_id
        #      descriptor4_id
        #      inciso_id
        #      operating_unit_id
        #      programa
        #      proyecto
        #      regime_id
