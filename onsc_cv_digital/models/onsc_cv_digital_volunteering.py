# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ONSCCVDigitalVolunteering(models.Model):
    _name = 'onsc.cv.volunteering'
    _description = 'Voluntariado'

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", index=True)
    country_id = fields.Many2one("res.country", string="País de la institución", required=True)
    company_type = fields.Selection([('public', 'Pública'), ('private', 'Privada')], string="Tipo de empresa",
                                    required=True)
    country_code = fields.Char("Código", related="country_id.code", readonly=True)
    # TO-DO: Revisar este campo, No esta en catalogo
    # inciso = fields.Char("Inciso")
    # TO-DO: Revisar este campo, No esta en catalogo
    # executing_unit = fields.Char("Unidad ejecutora")
    company_name = fields.Char("Empresa")
    unit_name = fields.Char("Área/Unidad")
    description_tasks = fields.Char(string="Descripción de tareas", required=True)
    volunteering_task_ids = fields.One2many("onsc.cv.volunteering.task", inverse_name="volunteering_id",
                                            string="Tareas", required=False, )
    start_date = fields.Date("Período desde", required=True)
    currently_volunteering = fields.Selection(string="Voluntario actualmente", selection=[('si', 'Si'), ('no', 'No')],
                                              required=True, )
    end_date = fields.Date("Período hasta", required=True)
    hours_monthly = fields.Integer("Cantidad de horas mensuales", required=True)
    receipt_file = fields.Binary("Comprobante", required=True)
    receipt_description = fields.Char("Descripción del comprobante")

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


class ONSCCVDigitalVolunteeringTask(models.Model):
    _name = 'onsc.cv.volunteering.task'
    _description = 'Tareas realizadas'

    volunteering_id = fields.Many2one("onsc.cv.volunteering", string="Voluntariado", index=True)
    key_task_id = fields.Many2one("onsc.cv.key.task", string="Tareas clave", required=True)
    work_area_id = fields.Many2one("onsc.cv.work.area", string="Área de trabajo donde se aplicó la tarea clave",
                                   required=True)
