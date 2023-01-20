# -*- coding: utf-8 -*-

from odoo import models, fields, api


def calc_full_name(first_name, second_name, last_name_1, last_name_2):
    name_values = [first_name,
                   second_name,
                   last_name_1,
                   last_name_2]
    return ' '.join([x for x in name_values if x])


class HrEmployee(models.Model):
    _name = "hr.employee"
    _inherit = ['hr.employee', 'onsc.contact.common.data']

    full_name = fields.Char('Nombre', compute='_compute_full_name', store=True)
    first_name = fields.Char(string="Primer nombre")
    second_name = fields.Char(string="Segundo nombre")
    first_surname = fields.Char(string="Primer apellido")
    second_surname = fields.Char(string="Segundo apellido")
    photo_updated_date = fields.Date(string="Fecha de foto de la/del funcionaria/o")
    emissor_country_id = fields.Many2one('res.country', string=u'País emisor del documento', )
    document_type_id = fields.Many2one('onsc.cv.document.type', string=u'Tipo de documento', )
    nro_doc = fields.Char(string=u'Número de documento de identidad ')
    identity_document_expiration_date_doc = fields.Date(string=u'Fecha de vencimiento documento de identidad')
    birthdate = fields.Date(string=u'Fecha de nacimiento')

    @api.depends('first_name', 'second_name', 'first_surname', 'second_surname')
    def _compute_full_name(self):
        for record in self:
            full_name = calc_full_name(record.first_name, record.second_name,
                                       record.first_surname, record.second_surname)
            if full_name:
                record.full_name = full_name
            else:
                record.full_name = record.name

    @api.model
    def create(self, values):
        full_name = calc_full_name(values.get('first_name'), values.get('second_name'),
                                   values.get('first_surname'), values.get('second_surname'))
        if full_name:
            values['name'] = full_name
        res = super(HrEmployee, self).create(values)
        return res

    def write(self, values):
        res = super(HrEmployee, self).write(values)
        # Actualizar los nombres en los registros con el campo calculado en caso que existan diferencias
        for rec in self.filtered(lambda x: x.name != x.full_name and x.full_name):
            rec.name = rec.full_name
        return res
