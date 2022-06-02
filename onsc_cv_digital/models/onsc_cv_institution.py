# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ONSCCVIntitution(models.Model):
    _name = 'onsc.cv.institution'
    _description = 'Institución'
    _rec_name = 'name_country'
    _inherit = ['onsc.cv.abstract.config']

    name = fields.Char("Nombre de la institución", required=True, tracking=True)
    country_id = fields.Many2one('res.country', string=u'País', ondelete='restrict', required=True, tracking=True)
    enable_mec = fields.Boolean(string=u'Habilitada por el MEC', tracking=True)
    name_country = fields.Char("Nombre y país de la institución", compute='_compute_name_country_id',
                               store=True)
    subinstitution_ids = fields.One2many('onsc.cv.subinstitution', 'institution_id', string=u"Sub institución",
                                         tracking=True)

    @api.depends('name', 'country_id')
    def _compute_name_country_id(self):
        for record in self:
            if record.name or record.country_id.name:
                record.name_country = '%s (%s)' % (record.name or '', record.country_id.code or '')
            else:
                record.name_country = ''

    def _check_validate(self, args2validate, message=""):
        args2validate = [
            ('name', '=', self.name),
            ('country_id', '=', self.country_id.id),
        ]
        return super(ONSCCVIntitution, self)._check_validate(
            args2validate,
            _("Ya existe un registro validado para %s, País %s" % (
                self.name, self.country_id.display_name))
        )
