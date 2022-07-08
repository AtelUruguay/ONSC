# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ONSCCVAbstractWork(models.AbstractModel):
    _name = 'onsc.cv.abstract.work'
    _description = 'Modelo abstracto para modelos de trabajos'

    country_id = fields.Many2one("res.country", string="País", required=True)
    country_code = fields.Char("Código", related="country_id.code", readonly=True)
    company_type = fields.Selection([('public', 'Pública'), ('private', 'Privada')], string="Tipo de empresa",
                                    required=True)
    # TO-DO: Revisar este campo, No esta en catalogo
    # inciso = fields.Char("Inciso")
    # TO-DO: Revisar este campo, No esta en catalogo
    # executing_unit = fields.Char("Unidad ejecutora")
    company_name = fields.Char("Empresa")
    hours_worked_monthly = fields.Integer("Cantidad de horas trabajadas mensualmente", required=True)
    description_tasks = fields.Char(string="Descripción de tareas", required=True)
    receipt_file = fields.Binary("Comprobante", required=True)
    start_date = fields.Date("Período desde", required=True)
    end_date = fields.Date("Período hasta", required=True)

    @api.onchange('start_date', 'end_date')
    def onchange_date_validation(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.start_date > rec.end_date:
                rec.start_date = False
                return {
                    'warning': {
                        'title': _("Atención"),
                        'type': 'notification',
                        'message': _(
                            "El período de inicio debe ser anterior a la período de finalización"
                        )
                    },

                }


class ONSCCVDigitalOriginInstitutionTask(models.Model):
    _name = 'onsc.cv.origin.institution.task'
    _description = 'Tareas realizadas'

    key_task_id = fields.Many2one("onsc.cv.key.task", string="Tareas clave", required=True)
    area_id = fields.Many2one("onsc.cv.work.area", string="Área de trabajo donde se aplicó la tarea clave",
                              required=True)
