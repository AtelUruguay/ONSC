# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCCVStreet(models.Model):
    _name = 'onsc.cv.street'
    _description = 'Calles para Uruguay'
    _rec_name = 'street'

    code = fields.Char(string=u"Código", required=True)
    state_id = fields.Many2one('res.country.state', string='Departamento', ondelete='restrict', required=True,
                               domain="[('country_id.code','=','UY')]")
    cv_location_id = fields.Many2one('onsc.cv.location', u'Localidad/Ciudad', ondelete='restrict',
                                     domain="[('state_id','=',state_id)]", required=True)
    street = fields.Char(string="Calle", required=True)
    active = fields.Boolean(string='Activo', default=True, tracking=True)

    @api.onchange('state_id')
    def _onchange_state_id(self):
        if (self.state_id and self.state_id != self.cv_location_id.state_id) or self.state_id.id is False:
            self.cv_location_id = False

    @api.model
    def create(self, values):
        if 'code' not in values or ('code' in values and values.get('code') is False):
            values['code'] = self.env['ir.sequence'].next_by_code('onsc.cv.street.code')
        return super(ONSCCVStreet, self).create(values)

    _sql_constraints = [
        ('country_street_location_id_uniq', 'unique(cv_location_id, street)',
         u'La combinación: calle y departamento debe ser única'),
        ('code_street_unique', 'unique(code)', u'El código debe ser único'),
    ]
