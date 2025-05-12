# -*- coding: utf-8 -*-

from odoo import models, fields, api

EVALUATION_TYPE = [
    ('self_evaluation', 'Autoevaluación'),
    ('leader_evaluation', 'Evaluación de líder'),
    ('collaborator', 'Evaluación de colaborador/a'),
    ('environment_evaluation', 'Evaluación de entorno'),
    ('gap_deal', 'Acuerdo de Brecha'), ]


class ReportCompetenciaBrecha(models.Model):
    _name = 'report.competencia.brecha'
    _description = 'Reporte de Competencias por Brecha'

    comp_id = fields.Many2one('onsc.desempeno.skill', string=u'Competencia')
    grado_id = fields.Many2one('onsc.desempeno.degree', string=u'Grado de necesidad de desarrollo')
    inciso_id = fields.Many2one('onsc.catalog.inciso', string=u'Inciso')
    operating_unit_id = fields.Many2one('operating.unit', string=u'UE')
    uo_id = fields.Many2one('hr.department', string=u'UO')
    general_cycle_id = fields.Many2one('onsc.desempeno.general.cycle', string='Año')
    evaluation_type = fields.Selection(EVALUATION_TYPE, string=u'Tipo de evaluación')
    niveles_id = fields.Many2one('onsc.desempeno.level', string=u'Nivel del evaluado')
    cant = fields.Integer(string=u'Cantidad', readonly=True)
    porcent = fields.Integer(string=u'Porcentaje del total de formularios', readonly=True)
    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(ReportCompetenciaBrecha, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                              orderby=orderby, lazy=lazy)
        if 'comp_id' in groupby and 'grado_id' in groupby:
            comp_groups = {}
            for line in res:
                comp_id = line['comp_id'][0] if line['comp_id'] else None
                if comp_id not in comp_groups:
                    comp_groups[comp_id] = {'total_cant': 0, 'lines': []}
                comp_groups[comp_id]['total_cant'] += line['cant']
                comp_groups[comp_id]['lines'].append(line)
            new_res = []
            for comp_id, group_data in comp_groups.items():
                total_cant = group_data['total_cant']
                for line in group_data['lines']:
                    if 'cant:sum' in fields and 'porcent:sum' in fields and total_cant > 0:
                        line['porcent'] = (line['cant'] / total_cant) * 100
                    elif 'porcent:sum' in fields:
                        fields.remove('porcent:sum')
                    new_res.append(line)
            return new_res
        else:
            total_cant = sum(line['cant'] for line in res if line['cant'])
            if total_cant > 0:
                for line in res:
                    if 'cant:sum' in fields and 'porcent:sum' in fields:
                        line['porcent'] = (line['cant'] / total_cant) * 100
                    else:
                        if 'porcent:sum' in fields:
                            fields.remove('porcent:sum')
            return res

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields=allfields, attributes=attributes)
        campos_ocultos = ['create_uid', 'create_date', 'write_uid', 'write_date']
        for campo in campos_ocultos:
            res.pop(campo, None)
        for field in ['cant', 'porcent']:
            if field in res:
                res[field]['selectable'] = False
                res[field]['sortable'] = False
        return res

    def _compute_should_disable_form_edit(self):
        for record in self:
            record.should_disable_form_edit = True

