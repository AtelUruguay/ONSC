# -*- coding: utf-8 -*-

from odoo import fields, models

CV_SEX = [('male', 'Masculino'), ('feminine', 'Femenino')]


class ONSCPartnerCommonData(models.AbstractModel):
    _name = 'onsc.partner.common.data'
    _description = 'Modelo abstracto común para los datos de Contacto'

    cv_first_name = fields.Char(u'Primer nombre')
    cv_second_name = fields.Char(u'Segundo nombre')
    cv_last_name_1 = fields.Char(u'Primer apellido')
    cv_last_name_2 = fields.Char(u'Segundo apellido')

    cv_birthdate = fields.Date(u'Fecha de nacimiento')
    cv_sex = fields.Selection(CV_SEX, u'Sexo')
    cv_expiration_date = fields.Date(u'Fecha de vencimiento documento de identidad')

    cv_emissor_country_id = fields.Many2one('res.country', u'País emisor del documento')
    cv_document_type_id = fields.Many2one('onsc.cv.document.type', u'Tipo de documento')
    cv_nro_doc = fields.Char(u'Número de documento', history=True)

