from odoo import fields, models


class ReportONSCDesempenoEvaluationReport(models.TransientModel):
    _name = "report.onsc.desempeno.evaluation.report"
    _description = "Asistente del reporte XLS para Resumen de evaluaciones"
    _inherit = "xlsx.report"

    results = fields.Many2many(
        comodel_name="onsc.desempeno.evaluation.report",
        relation="mm_xls_desempeno_evaluation_report",
        ondelete='cascade',
    )
