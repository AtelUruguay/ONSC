# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError
# CAMPOS A GUARDAR EN HISTORICO. UTIL PARA EN HERENCIAS NO REPETIR CAMPOS PARA SOLO PONER history=True
HISTORY_COLUMNS = [
    'position',
    'country_id',
    'city_id',
    'start_date',
    'currently_working',
    'end_date',
    'company_type',
    'country_code',
    'unit_name',
    'entry_institution_id',
    'hierarchical_level_id',
    'take_decisions',
    'is_paid_activity',
    'people_charge_qty',
    'organizational_units_charge',
    'hours_worked_monthly',
    'receipt_file',
    'receipt_filename',
    'description_tasks',
    'causes_discharge',
    'inciso_id',
    'operating_unit_id',
    'company_name_calc',
]
# ELEMENTOS A MOSTRAR EN LA VISTA LISTA (RESPETA EL ORDEN)
TREE_HISTORY_COLUMNS = {
    'start_date': 'Inicio',
    'end_date': 'Fin',
    'position': 'Cargo desempeñado',
    'company_name_calc': 'Empresa',
    'unit_name': 'Área/Unidad',
}


class ONSCLegajoWorkExperience(models.Model):
    _name = 'onsc.legajo.work.experience'
    _inherit = ['onsc.cv.work.experience', 'model.history']
    _description = 'Legajo - Experiencia laboral'
    _history_model = 'onsc.legajo.work.experience.history'
    _history_columns = HISTORY_COLUMNS
    _tree_history_columns = TREE_HISTORY_COLUMNS

    employee_id = fields.Many2one("hr.employee", string=u"Funcionario")
    legajo_id = fields.Many2one("onsc.legajo", string=u"Legajo")
    origin_record_id = fields.Many2one(
        "onsc.cv.work.experience",
        string=u"Experiencia laboral origen",
        ondelete="set null")

    company_name_calc = fields.Char('Empresa', history=True)

    task_ids = fields.One2many(
        "onsc.legajo.work.experience.task",
        inverse_name="legajo_work_experience_id",
        string="Tareas",
        history_fields="key_task_id,area_id"
    )

    def button_show_history(self):
        model_view_form_id = self.env.ref('onsc_cv_digital_legajo.onsc_legajo_work_experience_form_view').id
        return self.with_context(model_view_form_id=model_view_form_id,
                                 as_of_date=fields.Date.today()).get_history_record_action(
            history_id=False,
            res_id=self.id,
        )


class ONSCLegajoWorkExperienceTask(models.Model):
    _name = 'onsc.legajo.work.experience.task'
    _inherit = 'onsc.cv.work.experience.task'
    _description = 'Legajo - Tareas de experiencia laboral'
    def read(self, fields=None, load='_classic_read'):
        """ read([fields])

        Reads the requested fields for the records in ``self``, low-level/RPC
        method. In Python code, prefer :meth:`~.browse`.

        :param fields: list of field names to return (default is all fields)
        :return: a list of dictionaries mapping field names to their values,
                 with one dictionary per record
        :raise AccessError: if user has no read rights on some of the given
                records
        """
        fields = self.check_field_access_rights('read', fields)

        # fetch stored fields from the database to the cache
        stored_fields = set()
        for name in fields:
            field = self._fields.get(name)
            if not field:
                raise ValueError("Invalid field %r on model %r" % (name, self._name))
            if field.store:
                stored_fields.add(name)
            elif field.compute:
                # optimization: prefetch direct field dependencies
                for dotname in self.pool.field_depends[field]:
                    f = self._fields[dotname.split('.')[0]]
                    if f.prefetch and (not f.groups or self.user_has_groups(f.groups)):
                        stored_fields.add(f.name)
        self._read(stored_fields)

        result = self._read_format(fnames=fields, load=load)
        return result

    def _read_format(self, fnames, load='_classic_read'):
        """Returns a list of dictionaries mapping field names to their values,
        with one dictionary per record that exists.

        The output format is similar to the one expected from the `read` method.

        The current method is different from `read` because it retrieves its
        values from the cache without doing a query when it is avoidable.
        """
        data = [(record, {'id': record._ids[0]}) for record in self]
        use_name_get = (load == '_classic_read')
        for name in fnames:
            convert = self._fields[name].convert_to_read
            for record, vals in data:
                # missing records have their vals empty
                if not vals:
                    continue
                try:
                    vals[name] = self._fields[name].convert_to_read(record[name], record, use_name_get)
                except MissingError:
                    vals.clear()
        result = [vals for record, vals in data if vals]

        return result

    legajo_work_experience_id = fields.Many2one(
        "onsc.legajo.work.experience",
        string="Experiencia laboral",
        ondelete='cascade'
    )


# HISTORICOS
class ONSCLegajoWorkExperienceHistory(models.Model):
    _name = 'onsc.legajo.work.experience.history'
    _inherit = ['model.history.data']
    _parent_model = 'onsc.legajo.work.experience'

    history_receipt_file = fields.Binary(string="Comprobante")
