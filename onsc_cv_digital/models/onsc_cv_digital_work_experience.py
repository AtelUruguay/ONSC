# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as cv_warning


class ONSCCVDigitalWorkExperience(models.Model):
    _name = 'onsc.cv.work.experience'
    _inherit = ['onsc.cv.abstract.work', 'onsc.cv.abstract.conditional.state']
    _description = 'Experiencia laboral'
    _catalogs_2validate = ['city_id']

    city_id = fields.Many2one("onsc.cv.location", string="Ciudad donde desempeñó", required=True)
    unit_name = fields.Char("Área/Unidad")
    entry_institution_id = fields.Many2one("onsc.cv.entry", string="Rubro de la institución", required=True)
    hierarchical_level_id = fields.Many2one("onsc.cv.experience.hierarchical.level", string="Nivel jerárquico",
                                            required=True)
    take_decisions = fields.Selection([('operative', 'Toma decisiones de la operativa'),
                                       ('strategic', 'Toma decisiones a nivel estratégico y de dirección')],
                                      string="Toma decisiones", required=True)
    people_charge_qty = fields.Integer("Cantidad de personas a cargo", required=True)
    organizational_units_charge = fields.Integer("Cantidad de unidades organizativas a cargo", required=True)
    # TO-DO: Revisar este campo, No esta en catalogo
    # reason_discharge = fields.Char("Causal de egreso")
    task_ids = fields.One2many("onsc.cv.work.experience.task", inverse_name="work_experience_id",
                               string="Tareas", copy=True)

    @api.onchange('country_id')
    def onchange_country_id(self):
        if self.city_id.country_id.id != self.country_id.id:
            self.city_id = False

    @api.onchange('city_id')
    def onchange_city_id(self):
        if self.city_id:
            self.country_id = self.city_id.country_id.id

    @api.onchange('task_ids')
    def onchange_task_ids(self):
        if len(self.task_ids) > 5:
            self.task_ids = self.task_ids[-5:]
            return cv_warning(_(u"Sólo se pueden seleccionar 5 tareas"))

    def _get_json_dict(self):
        json_dict = super(ONSCCVDigitalWorkExperience, self)._get_json_dict()
        json_dict.extend([
            "hours_worked_monthly",
            "currently_working",
            "position",
            "is_paid_activity",
            ("country_id", ['id', 'name']),
            "company_type",
            "company_name",
            "description_tasks",
            "start_date",
            "end_date",
            "take_decisions",
            "people_charge_qty",
            "organizational_units_charge",
            "unit_name",
            ("city_id", ['id', 'name']),
            ("entry_institution_id", ['id', 'name']),
            ("hierarchical_level_id", ['id', 'name']),
            ("task_ids", [
                'id',
                'name',
                ("key_task_id", ['id', 'name']),
                ("area_id", ['id', 'name'])
            ]),
        ])
        return json_dict


class ONSCCVDigitalOriginInstitutionTask(models.Model):
    _name = 'onsc.cv.work.experience.task'
    _description = 'Tareas de experiencia laboral'

    work_experience_id = fields.Many2one("onsc.cv.work.experience", string="Experiencia laboral", ondelete='cascade')
    key_task_id = fields.Many2one("onsc.cv.key.task", string="Tareas clave", required=True)
    area_id = fields.Many2one("onsc.cv.work.area", string="Área de trabajo donde se aplicó la tarea clave",
                              required=True)
