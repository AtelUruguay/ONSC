# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    institutional_email = fields.Char(string=u'Correo electrónico institucional', compute='_compute_institutional_email')

    def _compute_institutional_email(self):
        """
        PARA EXTENDER EN ADDONS DE CAPAS SUPERIORES QUE PRECISEN ADICIONAR COMPORTAMIENTOS A UN MAIN INSTITUCIONAL
        """
        for record in self:
            record.institutional_email = record.email

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
