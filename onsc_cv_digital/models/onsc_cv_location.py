# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCCVLocation(models.Model):
    _name = 'onsc.cv.location'
    _description = 'Ciudad/Localidad'
    _order = 'state_id, name'
    _inherit = ['onsc.cv.abstract.config']

    name = fields.Char(string='Nombre de Localidad', required=True, index=True, tracking=True)
    country_id = fields.Many2one('res.country', string=u'País', ondelete='restrict', required=True, tracking=True)
    state_id = fields.Many2one('res.country.state', string='Departamento', ondelete='restrict', required=True,
                               tracking=True,
                               domain="[('country_id','=',country_id)]")
    other_code = fields.Integer(string=u'Otro código', tracking=True)

    _sql_constraints = [
        ('localidad_name_by_state_unique', 'unique(name, state_id)',
         'Ya existe una Localidad con ese nombre en el mismo Departamento'), ]

    @api.onchange('country_id')
    def _onchange_country_id(self):
        self.state_id = False

    @api.model
    def create(self, values):
        values['name'] = values.get('name', '').upper()
        return super(ONSCCVLocation, self).create(values)

    def write(self, values):
        if values.get('name', False):
            values['name'] = values.get('name', '').upper()
        return super(ONSCCVLocation, self).write(values)
