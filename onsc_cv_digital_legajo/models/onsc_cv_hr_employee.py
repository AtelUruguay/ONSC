# -*- coding: utf-8 -*-

from odoo import models, fields


class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = ["hr.employee", 'onsc.contact.common.data']

    first_name = fields.Char(string="Primer nombre")
    second_name = fields.Char(string="Segundo nombre")
    first_surname = fields.Char(string="Primer apellido")
    second_surname = fields.Char(string="Segundo apellido")
    photo_date = fields.Date(string="Fecha de foto de la/del funcionaria/o")

    emissor_country_id = fields.Many2one('res.country', string=u'País emisor del documento', )
    document_type_id = fields.Many2one('onsc.cv.document.type', string=u'Tipo de documento', )
    nro_doc = fields.Char(string=u'Número de documento')
    identity_document_expiration_date_doc = fields.Date(string=u'Fecha de vencimiento documento de identidad')
    birthdate = fields.Date(string=u'Fecha de nacimiento')
