# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as cv_warning

WORKING_STATE = [('yes', 'Sí'), ('no', 'No')]
PAID_ACTIVITY_TYPES = WORKING_STATE


class ONSCCVAbstractWork(models.AbstractModel):
    _name = 'onsc.cv.abstract.work'
    _inherit = ['onsc.cv.abstract.documentary.validation']
    _description = 'Modelo abstracto para modelos de trabajos'

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", index=True, ondelete='cascade', required=True)
    hours_worked_monthly = fields.Integer("Cantidad de horas trabajadas mensualmente")
    currently_working = fields.Selection(string="Actualmente trabajando", selection=WORKING_STATE)
    position = fields.Char("Cargo")
    is_paid_activity = fields.Selection(string="¿Actividad remunerada?", selection=PAID_ACTIVITY_TYPES)
    country_id = fields.Many2one("res.country", string="País", required=True)
    country_code = fields.Char("Código", related="country_id.code", readonly=True)
    company_type = fields.Selection([('public', 'Pública'),
                                     ('private', 'Privada'),
                                     ('both', 'Pública/Privada')],
                                    string="Tipo de empresa")
    company_name = fields.Char("Empresa")
    description_tasks = fields.Char(string="Descripción de tareas")
    receipt_file = fields.Binary("Comprobante")
    receipt_filename = fields.Char('Nombre del documento digital')
    receipt_description = fields.Char("Descripción del comprobante")
    start_date = fields.Date("Período desde", required=True)
    end_date = fields.Date("Período hasta")

    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date and self.start_date > fields.Date.today():
            self.start_date = False
            return cv_warning(_(u"El período desde debe ser menor que la fecha actual"))
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.start_date = False
            return cv_warning(_("El período desde no puede ser mayor que el período hasta"))

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date and self.end_date > fields.Date.today():
            self.end_date = False
            return cv_warning(_(u"El período hasta debe ser menor que la fecha actual"))
        if self.end_date and self.start_date and self.end_date < self.start_date:
            self.end_date = False
            return cv_warning(_("El período hasta no puede ser menor que el período desde"))

    @api.onchange('hours_worked_monthly')
    def onchange_hours_worked_monthly(self):
        if self.hours_worked_monthly and self.hours_worked_monthly < 45:
            return cv_warning(_("Advertencia: la carga horaria mensual es menor que 45 horas"))


class ONSCCVDigitalOriginInstitutionTask(models.AbstractModel):
    _name = 'onsc.cv.origin.abstract.task'
    _description = 'Tareas realizadas'

    key_task_id = fields.Many2one("onsc.cv.key.task", string="Tareas clave", required=True)
    area_id = fields.Many2one("onsc.cv.work.area", string="Área de trabajo donde se aplicó la tarea clave",
                              required=True)


class ONSCCVWorkInvestigationReceiptFile(models.AbstractModel):
    _name = 'onsc.cv.work.abstract.receipt.file'
    _description = 'Grilla de comprobantes'

    receipt_file = fields.Binary("Comprobante", required=True)
    receipt_filename = fields.Char('Nombre del documento digital', required=True)
    receipt_description = fields.Char("Descripción del comprobante", required=True)
