# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
import json

STATES = [('incomplete', 'Incompleto'),
          ('in_progress', 'En curso'),
          ('completed', 'Finalizado')]


class ONSCCVAbstractFormation(models.Model):
    _name = 'onsc.cv.abstract.formation'
    _description = 'Modelo abstracto de entidades de formación'

    cv_digital_id = fields.Many2one('onsc.cv.digital', string=u'CV digital', required=True)
    institution_id = fields.Many2one("onsc.cv.institution", string=u"Institución", required=True)
    institution_id_domain = fields.Char(compute='_compute_institution_id_domain')
    subinstitution_id = fields.Many2one("onsc.cv.subinstitution", string=u"Sub institución", required=True)
    country_id = fields.Many2one('res.country', string=u'País de la institución', required=True)
    country_id_domain = fields.Char(compute='_compute_country_id_domain')
    state = fields.Selection(string="Estado", selection=STATES, required=True)
    start_date = fields.Date(string="Fecha de inicio", required=True)
    end_date = fields.Date(string="Fecha finalización")
    other_relevant_information = fields.Text(string="Otra información relevante")
    # Campo para redefinir
    knowledge_acquired_ids = fields.Many2many('onsc.cv.knowledge', "Conocimientos adquiridos", store=False)

    @api.depends('country_id')
    def _compute_institution_id_domain(self):
        for rec in self:
            if rec.country_id:
                rec.institution_id_domain = json.dumps(
                    [('country_id', '=', rec.country_id.id)]
                )
            else:
                rec.institution_id_domain = json.dumps(
                    [])

    @api.depends('institution_id')
    def _compute_country_id_domain(self):
        for rec in self:
            if rec.institution_id:
                rec.country_id_domain = json.dumps(
                    [('id', '=', rec.institution_id.country_id.id)]
                )
            else:
                rec.country_id_domain = json.dumps([])

    @api.onchange('institution_id')
    def onchange_institution_id(self):
        if self.institution_id.country_id:
            self.country_id = self.institution_id.country_id.id
        else:
            self.country_id = False
        if (self.institution_id and self.institution_id != self.subinstitution_id.institution_id) or \
                self.institution_id is False:
            self.subinstitution_id = False

    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date and self.end_date and self.state == 'completed' and self.end_date <= self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def onchange_end_date(self):
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            self.end_date = self.start_date

    @api.onchange('knowledge_acquired_ids')
    def onchange_knowledge_acquired_ids(self):
        if len(self.knowledge_acquired_ids) > 5:
            self.knowledge_acquired_ids = self.knowledge_acquired_ids[:5]
            return {
                'warning': {
                    'title': _("Atención"),
                    'type': 'notification',
                    'message': _(
                        "Sólo se pueden seleccionar 5 tipos de conocimientos"
                    )
                },

            }


class ONSCAbstractFormationLine(models.Model):
    _name = 'onsc.cv.abstract.formation.line'
    _description = 'Modelo abstracto de líneas de formación'

    educational_area_id = fields.Many2one('onsc.cv.educational.areas', string=u'Área de educación', required=True)
    educational_subarea_id = fields.Many2one('onsc.cv.educational.subarea', string=u'Sub área de educación',
                                             required=True)
    discipline_educational_id = fields.Many2one('onsc.cv.discipline.educational', string=u'Disciplina de educación',
                                                required=True)
