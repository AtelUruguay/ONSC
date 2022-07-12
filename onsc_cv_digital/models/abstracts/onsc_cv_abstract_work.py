# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

WORKING_STATE = [('yes', 'Sí'), ('no', 'No')]
PAID_ACTIVITY_TYPES = WORKING_STATE


class ONSCCVAbstractWork(models.AbstractModel):
    _name = 'onsc.cv.abstract.work'
    _description = 'Modelo abstracto para modelos de trabajos'

    # TO-DO: Revisar este campo, No esta en catalogo
    # inciso = fields.Char("Inciso")
    # TO-DO: Revisar este campo, No esta en catalogo
    # executing_unit = fields.Char("Unidad ejecutora")
    hours_worked_monthly = fields.Integer("Cantidad de horas trabajadas mensualmente", required=True,
                                          help='“En caso de no disponer las horas se debe estimar')
    description_tasks = fields.Char(string="Descripción de tareas", required=False)
    start_date = fields.Date("Período desde", required=True)
    end_date = fields.Date("Período hasta", required=False)
    currently_working = fields.Selection(string="Actualmente trabajando", selection=WORKING_STATE, required=True)
    position = fields.Char("Cargo", required=True)
    is_paid_activity = fields.Selection(string="¿Actividad remunerada?", selection=PAID_ACTIVITY_TYPES, required=True)

    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            self.end_date = self.start_date

    @api.onchange('hours_worked_monthly')
    def onchange_hours_worked_monthly(self):
        if self.hours_worked_monthly and self.hours_worked_monthly < 45:
            return {
                'warning': {
                    'title': _("Atención"),
                    'type': 'notification',
                    'message': _(
                        "Advertencia la carga horaria mensual es menor que 45 horas"
                    )
                },

            }
