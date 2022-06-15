# -*- coding: utf-8 -*-

from odoo import models, api, fields


class ResUsers(models.Model):
    """INFORMACION Y COMPORTAMIENTO PROPIO DE INTEGRACIONES DNIC E IDUY"""
    _inherit = 'res.users'

    @api.model
    def _prepare_userinfo_dict(self, provider, params):
        result = super(ResUsers, self)._prepare_userinfo_dict(provider, params)
        _iddigital_doc_type = params.get('tipo_documento', False)
        if _iddigital_doc_type and _iddigital_doc_type.get('codigo', False):
            doc_type = self.env['onsc.cv.document.type'].search(
                [('code', '=', _iddigital_doc_type.get('codigo', False))], limit=1)
        result.update({
            'cv_emissor_country_id': result.get('country_id', False),
            'cv_first_name': params.get('primer_nombre', False),
            'cv_second_name': params.get('segundo_nombre', False),
            'cv_last_name_1': params.get('primer_apellido', False),
            'cv_last_name_2': params.get('segundo_apellido', False),
            'cv_document_type_id': doc_type.id,
            'cv_nro_doc': params.get('numero_documento', False),
            'is_partner_cv': True
        })
        return result


class ResPartner(models.Model):
    """INFORMACION Y COMPORTAMIENTO PROPIO DE INTEGRACIONES DNIC E IDUY"""
    _inherit = 'res.partner'

    cv_dnic_name_1 = fields.Char(u'Primer nombre CI')
    cv_dnic_name_2 = fields.Char(u'Segundo nombre CI')
    cv_dnic_lastname_1 = fields.Char(u'Primer apellido CI')
    cv_dnic_lastname_2 = fields.Char(u'Segundo apellido CI')
    cv_last_name_adoptive_1 = fields.Char(u'Primer apellido adoptivo')
    cv_last_name_adoptive_2 = fields.Char(u'Segundo apellido adoptivo')
