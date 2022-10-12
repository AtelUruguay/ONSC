# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as cv_warning


class ONSCCVDigitalVolunteering(models.Model):
    _name = 'onsc.cv.volunteering'
    _inherit = 'onsc.cv.abstract.work'
    _description = 'Voluntariado'

    unit_name = fields.Char("Área/Unidad")
    volunteering_task_ids = fields.One2many("onsc.cv.volunteering.task", inverse_name="volunteering_id",
                                            copy=True,
                                            string="Tareas")
    currently_volunteering = fields.Selection(string="Voluntario actualmente", selection=[('si', 'Si'), ('no', 'No')],
                                              required=True, )
    hours_monthly = fields.Char("Cantidad de horas mensuales", required=True,
                                help='“En caso de no disponer las horas se debe estimar')

    @api.onchange('hours_monthly')
    def onchange_hours_monthly(self):
        if self.hours_monthly and not (self.hours_monthly.isnumeric()):
            self.hours_monthly = ''.join(filter(str.isdigit, self.hours_monthly))
            return cv_warning(_("La Cantidad de horas mensuales no puede contener letras"))

    def _get_json_dict(self):
        json_dict = super(ONSCCVDigitalVolunteering, self)._get_json_dict()
        json_dict.extend([
            "position",
            "is_paid_activity",
            ("country_id", ['id', 'name']),
            "company_type",
            "company_name",
            "description_tasks",
            "start_date",
            "end_date",
            "unit_name",
            "currently_volunteering",
            "hours_monthly",
            ("volunteering_task_ids", [
                'id',
                'name',
                ("key_task_id", ['id', 'name']),
                ("area_id", ['id', 'name']),
            ]),
        ])
        return json_dict


class ONSCCVDigitalVolunteeringTask(models.Model):
    _name = 'onsc.cv.volunteering.task'
    _description = 'Tareas de voluntariado'

    volunteering_id = fields.Many2one("onsc.cv.volunteering", string="Voluntariado")
    key_task_id = fields.Many2one("onsc.cv.key.task", string="Tareas clave", required=True)
    area_id = fields.Many2one("onsc.cv.work.area", string="Área de trabajo donde se aplicó la tarea clave",
                              required=True)
