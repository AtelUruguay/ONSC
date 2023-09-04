import base64
import io
import logging

import openpyxl as openpyxl

from odoo import models, fields

STATE = [
    ('ok', 'OK'),
    ('error', 'Error'),
    ('in_process', 'Procesando'),
    ('process', 'Procesado'),
]
_logger = logging.getLogger(__name__)
try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')


class ONSCMigratio(models.Model):
    _name = "onsc.migration"

    state = fields.Selection(STATE, string='Estado', readonly=True)
    error = fields.Text("Error")
    document_file = fields.Binary(string='Archivo de carga', required=True)
    document_filename = fields.Char('Nombre del documento')
    line_ids = fields.One2many('onsc.migration.line', 'migration_id', string='Líneas')

    def button_run_process(self):
        try:
            if self.document_file:
                excel_data = io.BytesIO(base64.b64decode(self.document_file))
                workbook = openpyxl.load_workbook(excel_data, data_only=True)

                sheet = workbook.active

                message_error = []

                for row in sheet.iter_rows(min_row=2, values_only=True):
                    row_dict = {}

                    self._cr.execute("""SELECT id FROM res_country  WHERE code = %s""", (row[0],))
                    country_id = self._cr.fetchone()

                    self._cr.execute("""SELECT id FROM onsc_cv_document_type  WHERE code = %s""", (row[1],))
                    doc_type_id = self._cr.fetchone()

                    self._cr.execute("""SELECT id FROM onsc_cv_status_civil  WHERE code = %s""", (str(row[8]),))
                    marital_status_id = self._cr.fetchone()

                    self._cr.execute("""SELECT id FROM onsc_cv_gender  WHERE code = %s""", (str(row[10]),))
                    gender_id = self._cr.fetchone()

                    if row[0] != row[11]:
                        self._cr.execute("""SELECT id FROM res_country  WHERE code = %s""", (row[11],))
                        birth_country_id = self._cr.fetchone()
                    else:
                        birth_country_id = country_id

                    self._cr.execute("""SELECT id FROM res_country_state  WHERE code = %s""", (row[18],))
                    address_state_id = self._cr.fetchone()
                    self._cr.execute("""SELECT id FROM onsc_cv_location  WHERE other_code = %s""", (str(row[19]),))
                    address_location_id = self._cr.fetchone()
                    self._cr.execute("""SELECT id FROM onsc_cv_street  WHERE code = %s""", (str(row[20]),))
                    address_street_id = self._cr.fetchone()
                    self._cr.execute("""SELECT id FROM onsc_cv_street  WHERE code = %s""", (str(row[22]),))
                    address_street2_id = self._cr.fetchone()
                    self._cr.execute("""SELECT id FROM onsc_cv_street  WHERE code = %s""", (str(row[23]),))
                    address_street3_id = self._cr.fetchone()
                    self._cr.execute("""SELECT id FROM onsc_legajo_health_provider  WHERE code = %s""", (str(row[30]),))
                    health_provider_id = self._cr.fetchone()
                    self._cr.execute("""SELECT id FROM onsc_catalog_inciso  WHERE budget_code = %s""", (str(row[35]),))
                    inciso_id = self._cr.fetchone()
                    self._cr.execute("""SELECT id FROM operating_unit  WHERE budget_code = %s""", (str(row[36]),))
                    operating_unit_id = self._cr.fetchone()
                    self._cr.execute("""SELECT id FROM onsc_legajo_office  WHERE programa = %s and proyecto = %s""",
                                     (str(row[37]), str(row[38])))
                    program_project_id = self._cr.fetchone()
                    self._cr.execute("""SELECT id FROM onsc_legajo_regime  WHERE "codRegimen" = %s """, (str(row[39]),))
                    regime_id = self._cr.fetchone()
                    self._cr.execute("""SELECT id FROM onsc_catalog_descriptor1  WHERE code = %s""", (str(row[40]),))
                    descriptor1_id = self._cr.fetchone()
                    self._cr.execute("""SELECT id FROM onsc_catalog_descriptor2  WHERE code = %s""", (str(row[41]),))
                    descriptor2_id = self._cr.fetchone()
                    self._cr.execute("""SELECT id FROM onsc_catalog_descriptor3  WHERE code = %s""", (str(row[42]),))
                    descriptor3_id = self._cr.fetchone()
                    self._cr.execute("""SELECT id FROM onsc_catalog_descriptor4  WHERE code = %s""", (str(row[43]),))
                    descriptor4_id = self._cr.fetchone()
                    self._cr.execute("""SELECT id FROM onsc_catalog_occupation  WHERE code = %s""", (str(row[48]),))
                    occupation_id = self._cr.fetchone()
                    self._cr.execute("""SELECT id FROM onsc_legajo_income_mechanism  WHERE code = %s""",
                                     (str(row[49]),))
                    income_mechanism_id = self._cr.fetchone()
                    self._cr.execute(
                        """SELECT id FROM onsc_legajo_norm  WHERE "tipoNorma" = %s and "numeroNorma"= %s and "anioNorma" = %s and "articuloNorma"= %s """,
                        (str(row[52]), str(row[53]), str(row[54]), str(row[55])), )
                    norm_id = self._cr.fetchone()
                    self._cr.execute("""SELECT id FROM hr_department  WHERE code = %s """, (str(row[68]),))
                    department_id = self._cr.fetchone()
                    self._cr.execute(
                        """SELECT id FROM onsc_legajo_jornada_retributiva  WHERE "codigoJornada" = %s  limit 1""",
                        (str(row[81]),))
                    retributive_day_id = self._cr.fetchone()
                    self._cr.execute(
                        """SELECT id FROM onsc_legajo_jornada_retributiva  WHERE "codigoJornada" = %s  limit 1""",
                        (str(row[82]),))
                    retributive_day_formal_id = self._cr.fetchone()
                    self._cr.execute(
                        """SELECT id FROM onsc_legajo_security_job  WHERE name = %s """, (str(row[85]),))
                    security_job_id = self._cr.fetchone()

                    row_dict['migration_id'] = self.id
                    if country_id:
                        row_dict['country_id'] = country_id[0]
                    else:
                        message_error.append(
                            " \n El Pais del documento es obligatorio")
                    if doc_type_id:
                        row_dict['doc_type_id'] = country_id[0]
                    else:
                        message_error.append(
                            " \n El tipo de documento es obligatorio")

                    row_dict['doc_nro'] = row[2]
                    row_dict['first_name'] = row[3]
                    row_dict['second_name'] = row[4]
                    row_dict['first_surname'] = row[5]
                    row_dict['second_surname'] = row[6]
                    row_dict['name_ci'] = row[7]
                    if marital_status_id:
                        row_dict['marital_status_id'] = marital_status_id[0]
                    if type(row[9]).__name__ == 'datetime':
                        row_dict['birth_date'] =row[9].strftime("%Y-%m-%d")
                    if gender_id:
                        row_dict['gender_id'] = gender_id[0]
                    if birth_country_id:
                        row_dict['birth_country_id'] = birth_country_id[0]

                    row_dict['citizenship'] = row[12]
                    row_dict['crendencial_serie'] = row[13]
                    row_dict['credential_number'] = row[14]
                    row_dict['personal_phone'] = row[15]
                    row_dict['email'] = row[16]
                    row_dict['email_inst'] = row[17]
                    if address_state_id:
                        row_dict['address_state_id'] = address_state_id[0]
                    else:
                        message_error.append(
                            " \n El Departamento es obligatorio")
                    if address_location_id:
                        row_dict['address_location_id'] = address_location_id[0]
                    else:
                        message_error.append(
                            " \n La localidad es obligatoria")
                    if address_street2_id:
                        row_dict['address_street2_id'] = address_street2_id[0]
                    if address_street3_id:
                        row_dict['address_street3_id'] = address_street3_id[0]

                    row_dict['address_nro_door'] = row[21]
                    row_dict['address_is_bis'] = row[24]
                    row_dict['address_apto'] = row[25]
                    row_dict['address_place'] = row[26]
                    row_dict['address_zip'] = row[27]
                    row_dict['address_block'] = row[28]
                    row_dict['address_sandlot'] = row[29]
                    if health_provider_id:
                        row_dict['health_provider_id'] = health_provider_id[0]

                    if row[31]:
                        if type(row[31]).__name__ == 'datetime':
                            row_dict['date_income_public_administration'] = row[31].strftime("%Y-%m-%d")
                        else:
                            message_error.append(
                                " \n El tipo de dato de  la Fecha de ingreso a la administración pública es incorrecto")
                    else:
                        message_error.append(
                            " \n La Fecha de ingreso a la administración pública es obligatoria")


                    row_dict['inactivity_years'] = row[32]
                    if type(row[33]).__name__ == 'datetime':
                        row_dict['graduation_date'] = row[33].strftime("%Y-%m-%d")
                    if type(row[34]).__name__ == 'datetime':
                        row_dict['graduation_date'] = row[35].strftime("%Y-%m-%d")
                    if inciso_id:
                        row_dict['inciso_id'] = inciso_id[0]
                    else:
                        message_error.append(
                            " \n El incisio es obligatorio")
                    if row[70] == 'null' and not operating_unit_id:
                        message_error.append(
                            " \n La UE es obligatoria")

                    elif operating_unit_id:
                         row_dict['operating_unit_id'] = operating_unit_id[0]

                    if row[70] == 'null' and not program_project_id:
                        message_error.append(
                            " \n La Progrma es obligatorio")

                    elif program_project_id:
                        row_dict['program_project_id'] = program_project_id[0]

                    if row[70] == 'null' and not regime_id:
                        message_error.append(
                            " \nEl regimen es obligatorio")

                    elif regime_id:
                        row_dict['program_project_id'] = regime_id[0]

                    if descriptor1_id:
                        row_dict['descriptor1_id'] = descriptor1_id[0]
                    if descriptor2_id:
                        row_dict['descriptor1_id'] = descriptor2_id[0]
                    if descriptor3_id:
                        row_dict['descriptor3_id'] = descriptor3_id[0]
                    else:
                        message_error.append(
                            " \n El descriptor 3 es obligatorio")
                    if descriptor4_id:
                        row_dict['descriptor4_id'] = descriptor4_id[0]

                    row_dict['nro_puesto'] = int(row[44])

                    row_dict['nro_place'] = int(row[45])
                    row_dict['sec_place'] = int(row[46])
                    row_dict['state_place'] = row[47]
                    if occupation_id:
                        row_dict['occupation_id'] = occupation_id[0]
                    if income_mechanism_id:
                        row_dict['income_mechanism_id'] = income_mechanism_id[0]

                    row_dict['call_number'] = row[50]
                    row_dict['reason_description'] = row[51]
                    if norm_id:
                       row_dict['norm_id'] = norm_id and norm_id[0]
                    row_dict['resolution_description'] = row[56]
                    if type(row[57]).__name__ == 'datetime':
                        row_dict['resolution_date'] = row[57].strftime("%Y-%m-%d")

                    row_dict['resolution_type'] = row[58]
                    if department_id:
                         row_dict['department_id'] = department_id and department_id[0] or False
                    if retributive_day_id:
                        row_dict['retributive_day_id'] = retributive_day_id[0]
                    else:
                        message_error.append(
                            " \n La Jornada Formal es obligatoria")
                    if retributive_day_formal_id:
                        row_dict['retributive_day_formal_id'] = retributive_day_formal_id[0]
                    else:
                        message_error.append(
                            " \n El descriptor 3 es obligatorio")
                    if security_job_id:
                        row_dict['security_job_id'] =security_job_id[0]

                    if row[70] != 'null':
                        self._cr.execute("""SELECT id FROM onsc_catalog_inciso  WHERE budget_code = %s""",
                                         (str(row[59]),))
                        inciso_des_id = self._cr.fetchone()
                        self._cr.execute("""SELECT id FROM operating_unit  WHERE budget_code = %s""", (str(row[60]),))
                        operating_unit_des_id = self._cr.fetchone()
                        self._cr.execute("""SELECT id FROM operating_unit  WHERE programa = %s and proyecto = %s""",
                                         (str(row[60]), str(row[61])))
                        program_project_des_id = self._cr.fetchone()
                        self._cr.execute("""SELECT id FROM onsc_legajo_regime  WHERE "codRegimen" = %s """,
                                         (str(row[62]),))
                        regime_des_id = self._cr.fetchone()
                        self._cr.execute("""SELECT id FROM onsc_legajo_commission_regime  WHERE "codRegimen" = %s """,
                                         (str(row[71]),))
                        regime_commission_id = self._cr.fetchone()
                        self._cr.execute(
                            """SELECT id FROM onsc_legajo_norm  WHERE "tipoNorma" = %s and "numeroNorma"= %s and "anioNorma" = %s and "articuloNorma"= %s """,
                            (str(row[73]), str(row[74]), str(row[75]), str(row[76])))
                        norm_des_id = self._cr.fetchone()
                        if inciso_des_id:
                            row_dict['inciso_des_id'] = inciso_des_id[0]
                        else:
                            message_error.append(
                                " \n El inciso destino es obligatorio")
                        if operating_unit_des_id:
                            row_dict['operating_unit_des_id'] = operating_unit_des_id[0]
                        if program_project_des_id:
                            row_dict['program_project_des_id'] = program_project_des_id[0]
                        if regime_des_id:
                            row_dict['regime_des_id'] = regime_des_id[0]

                        row_dict['nro_puesto_des'] = int(row[64])
                        row_dict['nro_place_des '] = int(row[65])
                        row_dict['sec_place_des'] = int(row[66])
                        row_dict['state_place_des'] = row[67]
                        if row[69]:
                            if type(row[69]).__name__ == 'datetime':
                                row_dict['date_start_commission'] = row[69].strftime("%Y-%m-%d")
                            else:
                                message_error.append(
                                    " \n El tipo de dato de la FFecha inicio comisión es incorrecto")
                        else:
                            message_error.append(
                                " \n La Fecha inicio comisión es obligatoria")
                        if row[70]:
                            row_dict['type_commission'] = row[70]
                        else:
                            message_error.append(
                                " \n La Fecha inicio comisión es obligatoria")

                        if regime_commission_id:

                            row_dict['regime_commission_id'] = regime_commission_id[0]
                        if row[73]:
                            row_dict['reason_commision'] = row[73]
                        else:
                            message_error.append(
                                " \n La descripción motivo comisión s obligatoria")

                        if norm_des_id:
                            row_dict['norm_comm_id'] =  norm_des_id[0]
                        if row[77]:
                            row_dict['resolution_comm_description'] = row[77]
                        else:
                            message_error.append(
                                " \n La descripción de la Resolucion comisión es obligatoria")

                        row_dict['resolution_comm_date'] = type(row[78]).__name__ == 'datetime' and row[78].strftime(
                            "%Y-%m-%d") or False
                        row_dict['resolution_comm_type'] = row[79] or False
                    else:

                        row_dict['end_date_contract'] = type(row[80]).__name__ == 'datetime' and row[80].strftime(
                            "%Y-%m-%d") or False
                    row_dict['state_move'] = row[84] or False
                    if row_dict['state_move'] == 'BP':
                        self._cr.execute(
                            """SELECT id FROM onsc_legajo_norm  WHERE "tipoNorma" = %s and "numeroNorma"= %s and "anioNorma" = %s and "articuloNorma"= %s """,
                            (str(row[89]), str(row[90]), str(row[91]), str(row[92])))
                        norm_dis_id = self._cr.fetchone()
                        self._cr.execute("""SELECT id FROM onsc_legajo_causes_discharge  WHERE "codRegimen" = %s """,
                                         (str(row[86]),))
                        causes_discharge_id = self._cr.fetchone()

                        row_dict['id_movimiento'] = row[83] or False
                        row_dict['end_date'] = type(row[87]).__name__ == 'datetime' and row[87].strftime(
                            "%Y-%m-%d") or False
                        row_dict['causes_discharge_id'] = causes_discharge_id and causes_discharge_id[0] or False
                        row_dict['reason_discharge'] = row[88] or False
                        row_dict['norm_dis_id'] = norm_dis_id and norm_dis_id[0] or False

                        row_dict['resolution_dis_description'] = row[93] or False
                        row_dict['resolution_dis_date'] = type(row[94]).__name__ == 'datetime' and row[94].strftime(
                            "%Y-%m-%d") or False
                        row_dict['resolution_dis_type'] = row[95] or False

                    elif row_dict['state_move'] == 'AP':
                        row_dict['id_movimiento'] = row[83] or False
                    self._cr.execute(
                        """INSERT INTO "onsc_migration_line" (%s) VALUES %s RETURNING id""" % (
                            ', '.join(row_dict.keys()),
                            tuple(row_dict.values())
                        ),
                    )
                self.env.cr.commit()

            return True
        except Exception:
            self.suspend_security().write({'error': "Error al procesar el archivo", 'state': 'error'})


class ONSCMigrationLine(models.Model):
    _name = "onsc.migration.line"

    migration_id = fields.Many2one('onsc.migration', string='Cabezal migracion')
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
                                   selection=[('L', 'Legal'), ('N', 'Natural'),
                                              ('E', 'Extranjero')])
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
    department_id = fields.Many2one("hr.department", string="Unidad organizativa destino")
    date_start_commission = fields.Date(string='Fecha inicio comisión')
    type_commission = fields.Selection(string="ETipo de Comisión",
                                       selection=[('CS', 'Comisión de Servicio'), ('PC', 'Pase en Comisión')])

    regime_commission_id = fields.Many2one('onsc.legajo.commission.regime', string='Régimen de comisión')
    reason_commision = fields.Text(string='Descr motivo comisión')
    norm_comm_id = fields.Many2one('onsc.legajo.norm', string='Norma comisión')
    norm_comm_type = fields.Char(string="Tipo norma", related="norm_comm_id.tipoNorma", store=True, readonly=True)
    norm_comm_number = fields.Integer(string='Número de norma', related="norm_comm_id.numeroNorma",
                                      store=True, readonly=True)
    norm_comm_year = fields.Integer(string='Año de norma', related="norm_comm_id.anioNorma", store=True,
                                    readonly=True)
    norm_comm_article = fields.Integer(string='Artículo de norma', related="norm_comm_id.articuloNorma",
                                       store=True, readonly=True)
    resolution_comm_description = fields.Char(string='Descripción de la resolución')
    resolution_comm_date = fields.Date(string='Fecha de la resolución')
    resolution_comm_type = fields.Char(string='Tipo de resolución')
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
    norm_dis_id = fields.Many2one('onsc.legajo.norm', string='Norma comisión')
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
