# -*- coding: utf-8 -*-

import logging

from odoo import fields, models, api
from odoo.addons.onsc_cv_digital.soap import soap_error_codes as cv_digital_soap_error_codes
from odoo.osv import expression

from ..soap import soap_error_codes

_logger = logging.getLogger(__name__)


class ONSCCVDigitalCall(models.Model):
    _name = 'onsc.cv.digital.call'
    _inherit = 'onsc.cv.digital.call'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_call_documentary_validation') and self.user_has_groups(
                'onsc_cv_digital.group_validador_documental_cv'):
            configs = self.env['onsc.catalog.validators.inciso.ue'].search([('user_id', '=', self.env.user.id)])
            args = expression.AND([[
                ('preselected', '=', 'yes'),
                ('inciso_id', 'in', configs.mapped('inciso_id').ids),
                ('operating_unit_id', 'in', configs.mapped('operating_unit_id').ids)], args])
        return super(ONSCCVDigitalCall, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                      access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_call_documentary_validation') and self.user_has_groups(
                'onsc_cv_digital.group_validador_documental_cv'):
            configs = self.env['onsc.catalog.validators.inciso.ue'].search([('user_id', '=', self.env.user.id)])
            domain = expression.AND([[
                ('preselected', '=', 'yes'),
                ('inciso_id.company_id', 'in', configs.mapped('inciso_id').ids),
                ('operating_unit_id', 'in', configs.mapped('operating_unit_id').ids)], domain])
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora", )

    def _get_call_close_vals(self,
                             operating_number_code,
                             is_trans,
                             is_afro,
                             is_disabilitie,
                             is_victim):
        operating_unit = self.env['operating.unit'].sudo().search([
            ('code', '=', operating_number_code)
        ], limit=1)
        if len(operating_unit) == 0:
            return cv_digital_soap_error_codes._raise_fault(soap_error_codes.LOGIC_160)
        vals = super(ONSCCVDigitalCall, self)._get_call_close_vals(operating_number_code,
                                                                   is_trans,
                                                                   is_afro,
                                                                   is_disabilitie,
                                                                   is_victim)
        vals.update({
            'inciso_id': operating_unit.inciso_id.id,
            'operating_unit_id': operating_unit.id,
        })
        return vals

    def _get_mailto_send_notification_document_validators(self):
        if len(self) == 0:
            return
        self = self[0]
        users = self.env['onsc.catalog.validators.inciso.ue'].search([
            ('operating_unit_id', '=', self.operating_unit_id.id),
        ]).user_id
        emailto = ','.join(users.filtered(lambda x: x.partner_id.email).mapped('partner_id.email'))
        return {'email_to': emailto}
