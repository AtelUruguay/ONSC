# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ONSCCVSubintitution(models.Model):
    _name = 'onsc.cv.subinstitution'
    _description = 'Sub institución'
    _inherit = ['onsc.cv.abstract.config']
    _fields_2check_unicity = ['name', 'institution_id', 'state']

    name = fields.Char("Nombre de la sub institución", required=True, tracking=True)
    country_id = fields.Many2one('res.country', string=u'País', ondelete='restrict', required=True, tracking=True)
    institution_id = fields.Many2one('onsc.cv.institution', string=u'Institución', tracking=True, required=True)

    @api.onchange('country_id')
    def onchange_country_id(self):
        if self.country_id != self.institution_id.country_id or self.country_id.id is False:
            self.institution_id = False

    @api.onchange('institution_id')
    def onchange_institution_id(self):
        if self.institution_id.country_id:
            self.country_id = self.institution_id.country_id

    def _get_conditional_unicity_message(self):
        return _("Ya existe un registro validado para %s, Institución: %s" % (self.name,
                                                                              self.institution_id.display_name))
