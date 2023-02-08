# -*- coding: utf-8 -*-

from odoo import fields, models, api

BLOOD_TYPE = [('unknown', 'Desconocido'), ('O+', 'O+'), ('A+', 'A+'), ('B+', 'B+'), ('AB+', 'AB+'), ('O-', 'O-'),
              ('A-', 'A-'), ('B-', 'B-'), ('AB-', 'AB-')]
name_doc_one = u'Documento digitalizado "Partida de matrimonio / Partida de unión concubinaria / '
name_doc_two = u'Certificado de convivencia / Partida o Certificado de divorcio / Partida de defunción'
digitized_document_full_name = f'{name_doc_one}{name_doc_two}'


class ONSCCVLegajoAbstractCommon(models.AbstractModel):
    _name = 'onsc.cv.legajo.abstract.common'

    # Información de salud
    @property
    def prefix_by_phones(self):
        res = super().prefix_by_phones
        return res + [('prefix_emergency_phone_id', 'emergency_service_telephone')]

    @api.model
    def domain_prefix_emergency_phone_id(self):
        country_id = self.env['res.country'].search([('code', '=', 'UY')])

        return [('country_id', 'in', country_id.ids)]

    mergency_service_id = fields.Many2one("onsc.legajo.emergency", u"Servicio de emergencia móvil")
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

    other_information_official = fields.Text(string="Otra información del funcionario/a")

    # Datos del Legajo
    institutional_email = fields.Char(string=u'Correo electrónico institucional')
    digitized_document_file = fields.Binary(string=digitized_document_full_name)
    digitized_document_filename = fields.Char('Nombre del documento Digitalizado')
    gender_date = fields.Date(string="Fecha de información género")
    status_civil_date = fields.Date(string="Fecha de información estado civil")
    disability_date = fields.Date(string="Fecha de información discapacidad")
