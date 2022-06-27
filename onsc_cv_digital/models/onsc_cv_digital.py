# -*- coding: utf-8 -*-

from lxml import etree
from odoo import fields, models, api, _
from odoo.addons.onsc_cv_digital.models.catalogs.res_partner import CV_SEX
from odoo.addons.onsc_cv_digital.models.utils import get_help_online_action
from odoo.exceptions import ValidationError


class ONSCCVDigital(models.Model):
    _name = 'onsc.cv.digital'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Currículum digital'
    _rec_name = 'cv_full_name'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ONSCCVDigital, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                         submenu=submenu)
        if self.env.user.has_group('onsc_cv_digital.group_user_cv') and self.search_count(
                [('partner_id', '=', self.env.user.partner_id.id), ('active', 'in', [False, True])]):
            doc = etree.XML(res['arch'])
            if view_type in ['form', 'tree', 'kanban']:
                for node_form in doc.xpath("//%s" % (view_type)):
                    node_form.set('create', '0')
            res['arch'] = etree.tostring(doc)
        return res

    def _default_partner_id(self):
        return self.env['res.partner'].search([('user_ids', 'in', self.env.user.id)], limit=1)

    partner_id = fields.Many2one(
        "res.partner",
        string="Contacto",
        required=True, index=True,
        default=_default_partner_id)
    active = fields.Boolean(
        string="Activo", default=True)
    is_partner_cv = fields.Boolean(u'¿Es un contacto de CV?')
    is_cv_uruguay = fields.Boolean(
        string='¿Es documento uruguayo?',
        related='partner_id.is_cv_uruguay', store=True)
    cv_full_name = fields.Char('Nombre', related='partner_id.cv_full_name', store=True)

    cv_emissor_country_id = fields.Many2one(
        'res.country',
        string=u'País emisor del documento',
        related='partner_id.cv_emissor_country_id', store=True, tracking=True)
    cv_document_type_id = fields.Many2one(
        'onsc.cv.document.type',
        string=u'Tipo de documento',
        related='partner_id.cv_document_type_id', store=True, tracking=True)
    cv_nro_doc = fields.Char(
        string=u'Número de documento',
        related='partner_id.cv_nro_doc', store=True, tracking=True)
    image_1920 = fields.Image(
        string="Image",
        max_width=1920, max_height=1920,
        related='partner_id.image_1920', store=True, readonly=False, tracking=True)
    avatar_128 = fields.Image(
        string="Avatar 128",
        max_width=128, max_height=128,
        related='partner_id.avatar_128')
    cv_birthdate = fields.Date(
        string=u'Fecha de nacimiento',
        related='partner_id.cv_birthdate', store=True, readonly=False, tracking=True)
    cv_sex = fields.Selection(
        CV_SEX,
        string=u'Sexo',
        related='partner_id.cv_sex', store=True, readonly=False, tracking=True)
    cv_sex_updated_date = fields.Date(
        string=u'Fecha de información sexo',
        related='partner_id.cv_sex_updated_date', store=True, readonly=False, tracking=True)
    cv_expiration_date = fields.Date(
        string=u'Fecha de vencimiento documento de identidad',
        related='partner_id.cv_expiration_date', store=True, readonly=False, tracking=True)
    email = fields.Char(
        string="Email",
        related='partner_id.email', store=True)

    # INFORMACION GENERAL
    # Genero
    cv_gender_id = fields.Many2one("onsc.cv.gender", string=u"Género", required=True, )
    is_cv_gender_option_other_enable = fields.Boolean(
        u'¿Permitir opción otra/o?',
        related='cv_gender_id.is_option_other_enable',
        store=True)
    cv_gender2 = fields.Char(string=u"Otro género")
    cv_gender_record = fields.Binary(string="Constancia de identidad de género")
    is_cv_gender_public = fields.Boolean(string="¿Permite que su género sea público?")
    is_cv_gender_record = fields.Boolean(u'Constancia', related='cv_gender_id.record')

    # Raza
    cv_race_ids = fields.Many2many("onsc.cv.race", string=u"Raza", required=True,
                                   domain="[('race_type','in',['race','both'])]")
    is_cv_race_option_other_enable = fields.Boolean(
        u'¿Permitir opción otra/o?',
        compute='_compute_cv_race_values', store=True)
    is_multiple_cv_race_selected = fields.Boolean(
        u'Múltiples razas seleccionadas',
        compute='_compute_cv_race_values', store=True)
    cv_race2 = fields.Char(string=u"Otra raza")
    cv_first_race_id = fields.Many2one("onsc.cv.race", string="¿Con que raza se reconoce principalmente?",
                                       domain="[('id','in',cv_race_ids)]")
    is_cv_race_public = fields.Boolean(string="¿Permite que su raza sea público?")

    @api.constrains('cv_sex_updated_date')
    def _check_valid_certificate(self):
        today = fields.Date.from_string(fields.Date.today())
        for record in self:
            if fields.Date.from_string(record.cv_sex_updated_date) > today:
                raise ValidationError(_("La Fecha de información sexo no puede ser posterior a la fecha actual"))

    @api.depends('cv_race_ids')
    def _compute_cv_race_values(self):
        for record in self:
            record.is_cv_race_option_other_enable = len(
                record.cv_race_ids.filtered(lambda x: x.is_option_other_enable)) > 0
            record.is_multiple_cv_race_selected = len(record.cv_race_ids) > 1

    def button_go_help(self):
        return get_help_online_action(_url)
