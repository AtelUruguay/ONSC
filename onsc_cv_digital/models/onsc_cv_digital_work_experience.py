# -*- coding: utf-8 -*-
from odoo import fields, models


class ONSCCVDigitalWorkExperience(models.Model):

    _name = 'onsc.cv.work.experience'
    _description = 'Experiencia laboral'
    _inherit = 'onsc.cv.abstract.origin.institution'

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", index=True)
    position = fields.Char("Cargo", required=True)
    city_id = fields.Many2one("onsc.cv.location", string="Ciudad donde desempeñó", required=True)
    unit_name = fields.Char("Área/Unidad")
    entry_institution_id = fields.Many2one("onsc.cv.entry", string="Rubro de la institución", required=True)
    hierarchical_level_id = fields.Many2one("onsc.cv.experience.hierarchical.level", string="Nivel jerárquico",
                                            required=True)
    take_decisions = fields.Selection([('operative', 'Toma decisiones de la operativa'),
                                       ('strategic', 'Toma decisiones a nivel estratégico y de dirección')],
                                      string="Toma decisiones", required=True)
    is_paid_activity = fields.Selection(string="¿Actividad remunerada?", selection=[('si', 'Si'), ('no', 'No'), ],
                                        required=True, )
    people_charge = fields.Integer("Cantidad de personas a cargo", required=True)
    organizational_units_charge = fields.Integer("Cantidad de unidades organizativas a cargo", required=True)
    currently_working = fields.Selection(string="Actualmente trabajando", selection=[('si', 'Si'), ('no', 'No')],
                                         required=True, )
    # TO-DO: Revisar este campo, No esta en catalogo
    # reason_discharge = fields.Char("Causal de egreso")
    task_ids = fields.One2many("onsc.cv.origin.institution.task", inverse_name="work_experience_id",
                               string="Tareas", required=False, )


class ONSCCVDigitalOriginInstitutionTask(models.Model):
    _inherit = 'onsc.cv.origin.institution.task'

    work_experience_id = fields.Many2one("onsc.cv.work.experience", string="Experiencia laboral", index=True)
