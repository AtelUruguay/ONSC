import base64
import io
import logging

import openpyxl as openpyxl
from odoo.addons.onsc_base.onsc_useful_tools import calc_full_name as calc_full_name

from odoo import models, fields, tools
from odoo.exceptions import ValidationError

STATE = [
    ('draft', 'Borrador'),
    ('error', 'Error'),
    ('in_process', 'Procesando'),
    ('process', 'Procesado'),
]

CITIZENSHIP = [
    ('legal', 'Legal'),
    ('natural', 'Natural'),
    ('extranjero', 'Extranjero')]

REQUIRED_FIELDS = {
    'country_id',
    'doc_type_id',
    'doc_nro',
    'first_name',
    'first_surname',
    'birth_date',
    'sex',
    'date_income_public_administration',
    'inciso_id',
    'retributive_day_id',
    'retributive_day_formal',
    'date_start'
}

REQUIRED_FIELDS_COMM = {
    'inciso_des_id',
    'date_start_commission',
    'reason_commision',
    'resolution_comm_description',
    'resolution_comm_date',
    'resolution_comm_type',
}

REQUIRED_FIELDS_COMM_DESTINATION_AC = {
    'nro_puesto_des',
    'nro_place_des',
    'sec_place_des',
}

REQUIRED_FIELDS_COMM_ORIGIN_AC = {
    'nro_puesto',
    'nro_place',
    'sec_place',
}

_logger = logging.getLogger(__name__)


class ONSCMigration(models.Model):
    _name = "onsc.migration"

    state = fields.Selection(STATE, string='Estado', readonly=True, default='draft')
    error = fields.Text("Error")
    document_file = fields.Binary(string='Archivo de carga', required=True)
    document_filename = fields.Char('Nombre del documento', store=True)
    line_ids = fields.One2many('onsc.migration.line', 'migration_id', domain=[('state', '!=', 'error')],
                               string='Líneas')
    error_line_ids = fields.One2many(
        comodel_name='onsc.migration.line',
        inverse_name='migration_id',
        domain=[('state', '=', 'error')],
        string='Líneas con errores')

    def button_process(self):
        self._cr.execute("""update "onsc_migration_line" set state ='in_process' where id =  %s """ % self.id)
        self.env.cr.commit()
        self.process_binary()
        return True

    def _set_base_vals(self, row_dict, row):
        row_dict.update({
            'migration_id': self.id,
            'doc_nro': row[2] and str(row[2]),
            'first_name': row[3] and str(row[3]),
            'second_name': row[4] and str(row[4]),
            'first_surname': row[5] and str(row[5]),
            'second_surname': row[6] and str(row[6]),
            'name_ci': row[7] and str(row[7]),
            'birth_date': self.is_datetime(row[9]) and row[9].strftime("%Y-%m-%d"),
            'sex': row[11] and str(row[11]),
            'citizenship': row[13],
            'crendencial_serie': row[14] and str(row[14]),
            'credential_number': row[15] and str(row[15]),
            'personal_phone': row[16] and str(row[16]),
            'email': row[17] and str(row[17]),
            'email_inst': row[18] and str(row[18]),
            'address_nro_door': row[22] and str(row[22]),
            'address_is_bis': row[25],
            'address_apto': row[26] and str(row[26]),
            'address_place': row[27] and str(row[27]),
            'address_zip': row[28] and str(row[28]),
            'address_block': row[29] and str(row[29]),
            'address_sandlot': row[30] and str(row[30]),
            'date_income_public_administration': self.is_datetime(row[32]) and row[32].strftime("%Y-%m-%d"),
            'inactivity_years': row[33],
            'graduation_date': self.is_datetime(row[34]) and row[34].strftime("%Y-%m-%d"),
            'date_start': self.is_datetime(row[35]) and row[35].strftime("%Y-%m-%d"),
            'nro_puesto': row[45] and str(row[45]),
            'nro_place': row[46] and str(row[46]),
            'sec_place': row[47] and str(row[47]),
            'call_number': row[51] and str(row[51]),
            'reason_description': row[52] and str(row[52]),
            'resolution_description': row[57],
            'resolution_date': self.is_datetime(row[58]) and row[58].strftime("%Y-%m-%d"),
            'resolution_type': row[59],
            'retributive_day_formal': row[83],
            'retributive_day_formal_desc': row[84], })

    def _set_m2o_values(self, row_dict, row):
        country_id = row[0] and self.get_country(str(row[0]))
        doc_type_id = row[1] and self.get_doc_type(str(row[1]))
        marital_status_id = row[8] and self.get_status_civil(str(row[8]))
        gender_id = row[10] and self.get_gender(str(row[10]))
        if row[12] and row[0] != row[12]:
            birth_country_id = row[12] and self.get_country(str(row[12]))
        elif row[12]:
            birth_country_id = country_id
        else:
            birth_country_id = None
        address_state_id = row[19] and self.get_country_state(
            str(row[19]), country_id and country_id[0])
        address_location_id = self.is_numeric(row[20]) and self.get_location(
            str(row[20]), address_state_id and address_state_id[0])
        address_street_id = row[21] and self.get_street(str(row[21]),
                                                        address_location_id and address_location_id[0])
        address_street2_id = row[23] and self.get_street(str(row[23]),
                                                         address_location_id and address_location_id[0])
        address_street3_id = self.get_street(str(row[24]), address_location_id and address_location_id[0])
        health_provider_id = row[31] and self.get_health_provider(str(row[31]))
        inciso_id = row[36] and self.get_inciso(str(row[36]))
        operating_unit_id = row[37] and self.get_operating_unit(str(row[37]), inciso_id and inciso_id[0])
        program_project_id = self.get_office(
            str(row[38]),
            str(row[39]),
            operating_unit_id and operating_unit_id[0])
        regime_id = row[40] and self.get_regime(str(row[40]))
        descriptor1_id = row[41] and self.get_descriptor1(str(row[41]))
        descriptor2_id = row[42] and self.get_descriptor2(str(row[42]))
        descriptor3_id = row[43] and self.get_descriptor3(str(row[43]))
        descriptor4_id = row[44] and self.get_descriptor4(str(row[44]))
        state_place_id = row[48] and self.get_state_place(str(row[48]))
        occupation_id = row[49] and self.get_occupation(str(row[49]))
        income_mechanism_id = row[50] and self.get_income_mechanism(str(row[50]))
        norm_id = row[53] and self.get_norm(
            str(row[53]),
            row[54],
            row[55],
            row[56],
            inciso_id and inciso_id[0]
        )
        budget_item_id = self.get_budget_item(
            row,
            descriptor3_id and descriptor3_id[0],
            descriptor1_id and descriptor1_id[0],
            descriptor2_id and descriptor2_id[0],
            descriptor4_id and descriptor4_id[0]
        )

        security_job_id = row[87] and self.get_security_job(str(row[87]))

        row_dict.update({
            'country_id': country_id and country_id[0],
            'doc_type_id': doc_type_id and doc_type_id[0],
            'marital_status_id': marital_status_id and marital_status_id[0],
            'gender_id': gender_id and gender_id[0],
            'birth_country_id': birth_country_id and birth_country_id[0],
            'address_state_id': address_state_id and address_state_id[0],
            'address_street_id': address_street_id and address_street_id[0],
            'address_street2_id': address_street2_id and address_street2_id[0],
            'address_street3_id': address_street3_id and address_street3_id[0],
            'address_location_id': address_location_id and address_location_id[0],
            'health_provider_id': health_provider_id and health_provider_id[0],
            'inciso_id': inciso_id and inciso_id[0],
            'operating_unit_id': operating_unit_id and operating_unit_id[0],
            'program_project_id': program_project_id and program_project_id[0],
            'regime_id': regime_id and regime_id[0],
            'descriptor1_id': descriptor1_id and descriptor1_id[0],
            'descriptor2_id': descriptor2_id and descriptor2_id[0],
            'descriptor3_id': descriptor3_id and descriptor3_id[0],
            'descriptor4_id': descriptor4_id and descriptor4_id[0],
            'budget_item_id': budget_item_id and budget_item_id[0],
            'state_place_id': state_place_id and state_place_id[0],
            'occupation_id': occupation_id and occupation_id[0],
            'income_mechanism_id': income_mechanism_id and income_mechanism_id[0],
            'norm_id': norm_id and norm_id[0],

            # 'retributive_day_formal_id': retributive_day_formal_id,
            'security_job_id': security_job_id and security_job_id[0],
        })
        if not row[71]:
            retributive_day_id = row[82] and self.get_jornada_retributiva(
                str(row[82]),
                program_project_id and program_project_id[0])

            department_id = row[69] and self.get_department(str(row[69]),
                                                            operating_unit_id and operating_unit_id[0])
            row_dict.update({
                'retributive_day_id': row[82] and retributive_day_id and retributive_day_id[0],
                'department_id': department_id and department_id[0], })

    def process_binary(self):
        try:
            MigrationLine = self.env['onsc.migration.line'].suspend_security()
            if not self.document_file:
                return
            row_number = 0
            excel_data = io.BytesIO(base64.b64decode(self.document_file))
            workbook = openpyxl.load_workbook(excel_data, data_only=True)
            sheet = workbook.active

            for row in sheet.iter_rows(min_row=2, values_only=True):
                row_number += 1

                if not row[0] and not row[1] and not row[2]:
                    break

                row_dict = {}
                self._set_base_vals(row_dict, row)
                self._set_m2o_values(row_dict, row)

                if row_dict['norm_id']:
                    row_dict.update({
                        'norm_type': row[53] and str(row[53]),
                        'norm_number': row[54],
                        'norm_year': row[55],
                        'norm_article': row[56], })

                # SI ES COMISION
                if row[71]:
                    inciso_des_id = row[60] and self.get_inciso(str(row[60]))
                    operating_unit_des_id = row[61] and self.get_operating_unit(
                        str(row[61]),
                        inciso_des_id and inciso_des_id[0])
                    program_project_des_id = self.get_office(
                        str(row[62]),
                        str(row[63]),
                        operating_unit_des_id and operating_unit_des_id[0]
                    )
                    regime_des_id = row[64] and self.get_regime(str(row[64]))
                    state_place_des_id = row[68] and self.get_state_place(str(row[68]))
                    regime_commission_id = row[72] and self.get_commision_regime(str(row[72]))
                    norm_comm_id = row[74] and self.get_norm(
                        str(row[74]),
                        row[75],
                        row[76],
                        row[77],
                        inciso_des_id and inciso_des_id[0]
                    )
                    department_id = row[69] and self.get_department(str(row[69]),
                                                                    operating_unit_des_id and operating_unit_des_id[0])

                    row_dict['inciso_des_id'] = inciso_des_id and inciso_des_id[0]
                    row_dict['operating_unit_des_id'] = operating_unit_des_id and operating_unit_des_id[0]
                    row_dict['program_project_des_id'] = program_project_des_id and program_project_des_id[0]
                    row_dict['regime_des_id'] = regime_des_id and regime_des_id[0]
                    row_dict['nro_puesto_des'] = row[65]
                    row_dict['nro_place_des'] = row[66]
                    row_dict['sec_place_des'] = row[67]
                    row_dict['state_place_des_id'] = state_place_des_id and state_place_des_id[0]
                    row_dict['date_start_commission'] = self.is_datetime(row[70]) and row[70].strftime("%Y-%m-%d")
                    row_dict['type_commission'] = row[71]
                    row_dict['regime_commission_id'] = regime_commission_id and regime_commission_id[0]
                    row_dict['reason_commision'] = row[73]
                    row_dict['norm_comm_id'] = norm_comm_id and norm_comm_id[0]
                    if norm_comm_id:
                        row_dict['norm_comm_type'] = row[74]
                        row_dict['norm_comm_number'] = row[75]
                        row_dict['norm_comm_year'] = row[76]
                        row_dict['norm_comm_article'] = row[77]
                    row_dict['resolution_comm_description'] = row[78]
                    row_dict['resolution_comm_date'] = self.is_datetime(row[79]) and row[79].strftime("%Y-%m-%d")
                    row_dict['resolution_comm_type'] = row[80]
                    if row[82] and inciso_des_id:
                        if inciso_des_id[1] is True:
                            retributive_day_id = self.get_jornada_retributiva(
                                str(row[82]),
                                program_project_des_id and program_project_des_id[0])
                            row_dict['retributive_day_id'] = row[82] and retributive_day_id and retributive_day_id[0]
                        elif row_dict['program_project_id']:
                            retributive_day_id = self.get_jornada_retributiva(
                                str(row[82]), row_dict['program_project_id'])
                            row_dict['retributive_day_id'] = row[82] and retributive_day_id and retributive_day_id[0]
                    row_dict['department_id'] = department_id and department_id[0]
                else:
                    row_dict['end_date_contract'] = self.is_datetime(row[81]) and row[81].strftime("%Y-%m-%d")

                row_dict['id_movimiento'] = self.is_numeric(row[85]) and int(row[85])
                row_dict['state_move'] = row[86]
                if row_dict['state_move'] == 'BP':
                    norm_dis_id = row[91] and self.get_norm(
                        str(row[91]),
                        row[92],
                        row[93],
                        row[94],
                        row_dict.get('inciso_id')
                    )
                    row_dict['norm_dis_id'] = norm_dis_id and norm_dis_id[0]
                    if norm_dis_id:
                        row_dict['norm_dis_type'] = row[91]
                        row_dict['norm_dis_number'] = row[92]
                        row_dict['norm_dis_year'] = row[93]
                        row_dict['norm_dis_article'] = row[94]

                    causes_discharge_id = row[88] and self.get_causes_discharge(str(row[88]))
                    row_dict['end_date'] = self.is_datetime(row[89]) and row[89].strftime("%Y-%m-%d")
                    row_dict['causes_discharge_id'] = causes_discharge_id and causes_discharge_id[0]
                    row_dict['reason_discharge'] = row[90]
                    row_dict['resolution_dis_description'] = row[5]
                    row_dict['resolution_dis_date'] = self.is_datetime(row[96]) and row[96].strftime("%Y-%m-%d")
                    row_dict['resolution_dis_type'] = row[97]

                cleaned_data = {}
                for clave, valor in row_dict.items():
                    if valor is not None and valor != '' and valor is not False:
                        cleaned_data[clave] = valor.strip() if isinstance(valor, str) else valor

                new_line = MigrationLine.create(cleaned_data)
                message_error = self.validate(row, row_dict)
                new_line.validate_line(message_error)
                self.env.cr.commit()
            self.write({'state': 'process'})
            return True

        except Exception as e:
            error = "Línea %s Error: %s" % (row_number, tools.ustr(e))
            self.suspend_security().write({'error': error, 'state': 'error'})

    def validate(self, row, row_dict):
        message_error = []
        if row[59] and row_dict['resolution_type'] not in ['M', 'P', 'U']:
            message_error.append("Tipo de resolución no es válido")
        if row[11] and row_dict['sex'] not in ['male', 'feminine']:
            message_error.append("Sexo no es válido")
        if row[13] and row_dict['citizenship'] not in [tupla[0] for tupla in CITIZENSHIP]:
            message_error.append("El campo Ciudadanía no es válido")

        if (not row[65] and not row[66] and not row[67]) and (not row[45] and not row[46] and not row[47]):
            message_error.append("Los campo PLaza, Sec. Plaza y Puesto no son válidos")

        self._validate_m2o(row, row_dict, message_error)
        self._validate_norm(row, row_dict, message_error)
        self._validate_address(row, row_dict, message_error)
        self._validate_descriptors(row, row_dict, message_error)
        self._validate_commision(row, row_dict, message_error)
        return message_error

    def _validate_m2o(self, row, row_dict, message_error):

        if row[10] and not row_dict['gender_id']:
            message_error.append("El campo Género no es válido")
        if row[12] and not row_dict['birth_country_id']:
            message_error.append("El campo país de nacimiento no es válido")
        if row[31] and not row_dict['health_provider_id']:
            message_error.append("El campo Codigo de salud no es válido")
        if row[36] and not row_dict['inciso_id']:
            message_error.append("El campo Inciso no es válido")
        if row[37] and not row_dict['operating_unit_id']:
            message_error.append("El campo Unidad ejecutora no es válido")
        if row[38] and row[39] and not row_dict['program_project_id']:
            message_error.append("El campo Programa-Proyecto no es válido")
        if row[48] and not row_dict['state_place_id']:
            message_error.append("El campo Estado plaza no es válido")
        if row[49] and not row_dict['occupation_id']:
            message_error.append("El campo Ocupación no es válido")
        if row[50] and not row_dict['income_mechanism_id']:
            message_error.append("El campo Mecanismo de ingreso no es válido")
        if row[69] and not row_dict['department_id']:
            message_error.append("El campo Unidad organizativa no es válido")

        if row[87] and not row_dict['security_job_id']:
            message_error.append("El campo Seguridad de Puesto no es válido")
        if not row_dict['budget_item_id']:
            message_error.append("El campo Partida presupuestal no es válido")

    def _validate_norm(self, row, row_dict, message_error):
        if row[86] == 'BP' and row[88] and not row_dict['causes_discharge_id']:
            message_error.append("El campo Casual de egreso no es válido")
        if row[86] == 'BP' and (row[91] or row[92] or row[93] or row[94]) and not row_dict['norm_dis_id']:
            message_error.append("El campo Norma de la baja no es válido")
        if (row[53] or row[54] or row[55] or row[56]) and not row_dict['norm_id']:
            message_error.append("El campo Norma no es válido")

    def _validate_address(self, row, row_dict, message_error):
        if row[19] and not row_dict['address_state_id']:
            message_error.append("El campo Departamento no es válido")
        if row[20] and not row_dict['address_location_id']:
            message_error.append("El campo Localidad no es válido")
        if row[21] and not row_dict['address_street_id']:
            message_error.append("El campo Calle no es válido")
        if row[23] and not row_dict['address_street2_id']:
            message_error.append("El campo Esquina 1 no es válido")
        if row[24] and not row_dict['address_street3_id']:
            message_error.append("El campo Esquina 2 no es válido")
        if row[25] and not row_dict['address_is_bis']:
            message_error.append("El campo Bis no es válido")

    def _validate_descriptors(self, row, row_dict, message_error):
        if row[40] and not row_dict['regime_id']:
            message_error.append("El campo Régimen no es válido")
        if row[41] and not row_dict['descriptor1_id']:
            message_error.append("El campo Descriptor1 no es válido")
        if row[42] and not row_dict['descriptor2_id']:
            message_error.append("El campo Descriptor2 no es válido")
        if not row_dict['descriptor3_id']:
            message_error.append("El campo Descriptor3 no es válido")
        if row[44] and not row_dict['descriptor4_id']:
            message_error.append("El campo Descriptor4 no es válido")

    def _validate_commision(self, row, row_dict, message_error):
        if not row[71]:
            return
        if row[60] and not row_dict['inciso_des_id']:
            message_error.append("El campo Inciso destino no es válido")
        if row[61] and not row_dict['operating_unit_des_id']:
            message_error.append("El campo Unidad ejecutora destino no es válido")
        if row[62] and not row_dict['program_project_des_id']:
            message_error.append("El campo Programa-Proyecto destino no es válido")
        if row[64] and not row_dict['regime_des_id']:
            message_error.append("El campo Régimen destino no es válido")
        if row[68] and not row_dict['state_place_des_id']:
            message_error.append("El campo Plaza destino no es válido")
        if row[72] and not row_dict['regime_commission_id']:
            message_error.append("El campo Régimen de la comisión no es válido")
        if (row[74] or row[75] or row[76] or row[77]) and not row_dict['norm_comm_id']:
            message_error.append("El campo Norma comisión no es válido")
        if row[72] and not row_dict['regime_commission_id']:
            message_error.append("El campo Régimen de la comisión no es válido")

    def is_datetime(self, row):
        return type(row).__name__ == 'datetime' or False

    def is_numeric(self, row):
        return type(row).__name__ == 'int' or False

    def check_line(self, doc_nro, nro_puesto, nro_place, sec_place):
        self._cr.execute(
            """SELECT count(id) FROM onsc_migration_line WHERE state != 'error' and doc_nro = %s and nro_puesto = %s and nro_place =%s and sec_place =%s""",
            (doc_nro, nro_puesto, nro_place, sec_place))
        return self._cr.fetchone()[0]

    def get_country(self, code):
        self._cr.execute("""SELECT id FROM res_country WHERE code = %s""", (code,))
        return self._cr.fetchone()

    def get_doc_type(self, code):
        self._cr.execute("""SELECT id FROM onsc_cv_document_type WHERE code = %s""", (code,))
        return self._cr.fetchone()

    def get_status_civil(self, code):
        self._cr.execute("""SELECT id FROM onsc_cv_status_civil WHERE code = %s""", (code,))
        return self._cr.fetchone()

    def get_gender(self, code):
        self._cr.execute("""SELECT id FROM onsc_cv_gender WHERE code = %s""", (code,))
        return self._cr.fetchone()

    def get_country_state(self, code, country_id=None):
        self._cr.execute("""SELECT id FROM res_country_state WHERE code = %s AND country_id = %s""",
                         (code, country_id))
        return self._cr.fetchone()

    def get_location(self, code, address_state_id=None):
        self._cr.execute("""SELECT id FROM onsc_cv_location WHERE other_code = %s AND state_id = %s""",
                         (code, address_state_id))
        return self._cr.fetchone()

    def get_street(self, code, address_location_id=None):
        if address_location_id is False:
            self._cr.execute("""SELECT id FROM onsc_cv_street WHERE code = %s AND cv_location_id is null""",
                             (code,))
        else:
            self._cr.execute("""SELECT id FROM onsc_cv_street WHERE code = %s AND cv_location_id = %s""",
                             (code, address_location_id))
        return self._cr.fetchone()

    def get_health_provider(self, code):
        self._cr.execute("""SELECT id FROM onsc_legajo_health_provider WHERE code = %s""", (code,))
        return self._cr.fetchone()

    def get_inciso(self, code):
        self._cr.execute("""SELECT id, is_central_administration FROM onsc_catalog_inciso WHERE budget_code = %s""", (code,))
        return self._cr.fetchone()

    def get_operating_unit(self, code, inciso_id=None):
        self._cr.execute("""SELECT id FROM operating_unit WHERE budget_code = %s AND inciso_id=%s""",
                         (code, inciso_id))
        return self._cr.fetchone()

    def get_office(self, programa, proyecto, operating_unit_id=None):
        self._cr.execute("""SELECT id FROM onsc_legajo_office WHERE programa = %s AND proyecto = %s AND "unidadEjecutora"=%s
        """, (programa, proyecto, operating_unit_id))
        return self._cr.fetchone()

    def get_regime(self, code):
        self._cr.execute("""SELECT id FROM onsc_legajo_regime WHERE "codRegimen" = %s """, (code,))
        return self._cr.fetchone()

    def get_descriptor1(self, code):
        self._cr.execute("""SELECT id FROM onsc_catalog_descriptor1 WHERE code = %s""", (code,))
        return self._cr.fetchone()

    def get_descriptor2(self, code):
        self._cr.execute("""SELECT id FROM onsc_catalog_descriptor2 WHERE code = %s""", (code,))
        return self._cr.fetchone()

    def get_descriptor3(self, code):
        self._cr.execute("""SELECT id FROM onsc_catalog_descriptor3 WHERE code = %s""", (code,))
        return self._cr.fetchone()

    def get_descriptor4(self, code):
        self._cr.execute("""SELECT id FROM onsc_catalog_descriptor4 WHERE code = %s""", (code,))
        return self._cr.fetchone()

    def get_occupation(self, code):
        self._cr.execute("""SELECT id FROM onsc_catalog_occupation WHERE code = %s""", (code,))
        return self._cr.fetchone()

    def get_state_place(self, code):
        self._cr.execute("""SELECT id FROM onsc_legajo_state_square WHERE code = %s""", (code,))
        return self._cr.fetchone()

    def get_income_mechanism(self, code):
        self._cr.execute("""SELECT id FROM onsc_legajo_income_mechanism WHERE code = %s""", (code,))
        return self._cr.fetchone()

    def get_norm(self, tipoNorma, numeroNorma, anioNorma, articuloNorma, inciso_id=None):
        if self.is_numeric(numeroNorma) and self.is_numeric(anioNorma) and self.is_numeric(articuloNorma):
            self._cr.execute(
                """SELECT id FROM onsc_legajo_norm, onsc_catalog_inciso_onsc_legajo_norm_rel WHERE "tipoNormaSigla" = %s and "numeroNorma"= %s and "anioNorma" = %s and "articuloNorma"= %s and onsc_catalog_inciso_onsc_legajo_norm_rel.onsc_legajo_norm_id = onsc_legajo_norm.id AND onsc_catalog_inciso_onsc_legajo_norm_rel.onsc_catalog_inciso_id = %s""",
                (tipoNorma, numeroNorma, anioNorma, articuloNorma, inciso_id))
        return self._cr.fetchone()

    def get_budget_item(self, row, descriptor3_id=None, descriptor1_id=None, descriptor2_id=None, descriptor4_id=None):
        if not descriptor3_id:
            _sql = """SELECT id
                FROM onsc_legajo_budget_item
                WHERE
                "dsc3Id" is null"""
        else:
            _sql = """SELECT id
                FROM onsc_legajo_budget_item
                WHERE
                "dsc3Id" = %s""" % descriptor3_id
        if row[41]:
            if not descriptor1_id:
                _sql += """ AND "dsc1Id" is null"""
            else:
                _sql += """ AND "dsc1Id" = %s""" % descriptor1_id
        if row[42]:
            if not descriptor2_id:
                _sql += """ AND "dsc2Id" is null"""
            else:
                _sql += """ AND "dsc2Id" = %s""" % descriptor2_id
        if row[44]:
            if not descriptor4_id:
                _sql += """ AND "dsc4Id" is null"""
            else:
                _sql += """ AND "dsc4Id" = %s""" % descriptor4_id
        self._cr.execute(_sql)
        return self._cr.fetchone()

    def get_department(self, code, operating_unit_id=None):
        self._cr.execute("""SELECT id FROM hr_department WHERE code = %s AND operating_unit_id = %s""",
                         (code, operating_unit_id))
        return self._cr.fetchone()

    def get_jornada_retributiva(self, code, office_id):
        self._cr.execute(
            """SELECT id FROM onsc_legajo_jornada_retributiva WHERE "codigoJornada" = %s AND office_id = %s limit 1""",
            (code, office_id))
        return self._cr.fetchone()

    def get_security_job(self, code):
        self._cr.execute("""SELECT id FROM onsc_legajo_security_job WHERE name = %s""", (code,))
        return self._cr.fetchone()

    def get_causes_discharge(self, code):
        self._cr.execute("""SELECT id FROM onsc_legajo_causes_discharge WHERE code = %s """, (code,))
        return self._cr.fetchone()

    def get_commision_regime(self, code):
        self._cr.execute("""SELECT id FROM onsc_legajo_commission_regime WHERE cgn_code = %s """, (code,))
        return self._cr.fetchone()


class ONSCMigrationLine(models.Model):
    _name = "onsc.migration.line"

    migration_id = fields.Many2one('onsc.migration', string='Cabezal migracion', ondelete='cascade')
    error = fields.Char("Error", readonly=True)
    state = fields.Selection(STATE, string='Estado', readonly=True)
    country_id = fields.Many2one('res.country', string=u'País')
    doc_type_id = fields.Many2one('onsc.cv.document.type', string='Tipo de documento')
    doc_nro = fields.Char(string="Numero documento", index=True)
    first_name = fields.Char(string='Primer nombre')
    second_name = fields.Char(string='Segundo nombre')
    first_surname = fields.Char(string='Primer apellido')
    second_surname = fields.Char(string='Segundo apellido')
    name_ci = fields.Char(string='Nombre en cédula')
    marital_status_id = fields.Many2one("onsc.cv.status.civil", string="Estado civil")
    birth_date = fields.Date(string='Fecha de nacimiento')
    gender_id = fields.Many2one('onsc.cv.gender', string='Genero')
    sex = fields.Selection([('male', 'Masculino'), ('feminine', 'Femenino')], 'Sexo')
    birth_country_id = fields.Many2one('res.country', string=u'País de nacimiento')
    citizenship = fields.Selection(string="Ciudadanía",
                                   selection=CITIZENSHIP)
    crendencial_serie = fields.Char(string="Serie de la credencial", size=3)
    credential_number = fields.Char(string="Número de la credencial", size=6)
    personal_phone = fields.Char(string="Número de Teléfono")
    email = fields.Char(string="Email personal ")
    email_inst = fields.Char(string="Email institucional ")
    address_state_id = fields.Many2one('res.country.state', string='Departamento')
    address_location_id = fields.Many2one('onsc.cv.location', string="Localidad")
    address_street_id = fields.Many2one('onsc.cv.street', string="Calle")
    address_street2_id = fields.Many2one('onsc.cv.street', string="Esquina 1")
    address_street3_id = fields.Many2one('onsc.cv.street', string="Esquina 2")
    address_nro_door = fields.Char(string="Número de puerta")
    address_is_bis = fields.Selection(string="Bis", selection=[('S', 'SI'), ('N', 'NO')])
    address_apto = fields.Char(string="Apartamento")
    address_place = fields.Text(string="Paraje", size=200)
    address_zip = fields.Char(u'Código postal')
    address_block = fields.Char(string="Manzana", size=5)
    address_sandlot = fields.Char(string="Solar", size=5)
    health_provider_id = fields.Many2one("onsc.legajo.health.provider", u"Cobertura de salud")
    date_income_public_administration = fields.Date(string="Fecha de ingreso a la administración pública")
    inactivity_years = fields.Integer(string="Años de inactividad")
    graduation_date = fields.Date(string='Fecha de graduación')
    date_start = fields.Date(string="Fecha de alta")
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora")
    program_project_id = fields.Many2one('onsc.legajo.office', string='Programa - Proyecto')
    program = fields.Char(string='Programa', related="program_project_id.programa")
    project = fields.Char(string='Proyecto', related="program_project_id.proyecto")
    regime_id = fields.Many2one('onsc.legajo.regime', string='Régimen')
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor 1')
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor 2')
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor 3')
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor 4')
    nro_puesto = fields.Char(string="Puesto origen", index=True)
    nro_place = fields.Char(string="Plaza origen", index=True)
    sec_place = fields.Char(string="Secuencial Plaza origen", index=True)
    # state_place = fields.Selection(string="Estado plaza origen",
    #                                selection=[('O', 'Ocupado'), ('C', 'Fuera de cuadro'), ('R', 'Reservada'),
    #                                           ('S', 'Comisión saliente')])
    state_place_id = fields.Many2one('onsc.legajo.state.square', string='Estado plaza')
    occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación')
    income_mechanism_id = fields.Many2one('onsc.legajo.income.mechanism', string='Mecanismo de ingreso origen')
    call_number = fields.Char(string='Número de llamado origen')
    reason_description = fields.Char(string='Descripción del motivo alta')
    norm_id = fields.Many2one('onsc.legajo.norm', string='Norma')
    norm_type = fields.Char(string="Tipo norma")
    norm_number = fields.Integer(string='Número de norma')
    norm_year = fields.Integer(string='Año de norma')
    norm_article = fields.Integer(string='Artículo de norma')
    resolution_description = fields.Char(string='Descripción de la resolución')
    resolution_date = fields.Date(string='Fecha de la resolución')
    resolution_type = fields.Selection(
        [
            ('M', 'Inciso'),
            ('P', 'Presidencia o Poder ejecutivo'),
            ('U', 'Unidad ejecutora')
        ],
        string='Tipo de resolución'
    )
    inciso_des_id = fields.Many2one('onsc.catalog.inciso', string='Inciso destino')
    operating_unit_des_id = fields.Many2one("operating.unit", string="Unidad ejecutora destino")
    program_project_des_id = fields.Many2one('onsc.legajo.office', string='Programa - Proyecto destino')
    program_des = fields.Char(string='Programa destino', related="program_project_des_id.programa")
    project_des = fields.Char(string='Proyecto destino', related="program_project_des_id.proyecto")
    regime_des_id = fields.Many2one('onsc.legajo.regime', string='Régimen destino')
    nro_puesto_des = fields.Char(string="Puesto destino", index=True)
    nro_place_des = fields.Char(string="Plaza destino", index=True)
    sec_place_des = fields.Char(string="Secuencial Plaza destino", index=True)
    state_place_des_id = fields.Many2one('onsc.legajo.state.square', string='Estado plaza')
    department_id = fields.Many2one("hr.department", string="Unidad organizativa")
    date_start_commission = fields.Date(string='Fecha inicio comisión')
    type_commission = fields.Selection(string="Tipo de Comisión",
                                       selection=[('CS', 'Comisión de Servicio'), ('PC', 'Pase en Comisión')])

    regime_commission_id = fields.Many2one('onsc.legajo.commission.regime', string='Régimen de comisión')
    reason_commision = fields.Text(string='Descr motivo comisión')
    norm_comm_id = fields.Many2one('onsc.legajo.norm', string='Norma comisión')
    norm_comm_type = fields.Char(string="Tipo norma comisión")
    norm_comm_number = fields.Integer(string='Número de norma comisión')
    norm_comm_year = fields.Integer(string='Año de norma comisión')
    norm_comm_article = fields.Integer(string='Artículo de norma comisión')
    resolution_comm_description = fields.Char(string='Descripción de la resolución comisión')
    resolution_comm_date = fields.Date(string='Fecha de la resolución comisión')
    resolution_comm_type = fields.Char(string='Tipo de resolución comisión')
    end_date_contract = fields.Date(string="Vencimiento del contrato")
    retributive_day_id = fields.Many2one('onsc.legajo.jornada.retributiva',
                                         string='Carga horaria semanal según contrato')
    budget_item_id = fields.Many2one('onsc.legajo.budget.item', string='Partida presupuestal')
    retributive_day_formal = fields.Integer(string='Jornada Formal')
    retributive_day_formal_desc = fields.Char(string='Descripción de la jornada formal')
    # retributive_day_formal_id = fields.Many2one('onsc.legajo.jornada.retributiva', string='Jornada Formal')
    id_movimiento = fields.Char(string='id_movimiento')
    state_move = fields.Selection(string="Estado del Movimiento",
                                  selection=[('A', 'Aprobado'), ('AP', 'Alta pendiente'), ('BP', 'Baja pendiente')])
    security_job_id = fields.Many2one("onsc.legajo.security.job", string="Seguridad de puesto")
    end_date = fields.Date(string="Fecha de Baja")

    causes_discharge_id = fields.Many2one('onsc.legajo.causes.discharge', string='Causal de Egreso')
    reason_discharge = fields.Text(string='Descr motivo baja')
    norm_dis_id = fields.Many2one('onsc.legajo.norm', string='Norma de la baja')
    norm_dis_type = fields.Char(string="Tipo norma de la baja")
    norm_dis_number = fields.Integer(string='Número de norma de la baja')
    norm_dis_year = fields.Integer(string='Año de norma de la baja')
    norm_dis_article = fields.Integer(string='Artículo de norma de la baja')
    resolution_dis_description = fields.Char(string='Descripción de la resolución de la baja')
    resolution_dis_date = fields.Date(string='Fecha de la resolución de la baja')
    resolution_dis_type = fields.Char(string='Tipo de resolución de la baja')

    partner_id = fields.Many2one('res.partner', string='Contacto')

    def validate_line(self, message_error):
        for required_field in REQUIRED_FIELDS:
            if not eval('self.%s' % required_field):
                message_error.append("El campo %s no es válido" % self._fields[required_field].string)

        # BLOQUE DE VALIDACION DE FIELDS SELECTION
        if self.sex not in ('male', 'feminine'):
            message_error.append("El campo Sexo no es válido")
        if self.state_move not in ('A', 'AP', 'BP'):
            message_error.append("El campo Estado del Movimiento no es válido")
        if self.address_street_id:
            message_error = self.validate_adress(message_error)

        if self.type_commission:
            self._validate_line_commission(message_error)
        else:
            message_error = self._validate_line_no_required(message_error)

        if message_error:
            error = '\n'.join(message_error)
            state = 'error'
        else:
            error = ''
            state = 'draft'

        self._cr.execute(
            """UPDATE "onsc_migration_line" SET state = '%s',error = '%s' where id = %s """ % (state, error, self.id))

    def _validate_line_commission(self, message_error):
        for required_field in REQUIRED_FIELDS_COMM:
            if not eval('self.%s' % required_field):
                message_error.append("El campo %s no es válido" % self._fields[required_field].string)
        if self.inciso_id.is_central_administration:
            for required_field in REQUIRED_FIELDS_COMM_ORIGIN_AC:
                if not eval('self.%s' % required_field):
                    message_error.append("El campo %s no es válido" % self._fields[required_field].string)
        if self.inciso_des_id.is_central_administration:
            for required_field in REQUIRED_FIELDS_COMM_DESTINATION_AC:
                if not eval('self.%s' % required_field):
                    message_error.append("El campo %s no es válido" % self._fields[required_field].string)

    def _validate_line_no_required(self, message_error):
        if not self.program_project_id:
            message_error.append("No se encontró oficina para la combinación Programa/Proyecto")
        if not self.regime_id:
            message_error.append("El campo Regimen no es válido")
        if not self.operating_unit_id:
            message_error.append("El campo UE no es válido")
        if not self.nro_puesto:
            message_error.append("El campo Puesto origen no es válido")
        if not self.nro_place:
            message_error.append("El campo Plaza origen no es válido")
        if not self.sec_place:
            message_error.append("El campo Secuencial Plaza origen no es válido")
        return message_error

    def validate_adress(self, message_error):
        if not self.address_location_id:
            message_error.append("El campo Localidad no es válido")
        if not self.address_state_id:
            message_error.append("El campo Departamento no es válido")
        return message_error

    # FASE 2
    def _get_info_from_line(self):
        vals = ({
            'name': calc_full_name(self.first_name,
                                   self.second_name,
                                   self.first_surname,
                                   self.second_surname),
            'country_of_birth_id': self.birth_country_id.id,
            'institutional_email': self.email_inst,
            'health_provider_id': self.health_provider_id.id,
            'cv_first_name': self.first_name,
            'cv_second_name': self.second_name,
            'cv_last_name_1': self.first_surname,
            'cv_last_name_2': self.second_surname,
            'cv_birthdate': self.birth_date,
            'personal_phone': self.personal_phone,
            'email': self.email,
            'cv_nro_doc': self.doc_nro,
            'uy_citizenship': self.citizenship,
            'crendencial_serie': self.crendencial_serie,
            'credential_number': self.credential_number,
            'marital_status_id': self.marital_status_id and self.marital_status_id.id,
            'country_id': self.country_id.id,
            'cv_address_street_id': self.address_street_id.id,
            'cv_address_street2_id': self.address_street2_id.id,
            'cv_address_street3_id': self.address_street3_id.id,
            'cv_address_state_id': self.address_state_id.id,
            'cv_address_location_id': self.address_location_id.id,
            'cv_address_nro_door': self.address_nro_door,
            'cv_address_apto': self.address_apto,
            'cv_address_zip': self.address_zip,
            'cv_address_is_cv_bis': self.address_is_bis,
            'cv_address_place': self.address_place,
            'cv_address_block': self.address_block,
            'cv_address_sandlot': self.address_sandlot,
            'cv_gender_id': self.gender_id.id,
            'cv_sex': self.sex,
            'cv_sex_updated_date': self.create_date,
            'gender_date': self.create_date,
            'cv_emissor_country_id': self.country_id.id,
            'cv_document_type_id': self.doc_type_id.id,

        })
        return vals

    def _get_info_fromcv(self, cv_digital_id):

        vals = {'emergency_service_id': cv_digital_id.emergency_service_id.id,
                'prefix_emergency_phone_id': cv_digital_id.prefix_emergency_phone_id.id,
                'emergency_service_telephone': cv_digital_id.emergency_service_telephone,
                'digitized_document_file': cv_digital_id.digitized_document_file,
                'digitized_document_filename': cv_digital_id.digitized_document_filename,
                'health_department_id': cv_digital_id.health_department_id.id,
                'prefix_phone_id': cv_digital_id.prefix_phone_id.id,
                'prefix_mobile_phone_id': cv_digital_id.prefix_mobile_phone_id.id,
                'mobile_phone': cv_digital_id.mobile_phone,
                'allow_content_public': cv_digital_id.allow_content_public,
                'situation_disability': cv_digital_id.situation_disability,
                'see': cv_digital_id.see,
                'hear': cv_digital_id.hear,
                'walk': cv_digital_id.walk,
                'speak': cv_digital_id.speak,
                'realize': cv_digital_id.realize,
                'lear': cv_digital_id.lear,
                'interaction': cv_digital_id.interaction,
                'need_other_support': cv_digital_id.need_other_support,
                'is_need_other_support': cv_digital_id.is_need_other_support,
                'is_cv_gender_public': cv_digital_id.is_cv_gender_public,
                'is_cv_race_public': cv_digital_id.is_cv_race_public,
                'other_information_official': cv_digital_id.other_information_official,
                'is_driver_license': cv_digital_id.is_driver_license,
                'is_public_information_victim_violent': cv_digital_id.is_public_information_victim_violent,
                'cv_race2': cv_digital_id.cv_race2,
                'cv_race_ids': cv_digital_id.cv_race_ids,
                'cv_first_race_id': cv_digital_id.cv_first_race_id,
                'afro_descendants_filename': cv_digital_id.afro_descendants_filename,
                'afro_descendants_file': cv_digital_id.afro_descendants_file,
                'is_afro_descendants': cv_digital_id.is_afro_descendants,
                'afro_descendant_date': cv_digital_id.afro_descendant_date,
                'is_occupational_health_card': cv_digital_id.is_occupational_health_card,
                'occupational_health_card_date': cv_digital_id.occupational_health_card_date,
                'occupational_health_card_file': cv_digital_id.occupational_health_card_file,
                'occupational_health_card_filename': cv_digital_id.occupational_health_card_filename,
                'is_medical_aptitude_certificate_status': cv_digital_id.is_medical_aptitude_certificate_status,
                'medical_aptitude_certificate_date': cv_digital_id.medical_aptitude_certificate_date,
                'medical_aptitude_certificate_file': cv_digital_id.medical_aptitude_certificate_file,
                'medical_aptitude_certificate_filename': cv_digital_id.medical_aptitude_certificate_filename,
                'relationship_victim_violent_file': cv_digital_id.relationship_victim_violent_file,
                'is_victim_violent': cv_digital_id.is_victim_violent,
                'relationship_victim_violent_filename': cv_digital_id.relationship_victim_violent_filename,
                'people_disabilitie': cv_digital_id.people_disabilitie,
                'document_certificate_file': cv_digital_id.document_certificate_file,
                'document_certificate_filename': cv_digital_id.document_certificate_filename,
                'certificate_date': cv_digital_id.certificate_date,
                'to_date': cv_digital_id.to_date,
                'disability_date': cv_digital_id.disability_date,

                }
        return vals

    def process_line(self, limit=200):
        Partner = self.env['res.partner'].suspend_security()
        CVDigital = self.env['onsc.cv.digital'].suspend_security()
        Employee = self.env['hr.employee'].suspend_security()
        AltaVL = self.env['onsc.legajo.alta.vl'].suspend_security()
        Contract = self.env['hr.contract'].suspend_security()

        for line in self.search([('state', 'in', ['draft'])], limit=limit):
            try:
                employee = line._get_employee(Employee)  # existe el funcionario?
                if not employee:
                    partner = line._create_contact(Partner)
                    cv_digital = line._create_cv(CVDigital, partner)
                    if line.state_move != 'AP':
                        employee = line._create_employee(Employee, partner, cv_digital)
                        line._create_legajo(employee)
                        cv_digital.write({'is_docket': True})
                if line.state_move == 'AP':
                    line._create_alta_vl(AltaVL, partner)
                else:
                    contract = line._create_contract(Contract, employee)
                    if line.state_move == 'BP':
                        line.update_baja_vl(contract)

                line.write({'state': 'process'})
                self.env.cr.commit()
            except Exception as e:
                self.env.cr.rollback()
                line.write({
                    'state': 'error',
                    'error': tools.ustr(e)
                })
                self.env.cr.commit()

    def _create_contact(self, Partner):
        try:
            partner = Partner.search([
                ('cv_nro_doc', '=', self.doc_nro),
                ('cv_emissor_country_id', '=', self.country_id.id),
                ('cv_document_type_id', '=', self.doc_type_id.id),
            ], limit=1)
            if not partner:
                data_partner = {
                    'cv_sex': self.sex,
                    'cv_emissor_country_id': self.country_id.id,
                    'cv_nro_doc': self.doc_nro,
                    'cv_document_type_id': self.doc_type_id.id,
                    'email': self.email,
                    'cv_dnic_name_1': self.first_name,
                    'cv_dnic_name_2': self.second_name,
                    'cv_dnic_lastname_1': self.first_surname,
                    'cv_dnic_lastname_2': self.second_surname,
                    'cv_dnic_full_name': self.name_ci,
                    'cv_birthdate': self.birth_date,
                    'cv_first_name': self.first_name,
                    'cv_second_name': self.second_name,
                    'cv_last_name_1': self.first_surname,
                    'cv_last_name_2': self.second_surname,
                    'is_partner_cv': True,

                }
                partner = Partner.with_context(can_update_contact_cv=True).create(data_partner)
                # self.write({'partner_id': partner.id})
            else:
                data_partner = {
                    'cv_dnic_name_1': self.first_name,
                    'cv_dnic_name_2': self.second_name,
                    'cv_dnic_lastname_1': self.first_surname,
                    'cv_dnic_lastname_2': self.second_surname,
                    'cv_dnic_full_name': self.name_ci,
                    'cv_birthdate': self.birth_date,
                    'cv_first_name': self.first_name,
                    'cv_second_name': self.second_name,
                    'cv_last_name_1': self.first_surname,
                    'cv_last_name_2': self.second_surname,
                    'is_partner_cv': True,

                }
                partner.with_context(can_update_contact_cv=True).write(data_partner)
            return partner
            # self.write({'partner_id': partner.id})
            # self.env.cr.commit()
        except Exception as e:
            raise ValidationError("No se puedo crear el contacto: " + tools.ustr(e))
            # self.env.cr.rollback()
            # self.write({'state': 'error', 'error': "No se puedo crear el contacto: " + tools.ustr(e)})
            # self.env.cr.commit()

    def _create_cv(self, CVDigital, partner_id):
        try:
            cv_digital = CVDigital.search([
                ('partner_id', '=', partner_id.id),
                ('type', '=', 'cv')
            ], limit=1)
            if not cv_digital:
                data = {
                    'partner_id': partner_id.id,
                    'personal_phone': self.personal_phone,
                    'email': self.email_inst,
                    'country_id': self.country_id.id,
                    'marital_status_id': self.marital_status_id and self.marital_status_id.id,
                    'country_of_birth_id': self.birth_country_id.id,
                    'uy_citizenship': self.citizenship,
                    'crendencial_serie': self.crendencial_serie,
                    'credential_number': self.credential_number,
                    'cv_address_state_id': self.address_state_id.id,
                    'cv_address_location_id': self.address_location_id.id,
                    'cv_address_street_id': self.address_street_id.id,
                    'cv_address_street2_id': self.address_street2_id.id,
                    'cv_address_street3_id': self.address_street3_id.id,
                    'cv_address_zip': self.address_zip,
                    'cv_address_nro_door': self.address_nro_door,
                    'cv_address_is_cv_bis': self.address_is_bis,
                    'cv_address_apto': self.address_apto,
                    'cv_address_place': self.address_place,
                    'cv_address_block': self.address_block,
                    'cv_address_sandlot': self.address_sandlot,
                    'health_provider_id': self.health_provider_id.id,

                }
                return CVDigital.create(data)
            else:
                data = {'email': self.email_inst,
                        'marital_status_id': self.marital_status_id and self.marital_status_id.id,
                        'health_provider_id': self.health_provider_id.id
                        }
                cv_digital.write(data)
                return cv_digital
        except Exception as e:
            raise ValidationError("No se puedo crear el CV: " + tools.ustr(e))
            # self.env.cr.rollback()
            # self.write({'state': 'error', 'error': "No se puedo crear el CV: " + tools.ustr(e)})
            # self.env.cr.commit()

    def _create_alta_vl(self, AltaVL, partner_id):
        try:
            data_alta_vl = {
                'partner_id': partner_id.id,
                'full_name': partner_id.cv_full_name,
                'date_start': self.date_start,
                'inciso_id': self.inciso_id.id,
                'operating_unit_id': self.operating_unit_id.id,
                'cv_sex': self.sex,
                'cv_birthdate': self.birth_date,
                'cv_document_type_id': self.doc_type_id.id,
                # 'is_reserva_sgh': self.is_reserva_sgh,
                'crendencial_serie': self.crendencial_serie,
                'credential_number': self.credential_number,
                'regime_id': self.regime_id.id,
                'descriptor1_id': self.descriptor1_id.id if self.descriptor1_id else False,
                'descriptor2_id': self.descriptor2_id.id if self.descriptor2_id else False,
                'descriptor3_id': self.descriptor3_id.id if self.descriptor3_id else False,
                'descriptor4_id': self.descriptor4_id.id if self.descriptor4_id else False,
                'nroPuesto': self.nro_puesto,
                'nroPlaza': self.nro_place,
                'secPlaza': self.sec_place,
                'department_id': self.department_id.id if self.department_id else False,
                'security_job_id': self.security_job_id.id if self.security_job_id else False,
                'occupation_id': self.occupation_id.id if self.occupation_id else False,
                'date_income_public_administration': self.date_income_public_administration,
                'income_mechanism_id': self.income_mechanism_id.id if self.income_mechanism_id else False,
                'inactivity_years': self.inactivity_years,
                'graduation_date': self.graduation_date,
                'contract_expiration_date': self.end_date_contract,
                'reason_description': self.reason_description,
                'program_project_id': self.program_project_id.id if self.program_project_id else False,
                'resolution_description': self.resolution_description,
                'resolution_date': self.resolution_date,
                'resolution_type': self.resolution_type,
                'retributive_day_id': self.retributive_day_id.id if self.retributive_day_id else False,
                'norm_id': self.norm_id.id if self.norm_id else False,
                'call_number': self.call_number,
                'codigoJornadaFormal': self.retributive_day_formal,
                'country_of_birth_id': self.birth_country_id.id if self.birth_country_id else False,
                'marital_status_id': self.marital_status_id.id if self.marital_status_id else False,
                'uy_citizenship': self.citizenship,
                'personal_phone': self.personal_phone,
                'email': self.email,
                'cv_address_street_id': self.address_street_id.id if self.address_street_id else False,
                'cv_address_street2_id': self.address_street2_id.id if self.address_street2_id else False,
                'cv_address_street3_id': self.address_street3_id.id if self.address_street3_id else False,
                'health_provider_id': self.health_provider_id.id if self.health_provider_id else False,
                # 'mass_upload_id': self.id,
            }
            altavl = AltaVL.with_context(is_migration=True).create(data_alta_vl)

            return altavl
        except Exception as e:
            raise ValidationError("No se puedo crear el AltaVL: " + tools.ustr(e))
            # self.env.cr.rollback()
            # self.write({'state': 'error', 'error': "No se puedo crear el CV: " + tools.ustr(e)})
            # self.env.cr.commit()

    def _create_employee(self, Employee, partner_id, cv_digital):
        try:
            employee = Employee.search([
                ('cv_emissor_country_id', '=', self.country_id.id),
                ('cv_document_type_id', '=', self.doc_type_id.id),
                ('cv_nro_doc', '=', partner_id.cv_nro_doc),
            ], limit=1)
            if not employee:
                vals = self.suspend_security()._get_info_from_line()
                vals.update(self._get_info_fromcv(cv_digital))
                employee = Employee.suspend_security().create(vals)
            return employee

        except Exception as e:
            raise ValidationError("No se puedo crear el funcionario: " + tools.ustr(e))

    def _create_legajo(self, employee):
        return self.env['onsc.legajo']._get_legajo(
            employee,
            self.date_income_public_administration,
            self.inactivity_years)

    def _create_contract(self, Contract, employee):
        Job = self.env['hr.job'].suspend_security()
        vals_contract1 = {
            'employee_id': employee.id,
            'name': employee.name,
            'date_start': self.date_start or fields.Date.today(),
            'inciso_id': self.inciso_id.id,
            'operating_unit_id': self.operating_unit_id.id,
            'income_mechanism_id': self.income_mechanism_id.id,
            'program': self.program_project_id.programa,
            'project': self.program_project_id.proyecto,
            'regime_id': self.regime_id.id,
            'occupation_id': self.occupation_id.id,
            'descriptor1_id': self.descriptor1_id.id,
            'descriptor2_id': self.descriptor2_id.id,
            'descriptor3_id': self.descriptor3_id.id,
            'descriptor4_id': self.descriptor4_id.id,
            'position': self.nro_puesto,
            'workplace': self.nro_place,
            'sec_position': self.sec_place,
            'graduation_date': self.graduation_date,
            'reason_description': self.reason_description,
            'norm_code_id': self.norm_id.id,
            'resolution_description': self.resolution_description,
            'resolution_date': self.resolution_date,
            'resolution_type': self.resolution_type,
            'call_number': self.call_number,
            'contract_expiration_date': self.end_date_contract,
            'id_alta': self.id_movimiento,
            'state_square_id': self.state_place_id.id,
            'wage': 1
        }

        if not self.type_commission:
            vals_contract1.update({
                'legajo_state': 'active',
                'code_day': self.retributive_day_formal,
                'description_day': self.retributive_day_formal_desc,
                'retributive_day_id': self.retributive_day_id.id,
            })
            contracts = Contract.suspend_security().create(vals_contract1)
            if self.department_id and self.security_job_id:
                Job.create_job(
                    contracts,
                    self.department_id,
                    self.create_date,
                    self.security_job_id
                )
        else:
            vals_contract2 = vals_contract1.copy()
            vals_contract1.update({
                'legajo_state': 'outgoing_commission'
            })
            vals_contract2.update({
                'legajo_state': 'incoming_commission',
                'inciso_id': self.inciso_des_id.id,
                'operating_unit_id': self.operating_unit_des_id.id,
                'program': self.program_project_des_id.programa,
                'project': self.program_project_des_id.proyecto,
                'regime_id': self.regime_des_id.id,
                'position': self.nro_puesto_des,
                'workplace': self.nro_place_des,
                'sec_position': self.sec_place_des,
                'state_square_id': self.state_place_des_id.id,

            })

            if self.inciso_des_id.is_central_administration:
                contract1 = Contract.suspend_security().create(vals_contract1)
                vals_contract2.update({
                    'cs_contract_id': contract1.id,
                    'code_day': self.retributive_day_formal,
                    'description_day': self.retributive_day_formal_desc,
                    'retributive_day_id': self.retributive_day_id.id,
                })
            contract2 = Contract.suspend_security().create(vals_contract2)
            contracts = contract2
            contracts |= contract1

            if self.inciso_des_id and self.inciso_des_id.is_central_administration and self.department_id and self.security_job_id:
                Job.create_job(
                    contract2,
                    self.department_id,
                    self.date_start_commission,
                    self.security_job_id
                )

        return contracts

    def _get_employee(self, Employee, use_search_count=False):
        args = [
            ('cv_emissor_country_id', '=', self.country_id.id),
            ('cv_document_type_id', '=', self.doc_type_id.id),
            ('cv_nro_doc', '=', self.doc_nro),
        ]
        if use_search_count:
            return Employee.search_count(args)
        return Employee.search(args, limit=1)

    def update_baja_vl(self, contract_id):
        data = {
            'id_deregistration_discharge': self.id_movimiento,
            'reason_deregistration': self.reason_discharge or False,
            'norm_code_deregistration_id': self.norm_comm_id and self.norm_id.id or False,
            'type_norm_deregistration': self.norm_comm_type or False,
            'norm_number_deregistration': self.norm_comm_number or False,
            'norm_year_deregistration': self.norm_comm_year or False,
            'norm_article_deregistration': self.norm_comm_article or False,
            'resolution_description_deregistration': self.resolution_dis_description or False,
            'resolution_date_deregistration': self.resolution_dis_date or False,
            'resolution_type_deregistration': self.resolution_dis_type or False,
            'causes_discharge_id': self.causes_discharge_id and self.causes_discharge_id.id or False,
            'legajo_state': 'baja',
        }

        contract_id.suspend_security().write(data)
        contract_id.suspend_security().deactivate_legajo_contract(
            date_end=self.end_date
        )

        return True
