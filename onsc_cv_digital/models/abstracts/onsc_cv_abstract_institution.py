# -*- coding: utf-8 -*-

import json

from odoo import fields, models, api


class ONSCCVAbstractInstitution(models.AbstractModel):
    _name = 'onsc.cv.abstract.institution'
    _description = 'Modelo abstracto de entidades de con institución-subinstitución-pais'

    institution_id = fields.Many2one("onsc.cv.institution", string=u"Institución")
    institution_id_domain = fields.Char(compute='_compute_institution_id_domain')
    subinstitution_id = fields.Many2one("onsc.cv.subinstitution", string=u"Sub institución")
    country_id = fields.Many2one('res.country', string=u'País de la institución')
    country_id_domain = fields.Char(compute='_compute_country_id_domain')
    is_country_uy = fields.Boolean(string='¿Es el País Uruguay?', compute='_compute_is_country_uy')

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

    @api.depends('country_id')
    def _compute_is_country_uy(self):
        for rec in self:
            rec.is_country_uy = rec.country_id.id == self.env.ref('base.uy', raise_if_not_found=False).id

    @api.onchange('institution_id')
    def onchange_institution_id(self):
        if self.institution_id.country_id:
            self.country_id = self.institution_id.country_id.id
        else:
            self.country_id = False
        if (self.institution_id and self.institution_id != self.subinstitution_id.institution_id) or \
                self.institution_id.id is False:
            self.subinstitution_id = False

    @api.onchange('country_id')
    def onchange_country_id(self):
        if self.country_id and self.country_id != self.institution_id.country_id or self.country_id.id is False:
            self.institution_id = False
