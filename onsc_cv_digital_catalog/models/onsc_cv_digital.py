# -*- coding: utf-8 -*-

from odoo import models, api


class ONSCCVDigitalWorkExperience(models.Model):
    _name = 'onsc.cv.work.experience'
    _inherit = ['onsc.cv.work.experience', 'onsc.cv.operating.unit.abstract']

    @api.onchange('company_type')
    def onchange_company_type(self):
        if self.company_type == 'private':
            self.inciso_id = False
            self.operating_unit_id = False
        else:
            self.company_name = False


class ONSCCVDigitalVolunteering(models.Model):
    _name = 'onsc.cv.volunteering'
    _inherit = ['onsc.cv.volunteering', 'onsc.cv.operating.unit.abstract']

    @api.onchange('company_type')
    def onchange_company_type(self):
        if self.company_type == 'private':
            self.inciso_id = False
            self.operating_unit_id = False
        else:
            self.company_name = False
