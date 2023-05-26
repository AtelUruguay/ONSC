import binascii
import datetime
import json
import logging
import tempfile
from odoo.exceptions import ValidationError
from odoo import fields, models, api, _, tools
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
    lines_processed_ids = fields.One2many('onsc.legajo.mass.upload.line.alta.vl', 'mass_upload_id',
                                          domain=[('state', '=', 'done')], string='Líneas procesadas')
    state = fields.Selection([('draft', 'Borrador'), ('partially', 'Procesado con Error'), ('done', 'Procesado')],
                             default='draft', string='Estado')
    id_ejecucion = fields.Char(string='ID de ejecución', required=True, readonly=True,
                               states={'draft': [('readonly', False)]})
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

    @api.depends('altas_vl_ids')
    def _compute_altas_vl_count(self):
        for rec in self:
            rec.altas_vl_count = len(rec.altas_vl_ids)

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
        self.operating_unit_id = False

    @api.onchange('document_file')
    def onchange_document_file(self):
        self.line_ids = False

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
                [self.env.ref('onsc_cv_digital_legajo.onsc_legajo_alta_vl_tree').id, 'tree'],
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

    def action_process_excel(self):

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
        LegajoOffice = self.env['onsc.legajo.office']
        LegajoNorm = self.env['onsc.legajo.norm']

        for row_no in range(1, sheet.nrows):
            line = list(map(self.process_value, sheet.row(row_no)))
            global message_error
            message_error = []
            office = LegajoOffice.sudo().search([('programa', '=', line[27]), ('proyecto', '=', line[28])],
                                                limit=1)
            norm_id = LegajoNorm.sudo().search([('anioNorma', '=', line[47]), ('numeroNorma', '=', line[46]),
                                                ('articuloNorma', '=', line[48]), ('tipoNorma', '=', line[45])],
                                               limit=1)
            if not office:
                message_error.append("No se puedo encontrar la oficina con los códigos de programa %s y proyecto %s" % (
                    line[27], line[28]))

            if not norm_id:
                message_error.append(
                    " \nNo se puedo encontrar la norma con los códigos de año %s, número %s, artículo %s y tipo %s" % (
                        line[47], line[46], line[48], line[45]))

            descriptor1_id = MassLine.find_by_code_name_many2one('descriptor1_id', 'code', 'name', line[31])
            descriptor2_id = MassLine.find_by_code_name_many2one('descriptor2_id', 'code', 'name', line[32])
            descriptor3_id = MassLine.find_by_code_name_many2one('descriptor3_id', 'code', 'name', line[33])
            descriptor4_id = MassLine.find_by_code_name_many2one('descriptor4_id', 'code', 'name', line[34])
            budget_item_id = self.get_partida(descriptor1_id, descriptor2_id, descriptor3_id, descriptor4_id)
            if not budget_item_id:
                message_error.append(
                    line.message_error + " \nNo se puedo encontrar la partida con datos de los descriptores")

            values = {
                'nro_line': row_no,
                'mass_upload_id': self.id,
                'document_number': line[0],
                'cv_sex': line[1],
                'birth_date': datetime.datetime.fromordinal(datetime.datetime(1900, 1, 1).toordinal() + line[2] - 2) if
                line[2] else False,
                'document_country_id': MassLine.find_by_code_name_many2one('document_country_id', 'code', 'name',
                                                                           line[3]),
                'marital_status_id': MassLine.find_by_code_name_many2one('marital_status_id', 'code', 'name', line[4]),
                'birth_country_id': MassLine.find_by_code_name_many2one('birth_country_id', 'code', 'name', line[5]),
                'citizenship': line[6],
                'crendencial_serie': line[7],
                'credential_number': line[8],
                'personal_phone': line[9],
                'mobile_phone': line[10],
                'email': line[11],
                'address_state_id': MassLine.find_by_code_name_many2one('address_state_id', 'code', 'name', line[12]),
                'address_location_id': MassLine.find_by_code_name_many2one('address_location_id', 'code', 'name',
                                                                           line[13]),
                'address_street_id': MassLine.find_by_code_name_many2one('address_street_id', 'code', 'street',
                                                                         line[14]),
                'address_street2_id': MassLine.find_by_code_name_many2one('address_street2_id', 'code', 'street',
                                                                          line[15]),
                'address_street3_id': MassLine.find_by_code_name_many2one('address_street3_id', 'code', 'street',
                                                                          line[16]),
                'address_zip': line[17],
                'address_nro_door': line[18],
                'address_is_bis': line[19],
                'address_apto': line[20],
                'address_place': line[21],
                'address_block': line[22],
                'address_sandlot': line[23],
                'date_start': datetime.datetime.fromordinal(datetime.datetime(1900, 1, 1).toordinal() + line[24] - 2) if
                line[24] else False,
                'income_mechanism_id': MassLine.find_by_code_name_many2one('income_mechanism_id', 'code', 'name',
                                                                           line[25]),
                'call_number': line[26],
                'program_project_id': office.id if office else False,
                'is_reserva_sgh': line[29],
                'regime_id': MassLine.find_by_code_name_many2one('regime_id', 'codRegimen', 'descripcionRegimen',
                                                                 line[30]),
                'descriptor1_id': descriptor1_id,
                'descriptor2_id': descriptor2_id,
                'descriptor3_id': descriptor3_id,
                'descriptor4_id': descriptor4_id,
                'nroPuesto': line[35],
                'nroPlaza': line[36],
                'department_id': MassLine.find_by_code_name_many2one('department_id', 'code', 'name', line[37]),
                'security_job_id': MassLine.find_by_code_name_many2one('security_job_id', 'name', 'name', line[38]),
                'occupation_id': MassLine.find_by_code_name_many2one('occupation_id', 'code', 'name', line[39]),
                'date_income_public_administration': datetime.datetime.fromordinal(
                    datetime.datetime(1900, 1, 1).toordinal() + line[40] - 2) if line[40] else False,
                'inactivity_years': line[41],
                'graduation_date': datetime.datetime.fromordinal(
                    datetime.datetime(1900, 1, 1).toordinal() + line[42] - 2) if line[42] else False,
                'contract_expiration_date': datetime.datetime.fromordinal(
                    datetime.datetime(1900, 1, 1).toordinal() + line[43] - 2) if line[
                    43] else False,
                'reason_description': line[44],
                'norm_id': norm_id.id if norm_id else False,
                'resolution_description': line[49],
                'resolution_date': datetime.datetime.fromordinal(
                    datetime.datetime(1900, 1, 1).toordinal() + line[50] - 2) if line[
                    50] else False,
                'resolution_type': line[51],
                'retributive_day_id': MassLine.find_by_code_name_many2one('retributive_day_id', 'codigoJornada',
                                                                          'descripcionJornada', line[52]),
                'additional_information': line[53],
                'message_error': '',
            }
            values, validate_error = MassLine.validate_fields(values)
            if validate_error:
                values['message_error'] = values['message_error'] + '\n' + validate_error

            if message_error:
                values['message_error'] = values['message_error'] + '\n' + '\n'.join(message_error)

            if message_error or validate_error:
                values['state'] = 'error'
                values['message_error'] = 'Información faltante o no cumple validación' + values['message_error']
            else:
                values['message_error'] = ''

            existing_record = MassLine.search([('nro_line', '=', row_no), ('mass_upload_id', '=', self.id)], limit=1)
            if existing_record and existing_record.state != 'done':
                existing_record.update_line(values)
            if not existing_record:
                MassLine.create_line(values)

    def action_process(self):
        if not self.line_ids:
            raise ValidationError(_('No hay líneas para procesar'))

        Partner = self.env['res.partner']
        AltaVL = self.env['onsc.legajo.alta.vl']
        CVDigital = self.env['onsc.cv.digital']
        cv_document_type_id = self.env['onsc.cv.document.type'].sudo().search([('code', '=', 'ci')],
                                                                              limit=1).id or False

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
                    }
                    partner = Partner.create(data_partner)
                partner.update_dnic_values()
                line.write({'first_name': partner.cv_first_name,
                            'second_name': partner.cv_second_name,
                            'first_surname': partner.cv_last_name_1,
                            'second_surname': partner.cv_last_name_2,
                            'name_ci': partner.cv_dnic_full_name,
                            'message_error': '',
                            })
            except Exception as e:
                line.write({'state': 'error', 'message_error': "No se puedo crear el contacto: " + tools.ustr(e)})
                continue
            cv_digital = CVDigital.sudo().search([('partner_id', '=', partner.id)], limit=1)
            try:
                if not cv_digital:
                    CVDigital.create({'partner_id': partner.id,
                                      'personal_phone': line.personal_phone,
                                      'mobile_phone': line.mobile_phone,
                                      'email': line.email,
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
                                      })
                line.write({'message_error': ''})
            except Exception as e:
                line.write({'state': 'error', 'message_error': "No se puedo crear el CV: " + tools.ustr(e)})
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
                'crendencial_serie': line.crendencial_serie,
                'credential_number': line.credential_number,
                'regime_id': line.regime_id.id,
                'descriptor1_id': line.descriptor1_id.id if line.descriptor1_id else False,
                'descriptor2_id': line.descriptor2_id.id if line.descriptor2_id else False,
                'descriptor3_id': line.descriptor3_id.id if line.descriptor3_id else False,
                'descriptor4_id': line.descriptor4_id.id if line.descriptor4_id else False,
                'nroPuesto': line.nroPuesto,
                'nroPlaza': line.nroPlaza,
                'department_id': line.department_id.id if line.department_id else False,
                'security_job_id': line.security_job_id.id if line.security_job_id else False,
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
                'additional_information': line.additional_information,
                'norm_id': line.norm_id.id if line.norm_id else False,
                'call_number': line.call_number,
                'mass_upload_id': self.id,
            }
            alta_vl_id = False
            try:
                alta_vl_id = AltaVL.create(data_alta_vl)
                line.write({'state': 'done'})
                alta_vl_id.with_context({'not_check_attached_document': True}).check_required_fieds_ws4()
            except Exception as e:
                line.write({'state': 'error',
                            'message_error': line.message_error + " \nNo se puedo crear el alta de vínculo laboral: " + tools.ustr(
                                e)})
                if alta_vl_id:
                    alta_vl_id.unlink()
                continue
            try:
                alta_vl_id.action_call_ws4()
            except:
                continue
        if not self.line_ids:
            self.state = 'done'
        else:
            self.state = 'partially'

    def get_partida(self, descriptor1_id, descriptor2_id, descriptor3_id, descriptor4_id):
        args = []
        domain = [('id', 'in', [])]
        if descriptor1_id:
            args = [('dsc1Id', '=', descriptor1_id)]
        if descriptor2_id:
            args = expression.AND([[('dsc2Id', '=', descriptor2_id)], args])

        if descriptor3_id:
            args = expression.AND([[('dsc3Id', '=', descriptor3_id)], args])
        if descriptor4_id:
            args = expression.AND([[('dsc4Id', '=', descriptor4_id)], args])
        return self.env['onsc.legajo.budget.item'].sudo().search(args, limit=1)


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

    mass_upload_id = fields.Many2one('onsc.legajo.mass.upload.alta.vl', string='Carga masiva')
    state = fields.Selection([('draft', 'Borrador'), ('error', 'Procesado con Error'), ('done', 'Procesado')],
                             string='Estado', default='draft')
    message_error = fields.Text(string='Mensaje de error')
    nro_line = fields.Integer(string='Nro de línea')
    first_name = fields.Char(string='Primer nombre')
    second_name = fields.Char(string='Segundo nombre')
    first_surname = fields.Char(string='Primer apellido')
    second_surname = fields.Char(string='Segundo apellido')
    name_ci = fields.Char(string='Nombre en cédula')
    cv_sex = fields.Selection([('male', 'Masculino'), ('feminine', 'Femenino')], u'Sexo')
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

    def get_fields(self):
        return self._fields

    def find_by_code_name_many2one(self, field, code_field, name_field, value):
        value = value.strip() if isinstance(value, str) else value
        record = self.env[self._fields[field].comodel_name].sudo().search(
            ['|', (code_field, '=', value), (name_field, '=', value)], limit=1)
        if record:
            return record.id
        elif len(value) == 0:
            return False
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
                    values[key] = True if 's' in value.lower() or '1' in value else False
                if field[key].type == 'selection':
                    for selection in self._fields[key].selection:
                        if value in selection[0]:
                            values[key] = selection[0]
                            break
                        elif value in selection[1]:
                            values[key] = selection[0]
                            break
                        elif value == '':
                            values[key] = False
                            break
                        else:
                            values[key] = False
                    if not values[key]:
                        raise
            except Exception as e:
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
