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
    summary_number = fields.Char(u'Número de sumario')
    record_number = fields.Char(u'Número de expediente')
    instructor_doc_number = fields.Char("Número documento")
    observations = fields.Char("Observaciones")
    display_inciso = fields.Char('Inciso', compute='_compute_display_inciso')
    display_ue = fields.Char('UE', compute='_compute_display_ue')
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', compute='_compute_inciso_id', store=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora",
                                        compute='_compute_operating_unit_id', store=True)
    cv_document_type_id = fields.Many2one('onsc.cv.document.type', u'Tipo de documento')
    country_id = fields.Many2one('res.country', u'País')
    legajo_id = fields.Many2one(comodel_name="onsc.legajo", string="Legajo", compute='_compute_legajo_id', store=True,
                                index=True)
    show_button_open_summary = fields.Boolean('Mostrar button abrir sumarios ',
                                              compute='_compute_show_button_open_summary')

    @api.depends('operating_unit_code', 'operating_unit_name')
    def _compute_display_ue(self):
        for rec in self:
            if rec.operating_unit_code or rec.operating_unit_name:
                rec.display_ue = '%s - %s' % (rec.operating_unit_code or '', rec.operating_unit_name or '')
            else:
                rec.display_ue = ''

    @api.depends('inciso_code', 'inciso_name')
    def _compute_display_inciso(self):
        for rec in self:
            if rec.inciso_code or rec.inciso_name:
                rec.display_inciso = '%s - %s' % (rec.inciso_code or '', rec.inciso_name or '')
            else:
                rec.display_inciso = ''

    def _compute_show_button_open_summary(self):
        inciso_id, operating_unit_id = self.get_inciso_operating_unit_by_user()
        for record in self:
            is_editable_ue = record.operating_unit_id.id == operating_unit_id
            is_editable_inciso = record.inciso_id.id == inciso_id
            record.show_button_open_summary = is_editable_ue or is_editable_inciso or record.state == 'C' or record.legajo_id.employee_id.user_id.id == self.env.user.id

    @api.depends('country_id', 'cv_document_type_id', 'nro_doc')
    def _compute_legajo_id(self):
        Legajo = self.env['onsc.legajo'].suspend_security()
        for record in self:
            record.legajo_id = Legajo.search([('emissor_country_id', '=', record.country_id.id),
                                              ('document_type_id', '=', record.cv_document_type_id.id),
                                              ('nro_doc', '=', record.nro_doc)
                                              ], limit=1)

    @api.depends('inciso_code')
    def _compute_inciso_id(self):
        Inciso = self.env['onsc.catalog.inciso'].suspend_security()
        for record in self:
            record.inciso_id = Inciso.search([('budget_code', '=', record.inciso_code)], limit=1)

    @api.depends('operating_unit_code','inciso_id')
    def _compute_operating_unit_id(self):
        OperatingUnit = self.env['operating.unit'].suspend_security()
        for record in self:
            record.operating_unit_id = OperatingUnit.search([('budget_code', '=', record.operating_unit_code),
                                                             ('inciso_id''=', record.inciso_id)], limit=1)

    def button_open_current_summary(self):
        action = self.sudo().env.ref('onsc_legajo.onsc_legajo_summary_form_action').read()[0]
        action.update({'res_id': self.id})
        return action

    def get_inciso_operating_unit_by_user(self):
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id
        return inciso_id, operating_unit_id

    def _has_summary(self, country_id, cv_document_type_id, nro_doc):
        summary = self.suspend_security().search_count([('country_id', '=', country_id.id),
                                                     ('cv_document_type_id', '=', cv_document_type_id.id),
                                                     ('nro_doc', '=', nro_doc), ('penalty_type_id.warning', '=', 's')])
        if len(summary) > 0:
            return True

        return False


class ONSCLegajoSummaryComunications(models.Model):
    _name = "onsc.legajo.summary.communications"
    _description = 'Comunicaciones del sumario'

    summary_id = fields.Many2one("onsc.legajo.summary", string=u"Sumario", required=True, index=True)
    communication_date = fields.Date("Fecha")
    instance = fields.Char("Instancia")
    communication_type = fields.Char(u"Tipo de comunicación")
