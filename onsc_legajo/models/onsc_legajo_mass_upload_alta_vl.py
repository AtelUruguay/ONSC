import binascii
import datetime
import json
import logging
import tempfile
from datetime import timedelta

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.osv import expression

_logger = logging.getLogger(__name__)
try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')


class ONSCMassUploadLegajoAltaVL(models.Model):
    _name = 'onsc.legajo.mass.upload.alta.vl'
    _description = 'Carga masiva de legajos de alta VL'
    _rec_name = "id_ejecucion"

    @api.model
    def default_get(self, fields):
        res = super(ONSCMassUploadLegajoAltaVL, self).default_get(fields)
        if self.user_has_groups(
                'onsc_legajo.group_legajo_carga_masiva_alta_vl_recursos_humanos_inciso') or self.user_has_groups(
            'onsc_legajo.group_legajo_carga_masiva_alta_vl_recursos_humanos_ue'):
            res['inciso_id'] = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        if self.user_has_groups('onsc_legajo.group_legajo_carga_masiva_alta_vl_recursos_humanos_ue'):
            res['operating_unit_id'] = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        return res

    line_ids = fields.One2many('onsc.legajo.mass.upload.line.alta.vl', 'mass_upload_id', string='Líneas',
                               domain=[('state', '!=', 'done')])
    line_count = fields.Integer(compute='_compute_line_count', string='Cantidad de lineas')
    lines_processed_ids = fields.One2many('onsc.legajo.mass.upload.line.alta.vl', 'mass_upload_id',
                                          domain=[('state', '=', 'done')], string='Líneas procesadas')
    state = fields.Selection([('draft', 'Borrador'), ('partially', 'Procesado con Error'), ('done', 'Procesado')],
                             default='draft', string='Estado')
    id_ejecucion = fields.Char(string='ID de ejecución', required=True)
    document_file = fields.Binary(string='Archivo de carga', required=True)
    document_filename = fields.Char(string="Nombre del documento adjunto")
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    is_inciso_readonly = fields.Boolean(compute="_compute_is_readonly")
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora")
    is_operating_unit_readonly = fields.Boolean(compute="_compute_is_readonly")
    operating_unit_id_domain = fields.Char(compute='_compute_operating_unit_id_domain')

    # Constrain para id de ejecucion  ,inciso  y unidad ejecutora
    @api.constrains('id_ejecucion', 'inciso_id', 'operating_unit_id')
    def _check_unique_id_ejecucion(self):
        for rec in self:
            if rec.id_ejecucion and rec.inciso_id and rec.operating_unit_id:
                domain = [('id_ejecucion', '=', rec.id_ejecucion), ('inciso_id', '=', rec.inciso_id.id),
                          ('operating_unit_id', '=', rec.operating_unit_id.id)]
                if self.search_count(domain) > 1:
                    raise UserError(
                        "Ya existe una carga masiva con el mismo ID de ejecución, inciso y unidad ejecutora")

    @api.depends('line_ids')
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids) + len(rec.lines_processed_ids)

    @api.depends('inciso_id')
    def _compute_is_readonly(self):
        for rec in self:
            rec.is_inciso_readonly = (self.user_has_groups(
                'onsc_legajo.group_legajo_carga_masiva_alta_vl_recursos_humanos_inciso') or self.user_has_groups(
                'onsc_legajo.group_legajo_carga_masiva_alta_vl_recursos_humanos_ue')) and not self.user_has_groups(
                'onsc_legajo.group_legajo_carga_masiva_alta_vl_administrar_altas_vl')
            rec.is_operating_unit_readonly = self.user_has_groups(
                'onsc_legajo.group_legajo_carga_masiva_alta_vl_recursos_humanos_ue') and not self.user_has_groups(
                'onsc_legajo.group_legajo_carga_masiva_alta_vl_administrar_altas_vl')

    @api.depends('inciso_id')
    def _compute_operating_unit_id_domain(self):
        for rec in self:
            domain = [('id', 'in', [])]
            if rec.inciso_id.id:
                domain = [('inciso_id', '=', rec.inciso_id.id)]
            self.operating_unit_id_domain = json.dumps(domain)

    @api.onchange('inciso_id')
    def onchange_inciso_id(self):
        self.operating_unit_id = False

    def action_view_lines(self):
        return {
            'type': 'ir.actions.act_window',
            'name': "Líneas de la carga masiva",
            'res_model': 'onsc.legajo.mass.upload.line.alta.vl',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.line_ids.ids + self.lines_processed_ids.ids)],
            'views': [
                [self.env.ref('onsc_legajo.view_onsc_legajo_mass_upload_line_alta_vl_tree').id, 'tree'],
                [self.env.ref('onsc_legajo.view_onsc_legajo_mass_upload_line_alta_vl_form').id, 'form'],
                [self.env.ref('onsc_legajo.view_onsc_legajo_mass_upload_line_alta_vl_search').id, 'search'],
            ]
        }

    def action_process(self):

        try:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.document_file))
            fp.seek(0)
            values = {}
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)

        except Exception:
            raise UserError(_("Archivo inválido"))

        MassLine = self.env['onsc.legajo.mass.upload.line.alta.vl']
        excel_base_date = datetime.datetime(1899, 12, 31)

        for row_no in range(1, sheet.nrows):
            line = list(map(lambda row: int(row.value) if isinstance(row.value, int) else int(row.value) if isinstance(
                row.value, float) else (row.value.encode('utf-8') if isinstance(row.value, bytes) else str(row.value)),
                            sheet.row(row_no)))
            global message_error
            message_error = []
            values = {
                'nro_line': row_no,
                'mass_upload_id': self.id,
                'document_idenfication': line[0],
                'first_name': line[1],
                'second_name': line[2],
                'first_surname': line[3],
                'second_surname': line[4],
                'first_surname_adopted': line[5],
                'second_surname_adopted': line[6],
                'name_ci': line[7],
                'sex': line[8],
                'birth_date': excel_base_date + timedelta(days=int(float(line[9]))) if line[9] else False,
                'document_country_id': MassLine.find_by_code_name_many2one('document_country_id', 'code', 'name',
                                                                           line[10]),
                'document_number': line[11],
                'marital_status_id': MassLine.find_by_code_name_many2one('marital_status_id', 'code', 'name', line[12]),
                'birth_country_id': MassLine.find_by_code_name_many2one('birth_country_id', 'code', 'name', line[13]),
                'citizenship': line[14],
                'crendencial_serie': line[15],
                'credential_number': line[16],
                'personal_phone': line[17],
                'mobile_phone': line[18],
                'email': line[19],
                'address_state_id': MassLine.find_by_code_name_many2one('address_state_id', 'code', 'name', line[20]),
                'address_location_id': MassLine.find_by_code_name_many2one('address_location_id', 'code', 'name',
                                                                           line[21]),
                'address_street_id': MassLine.find_by_code_name_many2one('address_street_id', 'code', 'street',
                                                                         line[22]),
                'address_street2_id': MassLine.find_by_code_name_many2one('address_street2_id', 'code', 'street',
                                                                          line[23]),
                'address_street3_id': MassLine.find_by_code_name_many2one('address_street3_id', 'code', 'street',
                                                                          line[24]),
                'address_zip': line[25],
                'address_nro_door': line[26],
                'address_is_bis': line[27],
                'address_apto': line[28],
                'address_place': line[29],
                'address_block': line[30],
                'address_sandlot': line[31],
                'date_start': excel_base_date + timedelta(days=int(float(line[32]))) if line[32] else False,
                'income_mechanism_id': MassLine.find_by_code_name_many2one('income_mechanism_id', 'code', 'name',
                                                                           line[33]),
                'call_number': line[34],
                'program': line[35],
                'project': line[36],
                'is_reserva_sgh': line[37],
                'regime_id': MassLine.find_by_code_name_many2one('regime_id', 'codRegimen', 'descripcionRegimen',
                                                                 line[38]),
                'descriptor1_id': MassLine.find_by_code_name_many2one('descriptor1_id', 'code', 'name', line[39]),
                'descriptor2_id': MassLine.find_by_code_name_many2one('descriptor2_id', 'code', 'name', line[40]),
                'descriptor3_id': MassLine.find_by_code_name_many2one('descriptor3_id', 'code', 'name', line[41]),
                'descriptor4_id': MassLine.find_by_code_name_many2one('descriptor4_id', 'code', 'name', line[42]),
                'nroPuesto': line[43],
                'nroPlaza': line[44],
                'department_id': MassLine.find_by_code_name_many2one('department_id', 'code', 'name', line[45]),
                'security_job_id': MassLine.find_by_code_name_many2one('security_job_id', 'name', 'name', line[46]),
                'occupation_id': MassLine.find_by_code_name_many2one('occupation_id', 'code', 'name', line[47]),
                'date_income_public_administration': excel_base_date + timedelta(days=int(float(line[48]))) if line[
                    48] else False,
                'inactivity_years': line[49],
                'graduation_date': excel_base_date + timedelta(days=int(float(line[50]))) if line[50] else False,
                'contract_expiration_date': excel_base_date + timedelta(days=int(float(line[51]))) if line[
                    51] else False,
                'reason_description': line[52],
                'norm_type': line[53],
                'norm_number': line[54],
                'norm_year': line[55],
                'norm_article': line[56],
                'resolution_description': line[57],
                'resolution_date': excel_base_date + timedelta(days=int(float(line[58]))) if line[58] else False,
                'resolution_type': line[59],
                'retributive_day_id': MassLine.find_by_code_name_many2one('retributive_day_id', 'codigoJornada',
                                                                          'descripcionJornada', line[60]),
                'additional_information': line[61],
                'message_error': '',
            }
            values, validate_error = MassLine.validate_fields(values)
            if validate_error:
                values['message_error'] = values['message_error'] + '\n' + validate_error

            if message_error:
                values['message_error'] = values['message_error'] + '\n' + '\n'.join(message_error)

            if message_error or validate_error:
                values['state'] = 'error'
                self.state = 'partially'
                values['message_error'] = 'Información faltante o no cumple validación' + values['message_error']
            else:
                values['state'] = 'done'
                values['message_error'] = ''

            existing_record = MassLine.search([('nro_line', '=', row_no), ('mass_upload_id', '=', self.id)], limit=1)
            if existing_record and existing_record.state != 'done':
                existing_record.update_line(values)
            if not existing_record:
                MassLine.create_line(values)
        if not self.line_ids:
            self.state = 'done'
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Todas las líneas fueron procesadas con éxito',
                    'type': 'rainbow_man',
                }
            }


class ONSCMassUploadLineLegajoAltaVL(models.Model):
    _name = 'onsc.legajo.mass.upload.line.alta.vl'
    _description = 'Lineas para la carga masiva de legajos de alta VL'

    mass_upload_id = fields.Many2one('onsc.legajo.mass.upload.alta.vl', string='Carga masiva')
    state = fields.Selection([('draft', 'Borrador'), ('error', 'Procesado con Error'), ('done', 'Procesado')],
                             string='Estado', default='draft')
    message_error = fields.Text(string='Mensaje de error')
    nro_line = fields.Integer(string='Nro de línea')
    document_idenfication = fields.Char(string='Documento CI')
    first_name = fields.Char(string='Primer nombre', required=True)
    second_name = fields.Char(string='Segundo nombre')
    first_surname = fields.Char(string='Primer apellido', required=True)
    second_surname = fields.Char(string='Segundo apellido')
    first_surname_adopted = fields.Char(string='Primer apellido adoptivo')
    second_surname_adopted = fields.Char(string='Segundo apellido adoptivo')
    name_ci = fields.Char(string='Nombre en cedula')
    sex = fields.Char(string='Sexo')
    birth_date = fields.Date(string='Fecha de nacimiento')
    document_country_id = fields.Many2one('res.country', string='País del documento')
    document_type_id = fields.Many2one('onsc.cv.document.type', string='Tipo de documento')
    document_number = fields.Char(string='Nro documento')
    marital_status_id = fields.Many2one("onsc.cv.status.civil", string="Estado civil")
    birth_country_id = fields.Many2one('res.country', string='Lugar de nacimiento')
    citizenship = fields.Selection(string="Ciudadanía",
                                   selection=[('legal', 'Legal'), ('natural', 'Natural'),
                                              ('extranjero', 'Extranjero')])
    crendencial_serie = fields.Char(string="Serie de la credencial", size=3)
    credential_number = fields.Char(string="Número de la credencial", size=6)
    personal_phone = fields.Char(string="Teléfono Alternativo")
    mobile_phone = fields.Char(string="Teléfono Móvil")
    email = fields.Char(string="e-mail")
    address_state_id = fields.Many2one('res.country.state', string='Departamento')
    address_location_id = fields.Many2one('onsc.cv.location', string="Localidad")
    address_street_id = fields.Many2one('onsc.cv.street', string="Calle")
    address_street2_id = fields.Many2one('onsc.cv.street', string="Esquina 1")
    address_street3_id = fields.Many2one('onsc.cv.street', string="Esquina 2")
    address_zip = fields.Char(u'Código postal')
    address_nro_door = fields.Char(string="Número de puerta")
    address_is_bis = fields.Boolean(string="Bis")
    address_apto = fields.Char(string="Apartamento")
    address_place = fields.Text(string="Paraje", size=200)
    address_block = fields.Char(string="Manzana", size=5)
    address_sandlot = fields.Char(string="Solar", size=5)
    date_start = fields.Date(string="Fecha de alta")
    income_mechanism_id = fields.Many2one('onsc.legajo.income.mechanism', string='Mecanismo de ingreso')
    call_number = fields.Char(string='Número de llamado')
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    is_inciso_readonly = fields.Boolean(compute="_compute_is_readonly")
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora")
    is_operating_unit_readonly = fields.Boolean(compute="_compute_is_readonly")
    operating_unit_id_domain = fields.Char(compute='_compute_operating_unit_id_domain')
    program = fields.Char(string='Programa')
    project = fields.Char(string='Proyecto')
    is_reserva_sgh = fields.Boolean(string="¿Tiene reserva en SGH?")
    regime_id = fields.Many2one('onsc.legajo.regime', string='Régimen')
    # Datos para los Descriptores
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor 1')
    descriptor1_domain_id = fields.Char(compute='_compute_descriptor1_domain_id')
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor 2')
    descriptor2_domain_id = fields.Char(compute='_compute_descriptor2_domain_id')
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor 3')
    descriptor3_domain_id = fields.Char(compute='_compute_descriptor3_domain_id')
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor 4')
    descriptor4_domain_id = fields.Char(compute='_compute_descriptor4_domain_id')
    nroPuesto = fields.Char(string="Puesto")
    nroPlaza = fields.Char(string="Plaza")
    department_id = fields.Many2one("hr.department", string="Unidad organizativa")
    department_id_domain = fields.Char(compute='_compute_department_id_domain')
    security_job_id = fields.Many2one("onsc.legajo.security.job", string="Seguridad de puesto")
    occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación')
    date_income_public_administration = fields.Date(string="Fecha de ingreso a la administración pública")
    inactivity_years = fields.Integer(string="Años de inactividad")
    graduation_date = fields.Date(string='Fecha de graduación')
    contract_expiration_date = fields.Date(string='Vencimiento del contrato', )
    reason_description = fields.Char(string='Descripción del motivo')

    # Datos de la Norma
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
    retributive_day_id = fields.Many2one('onsc.legajo.jornada.retributiva', string='Jornada retributiva')
    additional_information = fields.Text(string="Información adicional")
    document_file = fields.Binary(string="Documento Adjunto")
    document_filename = fields.Char(string="Nombre del documento adjunto")

    @api.depends('inciso_id')
    def _compute_is_readonly(self):
        for rec in self:
            rec.is_inciso_readonly = (self.user_has_groups(
                'onsc_legajo.group_legajo_alta_vl_recursos_humanos_inciso') or self.user_has_groups(
                'onsc_legajo.group_legajo_alta_vl_recursos_humanos_ue')) and not self.user_has_groups(
                'onsc_legajo.group_legajo_alta_vl_administrar_altas_vl')
            rec.is_operating_unit_readonly = self.user_has_groups(
                'onsc_legajo.group_legajo_alta_vl_recursos_humanos_ue') and not self.user_has_groups(
                'onsc_legajo.group_legajo_alta_vl_administrar_altas_vl')

    @api.depends('inciso_id')
    def _compute_operating_unit_id_domain(self):
        for rec in self:
            domain = [('id', 'in', [])]
            if rec.inciso_id.id:
                domain = [('inciso_id', '=', rec.inciso_id.id)]
            self.operating_unit_id_domain = json.dumps(domain)

    @api.depends('inciso_id', 'operating_unit_id')
    def _compute_department_id_domain(self):
        for rec in self:
            domain = []
            if not rec.inciso_id and not rec.operating_unit_id:
                domain = [('id', 'in', [])]
            if rec.inciso_id.id:
                domain = [('inciso_id', '=', rec.inciso_id.id)]
            if rec.operating_unit_id:
                domain = expression.AND([[
                    ('operating_unit_id', '=', rec.operating_unit_id.id)
                ], domain])
            rec.department_id_domain = json.dumps(domain)

    @api.depends('inciso_id', 'operating_unit_id', 'is_reserva_sgh')
    def _compute_descriptor1_domain_id(self):
        domain = [('id', 'in', [])]
        for rec in self:
            if not rec.is_reserva_sgh:
                dsc1Id = self.env['onsc.legajo.budget.item'].search([]).mapped(
                    'dsc1Id')
                if dsc1Id:
                    domain = [('id', 'in', dsc1Id.ids)]
            rec.descriptor1_domain_id = json.dumps(domain)

    @api.depends('descriptor1_id')
    def _compute_descriptor2_domain_id(self):
        for rec in self:
            args = []
            domain = [('id', 'in', [])]
            if rec.descriptor1_id:
                args = [('dsc1Id', '=', rec.descriptor1_id.id)]
            dsc2Id = self.env['onsc.legajo.budget.item'].search(args).mapped('dsc2Id')
            if dsc2Id:
                domain = [('id', 'in', dsc2Id.ids)]
            rec.descriptor2_domain_id = json.dumps(domain)

    @api.depends('descriptor2_id')
    def _compute_descriptor3_domain_id(self):
        for rec in self:
            args = []
            domain = [('id', 'in', [])]
            if rec.descriptor1_id:
                args = [('dsc1Id', '=', rec.descriptor1_id.id)]
            if rec.descriptor2_id:
                args = expression.AND([[('dsc2Id', '=', rec.descriptor2_id.id)], args])
            dsc3Id = self.env['onsc.legajo.budget.item'].search(args).mapped('dsc3Id')
            if dsc3Id:
                domain = [('id', 'in', dsc3Id.ids)]
            rec.descriptor3_domain_id = json.dumps(domain)

    @api.depends('descriptor3_id')
    def _compute_descriptor4_domain_id(self):
        for rec in self:
            args = []
            domain = [('id', 'in', [])]
            if rec.descriptor1_id:
                args = [('dsc1Id', '=', rec.descriptor1_id.id)]
            if rec.descriptor2_id:
                args = expression.AND([[('dsc2Id', '=', rec.descriptor2_id.id)], args])
            if rec.descriptor3_id:
                args = expression.AND([[('dsc3Id', '=', rec.descriptor3_id.id)], args])
            dsc4Id = self.env['onsc.legajo.budget.item'].search(args).mapped('dsc4Id')
            if dsc4Id:
                domain = [('id', 'in', dsc4Id.ids)]
            rec.descriptor4_domain_id = json.dumps(domain)

    def get_fields(self):
        return self._fields

    def find_by_code_name_many2one(self, field, code_field, name_field, value):
        value = value.strip() if isinstance(value, str) else value
        record = self.env[self._fields[field].comodel_name].sudo().search(
            ['|', (code_field, '=', value), (name_field, '=', value)], limit=1)
        if record:
            return record.id
        else:
            message_error.append(
                'No se encontró el valor %s en el catálogo de %s' % (value, self._fields[field].string))

    def create_line(self, values):
        return self.create(values)

    def update_line(self, values):
        return self.write(values)

    def validate_fields(self, values):
        error = []
        for key, value in values.items():
            field = self._fields
            try:
                # valiar float
                if field[key].type == 'float':
                    values[key] = float(value) if value else 0.0
                # validar entero
                if field[key].type == 'integer':
                    values[key] = int(float(value)) if value else 0
                # validar boolean
                if field[key].type == 'boolean':
                    values[key] = True if value == '0' else False
            except Exception:
                error.append("El tipo de campo %s no es válido. El tipo de campo debe ser %s" % (
                    field[key].string, "numérico" if field[key].type == 'float' else "entero" if field[
                                                                                                     key].type == 'integer' else "Booleano"))
                values[key] = False
        error = '\n'.join(error)
        return values, error
