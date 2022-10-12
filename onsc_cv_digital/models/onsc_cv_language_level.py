# -*- coding: utf-8 -*-
from odoo import fields, models

NIVEL = [('d', 'Básico'), ('c', 'Intermedio'), ('b', 'Avanzado'), ('a', 'Nativo')]


class LenguageLevel(models.Model):
    _name = 'onsc.cv.language.level'
    _inherit = ['onsc.cv.abstract.documentary.validation']
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

    def _get_json_dict(self):
        json_dict = super(LenguageLevel, self)._get_json_dict()
        json_dict.extend([
            "spoken_level",
            ('spoken_level', lambda rec, field_name: rec.parser_selection_tovalue('spoken_level')),
            ('read_level', lambda rec, field_name: rec.parser_selection_tovalue('read_level')),
            ('write_level', lambda rec, field_name: rec.parser_selection_tovalue('write_level')),
            ("language_id", ['id', 'name'])
        ])
        return json_dict

    def parser_selection_tovalue(self, field_name):
        return dict(self._fields.get(field_name).selection).get(eval('self.%s' % field_name))
