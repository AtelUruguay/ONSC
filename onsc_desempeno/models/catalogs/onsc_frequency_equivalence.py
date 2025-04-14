# -*- coding: utf-8 -*-

from odoo import models, fields


class ONSCDesempenoGradequivalence(models.Model):
    _name = 'onsc.desempeno.grade.equivalence'
    _description = 'Equivalencia de frecuencia'
    _rec_name = 'degree_id'

    degree_id = fields.Many2one('onsc.desempeno.degree', string='Grado de Necesidad de Desarrollo', required=True)
    min_value = fields.Float(string='Mínimo', required=True)
    max_value = fields.Float(string='Máximo', required=True)
    active = fields.Boolean(string='Activo', default=True)

    _sql_constraints = [
        ("degree_id_check", "unique(degree_id)", "El grado no se puede configurar más de una ocasión"),
        ("min_max_check", "CHECK(min_value <= max_value)", "El valor mínimo debe ser menor o igual al valor máximo"),
    ]

    def get_grade_equivalence(self, value=float(0)):
        """
        Retrieves the grade equivalence for a given value.

        This method searches for a record where the given value falls within the
        range defined by 'min_value' and 'max_value'. It returns the first matching
        record found.

        Args:
            value (float): The value for which to find the grade equivalence.

        Returns:
            recordset: The first record that matches the search criteria, or an
            empty recordset if no match is found.
        """
        if value == float(0):
            args = [('min_value', '=', 0)]
        else:
            args = [('min_value', '<=', value), ('max_value', '>=', value)]
        return self.search(args, limit=1)


class ONSCDesempenoFrequencyEquivalence(models.Model):
    _name = 'onsc.desempeno.frequency.equivalence'
    _description = 'Equivalencia de frecuencia'

    name = fields.Char(
        string='Frecuencia',
        help='Frecuencia del comportamiento esperado',
        required=True
    )
    value = fields.Float(string='Valor', required=True)
    active = fields.Boolean(string='Activo', default=True)

    _sql_constraints = [
        ("frequency_check", "unique(name)", "La frecuencia no se puede configurar más de una ocasión"),
    ]
