# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        _logger.info('************MIGRACION CV 15.0.8.3.6')
        for cv in env['onsc.cv.digital'].search([]):
            cv.write({
                'country_id': cv.partner_id.country_id.id,
                'cv_address_state_id': cv.partner_id.state_id.id,
                'cv_address_location_id': cv.partner_id.cv_location_id.id,
                'cv_address_nro_door': cv.partner_id.cv_nro_door,
                'cv_address_apto': cv.partner_id.cv_apto,
                'cv_address_street': cv.partner_id.street,
                'cv_address_zip': cv.partner_id.zip,
                'cv_address_is_cv_bis': cv.partner_id.is_cv_bis,
                'cv_address_amplification': cv.partner_id.cv_amplification,
                'cv_address_place': cv.partner_id.cv_address_place,
                'cv_address_block': cv.partner_id.cv_address_block,
                'cv_address_sandlot': cv.partner_id.cv_address_sandlot,
            })
        _logger.info('************MIGRACION OK CV 15.0.8.3.6')
    except Exception as e:
        pass
