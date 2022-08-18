# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


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

    # TO-DO: Mejorar este metodo.Hasta ahora funciona con los M2O.
    def write(self, values):
        """
        Este metodo se utiliza para cuando se queriera desactivar un registro, revise si se esta usando ese dato en otro
        lugar. Si se esta usando no se puede desactivar.
        :return:
        """
        if 'active' in values and not values.get('active') and not self.env.context.get('no_check_active', False):
            modelo_name = self._name
            fields = self.env['ir.model.fields'].search([('relation', '=', modelo_name)])
            for field in fields:
                Models = self.env[field.model_id.model].search([(field.name, '=', self.id)])
                if Models:
                    raise ValidationError(_(u"No se puede desactivar el registro porque esta siendo usado"))

        return super(ONSCCatalogAbstractBase, self).write(values)


class ONSCCVCatalogAbstract(models.AbstractModel):
    _name = 'onsc.cv.catalog.abstract'
    _description = 'Clase abstracta de catálogo'

    code = fields.Char(string=u"Código", required=True)
    name = fields.Char(string=u"Nombre", required=True)
    description = fields.Text(string=u"Descripción")
