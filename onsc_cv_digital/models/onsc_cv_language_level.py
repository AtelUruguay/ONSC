# -*- coding: utf-8 -*-
from odoo import fields, models

NIVEL = [('d', 'Básico'), ('c', 'Intermedio'), ('b', 'Avanzado'), ('a', 'Nativo')]


class LenguageLevel(models.Model):
    _name = 'onsc.cv.language.level'
    _inherit = 'onsc.cv.abstract.common'
    _description = 'Idiomas'
    _order = 'spoken_level,read_level,write_level'

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", required=True, index=True, ondelete='cascade')
    language_id = fields.Many2one('onsc.cv.language', 'Idioma', required=True)
    spoken_level = fields.Selection(
        selection=NIVEL,
        required=True, string="Nivel hablado")
    read_level = fields.Selection(
        selection=NIVEL,
        required=True, string="Nivel leído")
    write_level = fields.Selection(
        selection=NIVEL,
        required=True, string="Nivel escrito")
