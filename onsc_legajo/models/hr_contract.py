# -*- coding:utf-8 -*-
import json

from odoo import fields, models, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora")
    operating_unit_id_domain = fields.Char(compute='_compute_operating_unit_id_domain')
    sec_position = fields.Char(string="Sec Plaza", required=True)

    income_mechanism_id = fields.Many2one('onsc.legajo.income.mechanism', string='Mecanismo de ingreso')
    call_number = fields.Char(string='Número de llamado')
    legajo_state = fields.Selection(
        [('active', 'Activo'), ('baja', 'Baja'), ('outgoing_commission', 'Comisión saliente'),
         ('incoming_commission', 'Comisión entrante')], string='Estado')
    cs_contract_id = fields.Many2one('hr.contract', string='Contrato cs')
    first_name = fields.Char(string=u'Primer nombre', related='employee_id.cv_first_name')
    second_name = fields.Char(string=u'Segundo nombre', related='employee_id.cv_second_name')
    last_name_1 = fields.Char(string=u'Primer apellido', related='employee_id.cv_last_name_1')
    last_name_2 = fields.Char(string=u'Segundo apellido', related='employee_id.cv_last_name_2')
    emissor_country_id = fields.Many2one('res.country', string=u'País emisor del documento',
                                         related='employee_id.cv_emissor_country_id')
    document_type_id = fields.Many2one('onsc.cv.document.type', string=u'Tipo de documento',
                                       related='employee_id.cv_document_type_id')
    nro_doc = fields.Char(u'Número de documento', related='employee_id.cv_nro_doc')
    program = fields.Char(string='Programa')
    project = fields.Char(string='Proyecto')
    regime_id = fields.Many2one('onsc.legajo.regime', string='Régimen')
    occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación')
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor1')
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor2')
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor3')
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor4')
    graduation_date = fields.Date(string='Fecha de graduación')
    position = fields.Char(string='Puesto')
    workplace = fields.Char(string='Plaza')
    reason_discharge = fields.Char(string='Descripción del motivo alta')
    norm_code_discharge_id = fields.Many2one('onsc.legajo.norm', string='Código de norma alta')
    norm_number_discharge = fields.Integer(string='Número de norma alta',
                                           related='norm_code_discharge_id.numeroNorma')
    norm_year_discharge = fields.Integer(string='Año de norma alta', related='norm_code_discharge_id.anioNorma')
    norm_article_discharge = fields.Integer(string='Artículo de norma alta',
                                            related='norm_code_discharge_id.articuloNorma')
    resolution_description_discharge = fields.Char(string='Descripción de la resolución')
    resolution_date_discharge = fields.Date(string='Fecha de la resolución')
    resolution_type_discharge = fields.Selection(
        [('m', 'Inciso'), ('p', 'Presidencia o Poder ejecutivo'), ('u', 'Unidad ejecutora')],
        string='Tipo de resolución alta')
    contract_expiration_date = fields.Date(string='Vencimiento del contrato')
    additional_information_discharge = fields.Char(string='Información adicional alta')
    code_day = fields.Char(string="Código de la jornada")
    description_day = fields.Char(string="Descripción de la Jornada")
    retributive_day_id = fields.Many2one('onsc.legajo.jornada.retributiva', string='Jornada retributiva')
    id_registration_discharge = fields.Char(string='Id de alta')
    id_deregistration_discharge = fields.Char(string='Id de baja')
    reason_deregistration = fields.Char(string='Descripción del motivo baja')
    norm_code_deregistration_id = fields.Many2one('onsc.legajo.norm', string='Código de la norma de baja')
    norm_number_deregistration = fields.Integer(string='Número de norma baja',
                                                related='norm_code_deregistration_id.numeroNorma')
    norm_year_deregistration = fields.Integer(string='Año de norma baja',
                                              related='norm_code_deregistration_id.anioNorma')
    norm_article_deregistration = fields.Integer(string='Artículo de norma baja',
                                                 related='norm_code_deregistration_id.articuloNorma')
    resolution_description_deregistration = fields.Char(string='Descripción de la resolución baja')
    resolution_date_deregistration = fields.Date(string='Fecha de la resolución baja')
    resolution_type_deregistration = fields.Selection(
        [('m', 'Inciso'), ('p', 'Presidencia o Poder ejecutivo'), ('u', 'Unidad ejecutora')],
        string='Tipo de resolución baja')
    causes_discharge_id = fields.Many2one("onsc.legajo.causes.discharge", string="Causal de egreso")
    causes_discharge_extended = fields.Char(string='Causal de egreso extendida')
    code_cgn = fields.Char(string='Código CGN', related='causes_discharge_id.code_cgn')
    additional_information_deregistration = fields.Char(string='Información adicional baja')
    attached_document_discharge_ids = fields.One2many('onsc.legajo.attached.document',
                                                      'contract_id',
                                                      string='Documentos adjuntos alta',
                                                      domain=[('type', '=', 'discharge')])
    attached_document_deregistration_ids = fields.One2many('onsc.legajo.attached.document',
                                                           'contract_id',
                                                           string='Documentos adjuntos baja',
                                                           domain=[('type', '=', 'deregistration')])
    job_ids = fields.One2many('hr.job', 'contract_id', string='Puestos')

    @api.onchange('inciso_id')
    def onchange_inciso(self):
        self.operating_unit_id = False

    @api.onchange('employee_id', 'sec_position')
    def onchange_employee(self):
        if self.employee_id:
            name = self.employee_id.cv_nro_doc if self.employee_id.cv_nro_doc else ''
            if self.employee_id.name and self.sec_position:
                name += ' - '
            if self.sec_position:
                name += self.sec_position if self.sec_position else ''
            self.name = name
        else:
            self.name = False

    @api.depends('date_start', 'date_end', 'inciso_id')
    def _compute_operating_unit_id_domain(self):
        for rec in self:
            if rec.inciso_id.id is False:
                self.operating_unit_id_domain = json.dumps([('id', 'in', [])])
            else:
                domain = [('inciso_id', '=', rec.inciso_id.id)]
                if rec.date_start:
                    domain = ['&'] + domain + [('start_date', '<=', fields.Date.to_string(rec.date_start))]
                if rec.date_end:
                    domain = ['&'] + domain + ['|', ('end_date', '>=', fields.Date.to_string(rec.date_end)),
                                               ('end_date', '=', False)]
                self.operating_unit_id_domain = json.dumps(domain)
