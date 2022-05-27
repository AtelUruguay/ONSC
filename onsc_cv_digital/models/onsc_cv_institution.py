# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ONSCCVIntitution(models.Model):
    _name = 'onsc.cv.institution'
    _description = 'Institución'
    _inherit = ['onsc.cv.abstract.config']

    name = fields.Char("Nombre de la Institución", required=True)
    country_id = fields.Many2one('res.country', string=u'País', ondelete='restrict', required=True)
    enable_mec = fields.Boolean(string=u'Habilitada por el MEC')
    name_country = fields.Char("Nombre y país de la institución", compute='_compute_name_country_id', readonly=True,
                               store=True)
    sub_institution_id = fields.One2many('onsc.cv.subinstitution', 'institution_id', string=u"Sub institución")

    @api.depends('name', 'country_id')
    def _compute_name_country_id(self):
        for record in self:
            if record.name and record.country_id.name:
                record.name_country = record.name + ' (' + record.country_id.name + ')'
