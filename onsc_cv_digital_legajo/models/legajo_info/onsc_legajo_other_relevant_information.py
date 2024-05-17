# -*- coding: utf-8 -*-
from odoo import fields, models

HISTORY_COLUMNS = [
    'theme',
    'description',
   ]

TREE_HISTORY_COLUMNS = [
    'theme',
    'description',
]

class ONSCCVOtherRelevantInformation(models.Model):
    _inherit = 'onsc.cv.other.relevant.information'
    _legajo_model = 'onsc.legajo.other.relevant.information'

class ONSCLegajoRelevantInformation(models.Model):
    _name = 'onsc.legajo.relevant.information'
    _inherit = ['onsc.cv.other.relevant.information', 'model.history']
    _description = u'Legajo - Otra información relevante'
    _history_model = 'onsc.legajo.relevant.information.history'
    _history_columns = HISTORY_COLUMNS
    _tree_history_columns = TREE_HISTORY_COLUMNS

    employee_id = fields.Many2one("hr.employee", string=u"Funcionario")
    legajo_id = fields.Many2one("onsc.legajo", string=u"Legajo")
    origin_record_id = fields.Many2one("onsc.cv.work.investigation", string=u"Investigación origen")

# HISTORICOS
class ONSCLegajoRelevantInformationHistory(models.Model):
    _name = 'onsc.legajo.work.investigation.history'
    _inherit = ['model.history.data']
    _parent_model = 'onsc.legajo.relevant.information'
