# -*- coding: utf-8 -*-

from odoo import fields, models, api

STATES = [
    ('A', 'Abierto'),
    ('N', 'Anulado'),
    ('C', 'Concluido'),
    ('E', 'Eliminado'),
    ('R', 'Remitido'),
    ('S', 'Resolución'),
]
SNSELECTION = [
    ('s', 'Si'),
    ('n', 'No'),
]


class ONSCLegajoSummary(models.Model):
    _name = "onsc.legajo.summary"
    _description = 'Sumario'
    _inherit = [
        'onsc.legajo.abstract.opaddmodify.security'
    ]

    last_update_date = fields.Date(string="Última actualización", readonly=True)
    emissor_country = fields.Char(u'País emisor del documento')
    document_type = fields.Char(u'Tipo de documento')
    nro_doc = fields.Char(u'Número de documento')
    inciso_code = fields.Integer("Inciso")
    inciso_name = fields.Char("Nombre Inciso")
    operating_unit_code = fields.Char("UE")
    operating_unit_name = fields.Char("Nombre UE")
    regime = fields.Char("Regimen")
    relationship_date = fields.Date(u"Fecha del vínculo")
    state = fields.Selection(STATES, string='Estado del sumario')
    summary_causal = fields.Char("Causal de sumario")
    act_date = fields.Date("Fecha del acto")
    interrogator_notify_date = fields.Date("Fecha de notificación al sumariante")
    summary_notify_date = fields.Date("Fecha de notificación al sumariado")
    summary_detail = fields.Char("Detalle de sanción")
    suspension = fields.Selection(SNSELECTION, string='Suspensión preventiva')
    start_date_suspension = fields.Date("Inicio")
    end_date_suspension = fields.Date("Fin")
    retention_percentage = fields.Float("Retención de haberes con porcentajes")
    instructor_name = fields.Char("Nombre completo")
    instructor_email = fields.Char("Correo electrónico")
    penalty_type_id = fields.Many2one("onsc.legajo.penalty.type", string=u"Tipo de sanción")
    communications_ids = fields.One2many("onsc.legajo.summary.communications",
                                         inverse_name="summary_id",
                                         string="Comunicaciones del sumario")
    cv_document_type_id = fields.Many2one('onsc.cv.document.type', u'Tipo de documento')  # tipo_doc
    country_id = fields.Many2one('res.country', u'País')  # cod_pais
    legajo_id = fields.Many2one(comodel_name="onsc.legajo", string="Legajo")
    summary_number = fields.Char(u'Número de sumario')
    record_number = fields.Char(u'Número de expediente')
    instructor_doc_number = fields.Char("Número documento ")
    display_inciso = fields.Char('Inciso', compute='_compute_display_inciso')
    display_ue = fields.Char('UE', compute='_compute_display_ue')
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora")

    @api.depends('operating_unit_code', 'operating_unit_id', 'operating_unit_name')
    def _compute_display_ue(self):
        for rec in self:
            if rec.operating_unit_id:
                rec.display_ue = rec.operating_unit_id.budget_code + '_' + rec.inciso_id.name
            else:
                rec.display_ue = rec.operating_unit_code + '_' + rec.operating_unit_name

    @api.depends('inciso_id', 'inciso_code', 'inciso_name')
    def _compute_display_ue(self):
        for rec in self:
            if rec.inciso_id:
                rec.display_inciso = rec.inciso_id.budget_code + '_' + rec.inciso_id.name
            else:
                rec.display_inciso = rec.inciso_code + '_' + rec.inciso_name

    def button_open_current_summary(self):
        action = self.sudo().env.ref('onsc_legajo.onsc_legajo_summary_action').read()[0]
        action.update({'res_id': self.id})
        return action


class ONSCLegajoSummaryComunications(models.Model):
    _name = "onsc.legajo.summary.communications"
    _description = 'Comunicaciones del sumario'
    _inherit = [
        'onsc.legajo.abstract.opaddmodify.security'
    ]

    summary_id = fields.Many2one("onsc.legajo.summary", string=u"Sumario")
    communication_date = fields.Date("Fecha")
    instance = fields.Char("Instancia")
    communication_type = fields.Char(u"Tipo de comunicación")
