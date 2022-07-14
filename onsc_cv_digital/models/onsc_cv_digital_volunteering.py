# -*- coding: utf-8 -*-
from odoo import fields, models


class ONSCCVDigitalVolunteering(models.Model):
    _name = 'onsc.cv.volunteering'
    _inherit = 'onsc.cv.abstract.work'
    _description = 'Voluntariado'

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", index=True, ondelete='cascade')
    unit_name = fields.Char("Área/Unidad")
    volunteering_task_ids = fields.One2many("onsc.cv.volunteering.task", inverse_name="volunteering_id",
                                            string="Tareas")
    currently_volunteering = fields.Selection(string="Voluntario actualmente", selection=[('si', 'Si'), ('no', 'No')],
                                              required=True, )
    hours_monthly = fields.Integer("Cantidad de horas trabajadas mensualmente", required=True,
                                   help='“En caso de no disponer las horas se debe estimar')


class ONSCCVDigitalVolunteeringTask(models.Model):
    _name = 'onsc.cv.volunteering.task'
    _inherit = 'onsc.cv.origin.abstract.task'
    _description = 'Tareas de voluntariado'

    volunteering_id = fields.Many2one("onsc.cv.volunteering", string="Voluntariado", ondelete='cascade')
