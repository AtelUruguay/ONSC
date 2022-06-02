# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ONSCCVSubintitution(models.Model):
    _name = 'onsc.cv.subinstitution'
    _description = 'Sub institución'
    _inherit = ['onsc.cv.abstract.config']

    name = fields.Char("Nombre de la sub institución", required=True, tracking=True)
    country_id = fields.Many2one('res.country', string=u'País', ondelete='restrict', required=True, tracking=True)
    institution_id = fields.Many2one('onsc.cv.institution', string=u'Institución', tracking=True, required=True)

    @api.onchange('country_id')
    def onchange_country_id(self):
        if self.country_id and self.country_id != self.institution_id.country_id:
            self.institution_id = False

    @api.onchange('institution_id')
    def onchange_institution_id(self):
        if self.institution_id.country_id:
            self.country_id = self.institution_id.country_id

    def _check_validate(self, args2validate, message=""):
        args2validate = [
            ('name', '=', self.name),
            ('institution_id', '=', self.institution_id.id),
        ]
        return super(ONSCCVSubintitution, self)._check_validate(
            args2validate,
            _("Ya existe un registro validado para %s, Institución %s" % (
                self.name, self.institution_id.display_name))
        )
