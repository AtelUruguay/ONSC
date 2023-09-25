import base64
import io
import logging

import openpyxl as openpyxl

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
    'descriptor3_id',
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

REQUIRED_FIELDS_COMM_AC = {
    'nro_puesto',
    'nro_place',
    'sec_place',
    'nro_puesto_des',
    'nro_place_des',
    'sec_place_des',
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
            'doc_nro': str(row[2]),
            'first_name': str(row[3]),
            'second_name': str(row[4]),
            'first_surname': str(row[5]),
            'second_surname': str(row[6]),
            'name_ci': str(row[7]),
            'birth_date': self.is_datetime(row[9]) and row[9].strftime("%Y-%m-%d"),
            'sex': str(row[11]),
            'citizenship': row[13],
            'crendencial_serie': str(row[14]),
            'credential_number': str(row[15]),
            'personal_phone': str(row[16]),
            'email': str(row[17]),
            'email_inst': str(row[18]),
            'address_nro_door': str(row[22]),
            'address_is_bis': row[25],
            'address_apto': str(row[26]),
            'address_place': str(row[27]),
            'address_zip': str(row[28]),
            'address_block': str(row[29]),
            'address_sandlot': str(row[30]),
            'date_income_public_administration': self.is_datetime(row[32]) and row[32].strftime("%Y-%m-%d"),
            'inactivity_years': row[33],
            'graduation_date': self.is_datetime(row[34]) and row[34].strftime("%Y-%m-%d"),
            'date_start': self.is_datetime(row[35]) and row[35].strftime("%Y-%m-%d"),
            'nro_puesto': str(row[45]),
            'nro_place': str(row[46]),
            'sec_place': str(row[47]),
            'call_number': str(row[51]),
            'reason_description': str(row[52]),
            'norm_type': str(row[53]),
            'norm_number': row[54],
            'norm_year': row[55],
            'norm_article': row[56],
            'resolution_description': row[57],
            'resolution_date': self.is_datetime(row[58]) and row[58].strftime("%Y-%m-%d"),
            'resolution_type': row[59],
            'retributive_day_formal': row[83],
            'retributive_day_formal_desc': row[84],

        })

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
        occupation_id = row[45] and self.get_occupation(str(row[49]))
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
        department_id = row[69] and self.get_department(str(row[69]),
                                                        operating_unit_id and operating_unit_id[0])
        retributive_day_id = row[82] and self.get_jornada_retributiva(
            str(row[82]),
            program_project_id and program_project_id[0])
        # retributive_day_formal_id = row[83] and self.get_jornada_retributiva(
        #     str(row[83]),
        #     program_project_id and program_project_id[0])
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
            'department_id': department_id and department_id[0],
            'retributive_day_id': retributive_day_id and retributive_day_id[0],
            # 'retributive_day_formal_id': retributive_day_formal_id,
            'security_job_id': security_job_id and security_job_id[0],
        })

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
                # count = self.check_line(str(row[2]), str(row[45]), str(row[46]), str(row[47]))
                if not row[0] and not row[1] and not row[2]:
                    break

                row_dict = {}
                self._set_base_vals(row_dict, row)
                self._set_m2o_values(row_dict, row)

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
                    row_dict['norm_comm_type'] = row[74]
                    row_dict['norm_comm_number'] = row[75]
                    row_dict['norm_comm_year'] = row[76]
                    row_dict['norm_comm_article'] = row[77]
                    row_dict['resolution_comm_description'] = row[78]
                    row_dict['resolution_comm_date'] = self.is_datetime(row[79]) and row[79].strftime("%Y-%m-%d")
                    row_dict['resolution_comm_type'] = row[80]
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
                    causes_discharge_id = row[88] and self.get_causes_discharge(str(row[88]))
                    row_dict['end_date'] = self.is_datetime(row[89]) and row[89].strftime("%Y-%m-%d")
                    row_dict['causes_discharge_id'] = causes_discharge_id and causes_discharge_id[0]
                    row_dict['reason_discharge'] = row[90]
                    row_dict['norm_dis_id'] = norm_dis_id and norm_dis_id[0]
                    row_dict['norm_dis_type'] = row[91]
                    row_dict['norm_dis_number'] = row[92]
                    row_dict['norm_dis_year'] = row[93]
                    row_dict['norm_dis_article'] = row[94]
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

        self._validate_m2o(row, row_dict, message_error)
        self._validate_norm(row, row_dict, message_error)
        self._validate_address(row, row_dict, message_error)
        self._validate_descriptors(row, row_dict, message_error)
        self._validate_commision(row, row_dict, message_error)
        return message_error

    def _validate_m2o(self, row, row_dict, message_error):
        if row[8] and not row_dict['marital_status_id']:
            message_error.append("El campo Estado civil no es válido")
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
        if row[82] and not row_dict['retributive_day_id']:
            message_error.append("El campo Jornada retributiva no es válido")
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
        if row[43] and not row_dict['descriptor3_id']:
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
        self._cr.execute("""SELECT id FROM onsc_catalog_inciso WHERE budget_code = %s""", (code,))
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
    doc_nro = fields.Char(string="Numero documento")
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
    nro_puesto = fields.Char(string="Puesto origen")
    nro_place = fields.Char(string="Plaza origen")
    sec_place = fields.Char(string="Secuencial Plaza origen")
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
    nro_puesto_des = fields.Char(string="Puesto destino")
    nro_place_des = fields.Char(string="Plaza destino")
    sec_place_des = fields.Char(string="Secuencial Plaza destino")
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
            for required_field in REQUIRED_FIELDS_COMM_AC:
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
    def _get_info_from_line(self, line):
        vals = ({
            'country_of_birth_id': line.birth_country_id.id,
            'institutional_email': line.email_inst,
            'health_provider_id': line.health_provider_id.id,
            'cv_first_name': line.first_name,
            'cv_second_name': line.second_name,
            'cv_last_name_1': line.first_surname,
            'cv_last_name_2': line.second_surname,
            'cv_birthdate': line.birth_date,
            'personal_phone': line.personal_phone,
            'email': line.email,
            'cv_nro_doc': line.doc_nro,
            # todo hacer casteo entre valores que viene en la planilla y los que seusa  en CV
            'uy_citizenship': line.citizenship,
            'crendencial_serie': line.crendencial_serie,
            'credential_number': line.credential_number,
            'marital_status_id': line.marital_status_id.id,
            'country_id': line.country_id.id,
            'cv_address_street_id': line.address_street_idaddress_street_id.id,
            'cv_address_street2_id': line.address_street2_id.id,
            'cv_address_street3_id': line.address_street3_id.id,
            'cv_address_state_id': line.address_state_id.id,
            'cv_address_location_id': line.address_location_id.id,
            'cv_address_nro_door': line.address_nro_door,
            'cv_address_apto': line.address_apto,
            'cv_address_zip': line.address_zip,
            'cv_address_is_cv_bis': line.address_is_bis,
            'cv_address_place': line.address_place,
            'cv_address_block': line.address_block,
            'cv_address_sandlot': line.address_sandlotself.cv_digital_id.cv_address_sandlot,
            'cv_gender_id': line.gender_id.id,

        })
        return vals

    def create_employee(self, line, cv_digital):
        try:
            employee = super(ONSCMigrationLine,
                             self.with_context(is_alta_vl=True)).suspend_security()._get_legajo_employee()
            cv = employee.cv_digital_id
            if cv_digital:
                vals = employee.with_context(is_migration=True).suspend_security._get_info_fromcv()
                cv.with_context(documentary_validation='cv_address',
                                user_id=self.env.user.id,
                                can_update_contact_cv=True).button_documentary_approve()
                cv.with_context(user_id=self.env.user.id,
                                documentary_validation='marital_status').button_documentary_approve()
                cv.with_context(user_id=self.env.user.id,
                                documentary_validation='civical_credential').button_documentary_approve()
                cv.with_context(user_id=self.env.user.id,
                                documentary_validation='nro_doc').button_documentary_approve()
            else:
                vals = self.suspend_security()._get_info_from_line()
            vals.update({
                'cv_birthdate': self.cv_birthdate,
            })
            employee.write(vals)
            cv.write({'is_docket': True})
        except Exception as e:
            raise ValidationError("No se puedo crear el funcionario: " + tools.ustr(e))
            # self.env.cr.rollback()
            # line.write({'state': 'error', 'error': "No se puedo crear el funcionario: " + tools.ustr(e)})
            # self.env.cr.commit()

    def process_line(self, limit=200):
        Partner = self.env['res.partner'].suspend_security()
        CVDigital = self.env['onsc.cv.digital'].suspend_security()
        Employee = self.env['hr.employee'].suspend_security()
        for line in self.search([('state', '=', 'ok')], limit=limit):
            try:
                if line._is_employee_in_system(Employee):
                    line.write({'state': 'process'})
                    continue
                partner_id = line._create_contact(Partner)
                cv_digital = line._create_cv(CVDigital, partner_id)
                if line.state != 'AP':
                    line.create_employee(cv_digital)
                line.write({'state': 'process'})
                self.env.cr.commit()
            except Exception as e:
                self.env.cr.rollback()
                self.write({
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
                    'is_partner_cv': True,
                    'email': self.email,
                    'cv_dnic_name_1': self.first_name,
                    'cv_dnic_name_2': self.second_name,
                    'cv_dnic_lastname_1': self.first_surname,
                    'cv_dnic_lastname_2': self.second_surname,
                    'cv_dnic_full_name': self.name_ci,
                    'cv_birthdate': self.birth_date,
                }
                partner = Partner.create(data_partner)
                self.write({'partner_id': partner.id})
            else:
                data_partner = {
                    'cv_dnic_name_1': self.first_name,
                    'cv_dnic_name_2': self.second_name,
                    'cv_dnic_lastname_1': self.first_surname,
                    'cv_dnic_lastname_2': self.second_surname,
                    'cv_dnic_full_name': self.name_ci,
                    'cv_birthdate': self.birth_date,
                }
                partner.write(data_partner)
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
                    'country_id': self.country_uy.id,
                    'marital_status_id': self.marital_status_id.id,
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
                    'health_provider_id': self.health_provider_id.id
                }
                return CVDigital.create(data)
            else:
                data = {'email': self.email_inst,
                        'marital_status_id': self.marital_status_id.id,
                        'health_provider_id': self.health_provider_id.id
                        }
                cv_digital.write(data)
                return cv_digital
        except Exception as e:
            raise ValidationError("No se puedo crear el CV: " + tools.ustr(e))
            # self.env.cr.rollback()
            # self.write({'state': 'error', 'error': "No se puedo crear el CV: " + tools.ustr(e)})
            # self.env.cr.commit()

    def _is_employee_in_system(self, Employee):
        return Employee.search_count([
            ('cv_emissor_country_id', '=', self.country_id.id),
            ('cv_document_type_id', '=', self.doc_type_id.id),
            ('cv_nro_doc', '=', self.doc_nro),
        ])
