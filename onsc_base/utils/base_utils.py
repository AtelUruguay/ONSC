# -*- coding: utf-8 -*-

from odoo import models


class ONSCBaseUtils(models.AbstractModel):
    _name = 'onsc.base.utils'
    _description = 'Base utils ONSC'

    def get_really_values_changed(self, recordset, values):
        """
        FILTRA DE TODOS LOS VALORES QUE SE MANDAN A CAMBIAR EN UN RECORDSET CUALES REALMENTE TIENEN DIFERENCIA
        :param recordset: Recordet a evaluar
        :param values: Dict of values, ejemplo: los que vienen en un write
        :return: Dict of values: los que realmente cambiaron
        """
        values_filtered = {}
        _fields_get = recordset.fields_get()
        for key, value in values.items():
            field_type = _fields_get.get(key).get('type')
            if field_type in ('integer', 'binary', 'date', 'datetime'):
                eval_str = "recordset.%s"
            elif field_type == 'many2one':
                eval_str = "recordset.%s.id"
            elif field_type in ['many2many', 'one2many']:
                eval_str = "recordset.%s.ids"
            else:
                eval_str = "recordset.%s"
            if eval(eval_str % (key)) != value:
                values_filtered.update({key: value})
        return values_filtered
