# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as warning_response


class ONSCLegajoMerito(models.Model):
    _name = "onsc.legajo.merito"
    _description = 'Mérito'
    _inherit = [
        'onsc.legajo.abstract.opaddmodify.security',
        'model.history'
    ]
    _history_model = 'onsc.legajo.merito.history'
    _tree_history_columns = [
        'inciso_id',
        'operating_unit_id',
        'title',
        'notification_date',
        'document_date',
        'digital_filename',
        'description',
    ]

    def _is_group_admin_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_hr_admin')

    def _is_group_inciso_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_hr_inciso')

    def _is_group_ue_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_hr_ue')

    def _is_group_consulta_security(self):
        return self.user_has_groups('onsc_legajo.group_legajo_consulta_legajos,onsc_legajo.group_legajo_consulta_milegajos')

    title = fields.Char(string="Título", required=True, history=True)
    document_date = fields.Date(string="Fecha del documento", required=True, history=True)
    digital_file = fields.Binary(string="Documento digitalizado", required=True, history=True)
    digital_filename = fields.Char(string="Documento digitalizado", required=True, history=True)
    description = fields.Text(string="Descripción del mérito", required=True, history=True)
    notification_date = fields.Date(string="Fecha de notificación", required=True, history=True)
    legajo_id = fields.Many2one(comodel_name="onsc.legajo", string="Legajo", required=True)

    @api.constrains("document_date")
    def _check_document_date(self):
        for record in self:
            if record.document_date > fields.Date.today():
                raise ValidationError("La fecha del documento debe ser menor o igual al día de hoy")

    @api.constrains("notification_date")
    def _check_notification_date(self):
        for record in self:
            if record.notification_date > fields.Date.today():
                raise ValidationError("La fecha de notificación debe ser menor o igual al día de hoy")

    @api.onchange('document_date')
    def onchange_document_date(self):
        if self.document_date and self.document_date > fields.Date.today():
            self.document_date = False
            return warning_response(_(u"La Fecha de documento debe ser menor o igual al día de hoy"))

    @api.onchange("notification_date")
    def onchange_notification_date(self):
        if self.notification_date and self.notification_date > fields.Date.today():
            self.notification_date = False
            return warning_response(_(u"La fecha de notificación debe ser menor o igual al día de hoy"))

    def button_show_history(self):
        model_view_form_id = self.env.ref('onsc_legajo.onsc_legajo_merito_form').id
        return self.with_context(model_view_form_id=model_view_form_id, as_of_date=fields.Date.today()).get_history_record_action(
            history_id=False,
            res_id=self.id,
        )

class ONSCLegajoHistory(models.Model):
    _inherit = ['model.history.data']
    _name = 'onsc.legajo.merito.history'
    _parent_model = 'onsc.legajo.merito'

    history_digital_file = fields.Binary(string="Documento digitalizado")
