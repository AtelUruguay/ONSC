# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ONSCCVSubintitution(models.Model):
    _name = 'onsc.cv.subinstitution'
    _description = 'Sub institución'
    _inherit = ['onsc.cv.abstract.config']
    _fields_2check_unicity = ['name', 'institution_id', 'state']

    name = fields.Char("Nombre de la sub institución", required=True, tracking=True)
    country_id = fields.Many2one('res.country', string=u'País', ondelete='restrict', required=True, tracking=True)
    institution_id = fields.Many2one('onsc.cv.institution', string=u'Institución', tracking=True, required=True)
    is_default = fields.Boolean(string=u'¿Usar por defecto?', tracking=True)

    @api.constrains('institution_id', 'is_default')
    def _check_subinstitution_default_unicity(self):
        for record in self.filtered(lambda x: x.active):
            if not record.institution_id.is_default and record.is_default:
                raise ValidationError(_("La institución debe tener el campo usar por defecto seleccionado"))
            if self.search_count([('is_default', '=', True),
                                  ('institution_id', '=', record.institution_id.id),
                                  ('id', '!=', record.id)]):
                raise ValidationError(_("La Sub institución por defecto debe ser única para la Institución"))

    @api.onchange('country_id')
    def onchange_country_id(self):
        if self.country_id != self.institution_id.country_id or self.country_id.id is False:
            self.institution_id = False

    @api.onchange('institution_id')
    def onchange_institution_id(self):
        if self.institution_id.country_id:
            self.country_id = self.institution_id.country_id

    def _check_validation_status(self):
        parent_states = self.mapped('institution_id.state')
        if 'to_validate' in parent_states or 'rejected' in parent_states:
            raise ValidationError(_("No se puede validar una Sub institución si la Institución no está validada"))
        return super(ONSCCVSubintitution, self)._check_validation_status()

    def _get_conditional_unicity_message(self):
        return _("Ya existe un registro validado para %s, Institución: %s" % (self.name,
                                                                              self.institution_id.display_name))

    @api.constrains('name_upper')
    def _check_name_upper(self):
        if not self.is_default:
            super(ONSCCVSubintitution, self)._check_name_upper()
