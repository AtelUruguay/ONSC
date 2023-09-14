# -*- coding: utf-8 -*-

from odoo import models, _


class ONSCBaseUtils(models.AbstractModel):
    _name = 'onsc.base.utils'
    _description = 'Base utils ONSC'

    def _get_catalog_id(self, Catalog, catalog_field, operation, operation_code, log_list):
        """
        Get the catalog ID based on the given operation code.
        :param Catalog: Env of Object. Ex: self.env['catalog']
        :param catalog_field: Field name of the catalog. Ex: 'code'
        :param operation: Record of the operation
        :param operation_code: Var name of the operation. Ex: 'tipo_doc'
        :param log_list: Log list to append errors
        :return: id or False
        """
        if not hasattr(operation, operation_code):
            return False
        int_valid_operation_value = isinstance(getattr(operation, operation_code), int)
        char_valid_operation_value = isinstance(getattr(operation, operation_code), str) and getattr(operation,
                                                                                                     operation_code) != ""
        if int_valid_operation_value or char_valid_operation_value:
            recordset = Catalog.search([(catalog_field, '=', getattr(operation, operation_code))], limit=1)
            if not recordset:
                log_list.append(_('No se encontró en el catálogo %s el valor %s') % (
                    Catalog._description, getattr(operation, operation_code)))
            return recordset.id
        return False

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
