# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCCVDigitalWorkExperience(models.Model):
    _name = 'onsc.cv.work.experience'
    _inherit = ['onsc.cv.work.experience', 'onsc.cv.operating.unit.abstract']


class ONSCCVDigitalVolunteering(models.Model):
    _name = 'onsc.cv.volunteering'
    _inherit = ['onsc.cv.volunteering', 'onsc.cv.operating.unit.abstract']
