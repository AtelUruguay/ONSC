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

    key = fields.Char(string="Llave")
    last_update_date = fields.Date(string="Última actualización", readonly=True)
    emissor_country = fields.Char(u'País emisor del documento')
    document_type = fields.Char(u'Tipo de documento')
    nro_doc = fields.Char(u'Número de documento')
    inciso_code = fields.Integer("Inciso")
    inciso_name = fields.Char("Nombre Inciso")
    operating_unit_code = fields.Integer("UE")
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
    retention_percentage = fields.Char("Retención de haberes con porcentajes")
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
    display_penalty_type = fields.Char(string=u"Tipo de sanción", compute='_compute_display_penalty_type')

    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, record.summary_number))
        return res

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

    @api.depends('penalty_type_id')
    def _compute_display_penalty_type(self):
        for rec in self:
            if rec.penalty_type_id:
                rec.display_penalty_type = '%s - %s' % (rec.penalty_type_id.sudo().code or '', rec.penalty_type_id.sudo().description or '')
            else:
                rec.display_penalty_type = ''

    def _compute_show_button_open_summary(self):
        inciso_id, operating_unit_id = self.get_inciso_operating_unit_by_user()
        for record in self:
            is_editable_ue = record.operating_unit_id.id == operating_unit_id.id and self.user_has_groups('onsc_legajo.group_legajo_hr_ue')
            is_editable_inciso = record.inciso_id.id == inciso_id.id and self.user_has_groups('onsc_legajo.group_legajo_hr_inciso')
            record.show_button_open_summary = is_editable_ue or is_editable_inciso or record.state == 'C' or record.legajo_id.employee_id.user_id.id == self.env.user.id

    @api.depends('country_id', 'cv_document_type_id', 'nro_doc')
    def _compute_legajo_id(self):
        Legajo = self.env['onsc.legajo'].suspend_security()
        for record in self:
            record.legajo_id = Legajo.search([('emissor_country_id', '=', record.country_id.id),
                                              ('document_type_id', '=', record.cv_document_type_id.id),
                                              ('nro_doc', '=', record.nro_doc)
                                              ], limit=1).id

    @api.depends('inciso_code')
    def _compute_inciso_id(self):
        Inciso = self.env['onsc.catalog.inciso'].suspend_security()
        for record in self:
            inciso_id = Inciso.search([('budget_code', '=', record.inciso_code)], limit=1)
            if inciso_id:
                record.inciso_id = inciso_id.id
                record.inciso_name = inciso_id.name

    @api.depends('operating_unit_code', 'inciso_id')
    def _compute_operating_unit_id(self):
        OperatingUnit = self.env['operating.unit'].suspend_security()
        for record in self:

            operating_unit_id = OperatingUnit.search([
                ('budget_code', '=', record.operating_unit_code),
                ('inciso_id', '=', record.inciso_id.id)
            ], limit=1)

            if operating_unit_id:
                record.operating_unit_id = operating_unit_id.id
                record.operating_unit_name = operating_unit_id.name

    def button_open_current_summary(self):
        action = self.sudo().env.ref('onsc_legajo.onsc_legajo_summary_form_action').read()[0]
        action.update({'res_id': self.id})
        return action

    def get_inciso_operating_unit_by_user(self):
        inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
        operating_unit_id = self.env.user.employee_id.job_id.contract_id.operating_unit_id
        return inciso_id, operating_unit_id

    def _has_summary(self, country_id, cv_document_type_id, nro_doc):
        """
        Check if a summary exists with the given criteria.

        This method searches for records that match the specified country, document type,
        document number, and penalty type warning. It returns True if at least one record
        is found, otherwise False.

        Args:
            country_id (recordset): The country record to match.
            cv_document_type_id (recordset): The document type record to match.
            nro_doc (str): The document number to match.
            baja_vl(Boolean): Si es baja_vl el criterio de summario es distinto
            (no tenga un sumario en estado diferente de Confirmado en el Inciso/UE del vínculo)

        Returns:
            bool: True if a matching record is found, False otherwise.
        """
        return self.suspend_security().search_count([
            ('country_id', '=', country_id.id),
            ('cv_document_type_id', '=', cv_document_type_id.id),
            ('nro_doc', '=', nro_doc),
            ('penalty_type_id.warning', '=', 's')]) > 0

    def _update_empty_legajo_records(self, legajo):
        """
        Updates empty legajo records with the given legajo information.

        This method searches for records with matching country, document type,
        and document number, and updates their legajo_id with the provided legajo's id.

        Args:
            legajo (record): The legajo record containing the information to update
                             the empty legajo records.

        Returns:
            None
        """
        self.suspend_security().search([
            ('country_id', '=', legajo.emissor_country_id.id),
            ('cv_document_type_id', '=', legajo.document_type_id.id),
            ('nro_doc', '=', legajo.nro_doc),
            ('legajo_id', '=', False)
        ]).write({'legajo_id': legajo.id})


class ONSCLegajoSummaryComunications(models.Model):
    _name = "onsc.legajo.summary.communications"
    _description = 'Comunicaciones del sumario'

    summary_id = fields.Many2one("onsc.legajo.summary", string=u"Sumario", required=True, index=True, ondelete='cascade')
    communication_date = fields.Date("Fecha")
    instance = fields.Char("Instancia")
    communication_type = fields.Char(u"Tipo de comunicación")
