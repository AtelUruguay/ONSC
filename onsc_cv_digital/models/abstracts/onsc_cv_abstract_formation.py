# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.addons.onsc_base.onsc_useful_tools import get_onchange_warning_response as cv_warning

STATES = [('incomplete', 'Incompleto'),
          ('in_progress', 'En curso'),
          ('completed', 'Finalizado')]


class ONSCCVAbstractFormation(models.AbstractModel):
    _name = 'onsc.cv.abstract.formation'
    _inherit = ['onsc.cv.abstract.documentary.validation']
    _description = 'Modelo abstracto de entidades de formación'

    cv_digital_id = fields.Many2one('onsc.cv.digital', string=u'CV', required=True, index=True, ondelete='cascade')
    state = fields.Selection(string="Estado", selection=STATES, copy=True)
    start_date = fields.Date(string="Fecha de inicio")
    end_date = fields.Date(string="Fecha finalización")
    other_relevant_information = fields.Text(string="Otra información relevante")
    # Campo para redefinir
    knowledge_acquired_ids = fields.Many2many(
        'onsc.cv.knowledge',
        "Conocimientos adquiridos",
        ondelete='restrict',
        store=False
    )

    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date and self.start_date > fields.Date.today():
            self.start_date = False
            return cv_warning(_(u"La fecha de inicio debe ser menor que la fecha actual"))
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.start_date = False
            return cv_warning(_(u"La fecha de inicio no puede ser mayor que la fecha de finalización"))

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date and self.end_date > fields.Date.today():
            self.end_date = False
            return cv_warning(_(u"La fecha de finalización debe ser menor que la fecha actual"))
        if self.end_date and self.start_date and self.end_date < self.start_date:
            self.end_date = False
            return cv_warning(_(u"La fecha de finalización no puede ser menor que la fecha de inicio"))

    @api.onchange('knowledge_acquired_ids')
    def onchange_knowledge_acquired_ids(self):
        if len(self.knowledge_acquired_ids) > 5:
            self.knowledge_acquired_ids = self.knowledge_acquired_ids[:5]
            return cv_warning(_(u"Sólo se pueden seleccionar 5 tipos de conocimientos"))


class ONSCAbstractFormationLine(models.AbstractModel):
    _name = 'onsc.cv.abstract.formation.line'
    _description = 'Modelo abstracto de líneas de formación'

    educational_area_id = fields.Many2one('onsc.cv.educational.areas', string=u'Área de educación', required=True)
    educational_subarea_id = fields.Many2one('onsc.cv.educational.subarea', string=u'Sub área de educación',
                                             required=True)
    discipline_educational_id = fields.Many2one('onsc.cv.discipline.educational', string=u'Disciplina de educación',
                                                required=True)

    @api.onchange('educational_area_id')
    def onchange_educational_area_id(self):
        if self.educational_area_id.id is False or (self.educational_area_id != self.educational_subarea_id.area_id):
            self.educational_subarea_id = False

    @api.onchange('educational_subarea_id')
    def onchange_educational_subarea_id(self):
        if self.educational_subarea_id.id is False or \
                (self.educational_subarea_id != self.discipline_educational_id.subarea_id):
            self.discipline_educational_id = False

    def _get_json_dict(self):
        return [
            ("educational_area_id", ['id', 'name']),
            ("educational_subarea_id", ['id', 'name']),
            ("discipline_educational_id", ['id', 'name']),
        ]
