# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ONSCCVLocation(models.Model):
    _name = 'onsc.cv.location'
    _description = 'Ciudad/Localidad'
    _order = 'state_id, name'
    _inherit = ['onsc.cv.abstract.config']

    name = fields.Char(string='Nombre de localidad', required=True, index=True, tracking=True)
    country_id = fields.Many2one('res.country', string=u'País', ondelete='restrict', required=True, tracking=True)
    state_id = fields.Many2one('res.country.state', string='Departamento', ondelete='restrict', required=True,
                               tracking=True,
                               domain="[('country_id','=',country_id)]")
    other_code = fields.Integer(string=u'Otro código', tracking=True)

    _sql_constraints = [
        ('localidad_name_by_state_unique', 'unique(name, state_id)',
         'Ya existe una localidad con ese nombre en el mismo departamento'), ]

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

    def _check_validate(self, args2validate=[], message=""):
        args2validate = [
            ('name', '=', self.name),
            ('state_id', '=', self.state_id.id),
        ]
        return super(ONSCCVLocation, self)._check_validate(
            args2validate,
            _("Ya existe un registro validado para %s, Departamento %s" % (
                self.name, self.state_id.display_name))
        )
