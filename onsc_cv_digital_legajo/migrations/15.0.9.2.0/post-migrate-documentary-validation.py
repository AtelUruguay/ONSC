# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        _logger.info('************MIGRACION onsc_cv_digital_legajo 15.0.9.2.0')
        env['onsc.cv.digital'].search([('type', '=', 'cv')]).validate_header_documentary_validation()
    except Exception:
        pass
