# -*- coding: utf-8 -*-


from odoo import fields, models, api

BLOOD_TYPE = [('unknown', 'Desconocido'), ('O+', 'O+'), ('A+', 'A+'), ('B+', 'B+'), ('AB+', 'AB+'), ('O-', 'O-'),
              ('A-', 'A-'), ('B-', 'B-'), ('AB-', 'AB-')]
name_doc_one = u'Documento digitalizado "Partida de matrimonio / Partida de unión concubinaria / '
name_doc_two = u'Certificado de convivencia / Partida o Certificado de divorcio / Partida de defunción'
digitized_document_full_name = f'{name_doc_one}{name_doc_two}'


class ONSCCVDigital(models.Model):
    _inherit = 'onsc.cv.digital'

    @property
    def prefix_by_phones(self):
        res = super().prefix_by_phones
        return res + [('prefix_emergency_phone_id', 'emergency_service_telephone')]

    @api.model
    def domain_prefix_emergency_phone_id(self):
        country_id = self.env['res.country'].search([('code', '=', 'UY')])

        return [('country_id', 'in', country_id.ids)]

    is_docket = fields.Boolean(string="Tiene legajo")
    is_docket_active = fields.Boolean(string="Tiene legajo activo")
    gender_date = fields.Date(string="Fecha de información género")
    gender_public_visualization_date = fields.Date(string="Fecha información visualización pública de género",
                                                   compute='_compute_gender_public_visualization_date', store=True)
    afro_descendant_date = fields.Date(string="Fecha de información afrodescendencia")
    status_civil_date = fields.Date(string="Fecha de información estado civil")
    address_info_date = fields.Date(string="Fecha de información domicilio",
                                    related='partner_id.address_info_date',
                                    readonly=False,
                                    store=True)
    disability_date = fields.Date(string="Fecha de información discapacidad")
    # Datos del Legajo ----<Page>
    institutional_email = fields.Char(string=u'Correo electrónico institucional', readonly=True)
    digitized_document_file = fields.Binary(string=digitized_document_full_name)
    digitized_document_filename = fields.Char('Nombre del documento Digitalizado')
    address_receipt_file = fields.Binary(related='partner_id.address_receipt_file', readonly=False)
    address_receipt_file_name = fields.Char(related='partner_id.address_receipt_file_name', readonly=False)
    # TO-DO: Revisar este campo, No esta en catalogo
    # mobile_mergency_service_id = fields.Many2one("model", u"Servicio de emergencia móvil")

    # mobile_mergency_service_id = fields.Many2one("model", u"Servicio de emergencia móvil", required=True)
    prefix_emergency_phone_id = fields.Many2one('res.country.phone', 'Prefijo',
                                                domain=domain_prefix_emergency_phone_id,
                                                default=lambda self: self.env['res.country.phone'].search(
                                                    [('country_id.code', '=', 'UY')]))
    emergency_service_telephone = fields.Char(string=u'Teléfono del servicio de emergencia')
    department_id = fields.Many2one('res.country.state', string=u'Departamento del prestador de salud',
                                    ondelete='restrict', tracking=True)
    # TO-DO: Revisar este campo, No esta en catalogo
    # health_provider_id = fields.Many2one("model", u"Prestador de Salud")
    blood_type = fields.Selection(BLOOD_TYPE, string=u'Tipo de sangre')
    information_contact_ids = fields.One2many('onsc.cv.information.contact', 'cv_digital_id',
                                              string=u'Información de Contacto')
    other_information_official = fields.Text(string="Otra información del funcionario/a")

    @api.depends('is_cv_gender_public')
    def _compute_gender_public_visualization_date(self):
        for record in self:
            record.gender_public_visualization_date = fields.Date.today()

    @api.onchange('is_docket')
    def onchange_is_docket(self):
        if self.is_docket is False:
            self.gender_date = False
            self.afro_descendant_date = False
            self.status_civil_date = False
            self.address_info_date = False
            self.disability_date = False

    def _check_todisable_dynamic_fields(self):
        return super(ONSCCVDigital, self)._check_todisable_dynamic_fields() or self.is_docket


class ONSCCVInformationContact(models.Model):
    _name = 'onsc.cv.information.contact'
    _description = 'Información de Contacto'
    _inherit = 'onsc.cv.abstract.phone.validated'

    @property
    def prefix_by_phones(self):
        res = super().prefix_by_phones
        return res + [('prefix_phone_id', 'contact_person_telephone')]

    cv_digital_id = fields.Many2one('onsc.cv.digital', string=u'CV', required=True, index=True, ondelete='cascade')
    name_contact = fields.Char(string=u'Nombre de persona de contacto', required=True)
    # TO-DO: Revisar este campo, No esta en catalogo
    # link_people_contact_id = fields.Many2one("model", u"Vínculo con persona de contacto", required=True)
    prefix_phone_id = fields.Many2one('res.country.phone', 'Prefijo',
                                      default=lambda self: self.env['res.country.phone'].search(
                                          [('country_id.code', '=', 'UY')]), required=True)
    contact_person_telephone = fields.Char(string=u'Teléfono de persona de contacto', required=True)
    phone_full = fields.Char(compute='_compute_phone_full', string=u'Teléfono de persona de contacto')
    remark_contact_person = fields.Text(string=u'Observación para la persona de contacto', required=True)

    @api.depends('prefix_phone_id', 'contact_person_telephone')
    def _compute_phone_full(self):
        for rec in self:
            rec.phone_full = '+%s %s' % (rec.prefix_phone_id.prefix_code, rec.contact_person_telephone)
