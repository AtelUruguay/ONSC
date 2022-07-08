# -*- coding: utf-8 -*-
from odoo import fields, models


class ONSCCVWorkTeaching(models.Model):
    _name = 'onsc.cv.work.teaching'
    _description = 'Docencia'
    _inherit = ['onsc.cv.abstract.work', 'onsc.cv.abstract.conditional.state']
    _catalogs2validate = ['institution_id', 'subinstitution_id']

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", index=True, ondelete='cascade', required=True)
