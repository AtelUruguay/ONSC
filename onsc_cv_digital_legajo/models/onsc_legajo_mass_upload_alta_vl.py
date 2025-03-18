# pylint: disable=E8102
import binascii
import datetime
import json
import logging
import tempfile

from odoo import fields, models, api, _, tools
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo import Command
from ...onsc_cv_digital.models.onsc_cv_useful_tools import is_valid_phone

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
        recursos_humanos_inciso = self.user_has_groups(
            'onsc_cv_digital_legajo.group_legajo_carga_masiva_alta_vl_recursos_humanos_inciso')
        recursos_humanos_ue = self.user_has_groups(
            'onsc_cv_digital_legajo.group_legajo_carga_masiva_alta_vl_recursos_humanos_ue')
        if recursos_humanos_inciso or recursos_humanos_ue:
            res['inciso_id'] = self.env.user.employee_id.job_id.contract_id.inciso_id.id
        if recursos_humanos_ue:
            res['operating_unit_id'] = self.env.user.employee_id.job_id.contract_id.operating_unit_id.id
        return res

    def _get_domain(self, args):
        if self.user_has_groups('onsc_cv_digital_legajo.group_legajo_carga_masiva_alta_vl_recursos_humanos_inciso'):
            inciso_id = self.env.user.employee_id.job_id.contract_id.inciso_id
            if inciso_id:
                args = expression.AND([[
                    ('inciso_id', '=', inciso_id.id)
                ], args])
        elif self.user_has_groups('onsc_cv_digital_legajo.group_legajo_carga_masiva_alta_vl_recursos_humanos_ue'):
            contract_id = self.env.user.employee_id.job_id.contract_id
            inciso_id = contract_id.inciso_id
            operating_unit_id = contract_id.operating_unit_id
            if inciso_id:
                args = expression.AND([[
                    ('inciso_id', '=', inciso_id.id)
                ], args])
            if operating_unit_id:
                args = expression.AND([[
                    ('operating_unit_id', '=', operating_unit_id.id)
                ], args])
        return args

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('is_from_menu'):
            args = self._get_domain(args)
        return super()._search(args, offset=offset, limit=limit, order=order, count=count,
                               access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('is_from_menu'):
            domain = self._get_domain(domain)
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    line_ids = fields.One2many('onsc.legajo.mass.upload.line.alta.vl', 'mass_upload_id', string='Líneas',
                               domain=[('state', '!=', 'done')])
    line_count = fields.Integer(compute='_compute_line_count', string='Cantidad de lineas')
    line2process_qty = fields.Integer(compute='_compute_line_count', string='Cantidad de lineas a procesar')
    lines_processed_ids = fields.One2many('onsc.legajo.mass.upload.line.alta.vl', 'mass_upload_id',
                                          domain=[('state', '=', 'done')], string='Líneas procesadas')
    state = fields.Selection([('draft', 'Borrador'), ('partially', 'Procesado con Error'), ('done', 'Procesado')],
                             default='draft', string='Estado')
    id_ejecucion = fields.Char(string='ID de ejecución')
    document_file = fields.Binary(string='Archivo de carga', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    document_filename = fields.Char(string="Nombre del documento adjunto")
    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso', required=True)
    is_inciso_readonly = fields.Boolean(compute="_compute_is_readonly")
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora")
    is_operating_unit_readonly = fields.Boolean(compute="_compute_is_readonly")
    operating_unit_id_domain = fields.Char(compute='_compute_operating_unit_id_domain')
    altas_vl_ids = fields.One2many('onsc.legajo.alta.vl', 'mass_upload_id', string='Altas VL')
    altas_vl_count = fields.Integer(compute='_compute_altas_vl_count', string='Cantidad de altas VL')
    is_can_process = fields.Boolean(compute='_compute_is_can_process', string='Puede procesar')
    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')

    alta_document_file = fields.Binary(
        string='Documento adjunto',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    alta_document_filename = fields.Char(string="Nombre del Documento adjunto")
    alta_document_description = fields.Char(string="Descripción del adjunto")
    alta_document_type_id = fields.Many2one('onsc.legajo.document.type', 'Tipo de documento')

    @api.depends('state')
    def _compute_should_disable_form_edit(self):
        for record in self:
            record.should_disable_form_edit = record.state != 'draft'

    @api.depends('line_ids', 'lines_processed_ids')
    def _compute_line_count(self):
        for rec in self:
            _process_qty = len(rec.line_ids)
            rec.line2process_qty = _process_qty
            rec.line_count = _process_qty + len(rec.lines_processed_ids)

    def _compute_altas_vl_count(self):
        for rec in self:
            rec.altas_vl_count = len(rec.altas_vl_ids)

    def _compute_is_can_process(self):
        for rec in self:
            rec.is_can_process = (rec.state == 'draft' and len(
                ' '.join(rec.line_ids.mapped('message_error')).strip())) == 0 and not rec.state == 'done'

    @api.depends('inciso_id')
    def _compute_is_readonly(self):
        for rec in self:
            if rec.state != 'draft':
                rec.is_inciso_readonly = True
                rec.is_operating_unit_readonly = True
            else:
                rec.is_inciso_readonly = (self.user_has_groups(
                    'onsc_cv_digital_legajo.group_legajo_carga_masiva_alta_vl_recursos_humanos_inciso') or self.user_has_groups(
                    'onsc_cv_digital_legajo.group_legajo_carga_masiva_alta_vl_recursos_humanos_ue')) and not self.user_has_groups(
                    'onsc_cv_digital_legajo.group_legajo_carga_masiva_alta_vl_administrar_altas_vl')
                rec.is_operating_unit_readonly = self.user_has_groups(
                    'onsc_cv_digital_legajo.group_legajo_carga_masiva_alta_vl_recursos_humanos_ue') and not self.user_has_groups(
                    'onsc_cv_digital_legajo.group_legajo_carga_masiva_alta_vl_administrar_altas_vl')

    @api.depends('inciso_id')
    def _compute_operating_unit_id_domain(self):
        for rec in self:
            domain = [('id', 'in', [])]
            if rec.inciso_id.id:
                domain = [('inciso_id', '=', rec.inciso_id.id)]
            self.operating_unit_id_domain = json.dumps(domain)

    @api.onchange('inciso_id')
    def onchange_inciso_id(self):
        if self.operating_unit_id.inciso_id != self.inciso_id:
            self.operating_unit_id = False

    @api.onchange('document_file')
    def onchange_document_file(self):
        self.line_ids = False

    @api.onchange('alta_document_file')
    def onchange_alta_document_file(self):
        if self.alta_document_file is False:
            self.alta_document_filename = False
            self.alta_document_description = False
            self.alta_document_type_id = False
            self.alta_document_type_id = False

    def action_view_lines(self):
        return {
            'type': 'ir.actions.act_window',
            'name': "Líneas de la carga masiva",
            'res_model': 'onsc.legajo.mass.upload.line.alta.vl',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.line_ids.ids + self.lines_processed_ids.ids)],
            'views': [
                [self.env.ref('onsc_cv_digital_legajo.view_onsc_legajo_mass_upload_line_alta_vl_tree').id, 'tree'],
                [self.env.ref('onsc_cv_digital_legajo.view_onsc_legajo_mass_upload_line_alta_vl_form').id, 'form'],
                [self.env.ref('onsc_cv_digital_legajo.view_onsc_legajo_mass_upload_line_alta_vl_search').id, 'search'],
            ]
        }

    def action_view_altas_vl_ids(self):
        return {
            'type': 'ir.actions.act_window',
            'name': "Altas de vínculo laboral",
            'res_model': 'onsc.legajo.alta.vl',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.altas_vl_ids.ids)],
            'views': [
                [self.env.ref('onsc_cv_digital_legajo.onsc_legajo_alta_vl_mass_tree').id, 'tree'],
                [self.env.ref('onsc_cv_digital_legajo.onsc_legajo_alta_vl_form').id, 'form'],
            ]
        }

    def process_value(self, row):
        if isinstance(row.value, int):
            return int(row.value)
        elif isinstance(row.value, float):
            return int(row.value)
        elif isinstance(row.value, bytes):
            return row.value.encode('utf-8')
        else:
            return str(row.value)

    def validate_cv_fields(self, value):
        error = []
        if value['credential_number'] and not str(value['credential_number']).isdigit():
            error.append("El número de credencial debe ser numérico")
        if value['crendencial_serie'] and not str(value['crendencial_serie']).isalpha():
            error.append("La serie de la credencial no puede contener números")
        prefix_phone_id = self.env['res.country.phone'].search(
            [('country_id.code', '=', 'UY')])
        phone_formatted, format_with_error, invalid_phone = is_valid_phone(str(value['personal_phone']),
                                                                           prefix_phone_id.country_id)
        if format_with_error or invalid_phone:
            error.append("El formato del teléfono alternativo es incorrecto")
        phone_formatted, format_with_error, invalid_phone = is_valid_phone(str(value['mobile_phone']),
                                                                           prefix_phone_id.country_id)
        if format_with_error or invalid_phone:
            error.append("El formato del teléfono móvil es incorrecto")
        return error

    def get_string_by_fieldname(self, field_name):
        MassLine = self.env['onsc.legajo.mass.upload.line.alta.vl']
        for nombre_campo, campo in MassLine.get_fields().items():
            if campo.name == field_name:
                return campo.string
        return ''

    def get_position(self, array, field_name):
        field_string = self.get_string_by_fieldname(field_name)

        if field_string in array:
            posicion = array.index(field_string)
            return posicion
        else:
            return message_error.append("La columna %s no corresponde al formato esperado" % field_string)

    # flake8: noqa: C901
    def action_process_excel(self):
        try:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.document_file))
            fp.seek(0)
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_name('Datos')
        except Exception:
            raise UserError(_("Archivo inválido"))
        MassLine = self.env['onsc.legajo.mass.upload.line.alta.vl']
        LegajoOffice = self.env['onsc.legajo.office']
        LegajoNorm = self.env['onsc.legajo.norm']
        country_code = "UY"
        country_uy_id = self.env['res.country'].search([
            ('code', 'in', [country_code.upper(), country_code.lower()])
        ], limit=1)
        column_names = sheet.row_values(0)
        limit = self.env.user.company_id.mass_upload_record_limit
        if limit < (sheet.nrows - 1):
            raise ValidationError(
                _('El archivo supera la cantidad de altas permitidas  %s') % limit)

        try:
            for row_no in range(1, sheet.nrows):
                line = list(map(self.process_value, sheet.row(row_no)))
                global message_error
                norm_id = False
                message_error = []
                warning_error = []
                office = False
                try:
                    office = LegajoOffice.sudo().search([
                        ('inciso', '=', self.inciso_id.id),
                        ('unidadEjecutora', '=', self.operating_unit_id.id),
                        '&', '|',
                        ('programa', '=', str(line[self.get_position(column_names, 'program')])),
                        ('programaDescripcion', '=', str(line[self.get_position(column_names, 'program')])),
                        '|',
                        ('proyecto', '=', str(line[self.get_position(column_names, 'project')])),
                        ('proyectoDescripcion', '=', str(line[self.get_position(column_names, 'project')]))
                    ], limit=1)
                except Exception:
                    message_error.append(
                        " \n Los datos para la oficina tiene un formato inválido")
                try:
                    norm_id = LegajoNorm.sudo().search(
                        [('anioNorma', '=', int(float(line[self.get_position(column_names, 'norm_year')]))),
                         ('numeroNorma', '=', int(float(line[self.get_position(column_names, 'norm_number')]))),
                         ('articuloNorma', '=', int(float(line[self.get_position(column_names, 'norm_article')]))),
                         ('tipoNorma', '=', line[self.get_position(column_names, 'norm_type')])],
                        limit=1)
                except Exception:
                    message_error.append(
                        " \n Los datos para la norma tiene un formato inválido")
                if not office:
                    message_error.append(
                        "No se pudo encontrar la oficina con los códigos de programa %s y proyecto %s" % (
                            line[self.get_position(column_names, 'program')],
                            line[self.get_position(column_names, 'project')]))

                if not norm_id:
                    message_error.append(
                        " \nNo se pudo encontrar la norma con los códigos de año %s, número %s, artículo %s y tipo %s" % (
                            line[self.get_position(column_names, 'norm_year')],
                            line[self.get_position(column_names, 'norm_number')],
                            line[self.get_position(column_names, 'norm_article')],
                            line[self.get_position(column_names, 'norm_type')]))

                descriptor1_id = MassLine.find_by_code_name_many2one('descriptor1_id', 'code', 'name', line[
                    self.get_position(column_names, 'descriptor1_id')])
                descriptor2_id = MassLine.find_by_code_name_many2one('descriptor2_id', 'code', 'name', line[
                    self.get_position(column_names, 'descriptor2_id')])
                descriptor3_id = MassLine.find_by_code_name_many2one('descriptor3_id', 'code', 'name', line[
                    self.get_position(column_names, 'descriptor3_id')])
                if not descriptor3_id:
                    message_error.append(
                        "El campo Descriptor 3  no está definido o no ha sido encontrado")
                descriptor4_id = MassLine.find_by_code_name_many2one('descriptor4_id', 'code', 'name', line[
                    self.get_position(column_names, 'descriptor4_id')])
                budget_item_id = self.get_partida(descriptor1_id, descriptor2_id, descriptor3_id, descriptor4_id)
                if not budget_item_id:
                    message_error.append("No se pudo encontrar la partida con datos de los descriptores")

                address_nro_door = line[self.get_position(column_names, 'address_nro_door')]
                if len(str(address_nro_door)) > 5:
                    message_error.append("El Número de puerta excede la longitud de 5")
                address_apto = line[self.get_position(column_names, 'address_apto')]
                if len(str(address_apto)) > 4:
                    message_error.append("El Número de apartamento excede la longitud de 4")
                address_zip = line[self.get_position(column_names, 'address_zip')]
                if len(str(address_zip)) > 6:
                    message_error.append("El Código Postal excede la longitud de 6")

                document_number = line[self.get_position(column_names, 'document_number')]
                sex = line[self.get_position(column_names, 'cv_sex')]
                birth_date = line[self.get_position(column_names, 'birth_date')]
                crendencial_serie = line[self.get_position(column_names, 'crendencial_serie')]
                credential_number = line[self.get_position(column_names, 'credential_number')]
                date_start = line[self.get_position(column_names, 'date_start')]
                date_income_public_administration = line[
                    self.get_position(column_names, 'date_income_public_administration')]
                graduation_date = line[self.get_position(column_names, 'graduation_date')]
                contract_expiration_date = line[self.get_position(column_names, 'contract_expiration_date')]
                resolution_date = line[self.get_position(column_names, 'resolution_date')]

                address_state_id = MassLine.find_by_code_name_many2one(
                    'address_state_id', 'code', 'name', line[self.get_position(column_names, 'address_state_id')]
                )
                address_location_id = MassLine.find_by_code_name_many2one(
                    'address_location_id', 'code', 'name', line[self.get_position(column_names, 'address_location_id')],
                    [('state_id', '=', address_state_id)]
                )
                address_street_id = MassLine.find_by_code_name_many2one(
                    'address_street_id', 'code', 'street', line[self.get_position(column_names, 'address_street_id')],
                    [('cv_location_id', '=', address_location_id)]
                )
                address_street2_id = MassLine.find_by_code_name_many2one(
                    'address_street2_id', 'code', 'street', line[self.get_position(column_names, 'address_street2_id')],
                    [('cv_location_id', '=', address_location_id)]
                )
                address_street3_id = MassLine.find_by_code_name_many2one(
                    'address_street3_id', 'code', 'street', line[self.get_position(column_names, 'address_street3_id')],
                    [('cv_location_id', '=', address_location_id)]
                )

                regime_id = MassLine.find_by_code_name_many2one('regime_id', 'codRegimen', 'descripcionRegimen',
                                                                line[self.get_position(column_names,
                                                                                       'regime_id')])
                legajo_state_id = MassLine.find_by_code_name_many2one('legajo_state_id', 'code', 'name', line[
                    self.get_position(column_names, 'legajo_state_id')])
                if not legajo_state_id:
                    message_error.append(
                        "El campo Departamento donde desempeña funciones no está definido o no ha sido encontrado")

                line_occupation_value = line[self.get_position(column_names, 'occupation_id')]
                occupation_id = MassLine.find_by_code_name_many2one('occupation_id', 'code', 'name',
                                                                    line_occupation_value)
                _is_occupation_required = self._is_occupation_required(descriptor1_id, regime_id)
                if line_occupation_value and not _is_occupation_required:
                    message_error.append("No corresponde ocupación para ese vínculo")
                if not occupation_id and _is_occupation_required:
                    message_error.append("El campo ocupación es obligatorio y no está definido o no ha sido encontrado")
                reason_description = line[self.get_position(column_names, 'reason_description')]
                resolution_description = line[self.get_position(column_names, 'resolution_description')]
                if len(str(reason_description)) > 50:
                    message_error.append("El campo Descripción del motivo no puede tener más de 50 caracteres.")
                if len(str(resolution_description)) > 100:
                    message_error.append("El campo Descripción de la resolución no puede tener más de 100 caracteres.")

                values = {
                    'nro_line': row_no,
                    'mass_upload_id': self.id,
                    'document_number': document_number if document_number else message_error.append(
                        " \nEl número de documento es obligatorio"),
                    'cv_sex': sex if sex else message_error.append(" \nEl sexo es obligatorio"),
                    'birth_date': datetime.datetime.fromordinal(
                        datetime.datetime(1900, 1, 1).toordinal() + birth_date - 2) if
                    birth_date else message_error.append(" \nLa fecha de nacimiento es obligatoria"),
                    'document_country_id': country_uy_id.id if country_uy_id else False,
                    'marital_status_id': MassLine.find_by_code_name_many2one('marital_status_id', 'code', 'name',
                                                                             line[self.get_position(column_names,
                                                                                                    'marital_status_id')]),
                    'birth_country_id': country_uy_id.id if country_uy_id else False,
                    'citizenship': line[self.get_position(column_names, 'citizenship')],
                    'crendencial_serie': str(crendencial_serie).upper(),
                    'credential_number': credential_number,
                    'personal_phone': line[self.get_position(column_names, 'personal_phone')],
                    'mobile_phone': line[self.get_position(column_names, 'mobile_phone')],
                    'email': line[self.get_position(column_names, 'email')],
                    'address_state_id': address_state_id,
                    'address_location_id': address_location_id,
                    'address_street_id': address_street_id,
                    'address_street2_id': address_street2_id,
                    'address_street3_id': address_street3_id,
                    'address_zip': address_zip,
                    'address_nro_door': address_nro_door,
                    'address_is_bis': line[self.get_position(column_names, 'address_is_bis')],
                    'address_apto': address_apto,
                    'address_place': line[self.get_position(column_names, 'address_place')],
                    'address_block': line[self.get_position(column_names, 'address_block')],
                    'address_sandlot': line[self.get_position(column_names, 'address_sandlot')],
                    'date_start': datetime.datetime.fromordinal(
                        datetime.datetime(1900, 1, 1).toordinal() + date_start - 2) if
                    date_start else False,
                    'income_mechanism_id': MassLine.find_by_code_name_many2one('income_mechanism_id', 'code', 'name',
                                                                               line[self.get_position(column_names,
                                                                                                      'income_mechanism_id')]),
                    'call_number': line[self.get_position(column_names, 'call_number')],
                    'program_project_id': office.id if office else False,
                    'is_reserva_sgh': line[self.get_position(column_names, 'is_reserva_sgh')],
                    'regime_id': regime_id,
                    'descriptor1_id': descriptor1_id,
                    'descriptor2_id': descriptor2_id,
                    'descriptor3_id': descriptor3_id,
                    'descriptor4_id': descriptor4_id,
                    'nroPuesto': line[self.get_position(column_names, 'nroPuesto')],
                    'nroPlaza': line[self.get_position(column_names, 'nroPlaza')],
                    'department_id': MassLine.find_by_code_name_many2one('department_id', 'code', 'name', line[
                        self.get_position(column_names, 'department_id')]),
                    'security_job_id': MassLine.find_by_code_name_many2one('security_job_id', 'name', 'name', line[
                        self.get_position(column_names, 'security_job_id')]),
                    'legajo_state_id': legajo_state_id,
                    'is_responsable_uo': line[self.get_position(column_names, 'is_responsable_uo')],
                    'occupation_id': occupation_id,
                    'date_income_public_administration': datetime.datetime.fromordinal(
                        datetime.datetime(1900, 1,
                                          1).toordinal() + date_income_public_administration - 2) if date_income_public_administration else False,
                    'inactivity_years': line[self.get_position(column_names, 'inactivity_years')],
                    'graduation_date': datetime.datetime.fromordinal(
                        datetime.datetime(1900, 1, 1).toordinal() + graduation_date - 2) if graduation_date else False,
                    'contract_expiration_date': datetime.datetime.fromordinal(
                        datetime.datetime(1900, 1,
                                          1).toordinal() + contract_expiration_date - 2) if contract_expiration_date else False,
                    'reason_description': reason_description,
                    'norm_id': norm_id.id if norm_id else False,
                    'resolution_description': resolution_description,
                    'resolution_date': datetime.datetime.fromordinal(
                        datetime.datetime(1900, 1, 1).toordinal() + resolution_date - 2) if resolution_date else False,
                    'resolution_type': line[self.get_position(column_names, 'resolution_type')],
                    'retributive_day_id': MassLine.find_by_code_name_many2one('retributive_day_id', 'codigoJornada',
                                                                              'descripcionJornada', line[
                                                                                  self.get_position(column_names,
                                                                                                    'retributive_day_id')]),
                    'additional_information': line[self.get_position(column_names, 'additional_information')],
                    'message_error': '',
                }
                if self._validate_exist_altaVL(values, country_uy_id, office):
                    warning_error.append(
                        "NOTIFICACIÓN: Esta persona ya cuenta con un movimiento pendiente de auditoría o auditado por CGN con la misma información de Inciso, UE, Programa, Proyecto, Régimen y Descriptores")
                values, validate_error = MassLine.validate_fields(values)
                message_error.extend(self.validate_cv_fields(values))
                if validate_error:
                    values['message_error'] = values['message_error'] + '\n' + validate_error

                if message_error:
                    values['message_error'] = values['message_error'] + '\n' + '\n'.join(message_error)

                if message_error or validate_error:
                    values['state'] = 'error'
                    values['message_error'] = 'Información faltante o no cumple validación' + values['message_error']
                else:
                    values['message_error'] = ''
                if warning_error:
                    values['warning_error'] = '\n'.join(warning_error)
                existing_record = MassLine.search([('nro_line', '=', row_no), ('mass_upload_id', '=', self.id)],
                                                  limit=1)
                if existing_record and existing_record.state != 'done':
                    existing_record.update_line(values)
                if not existing_record:
                    MassLine.create_line(values)
        except Exception as e:
            raise ValidationError(
                _('El archivo no es válido o no tiene el formato correcto. Detalle: %s') % tools.ustr(e))

    def _update_partner_info_if_needed(self, partner):
        if not partner:
            return False
        is_dnic_info_complete = partner.cv_dnic_name_1 and partner.cv_dnic_lastname_1
        if (not partner.cv_first_name or not partner.cv_last_name_1) and is_dnic_info_complete:
            partner.write({
                'cv_first_name': partner.cv_dnic_name_1,
                'cv_second_name': partner.cv_dnic_name_2,
                'cv_last_name_1': partner.cv_dnic_lastname_1,
                'cv_last_name_2': partner.cv_dnic_lastname_2,
            })
        return True

    def action_process(self):
        if not self.line_ids:
            raise ValidationError(_('No hay líneas para procesar'))

        Partner = self.env['res.partner']
        AltaVL = self.env['onsc.legajo.alta.vl']
        CVDigital = self.env['onsc.cv.digital']
        cv_document_type_id = self.env['onsc.cv.document.type'].sudo().search([('code', '=', 'ci')],
                                                                              limit=1).id or False
        country_code = "UY"
        country_uy = self.env['res.country'].search([
            ('code', 'in', [country_code.upper(), country_code.lower()])
        ], limit=1)
        for line in self.line_ids:
            partner = Partner.sudo().search([('cv_nro_doc', '=', line.document_number)], limit=1)
            try:
                if not partner:
                    data_partner = {
                        'cv_sex': line.cv_sex,
                        'cv_birthdate': line.birth_date,
                        'cv_emissor_country_id': line.document_country_id.id,
                        'cv_nro_doc': line.document_number,
                        'cv_document_type_id': cv_document_type_id,
                        'is_partner_cv': True,
                        'email': line.email,
                    }
                    partner = Partner.suspend_security().create(data_partner)
                    partner.suspend_security().update_dnic_values()
                Summary = self.env['onsc.legajo.summary'].suspend_security()
                if Summary._has_summary(partner.cv_emissor_country_id, partner.cv_document_type_id,
                                            partner.cv_nro_doc):
                        line.write({'state': 'error', 'message_error':  "Tenga en cuenta que la persona %s tuvo un sumario con sanción “Destitución”. Se recomienda que antes de confirmar verifique que sea correcto realizar este movimiento" % partner.cv_dnic_full_name})
                        continue
                self._update_partner_info_if_needed(partner)
                line.suspend_security().write({'first_name': partner.cv_first_name,
                                               'second_name': partner.cv_second_name,
                                               'first_surname': partner.cv_last_name_1,
                                               'second_surname': partner.cv_last_name_2,
                                               'name_ci': partner.cv_dnic_full_name,
                                               'partner_id': partner.id,
                                               'message_error': '',
                                               })
            except Exception as e:
                self.env.cr.rollback()
                line.write({'state': 'error', 'message_error': "No se pudo crear el contacto: " + tools.ustr(e)})
                self.env.cr.commit()
                continue
            cv_digital = CVDigital.sudo().search([('partner_id', '=', partner.id)], limit=1)
            try:
                if not cv_digital:
                    data = {'partner_id': partner.id,
                            'personal_phone': line.personal_phone,
                            'mobile_phone': line.mobile_phone,
                            'email': line.email,
                            'country_id': country_uy.id if country_uy else False,
                            'marital_status_id': line.marital_status_id.id,
                            'country_of_birth_id': line.birth_country_id.id,
                            'uy_citizenship': line.citizenship,
                            'crendencial_serie': line.crendencial_serie,
                            'credential_number': line.credential_number,
                            'cv_address_state_id': line.address_state_id.id,
                            'cv_address_location_id': line.address_location_id.id,
                            'cv_address_street_id': line.address_street_id.id,
                            'cv_address_street2_id': line.address_street2_id.id,
                            'cv_address_street3_id': line.address_street3_id.id,
                            'cv_address_zip': line.address_zip,
                            'cv_address_nro_door': line.address_nro_door,
                            'cv_address_is_cv_bis': line.address_is_bis,
                            'cv_address_apto': line.address_apto,
                            'cv_address_place': line.address_place,
                            'cv_address_block': line.address_block,
                            'cv_address_sandlot': line.address_sandlot,
                            }
                    error = self.validate_cv_fields(data)
                    if error:
                        raise ValidationError(''.join(error))
                    CVDigital.suspend_security().create(data)
                line.write({'message_error': ''})
                self.env.cr.commit()
            except Exception as e:
                self.env.cr.rollback()
                line.write({'state': 'error', 'message_error': "No se pudo crear el CV: " + tools.ustr(e)})
                self.env.cr.commit()
                continue

            data_alta_vl = {
                'partner_id': partner.id,
                'date_start': line.date_start,
                'inciso_id': self.inciso_id.id,
                'operating_unit_id': self.operating_unit_id.id,
                'cv_sex': line.cv_sex,
                'cv_birthdate': line.birth_date,
                'cv_document_type_id': cv_document_type_id,
                'is_reserva_sgh': line.is_reserva_sgh,
                'regime_id': line.regime_id.id,
                'descriptor1_id': line.descriptor1_id.id if line.descriptor1_id else False,
                'descriptor2_id': line.descriptor2_id.id if line.descriptor2_id else False,
                'descriptor3_id': line.descriptor3_id.id if line.descriptor3_id else False,
                'descriptor4_id': line.descriptor4_id.id if line.descriptor4_id else False,
                'nroPuesto': line.nroPuesto,
                'nroPlaza': line.nroPlaza,
                'department_id': line.department_id.id if line.department_id else False,
                'security_job_id': line.security_job_id.id if line.security_job_id else False,
                'legajo_state_id': line.legajo_state_id.id if line.legajo_state_id else False,
                'is_responsable_uo': line.is_responsable_uo,
                'occupation_id': line.occupation_id.id if line.occupation_id else False,
                'date_income_public_administration': line.date_income_public_administration,
                'income_mechanism_id': line.income_mechanism_id.id if line.income_mechanism_id else False,
                'inactivity_years': line.inactivity_years,
                'graduation_date': line.graduation_date,
                'contract_expiration_date': line.contract_expiration_date,
                'reason_description': line.reason_description,
                'program_project_id': line.program_project_id.id if line.program_project_id else False,
                'resolution_description': line.resolution_description,
                'resolution_date': line.resolution_date,
                'resolution_type': line.resolution_type,
                'retributive_day_id': line.retributive_day_id.id if line.retributive_day_id else False,
                'codigoJornadaFormal': line.retributive_day_id.codigoJornada,
                'descripcionJornadaFormal': line.retributive_day_id.descripcionJornada,
                'additional_information': line.additional_information,
                'norm_id': line.norm_id.id if line.norm_id else False,
                'call_number': line.call_number,
                'is_cv_validation_ok': True,
                'mass_upload_id': self.id,
            }
            is_presupuestado = line.regime_id.presupuesto
            is_reserva_sgh = line.is_reserva_sgh
            if is_presupuestado or is_reserva_sgh:
                vacante_value = {
                    'selected': True,
                    'nroPuesto': line.nroPuesto,
                    'nroPlaza': line.nroPlaza,
                    'Dsc3Id': line.descriptor3_id.code,
                    'Dsc4Id': line.descriptor4_id.code,
                    'descriptor3_id': line.descriptor3_id.id,
                    'descriptor4_id': line.descriptor4_id.id,
                    'codRegimen': line.regime_id.codRegimen,
                    'descripcionRegimen': line.regime_id.descripcionRegimen,
                    'regime_id': line.regime_id.id,
                }
                if line.retributive_day_id.codigoJornada.isdigit():
                    vacante_value.update({
                        'codigoJornadaFormal': int(line.retributive_day_id.codigoJornada),
                        'descripcionJornadaFormal': line.retributive_day_id.descripcionJornada,
                    })
                data_alta_vl.update({
                    'vacante_ids': [(0, 0, vacante_value)],
                })
                if self.alta_document_file:
                    data_alta_vl.update({
                        'attached_document_ids': [(Command.create({
                            'name': self.alta_document_description,
                            'document_type_id': self.alta_document_type_id.id,
                            'document_file': self.alta_document_file,
                            'document_file_name': self.alta_document_filename,
                            'type': 'discharge',
                        }))]
                    })
            try:
                alta_vl_id = AltaVL.create(data_alta_vl)
                # if self.alta_document_file:
                    # alta_vl_id.message_post(
                    #     body="Adjunto agregado por Alta Masiva.",
                    #     attachments=[(self.alta_document_filename, self.alta_document_file)]
                    # )
                alta_vl_id.with_context(no_update_extra=True)._update_altavl_info()
                line.write({'state': 'done'})
                self.env.cr.commit()
                alta_vl_id.with_context({'not_check_attached_document': True}).check_required_fields_ws4()
                self.env.cr.commit()
            except Exception as e:
                self.env.cr.rollback()
                line.write({'state': 'error',
                            'message_error': line.message_error + " \nNo se pudo crear el alta de vínculo laboral: " + tools.ustr(
                                e)})
                self.env.cr.commit()
                continue

        if not self.line_ids:
            self.state = 'done'
        else:
            self.state = 'partially'

        try:
            self.syncronize_ws4()
        except Exception as e:
            _logger.error("Error al sincronizar con WS4: " + tools.ustr(e))

    def _is_occupation_required(self, descriptor1_id, regime_id):
        if not regime_id:
            return True
        if descriptor1_id:
            descriptor1 = self.env['onsc.catalog.descriptor1'].browse(descriptor1_id)
        else:
            descriptor1 = self.env['onsc.catalog.descriptor1']
        regime = self.env['onsc.legajo.regime'].browse(regime_id)
        ue_code = ['13', '5', '7', '8']
        is_inciso_5 = self.inciso_id.budget_code == '5'
        is_valid_operating_unit = self.operating_unit_id.budget_code in ue_code
        base_condition = not (is_inciso_5 and is_valid_operating_unit)
        desc_condition = descriptor1.is_occupation_required or not descriptor1_id
        return base_condition and regime.is_public_employee and desc_condition

    def get_partida(self, descriptor1_id, descriptor2_id, descriptor3_id, descriptor4_id):
        args = []
        if descriptor1_id:
            args = [('dsc1Id', '=', descriptor1_id)]
        if descriptor2_id:
            args = expression.AND([[('dsc2Id', '=', descriptor2_id)], args])
        if descriptor3_id:
            args = expression.AND([[('dsc3Id', '=', descriptor3_id)], args])
        if descriptor4_id:
            args = expression.AND([[('dsc4Id', '=', descriptor4_id)], args])
        return self.env['onsc.legajo.budget.item'].sudo().search(args, limit=1)

    def syncronize_ws4(self):
        self.mapped('altas_vl_ids').with_context(not_check_attached_document=True).action_call_multi_ws4()

    @api.model
    def create(self, vals):
        vals['id_ejecucion'] = self.env['ir.sequence'].next_by_code('onsc.legajo.mass.upload.alta.vl.sequence')
        return super().create(vals)

    def unlink(self):
        if self.filtered(lambda x: x.altas_vl_ids):
            raise ValidationError(
                _("El registro no puede ser eliminado porque tiene altas de vínculo laboral asociadas"))
        return super(ONSCMassUploadLegajoAltaVL, self).unlink()

    def _validate_exist_altaVL(self, values,country_uy_id,office):
        exist_altaVL = False
        Partner = self.env['res.partner']
        Contract = self.env['hr.contract'].suspend_security()
        AltaVL = self.env['onsc.legajo.alta.vl'].suspend_security().with_context(is_from_menu = False)
        Employee = self.env['hr.employee'].suspend_security()

        cv_document_type_id = self.env['onsc.cv.document.type'].sudo().search([('code', '=', 'ci')],
                                                                              limit=1).id or False

        employee = Employee.search([
            ('cv_emissor_country_id', '=', country_uy_id.id),
            ('cv_document_type_id', '=', cv_document_type_id),
            ('cv_nro_doc', '=', values['document_number']),
        ], limit=1)

        partner = Partner.sudo().search([('cv_nro_doc', '=',values['document_number'])], limit=1)
        domain = [
            ('state', 'in', ['aprobado_cgn', 'pendiente_auditoria_cgn']),
            ('descriptor1_id', '=', values['descriptor1_id']),
            ('descriptor2_id', '=', values['descriptor2_id']),
            ('descriptor3_id', '=', values['descriptor3_id']),
            ('descriptor4_id', '=', values['descriptor4_id']),
            ('regime_id', '=', values['regime_id']),
            ('inciso_id', '=', self.inciso_id.id),
            ('program_project_id', '=', office.id),
            ('operating_unit_id', '=', self.operating_unit_id.id),
            ('partner_id', '=', partner.id),
        ]
        for alta_vl in AltaVL.search(domain):
            if alta_vl.state == 'pendiente_auditoria_cgn' or (alta_vl.state == 'aprobado_cgn' and Contract.search_count([
                ('descriptor1_id', '=', values['descriptor1_id']),
                ('descriptor2_id', '=', values['descriptor2_id']),
                ('descriptor3_id', '=', values['descriptor3_id']),
                ('descriptor4_id', '=', values['descriptor4_id']),
                ('regime_id', '=', values['regime_id']),
                ('inciso_id', '=', self.inciso_id.id),
                ('program', '=', office.programa),
                ('project', '=', office.proyecto),
                ('operating_unit_id', '=', self.operating_unit_id.id),
                ('legajo_id.emissor_country_id', '=', country_uy_id.id),
                ('legajo_id.document_type_id', '=', cv_document_type_id),
                ('legajo_id.nro_doc', '=', values['document_number']),
                ('legajo_state', '=', 'active')])):
                exist_altaVL = True
        return exist_altaVL


class ONSCMassUploadLineLegajoAltaVL(models.Model):
    _name = 'onsc.legajo.mass.upload.line.alta.vl'
    _description = 'Lineas para la carga masiva de legajos de alta VL'

    def read(self, fields=None, load="_classic_read"):
        Office = self.env['onsc.legajo.office'].sudo()
        RetributiveDay = self.env['onsc.legajo.jornada.retributiva'].sudo()
        LegajoNorm = self.env['onsc.legajo.norm'].sudo()
        result = super(ONSCMassUploadLineLegajoAltaVL, self).read(fields, load)
        for item in result:
            if item.get('program_project_id'):
                program_project_id = item['program_project_id'][0]
                item['program_project_id'] = (
                    item['program_project_id'][0], Office.browse(program_project_id)._custom_display_name())
            if item.get('retributive_day_id'):
                retributive_day_id = item['retributive_day_id'][0]
                item['retributive_day_id'] = (
                    item['retributive_day_id'][0], RetributiveDay.browse(retributive_day_id)._custom_display_name())
            if item.get('norm_id'):
                norm_id = item['norm_id'][0]
                item['norm_id'] = (item['norm_id'][0], LegajoNorm.browse(norm_id)._custom_display_name())
        return result

    mass_upload_id = fields.Many2one('onsc.legajo.mass.upload.alta.vl', string='Carga masiva', ondelete='cascade')
    state = fields.Selection([('draft', 'Borrador'), ('error', 'Procesado con Error'), ('done', 'Procesado')],
                             string='Estado', default='draft')
    message_error = fields.Text(string='Mensaje de error')
    warning_error = fields.Text(string='Mensaje de notificación')
    message = fields.Text(string='Mensajes', compute='_compute_message', store=True)
    nro_line = fields.Integer(string='Nro de línea')
    first_name = fields.Char(string='Primer nombre')
    second_name = fields.Char(string='Segundo nombre')
    first_surname = fields.Char(string='Primer apellido')
    second_surname = fields.Char(string='Segundo apellido')
    name_ci = fields.Char(string='Nombre en cédula')
    partner_id = fields.Many2one('res.partner', string='Contacto')
    cv_sex = fields.Selection([('male', 'Masculino'), ('feminine', 'Femenino')], 'Sexo')
    birth_date = fields.Date(string='Fecha de nacimiento')
    document_country_id = fields.Many2one('res.country', string='País del documento')
    document_number = fields.Char(string='C.I.')
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
    program = fields.Char(string='Programa')
    project = fields.Char(string='Proyecto')
    program_project_id = fields.Many2one('onsc.legajo.office', string='Programa - Proyecto')
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

    legajo_state_id = fields.Many2one(
        'onsc.legajo.res.country.department',
        string='Departamento donde desempeña funciones')
    is_responsable_uo = fields.Boolean(string="¿Responsable de UO?")
    occupation_id = fields.Many2one('onsc.catalog.occupation', string='Ocupación')
    date_income_public_administration = fields.Date(string="Fecha de ingreso a la administración pública")
    inactivity_years = fields.Integer(string="Años de inactividad")
    graduation_date = fields.Date(string='Fecha de graduación')
    contract_expiration_date = fields.Date(string='Vencimiento del contrato', )
    reason_description = fields.Char(string='Descripción del motivo')

    # Datos de la Norma
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
    retributive_day_id = fields.Many2one('onsc.legajo.jornada.retributiva', string='Jornada retributiva')
    additional_information = fields.Text(string="Información adicional")
    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')

    @api.depends('state')
    def _compute_should_disable_form_edit(self):
        for record in self:
            record.should_disable_form_edit = record.state not in ['draft', 'error']

    @api.depends('mass_upload_id')
    def _compute_department_id_domain(self):
        for rec in self:
            domain = []
            if not rec.mass_upload_id.inciso_id and not rec.mass_upload_id.operating_unit_id:
                domain = [('id', 'in', [])]
            if rec.mass_upload_id.inciso_id.id:
                domain = [('inciso_id', '=', rec.mass_upload_id.inciso_id.id)]
            if rec.mass_upload_id.operating_unit_id:
                domain = expression.AND([[
                    ('operating_unit_id', '=', rec.mass_upload_id.operating_unit_id.id)
                ], domain])
            rec.department_id_domain = json.dumps(domain)

    @api.depends('is_reserva_sgh')
    def _compute_descriptor1_domain_id(self):
        domain = [('id', 'in', [])]
        for rec in self:
            if not rec.is_reserva_sgh:
                dsc1Id = self.env['onsc.legajo.budget.item'].sudo().search([]).mapped(
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
            dsc2Id = self.env['onsc.legajo.budget.item'].sudo().search(args).mapped('dsc2Id')
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
            dsc3Id = self.env['onsc.legajo.budget.item'].sudo().search(args).mapped('dsc3Id')
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
            dsc4Id = self.env['onsc.legajo.budget.item'].sudo().search(args).mapped('dsc4Id')
            if dsc4Id:
                domain = [('id', 'in', dsc4Id.ids)]
            rec.descriptor4_domain_id = json.dumps(domain)

    @api.depends('message_error', 'warning_error')
    def _compute_message(self):
        for rec in self:
            items = []
            if rec.message_error:
                items.append(rec.message_error)
            if rec.warning_error:
                items.append(rec.warning_error)
            rec.message = '\n'.join(items)


    @api.onchange('descriptor1_id')
    def onchange_descriptor1(self):
        self.descriptor2_id = False
        self.descriptor3_id = False
        self.descriptor4_id = False

    @api.onchange('descriptor2_id')
    def onchange_descriptor2(self):
        self.descriptor3_id = False
        self.descriptor4_id = False

    @api.onchange('descriptor3_id')
    def onchange_descriptor3(self):
        self.descriptor4_id = False

    def get_fields(self):
        return self._fields

    def find_by_code_name_many2one(self, field, code_field, name_field, value, args=None):
        if args is None:
            args = []
        value = value.strip() if isinstance(value, str) else value
        args = expression.AND([['|', (code_field, '=', value), (name_field, '=', value)], args])
        record = self.env[self._fields[field].comodel_name].sudo().search(args, limit=1)
        if record:
            return record.id
        elif isinstance(value, str) and len(value) == 0:
            return False
        else:
            if field in ['address_location_id']:
                message_error.append(
                    'No se encontró el valor %s en el catálogo de %s para ese valor de Departamento' %
                    (value, self._fields[field].string))
            elif field in ['address_street_id', 'address_street2_id', 'address_street3_id']:
                message_error.append(
                    'No se encontró el valor %s en el catálogo de %s para esa Localidad' % (
                        value, self._fields[field].string))
            else:
                message_error.append(
                    'No se encontró el valor %s en el catálogo de %s' % (value, self._fields[field].string))

    def create_line(self, values):
        return self.create(values)

    def update_line(self, values):
        return self.write(values)

    # flake8: noqa: C901
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
                    values[key] = True if 's' in value.lower() or '1' in value else False
                if field[key].type == 'selection':
                    for selection in self._fields[key].selection:
                        if value == '':
                            values[key] = ''
                            break
                        elif value in selection[0]:
                            values[key] = selection[0]
                            break
                        elif value in selection[1]:
                            values[key] = selection[0]
                            break
                        else:
                            values[key] = False
                    if values[key] is False:
                        raise
            except Exception:
                type_field = ""
                if field[key].type == 'float':
                    type_field = "numérico"
                elif field[key].type == 'integer':
                    type_field = "entero"
                elif field[key].type == 'boolean':
                    type_field = "booleano"
                elif field[key].type == 'selection':
                    selection_values = ''
                    for selection in self._fields[key].selection:
                        selection_values += str(selection[1]) + ', '
                    type_field = ("de selección. Los valores posibles son los siguientes: %s" % selection_values[:-2])

                error.append('El tipo de campo "%s" no es válido. El tipo de campo debe ser %s. ' % (
                    field[key].string, type_field))
                values[key] = False
        error = '\n'.join(error)
        return values, error
