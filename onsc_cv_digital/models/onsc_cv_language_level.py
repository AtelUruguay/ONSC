# -*- coding: utf-8 -*-
from odoo import fields, models


class LenguageLevel(models.Model):
    _name = 'onsc.cv.language.level'
    _description = 'Idiomas'
    _order = 'language_id'

    cv_digital_id = fields.Many2one("onsc.cv.digital", string="CV", index=True, ondelete='cascade')
    language_id = fields.Many2one('onsc.cv.language', 'Idioma', required=True)
    spoken_level = fields.Selection(
        [('basic', 'Básico'), ('intermediate', 'Intermedio'), ('advanced', 'Avanzado'), ('native', 'Nativo')],
        required=True, string="Nivel hablado", default='basic')
    read_level = fields.Selection(
        [('basic', 'Básico'), ('intermediate', 'Intermedio'), ('advanced', 'Avanzado'), ('native', 'Nativo')],
        required=True, string="Nivel leído", default='basic')
    write_level = fields.Selection(
        [('basic', 'Básico'), ('intermediate', 'Intermedio'), ('advanced', 'Avanzado'), ('native', 'Nativo')],
        required=True, string="Nivel escrito", default='basic')
