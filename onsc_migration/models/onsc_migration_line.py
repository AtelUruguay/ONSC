import base64
import io
import logging

import openpyxl as openpyxl

from odoo import models, fields, tools

STATE = [
    ('draft', 'Borrador'),
    ('error', 'Error'),
    ('in_process', 'Procesando'),
    ('process', 'Procesado'),
]

REQUIRED_FIELDS = {'country_id', 'doc_type_id', 'doc_nro', 'first_name',
                   'date_income_public_administration', 'sex', 'state_move', 'first_surname', 'inciso_id',
                   'state_place',
                   'descriptor3_id', 'retributive_day_id', 'retributive_day_formal_id', 'state_move', 'sex',
                   'birth_date', 'date_start'}

REQUIRED_FIELDS_COMM = {'inciso_des_id', 'date_start_commission', 'state_place_des', 'reason_commision',
                        'resolution_comm_description', 'resolution_comm_date', 'resolution_comm_type', }

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

    def process_binary(self):
        try:
            if self.document_file:
                excel_data = io.BytesIO(base64.b64decode(self.document_file))
                workbook = openpyxl.load_workbook(excel_data, data_only=True)

                sheet = workbook.active

                for row in sheet.iter_rows(min_row=2, values_only=True):
                    count = self.check_line(str(row[2]), str(row[44]), str(row[45]), str(row[46]))
                    if count > 0:
                        continue
                    if not row[0] and not row[1] and not row[2]:
                        break

                    row_dict = {}

                    country_id = self.get_country(row[0].upper())
                    doc_type_id = self.get_doc_type(row[1].upper())
                    marital_status_id = self.get_status_civil(str(row[8]).upper())
                    gender_id = self.get_gender(str(row[10]).upper())
                    if row[12] and row[0] != row[12]:
                        birth_country_id = self.get_country(row[12].upper())
                    elif row[12]:
                        birth_country_id = country_id
                    else:
                        birth_country_id = None
                    address_state_id = self.get_country_state(str(row[19]).upper())
                    address_location_id = self.is_numeric(row[20]) and self.get_location(str(row[20])) or None
                    address_street_id = self.get_street(str(row[21]).upper())
                    address_street2_id = self.get_street(str(row[23]).upper())
                    address_street3_id = self.get_street(str(row[24]).upper())
                    health_provider_id = self.get_health_provider(str(row[31]).upper())
                    inciso_id = self.get_inciso(str(row[36]).upper())
                    operating_unit_id = self.get_operating_unit(str(row[37]).upper())
                    program_project_id = self.get_office(str(row[38]).upper(), str(row[39]).upper())
                    regime_id = self.get_regime(str(row[40]))
                    descriptor1_id = self.get_descriptor1(str(row[41]).upper())
                    descriptor2_id = self.get_descriptor2(str(row[42]).upper())
                    descriptor3_id = self.get_descriptor3(str(row[43]).upper())
                    descriptor4_id = self.get_descriptor4(str(row[44]).upper())
                    occupation_id = self.get_occupation(str(row[49]).upper())
                    income_mechanism_id = self.get_income_mechanism(str(row[50]).upper())
                    norm_id = self.get_norm(str(row[53]).upper(), row[54], row[55], row[56])
                    department_id = self.get_department(str(row[69]).upper())
                    retributive_day_id = self.get_jornada_retributiva(str(row[82]).upper())
                    retributive_day_formal_id = self.get_jornada_retributiva(str(row[83]).upper())
                    security_job_id = self.get_security_job(str(row[86]).upper())

                    row_dict['migration_id'] = self.id
                    row_dict['country_id'] = country_id and country_id[0]
                    row_dict['doc_type_id'] = doc_type_id and doc_type_id[0]
                    row_dict['doc_nro'] = row[2]
                    row_dict['first_name'] = row[3]
                    row_dict['second_name'] = row[4]
                    row_dict['first_surname'] = row[5]
                    row_dict['second_surname'] = row[6]
                    row_dict['name_ci'] = row[7]
                    row_dict['marital_status_id'] = marital_status_id and marital_status_id[0]
                    row_dict['birth_date'] = self.is_datetime(row[9]) and row[9].strftime("%Y-%m-%d")
                    row_dict['gender_id'] = gender_id and gender_id[0]
                    row_dict['sex'] = row[11] and row[12].lower()
                    row_dict['birth_country_id'] = birth_country_id and birth_country_id[0]
                    row_dict['citizenship'] = row[13]
                    row_dict['crendencial_serie'] = row[14]
                    row_dict['credential_number'] = row[15]
                    row_dict['personal_phone'] = row[16]
                    row_dict['email'] = row[17]
                    row_dict['email_inst'] = row[18]
                    row_dict['address_state_id'] = address_state_id and address_state_id[0]
                    row_dict['address_street_id'] = address_street_id and address_street_id[0]
                    row_dict['address_location_id'] = address_location_id and address_location_id[0]
                    row_dict['address_street2_id'] = address_street2_id and address_street2_id[0]
                    row_dict['address_street3_id'] = address_street3_id and address_street3_id[0]
                    row_dict['address_nro_door'] = row[22]
                    row_dict['address_is_bis'] = row[25]
                    row_dict['address_apto'] = row[26]
                    row_dict['address_place'] = row[27]
                    row_dict['address_zip'] = row[28]
                    row_dict['address_block'] = row[29]
                    row_dict['address_sandlot'] = row[30]
                    row_dict['health_provider_id'] = health_provider_id and health_provider_id[0]
                    row_dict['date_income_public_administration'] = self.is_datetime(row[32]) and row[32].strftime(
                        "%Y-%m-%d")
                    row_dict['inactivity_years'] = row[33]
                    row_dict['graduation_date'] = self.is_datetime(row[34]) and row[34].strftime("%Y-%m-%d")
                    row_dict['date_start'] = self.is_datetime(row[35]) and row[35].strftime("%Y-%m-%d")
                    row_dict['inciso_id'] = inciso_id and inciso_id[0]
                    row_dict['operating_unit_id'] = operating_unit_id and operating_unit_id[0]
                    row_dict['program_project_id'] = program_project_id and program_project_id[0]
                    row_dict['regime_id'] = regime_id and regime_id[0]
                    row_dict['descriptor1_id'] = descriptor1_id and descriptor1_id[0]
                    row_dict['descriptor2_id'] = descriptor2_id and descriptor2_id[0]
                    row_dict['descriptor3_id'] = descriptor3_id and descriptor3_id[0]
                    row_dict['descriptor4_id'] = descriptor4_id and descriptor4_id[0]
                    row_dict['nro_puesto'] = row[45]
                    row_dict['nro_place'] = row[46]
                    row_dict['sec_place'] = row[47]
                    row_dict['state_place'] = row[48]
                    row_dict['occupation_id'] = occupation_id and occupation_id[0]
                    row_dict['income_mechanism_id'] = income_mechanism_id and income_mechanism_id[0]
                    row_dict['call_number'] = row[51]
                    row_dict['reason_description'] = row[52]
                    row_dict['norm_id'] = norm_id and norm_id[0]
                    row_dict['resolution_description'] = row[57]
                    row_dict['resolution_date'] = self.is_datetime(row[58]) and row[58].strftime("%Y-%m-%d")
                    row_dict['resolution_type'] = row[59]
                    row_dict['department_id'] = department_id and department_id[0]
                    row_dict['retributive_day_id'] = retributive_day_id[0]
                    row_dict['retributive_day_formal_id'] = retributive_day_formal_id[0]
                    row_dict['security_job_id'] = security_job_id and security_job_id[0]

                    if row[71]:

                        inciso_des_id = self.get_inciso(str(row[60]).upper())
                        operating_unit_des_id = self.get_operating_unit(str(row[61]).upper(), )
                        program_project_des_id = self.get_office(str(row[62]).upper(), str(row[63]).upper())
                        regime_des_id = self.get_regime(str(row[64]).upper())
                        regime_commission_id = self.get_commision_regime(str(row[72]))
                        norm_des_id = self.get_norm(str(row[74]).upper(), row[75], row[76], row[77])

                        row_dict['inciso_des_id'] = inciso_des_id[0]
                        row_dict['operating_unit_des_id'] = operating_unit_des_id and operating_unit_des_id[0]
                        row_dict['program_project_des_id'] = program_project_des_id and program_project_des_id[0]
                        row_dict['regime_des_id'] = regime_des_id and regime_des_id[0]
                        row_dict['nro_puesto_des'] = row[65]
                        row_dict['nro_place_des '] = row[66]
                        row_dict['sec_place_des'] = row[67]
                        row_dict['state_place_des'] = row[68]
                        row_dict['date_start_commission'] = self.is_datetime(row[70]) and row[70].strftime("%Y-%m-%d")
                        row_dict['type_commission'] = row[71]
                        row_dict['regime_commission_id'] = regime_commission_id and regime_commission_id[0]
                        row_dict['reason_commision'] = row[74]
                        row_dict['norm_comm_id'] = norm_des_id and norm_des_id[0]
                        row_dict['resolution_comm_description'] = row[78]
                        row_dict['resolution_comm_date'] = self.is_datetime(row[79]) and row[79].strftime("%Y-%m-%d")
                        row_dict['resolution_comm_type'] = row[80]

                    else:
                        row_dict['end_date_contract'] = self.is_datetime(row[81]) and row[81].strftime("%Y-%m-%d")

                    row_dict['id_movimiento'] = self.is_numeric(row[84]) and int(row[84])
                    row_dict['state_move'] = row[85]
                    if row_dict['state_move'] == 'BP':
                        norm_dis_id = self.get_norm(str(row[90]).upper(), row[91], row[92], row[93])
                        causes_discharge_id = self.get_causes_discharge(str(row[87]).upper())
                        row_dict['end_date'] = self.is_datetime(row[88]) and row[88].strftime("%Y-%m-%d")
                        row_dict['causes_discharge_id'] = causes_discharge_id and causes_discharge_id[0]
                        row_dict['reason_discharge'] = row[89]
                        row_dict['norm_dis_id'] = norm_dis_id and norm_dis_id[0]
                        row_dict['resolution_dis_description'] = row[94]
                        row_dict['resolution_dis_date'] = self.is_datetime(row[95]) and row[95].strftime("%Y-%m-%d")
                        row_dict['resolution_dis_type'] = row[96]

                    row_dict_limpio = row_dict.copy()

                    for clave, valor in row_dict.items():
                        if valor is None or valor == '' or valor is False:
                            del row_dict_limpio[clave]

                    self._cr.execute(
                        """INSERT INTO "onsc_migration_line" (%s) VALUES %s RETURNING id""" % (
                            ', '.join(row_dict_limpio.keys()),
                            tuple(row_dict_limpio.values())
                        ),
                    )
                    line = self._cr.fetchone()[0]
                    message_error = self.validate(row, row_dict)
                    self.env['onsc.migration.line'].suspend_security().browse(line).validate_line(message_error)
                    self.env.cr.commit()
            self.write({'state': 'process'})
            return True

        except Exception as e:
            self.suspend_security().write({'error': tools.ustr(e), 'state': 'error'})

    def validate(self, row, row_dict):
        message_error = []
        if row[8] and not row_dict['marital_status_id']:
            message_error.append("El campo Estado civil no es válido")
        if row[10] and not row_dict['gender_id']:
            message_error.append("El campo Género no es válido")
        return message_error

    def is_datetime(self, row):
        return type(row).__name__ == 'datetime' or False

    def is_numeric(self, row):
        return type(row).__name__ == 'int' or False

    def check_line(self, doc_nro, nro_puesto, nro_place, sec_place):
        self._cr.execute(
            """SELECT count(id) FROM onsc_migration_line  WHERE migration_id = %s and upper(doc_nro) = %s and nro_puesto = %s and nro_place =%s and sec_place =%s""",
            (self.id, doc_nro, nro_puesto, nro_place, sec_place))
        return self._cr.fetchone()[0]

    def get_country(self, code):
        self._cr.execute("""SELECT id FROM res_country  WHERE upper(code) = %s""", (code.upper(),))
        return self._cr.fetchone()

    def get_doc_type(self, code):
        self._cr.execute("""SELECT id FROM onsc_cv_document_type  WHERE upper(code) = %s""", (code,))
        return self._cr.fetchone()

    def get_status_civil(self, code):
        self._cr.execute("""SELECT id FROM onsc_cv_status_civil  WHERE upper(code) = %s""", (code,))
        return self._cr.fetchone()

    def get_gender(self, code):
        self._cr.execute("""SELECT id FROM onsc_cv_gender  WHERE upper(code) = %s""", (code,))
        return self._cr.fetchone()

    def get_country_state(self, code):
        self._cr.execute("""SELECT id FROM res_country_state  WHERE upper(code) = %s""", (code,))
        return self._cr.fetchone()

    def get_location(self, code):
        self._cr.execute("""SELECT id FROM onsc_cv_location  WHERE other_code = %s""", (code,))
        return self._cr.fetchone()

    def get_street(self, code):
        self._cr.execute("""SELECT id FROM onsc_cv_street  WHERE code = %s""", (code,))
        return self._cr.fetchone()

    def get_health_provider(self, code):
        self._cr.execute("""SELECT id FROM onsc_legajo_health_provider  WHERE upper(code) = %s""", (code,))
        return self._cr.fetchone()

    def get_inciso(self, code):
        self._cr.execute("""SELECT id FROM onsc_catalog_inciso  WHERE upper(budget_code) = %s""", (code,))
        return self._cr.fetchone()

    def get_operating_unit(self, code):
        self._cr.execute("""SELECT id FROM operating_unit  WHERE upper(budget_code) = %s""", (code,))
        return self._cr.fetchone()

    def get_office(self, programa, proyecto):
        self._cr.execute("""SELECT id FROM onsc_legajo_office  WHERE upper(programa) = %s and upper(proyecto) = %s""",
                         (programa, proyecto))
        return self._cr.fetchone()

    def get_regime(self, code):
        self._cr.execute("""SELECT id FROM onsc_legajo_regime  WHERE "codRegimen" = %s """, (code,))
        return self._cr.fetchone()

    def get_descriptor1(self, code):
        self._cr.execute("""SELECT id FROM onsc_catalog_descriptor1  WHERE upper(code) = %s""", (code,))
        return self._cr.fetchone()

    def get_descriptor2(self, code):
        self._cr.execute("""SELECT id FROM onsc_catalog_descriptor2  WHERE upper(code) = %s""", (code,))
        return self._cr.fetchone()

    def get_descriptor3(self, code):
        self._cr.execute("""SELECT id FROM onsc_catalog_descriptor3  WHERE upper(code) = %s""", (code,))
        return self._cr.fetchone()

    def get_descriptor4(self, code):
        self._cr.execute("""SELECT id FROM onsc_catalog_descriptor4  WHERE upper(code) = %s""", (code,))
        return self._cr.fetchone()

    def get_occupation(self, code):
        self._cr.execute("""SELECT id FROM onsc_catalog_occupation  WHERE upper(code) = %s""", (code,))
        return self._cr.fetchone()

    def get_income_mechanism(self, code):
        self._cr.execute("""SELECT id FROM onsc_legajo_income_mechanism  WHERE upper(code) = %s""", (code,))
        return self._cr.fetchone()

    def get_norm(self, tipoNorma, numeroNorma, anioNorma, articuloNorma):
        self._cr.execute(
            """SELECT id FROM onsc_legajo_norm  WHERE upper("tipoNormaSigla") = %s and "numeroNorma"= %s and "anioNorma" = %s and "articuloNorma"= %s""",
            (tipoNorma, numeroNorma, anioNorma, articuloNorma))
        return self._cr.fetchone()

    def get_department(self, code):
        self._cr.execute("""SELECT id FROM hr_department  WHERE upper(code) = %s""", (code,))
        return self._cr.fetchone()

    def get_jornada_retributiva(self, code):
        self._cr.execute(
            """SELECT id FROM onsc_legajo_jornada_retributiva  WHERE upper("codigoJornada") = %s  limit 1""", (code,))
        return self._cr.fetchone()

    def get_security_job(self, code):
        self._cr.execute("""SELECT id FROM onsc_legajo_security_job  WHERE upper(name) = %s""", (code,))
        return self._cr.fetchone()

    def get_causes_discharge(self, code):
        self._cr.execute("""SELECT id FROM onsc_legajo_causes_discharge  WHERE upper(code) = %s """, (code,))
        return self._cr.fetchone()

    def get_commision_regime(self, code):
        self._cr.execute("""SELECT id FROM onsc_legajo_commission_regime  WHERE cgn_code = %s """, (code,))


class ONSCMigrationLine(models.Model):
    _name = "onsc.migration.line"

    migration_id = fields.Many2one('onsc.migration', string='Cabezal migracion')
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
    birth_country_id = fields.Many2one('res.country', string=u'País de nacimiento')
    citizenship = fields.Selection(string="Ciudadanía",
                                   selection=[('legal', 'Legal'), ('natural', 'Natural'),
                                              ('extranjero', 'Extranjero')])
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
    state_place = fields.Selection(string="Estado plaza origen",
                                   selection=[('O', 'O'), ('C', 'C'), ('R', 'R(no com.)'), ('S', 'S(comisiones)')])
    occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación origen')
    income_mechanism_id = fields.Many2one('onsc.legajo.income.mechanism', string='Mecanismo de ingreso origen')
    call_number = fields.Char(string='Número de llamado origen')
    reason_description = fields.Char(string='Descripción del motivo alta')
    norm_id = fields.Many2one('onsc.legajo.norm', string='Norma')
    norm_type = fields.Char(string="Tipo norma", related="norm_id.tipoNorma", store=True, readonly=True)
    norm_number = fields.Integer(string='Número de norma', related="norm_id.numeroNorma",
                                 store=True, readonly=True)
    norm_year = fields.Integer(string='Año de norma', related="norm_id.anioNorma", store=True,
                               readonly=True)
    norm_article = fields.Integer(string='Artículo de norma', related="norm_id.articuloNorma",
                                  store=True, readonly=True)
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
    state_place_des = fields.Selection(string="Estado plaza destino",
                                       selection=[('O', 'O'), ('C', 'C'), ('R', 'R(no com.)'), ('S', 'S(comisiones)')])
    department_id = fields.Many2one("hr.department", string="Unidad organizativa")
    date_start_commission = fields.Date(string='Fecha inicio comisión')
    type_commission = fields.Selection(string="ETipo de Comisión",
                                       selection=[('CS', 'Comisión de Servicio'), ('PC', 'Pase en Comisión')])

    regime_commission_id = fields.Many2one('onsc.legajo.commission.regime', string='Régimen de comisión')
    reason_commision = fields.Text(string='Descr motivo comisión')
    norm_comm_id = fields.Many2one('onsc.legajo.norm', string='Norma comisión')
    norm_comm_type = fields.Char(string="Tipo norma comisión", related="norm_comm_id.tipoNorma", store=True,
                                 readonly=True)
    norm_comm_number = fields.Integer(string='Número de norma comisión', related="norm_comm_id.numeroNorma",
                                      store=True, readonly=True)
    norm_comm_year = fields.Integer(string='Año de norma comisión', related="norm_comm_id.anioNorma", store=True,
                                    readonly=True)
    norm_comm_article = fields.Integer(string='Artículo de norma comisión', related="norm_comm_id.articuloNorma",
                                       store=True, readonly=True)
    resolution_comm_description = fields.Char(string='Descripción de la resolución comisión')
    resolution_comm_date = fields.Date(string='Fecha de la resolución comisión')
    resolution_comm_type = fields.Char(string='Tipo de resolución comisión')
    end_date_contract = fields.Date(string="Vencimiento del contrato")
    retributive_day_id = fields.Many2one('onsc.legajo.jornada.retributiva',
                                         string='Carga horaria semanal según contrato')
    retributive_day_formal_id = fields.Many2one('onsc.legajo.jornada.retributiva', string='Jornada Formal')
    id_movimiento = fields.Char(string='id_movimiento')
    state_move = fields.Selection(string="Estado del Moviento",
                                  selection=[('A', 'Aprobado'), ('AP', 'Alta pendiente'), ('BP', 'Baja pendiente')])
    security_job_id = fields.Many2one("onsc.legajo.security.job", string="Seguridad de puesto")
    end_date = fields.Date(string="Fecha de Baja")

    causes_discharge_id = fields.Many2one('onsc.legajo.causes.discharge', string='Causal de Egreso')
    reason_discharge = fields.Text(string='Descr motivo baja')
    norm_dis_id = fields.Many2one('onsc.legajo.norm', string='Norma comisión baja')
    norm_dis_type = fields.Char(string="Tipo norma de la baja", related="norm_dis_id.tipoNorma", store=True,
                                readonly=True)
    norm_dis_number = fields.Integer(string='Número de norma de la baja', related="norm_dis_id.numeroNorma",
                                     store=True, readonly=True)
    norm_dis_year = fields.Integer(string='Año de norma de la baja', related="norm_dis_id.anioNorma", store=True,
                                   readonly=True)
    norm_dis_article = fields.Integer(string='Artículo de norma de la baja', related="norm_dis_id.articuloNorma",
                                      store=True, readonly=True)
    resolution_dis_description = fields.Char(string='Descripción de la resolución de la baja')
    resolution_dis_date = fields.Date(string='Fecha de la resolución de la baja')
    resolution_dis_type = fields.Char(string='Tipo de resolución de la baja')
    sex = fields.Selection([('male', 'Masculino'), ('feminine', 'Femenino')], 'Sexo')

    def validate_line(self, message_error):

        for required_field in REQUIRED_FIELDS:
            if not eval('self.%s' % required_field):
                message_error.append("El campo %s no es válido" % self._fields[required_field].string)

        if self.address_street_id:
            message_error = self.validate_adress(message_error)

        if self.type_commission:
            for required_field in REQUIRED_FIELDS_COMM:
                if not eval('self.%s' % required_field):
                    message_error.append("El campo %s no es válido" % self._fields[required_field].string)
        else:
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

        if message_error:
            error = '\n'.join(message_error)
            state = 'error'
        else:
            error = ''
            state = 'draft'

        self._cr.execute(
            """update "onsc_migration_line" set state = '%s',error = '%s' where id = %s """ % (state, error, self.id))

    def validate_adress(self, message_error):

        if not self.address_location_id:
            message_error.append("El campo Localidad no es válido")
        if not self.address_state_id:
            message_error.append("El campo Departamento no es válido")
        return message_error

    def write(self, vals):
        result = super(ONSCMigrationLine, self).write(vals)

        return result
