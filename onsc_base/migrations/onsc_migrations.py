# -*- coding: utf-8 -*-

from odoo import models


class ONSCMigrations(models.Model):
    _name = 'onsc.migrations'
    _description = 'Migraciones manuales a ambientes'

    def _v27(self):
        # onsc_cv_digital 15.0.27.0.0
        BFormation = self.env['onsc.cv.basic.formation'].sudo().with_context(ignore_base_restrict=True)
        AFormation = self.env['onsc.cv.advanced.formation'].sudo().with_context(ignore_base_restrict=True)

        args = [
            ('cv_digital_id.is_docket_active', '=', True),
            ('cv_digital_id.type', '=', 'cv'),
            ('documentary_validation_state', '=', 'validated')
        ]

        for record in BFormation.search(args):
            record.set_legajo_validated_records()
        for record in AFormation.search(args):
            record.set_legajo_validated_records()

        return True
