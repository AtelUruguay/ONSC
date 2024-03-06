# -*- coding: utf-8 -*-

from odoo import models, api


class ResUsers(models.Model):
    """INFORMACION Y COMPORTAMIENTO PROPIO DE INTEGRACIONES DNIC E IDUY"""
    _inherit = 'res.users'

    @api.model
    def _prepare_userinfo_dict(self, provider, params):
        result = super(ResUsers, self)._prepare_userinfo_dict(provider, params)
        nickname = params.get('nickname', False)
        doc_type = self.env['onsc.cv.document.type'].search(
            [('code', '=', nickname.split('-')[1])], limit=1)
        result.update({
            'cv_emissor_country_id': result.get('country_id', False),
            'cv_first_name': params.get('primer_nombre', False),
            'cv_second_name': params.get('segundo_nombre', False),
            'cv_last_name_1': params.get('primer_apellido', False),
            'cv_last_name_2': params.get('segundo_apellido', False),
            'cv_document_type_id': doc_type.id,
            'cv_nro_doc': params.get('numero_documento', False),
            'is_partner_cv': True,
            'cv_source_info_auth_type': 'id_uy'
        })
        return result

    @api.model
    def _get_user(self, provider, params):
        oauth_user = super(ResUsers, self.with_context(can_update_contact_cv=True))._get_user(provider, params)
        # LLamada al servicio de DNIC
        if oauth_user._context.get('is_new_user', False):
            oauth_user.partner_id.update_dnic_values(jump_error=True)
        return oauth_user

    @api.model
    def create(self, values):
        existing_partner = self._get_existing_partner(values)
        if existing_partner:
            values.update({'partner_id': existing_partner.id})
        return super(ResUsers, self).create(values)

    def _get_existing_partner(self, values):
        if values.get('is_partner_cv'):
            return self.env['res.partner'].search([
                ('cv_emissor_country_id', '=', values.get('cv_emissor_country_id')),
                ('cv_document_type_id', '=', values.get('cv_document_type_id')),
                ('cv_nro_doc', '=', values.get('cv_nro_doc')),
            ], limit=1)
        return self.env['res.partner']
