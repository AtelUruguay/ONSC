# -*- coding: utf-8 -*-
from odoo import fields, models


class ONSCLegajoWorkExperience(models.Model):
    _name = 'onsc.legajo.work.experience'
    _inherit = 'onsc.cv.work.experience'
    _description = 'Legajo - Experiencia laboral'

    employee_id = fields.Many2one("hr.employee", string=u"Funcionario")
    legajo_id = fields.Many2one("onsc.legajo", string=u"Legajo")
    origin_work_experience_id = fields.Many2one("onsc.cv.work.experience", string=u"Experiencia laboral origen")

    task_ids = fields.One2many("onsc.legajo.work.experience.task", inverse_name="legajo_work_experience_id",
                               string="Tareas", copy=True)

class ONSCLegajoOriginInstitutionTask(models.Model):
    _name = 'onsc.legajo.work.experience.task'
    _inherit = 'onsc.cv.work.experience.task'
    _description = 'Legajo - Tareas de experiencia laboral'

    legajo_work_experience_id = fields.Many2one(
        "onsc.legajo.work.experience",
        string="Experiencia laboral",
        ondelete='cascade'
    )

