# -*- coding: utf-8 -*-

from odoo import models, api, fields

DNIC_FROZEN_COLUMNS = [
    'cv_dnic_name_1',
    'cv_dnic_name_2',
    'cv_dnic_lastname_1',
    'cv_dnic_lastname_2',
    'cv_last_name_adoptive_1',
    'cv_last_name_adoptive_2',
]


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
            'is_partner_cv': True
        })
        return result

    @api.model
    def _get_user(self, provider, params):
        oauth_user = super(ResUsers, self.with_context(can_update_contact_cv=True))._get_user(provider, params)
        # LLamada al servicio de DNIC
        oauth_user.partner_id.update_dnic_values(jump_error=True)
        return oauth_user


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_frozen_columns(self):
        "Sobreescrito para incorporar las columnas DNIC como de no modificacion"
        return super(ResPartner, self)._get_frozen_columns() + DNIC_FROZEN_COLUMNS

    @api.depends('is_partner_cv', 'cv_first_name', 'cv_second_name', 'cv_last_name_1', 'cv_last_name_2',
                 'cv_dnic_name_1', 'cv_dnic_name_2', 'cv_dnic_lastname_1', 'cv_dnic_lastname_2')
    def _compute_cv_full_name(self):
        "Sobreescrito para calcular el cv_full_name si "
        for record in self:
            record.cv_full_name_updated_date = fields.Date.today()
            if record.is_partner_cv:
                if record.is_cv_uruguay and self.env.company.is_dnic_integrated:
                    name_values = [record.cv_dnic_name_1,
                                   record.cv_dnic_name_2,
                                   record.cv_dnic_lastname_1,
                                   record.cv_dnic_lastname_2]
                else:
                    name_values = [record.cv_first_name,
                                   record.cv_second_name,
                                   record.cv_last_name_1,
                                   record.cv_last_name_2]
                record.cv_full_name = ' '.join([x for x in name_values if x])
            else:
                record.cv_full_name = record.name

    def button_update_dnic_values(self):
        self.update_dnic_values()
