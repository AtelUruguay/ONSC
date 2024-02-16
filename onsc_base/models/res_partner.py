# -*- coding: utf-8 -*-

from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    institutional_email = fields.Char(string=u'Correo electrónico institucional',
                                      compute='_compute_institutional_email')

    def _compute_institutional_email(self):
        """
        PARA EXTENDER EN ADDONS DE CAPAS SUPERIORES QUE PRECISEN ADICIONAR COMPORTAMIENTOS A UN MAIN INSTITUCIONAL
        """
        for record in self:
            record.institutional_email = record.email

    def mail_partner_format(self):
        partners_format = dict()
        for partner in self:
            internal_users = partner.user_ids - partner.user_ids.filtered('share')
            main_user = internal_users[0] if len(internal_users) > 0 else partner.user_ids[0] if len(
                partner.user_ids) > 0 else self.env['res.users']
            partners_format[partner] = {
                "id": partner.id,
                "display_name": partner.display_name,
                "name": partner.name,
                "email": partner.institutional_email,
                "active": partner.active,
                "im_status": partner.im_status,
                "user_id": main_user.id,
                "is_internal_user": not partner.partner_share,
            }
            if 'guest' in self.env.context:
                partners_format[partner].pop('email')
        return partners_format

    def write(self, values):
        self._check_entities_values_before_write(values)
        res = super(ResPartner, self).write(values)
        return res

    def _check_entities_values_before_write(self, values):
        """
        PARA EXTENDER EN ADDONS DE CAPAS SUPERIORES QUE PRECISEN REVISAR TODOS LOS VALUES QUE ESTAN LLEGANDO ANTES DEL WRITE
        :param values: Diccionario de valores
        :return: True
        """
        return True
