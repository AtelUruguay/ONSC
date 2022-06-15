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
        result.update({
        })
        return result


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
                if record.is_cv_uruguay or not self.env.company.is_dnic_integrated:
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
