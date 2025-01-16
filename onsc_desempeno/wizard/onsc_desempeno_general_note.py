# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ONSCDesempenoGeneralNoteWizard(models.TransientModel):
    _name = 'onsc.desempeno.general.note'
    _description = 'Adicionar nota general'

    evaluation_id = fields.Many2one('onsc.desempeno.evaluation', string='Evaluación')
    message = fields.Text(string="Comentarios generales")

    def action_confirm(self):
        self.evaluation_id.write({'general_comments': self.message})
        return True

