# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCCatalogAbstractBase(models.AbstractModel):
    _name = 'onsc.catalog.abstract.base'
    _description = 'Modelo abstracto base de catálogo'

    @api.model
    def _get_default_identifier(self):
        return self.env['ir.sequence'].next_by_code('%s.identifier' % self._name)

    identifier = fields.Char('Identificador',
                             default=lambda x: x._get_default_identifier(),
                             copy=False,
                             tracking=True,
                             history=True)
    code = fields.Char(string="Código", required=True, copy=False, tracking=True, history=True)
    name = fields.Char(string="Nombre", required=True, tracking=True, history=True)
    start_date = fields.Date(string='Inicio de vigencia', tracking=True, history=True)
    end_date = fields.Date(string='Fin de vigencia', tracking=True, history=True)
    active = fields.Boolean(default=True, tracking=True, history=True)
    description = fields.Text(string='Descripción', copy=False, history=True)

    def toggle_active(self):
        self._check_toggle_active()
        return super().toggle_active()

    def _check_toggle_active(self):
        """

        :rtype: True or raise ValidationError
        """
        return True


class ONSCCVCatalogAbstract(models.AbstractModel):
    _name = 'onsc.cv.catalog.abstract'
    _description = 'Clase abstracta de catálogo'

    code = fields.Char(string=u"Código")
    name = fields.Char(string=u"Nombre")
    description = fields.Text(string=u"Descripción")
