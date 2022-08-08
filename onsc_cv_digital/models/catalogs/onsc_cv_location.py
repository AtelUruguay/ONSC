# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ONSCCVLocation(models.Model):
    _name = 'onsc.cv.location'
    _description = 'Ciudad/Localidad'
    _order = 'state_id, name'
    _inherit = ['onsc.cv.abstract.config']
    _fields_2check_unicity = ['name', 'state_id', 'state']

    name = fields.Char(string='Nombre de localidad', required=True, index=True, tracking=True)
    country_id = fields.Many2one('res.country', string=u'País', ondelete='restrict', required=True, tracking=True)
    state_id = fields.Many2one('res.country.state', string='Departamento', ondelete='restrict', required=True,
                               tracking=True,
                               domain="[('country_id','=',country_id)]")
    other_code = fields.Integer(string=u'Otro código', tracking=True)

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if (self.country_id and self.country_id != self.state_id.country_id) or self.country_id.id is False:
            self.state_id = False

    @api.model
    def create(self, values):
        values['name'] = values.get('name', '').upper()
        return super(ONSCCVLocation, self).create(values)

    def write(self, values):
        if values.get('name', False):
            values['name'] = values.get('name', '').upper()
        return super(ONSCCVLocation, self).write(values)

    def _get_conditional_unicity_message(self):
        return _("Ya existe un registro validado para %s, Departamento: %s" % (self.name, self.state_id.display_name))
