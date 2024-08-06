# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ONSCCVIntitution(models.Model):
    _name = 'onsc.cv.institution'
    _description = 'Institución'
    _rec_name = 'name_country'
    _inherit = ['onsc.cv.abstract.config']
    _fields_2check_unicity = ['name', 'country_id', 'state']

    name = fields.Char("Nombre de la institución", required=True, tracking=True)
    country_id = fields.Many2one('res.country', string=u'País', ondelete='restrict', required=True, tracking=True)
    enable_mec = fields.Boolean(string=u'Habilitada por el MEC', tracking=True)
    name_country = fields.Char("Nombre y país de la institución", compute='_compute_name_country_id',
                               store=True)
    subinstitution_ids = fields.One2many('onsc.cv.subinstitution', 'institution_id', string=u"Sub institución",
                                         tracking=True)
    is_unformal_education = fields.Boolean(string=u'Educación no formal', tracking=True)
    is_advanced_formation = fields.Boolean(string=u'Formación avanzada', tracking=True)
    is_basic_formation = fields.Boolean(string=u'Formación básica', tracking=True)
    is_default = fields.Boolean(string=u'¿Usar por defecto?', tracking=True)
    is_without_academic_program = fields.Boolean(string=u'¿Sin programa académico?', tracking=True)

    @api.depends('name', 'country_id')
    def _compute_name_country_id(self):
        for record in self:
            if record.name or record.country_id.name:
                record.name_country = '%s (%s)' % (record.name or '', record.country_id.code or '')
            else:
                record.name_country = ''

    @api.constrains('institution_id', 'is_default', 'country_id')
    def _check_institution_default_unicity(self):
        for record in self.filtered(lambda x: x.active):
            if record.is_default and self.search_count(
                    [('is_default', '=', True), ('country_id', '=', record.country_id.id),
                     ('id', '!=', record.id)]):
                raise ValidationError(_(u"La Institución por defecto debe ser única para el país"))

    def _get_conditional_unicity_message(self):
        return _("Ya existe un registro validado para %s, País: %s" % (self.name,
                                                                       self.country_id.display_name))

    @api.constrains('name_upper')
    def _check_name_upper(self):
        if not self.is_default:
            super(ONSCCVIntitution, self)._check_name_upper()
