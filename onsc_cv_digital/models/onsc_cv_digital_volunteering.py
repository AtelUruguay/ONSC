# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVDigitalVolunteering(models.Model):
    _name = 'onsc.cv.volunteering'
    _description = 'Voluntariado'
    _inherit = 'onsc.cv.abstract.origin.institution'

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", index=True)
    unit_name = fields.Char("Área/Unidad")
    volunteering_task_ids = fields.One2many("onsc.cv.origin.institution.task", inverse_name="volunteering_id",
                                            string="Tareas", required=False, )
    currently_volunteering = fields.Selection(string="Voluntario actualmente", selection=[('si', 'Si'), ('no', 'No')],
                                              required=True, )


class ONSCCVDigitalVolunteeringTask(models.Model):
    _description = 'Tareas realizadas'
    _inherit = 'onsc.cv.origin.institution.task'

    volunteering_id = fields.Many2one("onsc.cv.volunteering", string="Voluntariado", index=True)
