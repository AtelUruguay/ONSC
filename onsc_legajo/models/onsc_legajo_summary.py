# -*- coding: utf-8 -*-

from odoo import fields, models

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

    last_update_date = fields.Date(string="Fecha inicio", readonly=True)
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
    legajo_id = fields.Many2one(comodel_name="onsc.legajo", string="Legajo", index=True)


class ONSCLegajoSummaryComunications(models.Model):
    _name = "onsc.legajo.summary.communications"
    _description = 'Comunicaciones del sumario'

    summary_id = fields.Many2one("onsc.legajo.summary", string=u"Sumario", required=True, index=True)
    communication_date = fields.Date("Fecha")
    instance = fields.Char("Instancia")
    communication_type = fields.Char(u"Tipo de comunicación")
