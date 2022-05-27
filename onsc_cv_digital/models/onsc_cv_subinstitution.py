# -*- coding: utf-8 -*-

from odoo import fields, models


class ONSCCVSubintitution(models.Model):
    _name = 'onsc.cv.subinstitution'
    _description = 'Sub institución'
    _inherit = ['onsc.cv.abstract.config']

    name = fields.Char("Nombre de la Sub institución", required=True)
    country_id = fields.Many2one('res.country', string=u'País', ondelete='restrict', required=True)
    # TODO
    institution_id = fields.Many2one('onsc.cv.institution', string=u'Institución')
