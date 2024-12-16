# -*- coding: utf-8 -*-
import datetime
import logging

from email_validator import EmailNotValidError, validate_email

from odoo import models, fields, tools, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

CV_SEX = [('male', 'Masculino'), ('feminine', 'Femenino')]


class ONSCLegajoStagingWS7(models.Model):
    _name = 'onsc.legajo.staging.ws7'
    _description = 'Staging WS7'
    _rec_name = 'key'
    _order = 'fecha_aud ASC'

    info_income = fields.Char(string='Data de origen', )

    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora")

    key = fields.Char(string='Combinación única (fecha_aud-doc-mov-tipo_mov)', index=True)
    doc = fields.Char(string='doc', index=True)
    primer_nombre = fields.Char(string='primer_nombre')
    segundo_nombre = fields.Char(string='segundo_nombre')
    primer_ap = fields.Char(string='primer_ap')
    segundo_ap = fields.Char(string='segundo_ap')
    fecha_nac = fields.Date(string='fecha_nac')
    fecha_ing_adm = fields.Date(string='fecha_ing_adm')
    cod_mot_baja = fields.Char(string='cod_mot_baja')
    fecha_vig = fields.Date(string='fecha_vig')
    fecha_aud = fields.Datetime(string='fecha_aud')
    mov = fields.Char(string='mov', index=True)
    tipo_mov = fields.Char(string='tipo_mov', index=True)
    pdaId = fields.Char(string='pdaId', index=True)
    movimientoPadreId = fields.Char(string='movimientoPadreId', index=True)
    fecha_desde_vinc = fields.Char(string='fecha_desde_vinc')
    idPuesto = fields.Char(string='idPuesto')
    nroPlaza = fields.Char(string='nroPlaza')
    secPlaza = fields.Char(string='secPlaza')
    programa = fields.Char(string='programa')
    proyecto = fields.Char(string='proyecto')
    aniosInactividad = fields.Char(string='aniosInactividad')
    fechaGraduacion = fields.Date(string='fechaGraduacion')

    inciso = fields.Char(string='inciso')
    ue = fields.Char(string='ue')
    tipo_doc = fields.Char(string='tipo_doc')
    cod_pais = fields.Char(string='cod_pais')
    raza = fields.Char(string='raza')
    cod_mecing = fields.Char(string='cod_mecing')
    comi_reg = fields.Char(string='comi_reg')
    cod_desc1 = fields.Char(string='cod_desc1')
    cod_desc2 = fields.Char(string='cod_desc2')
    cod_desc3 = fields.Char(string='cod_desc3')
    cod_desc4 = fields.Char(string='cod_desc4')
    comi_inciso_dest = fields.Char(string='comi_inciso_dest')
    comi_ue_dest = fields.Char(string='comi_ue_dest')
    comi_mot_ext = fields.Char(string='comi_mot_ext')
    jornada_ret = fields.Char(string='jornada_ret')
    sexo = fields.Char(string='sexo')
    codigoEstadoCivil = fields.Char(string='codigoEstadoCivil')
    cod_reg = fields.Char(string='cod_reg')

    cv_document_type_id = fields.Many2one('onsc.cv.document.type', u'Tipo de documento')  # tipo_doc
    country_id = fields.Many2one('res.country', u'País')  # cod_pais
    race_id = fields.Many2one("onsc.cv.race", string=u"Raza")  # raza
    income_mechanism_id = fields.Many2one('onsc.legajo.income.mechanism', string='Mecanismo de ingreso')  # cod_mecing
    regime_id = fields.Many2one('onsc.legajo.regime', string='Régimen')  # cod_reg
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor1')  # cod_desc1
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor2')  # cod_desc2
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor3')  # cod_desc3
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor4')  # cod_desc4

    comision_inciso_dest_id = fields.Many2one('onsc.catalog.inciso', string='Inciso destino')  # comi_inciso_dest
    comision_operating_unit_dest_id = fields.Many2one(
        "operating.unit",
        string="Unidad ejecutora destino")  # comi_ue_dest
    extinction_commission_id = fields.Many2one(
        "onsc.legajo.reason.extinction.commission",
        string="Motivo de extinción de la comisión")  # comi_mot_ext
    commission_regime_id = fields.Many2one(
        'onsc.legajo.commission.regime',
        string='Régimen comisión')  # comi_reg
    retributive_day_id = fields.Many2one('onsc.legajo.jornada.retributiva', string='Jornada retributiva')  # jornada_ret

    budget_item_id = fields.Many2one('onsc.legajo.budget.item', string='Partida presupuestal')
    program_project_id = fields.Many2one('onsc.legajo.office', string='Oficina')

    # CV
    gender_id = fields.Many2one("onsc.cv.gender", string=u"Género")  # sexo
    cv_sex = fields.Selection(CV_SEX, u'Sexo')
    marital_status_id = fields.Many2one("onsc.cv.status.civil", string="Estado civil")  # codigoEstadoCivil

    state = fields.Selection(
        string='Estado',
        selection=[
            ('in_process', 'En proceso'),
            ('processed', 'Procesado'),
            ('error', 'Error'),
            ('na', 'No aplica')
        ], default='in_process')
    checked_bysystem = fields.Boolean(string='Analizada por el proceso')
    should_disable_form_edit = fields.Boolean(string="Deshabilitar botón de editar",
                                              compute='_compute_should_disable_form_edit')

    log = fields.Text(string='Log')

    def init(self):
        self._cr.execute("""CREATE INDEX IF NOT EXISTS onsc_legajo_staging_ws7_recordset_unique
        ON onsc_legajo_staging_ws7 (tipo_mov,"pdaId")""")

    @api.onchange('inciso_id')
    def onchange_inciso_id(self):
        self.operating_unit_id = False

    def _compute_should_disable_form_edit(self):
        for record in self:
            record.should_disable_form_edit = record.state not in ['error']

    def button_in_process(self):
        if len(self) == 0:
            self = self.search([('state', '=', 'error')])
        for record in self.filtered(lambda x: x.state not in ['na', 'processed']):
            record._set_mapped_vals()

    def _set_mapped_vals(self):
        RetributiveDay = self.env['onsc.legajo.jornada.retributiva'].suspend_security()
        BudgetItem = self.env['onsc.legajo.budget.item'].suspend_security()
        log_list = []

        vals = self._set_mapped_vals_get_logs(log_list)

        budget_item_args = []
        descriptor1_id = vals.get('descriptor1_id')
        descriptor2_id = vals.get('descriptor2_id')
        descriptor3_id = vals.get('descriptor3_id')
        descriptor4_id = vals.get('descriptor4_id')
        if descriptor1_id:
            budget_item_args.append(('dsc1Id', '=', descriptor1_id))
        if descriptor2_id:
            budget_item_args.append(('dsc2Id', '=', descriptor2_id))
        if descriptor3_id:
            budget_item_args.append(('dsc3Id', '=', descriptor3_id))
        if descriptor4_id:
            budget_item_args.append(('dsc4Id', '=', descriptor4_id))

        budget_item = BudgetItem.search(budget_item_args, limit=1)
        if not budget_item:
            log_list.append(_('No se encontró una Partida para la combinación de descriptores'))

        # OFICINA Y JORNADA RETRIBUTIVA
        retributive_day = RetributiveDay.search([
            ('codigoJornada', '=', self.jornada_ret),
            ('office_id.proyecto', '=', self.proyecto),
            ('office_id.programa', '=', self.programa),
            ('office_id.inciso', '=', vals.get('inciso_id')),
            ('office_id.unidadEjecutora', '=', vals.get('operating_unit_id'))
        ], limit=1)
        retributive_day_id = retributive_day.id
        office_id = retributive_day.office_id.id

        if not retributive_day_id:
            log_list.append(_('No se encontró la Jornada Retributiva para esa combinación de '
                              'Oficina (Inciso, UE, Programa, Proyecto)'))

        if len(log_list) > 0:
            state = 'error'
            log = ', '.join(log_list)
        else:
            state = 'in_process'
            log = False

        vals.update({
            'state': state,
            'log': log,
            'budget_item_id': budget_item.id,
            'retributive_day_id': retributive_day_id,
            'program_project_id': office_id,
        })
        self.write(vals)

    def _set_mapped_vals_get_logs(self, log_list):
        BaseUtils = self.env['onsc.base.utils'].sudo()
        Inciso = self.env['onsc.catalog.inciso'].suspend_security()
        OperatingUnit = self.env['operating.unit'].suspend_security()
        DocType = self.env['onsc.cv.document.type'].suspend_security()
        Country = self.env['res.country'].suspend_security()
        Race = self.env['onsc.cv.race'].suspend_security()
        IncomeMechanism = self.env['onsc.legajo.income.mechanism'].suspend_security()
        Regime = self.env['onsc.legajo.regime'].suspend_security()
        Descriptor1 = self.env['onsc.catalog.descriptor1'].suspend_security()
        Descriptor2 = self.env['onsc.catalog.descriptor2'].suspend_security()
        Descriptor3 = self.env['onsc.catalog.descriptor3'].suspend_security()
        Descriptor4 = self.env['onsc.catalog.descriptor4'].suspend_security()
        Gender = self.env['onsc.cv.gender'].suspend_security()
        MaritalStatus = self.env['onsc.cv.status.civil'].suspend_security()

        vals = {}
        if self.inciso and not self.inciso_id:
            inciso_id = BaseUtils._get_catalog_id(Inciso, 'budget_code', self, 'inciso', log_list)
        else:
            inciso_id = self.inciso_id.id
        vals.update({'inciso_id': inciso_id})
        if self.ue and not self.operating_unit_id:
            operating_unit_id = OperatingUnit.search([('budget_code', '=', str(self.ue)),
                                                      ('inciso_id', '=', inciso_id)], limit=1).id
        else:
            operating_unit_id = self.operating_unit_id.id
        if not operating_unit_id:
            log_list.append(_('No se encontró en el catálogo Unidad Ejecutora el valor self.ue'))
        vals.update({'operating_unit_id': operating_unit_id})
        if self.tipo_doc and not self.cv_document_type_id:
            cv_document_type_id = BaseUtils._get_catalog_id(DocType, 'code_other', self, 'tipo_doc', log_list)
        else:
            cv_document_type_id = self.cv_document_type_id.id
        vals.update({'cv_document_type_id': cv_document_type_id})
        if self.cod_pais and not self.country_id:
            country_id = BaseUtils._get_catalog_id(Country, 'code_rve', self, 'cod_pais', log_list)
        else:
            country_id = self.country_id.id
        vals.update({'country_id': country_id})
        if self.raza and not self.race_id:
            race_id = BaseUtils._get_catalog_id(Race, 'code', self, 'raza', log_list)
        else:
            race_id = self.race_id.id
        vals.update({'race_id': race_id})
        if self.cod_reg and not self.regime_id:
            regime_id = BaseUtils._get_catalog_id(Regime, 'codRegimen', self, 'cod_reg', log_list)
        else:
            regime_id = self.regime_id.id
        vals.update({'regime_id': regime_id})
        if self.cod_desc1 and not self.descriptor1_id:
            descriptor1_id = BaseUtils._get_catalog_id(Descriptor1, 'description', self, 'cod_desc1', log_list)
        else:
            descriptor1_id = self.descriptor1_id.id
        vals.update({'descriptor1_id': descriptor1_id})
        if self.cod_desc2 and not self.descriptor2_id:
            descriptor2_id = BaseUtils._get_catalog_id(Descriptor2, 'code', self, 'cod_desc2', log_list)
        else:
            descriptor2_id = self.descriptor2_id.id
        vals.update({'descriptor2_id': descriptor2_id})
        if self.cod_desc3 and not self.descriptor3_id:
            descriptor3_id = BaseUtils._get_catalog_id(Descriptor3, 'code', self, 'cod_desc3', log_list)
        else:
            descriptor3_id = self.descriptor3_id.id
        vals.update({'descriptor3_id': descriptor3_id})
        if self.cod_desc4 and not self.descriptor4_id:
            descriptor4_id = BaseUtils._get_catalog_id(Descriptor4, 'code', self, 'cod_desc4', log_list)
        else:
            descriptor4_id = self.descriptor4_id.id
        vals.update({'descriptor4_id': descriptor4_id})
        if self.sexo and not self.cv_sex:
            cv_sex = self.sexo == '2' and 'feminine' or 'male'
        else:
            cv_sex = self.cv_sex
        vals.update({'cv_sex': cv_sex})
        if self.codigoEstadoCivil and not self.marital_status_id:
            marital_status_id = BaseUtils._get_catalog_id(MaritalStatus, 'code', self, 'codigoEstadoCivil', log_list)
        else:
            marital_status_id = self.marital_status_id.id
        vals.update({'marital_status_id': marital_status_id})
        return vals

    # flake8: noqa: C901
    def process_staging(self, ids=False, limit=0, delay_to_analyze_in_days=0):
        datetime_start = fields.Datetime.now()
        Contract = self.env['hr.contract'].sudo()

        analyze_date_from = self.env.user.company_id.ws7_date_from - datetime.timedelta(days=delay_to_analyze_in_days)

        args = [('state', 'in', ['in_process', 'na']), ('checked_bysystem', '=', False)]
        if ids:
            args.append(('id', 'in', ids))

        current_pointer = 0
        records = self.search(args)
        for record in records:
            try:
                with self._cr.savepoint():
                    if limit:
                        current_pointer += 1
                    if current_pointer > limit:
                        return
                    if record.mov in ['ALTA', 'BAJA', 'COMISION', 'CAMBIO_DEPTO']:
                        self._check_movement(Contract, record)
                    elif record.mov in ['ASCENSO', 'TRANSFORMA', 'REESTRUCTURA',
                                        'TRANSFORMA_REDUE'] and record.tipo_mov == 'BAJA':
                        self.set_asc_transf_reest(Contract, record)
                    elif record.mov in ['RESERVA'] and record.tipo_mov == 'ALTA':
                        self.set_reserva(Contract, record)
                    elif record.mov in ['DESRESERVA'] and record.tipo_mov == 'BAJA':
                        self.set_desreserva(Contract, record)
                    elif record.mov in ['RENOVACION'] and record.tipo_mov == 'ALTA':
                        self.set_renovacion(Contract, record)
                    elif record.mov in ['CORRECCION_ASCENSO'] and record.tipo_mov == 'ALTA':
                        self.set_correccion_ascenso(Contract, record)
                    elif record.mov in ['CORRECCION_ALTA'] and record.tipo_mov == 'ALTA':
                        self.set_correccion_alta(Contract, record)
                    elif record.mov in ['CORRECCION_BAJA'] and record.tipo_mov == 'ALTA':
                        self.set_correccion_baja(Contract, record)
                    elif record.mov in ['CAMBIO_JORNADA']:
                        self.set_cambio_jornada(Contract, record)
                    elif record.mov in ['MODFU']:
                        self.set_modif_funcionario(Contract, record)

            except Exception as e:
                record.write({
                    'state': 'error',
                    'log': 'Error: %s' % tools.ustr(e)})

        self._send_ws7_processing_notification(records, datetime_start, analyze_date_from)

    def _check_movement(self, Contract, record):
        """
        Chequea que el movimiento exista en el sistema
        :param Contract: Recomendado: self.env['hr.contract'].sudo()
        :param operation: Recordset de la operacion
        :param error: Recordset del log de error
        """
        exist_contract = self._get_contract(
            Contract,
            record,
            use_simple_search=True,
            use_search_count=True
        )
        vals = {'checked_bysystem': True}
        if not exist_contract:
            vals['log'] = _('Contrato no encontrado')
        record.write(vals)

    def set_asc_transf_reest(self, Contract, record):
        records = record

        operation_dict = {
            'ASCENSO': 'Ascenso',
            'TRANSFORMA': 'Transformación',
            'REESTRUCTURA': 'Reestructuración'
        }

        # ENCUENTRA EL CONTRATO VIGENTE
        contract = self._get_contract(Contract, record, legajo_state_operator='!=', legajo_state='baja')
        if len(contract) == 0:
            record.write({
                'state': 'error',
                'log': _('Contrato no encontrado')})
            return

        second_movement = self._get_second_movement(record, 'ALTA')
        if not second_movement:
            record.write({
                'state': 'error',
                'log': _('Segundo movimiento no encontrado o en estado Error')})
            return

        # CASO CONTRACTO ACTUAL COMISION ENTRANTE Y CONTRATO ORIGINAL COMISION SALIENTE
        incoming_contract = self.env['hr.contract'].search([
            ('cs_contract_id', '=', contract.id),
            ('legajo_state', '=', 'incoming_commission')], limit=1)

        state_square_id = self.env.ref('onsc_legajo.onsc_legajo_o')
        
        if record.mov == 'ASCENSO':
            movement_description = self.env.user.company_id.ws7_new_ascenso_reason_description
        elif record.mov in ['TRANSFORMA','TRANSFORMA_REDUE']:
            movement_description = self.env.user.company_id.ws7_new_transforma_reason_description
        elif record.mov == 'REESTRUCTURA':
            movement_description = self.env.user.company_id.ws7_new_reestructura_reason_description
        else:
            movement_description = False

        if contract.legajo_state == 'outgoing_commission' and incoming_contract:
            # A (saliente): contract
            # B (entrante): incoming_contract
            # CASO CONTRATO A SALIENTE Y ENCUENTRA UN CONTRATO B ENTRANTE

            # si el movimiento es de la misma jerarquia inciso/ue del contrato entrante
            same_ue = second_movement.inciso_id.id == incoming_contract.inciso_id.id and \
                      second_movement.operating_unit_id.id == incoming_contract.operating_unit_id.id

            # GENERA NUEVO CONTRATO (C)

            new_contract_status = same_ue and 'active' or 'outgoing_commission'
            new_contract = self._get_contract_copy(
                contract,
                second_movement, new_contract_status,
                state_square_id=state_square_id.id,
                movement_description=operation_dict.get(record.mov),
            )
            self._copy_jobs(contract, new_contract, operation_dict.get(record.mov))

            if record.mov == 'ASCENSO':
                causes_discharge = self.env.user.company_id.ws7_ascenso_causes_discharge_id
            elif record.mov == 'TRANSFORMA':
                causes_discharge = self.env.user.company_id.ws7_transforma_causes_discharge_id
            else:
                causes_discharge = self.env.user.company_id.ws7_reestructura_causes_discharge_id

            # DESACTIVA EL CONTRATO SALIENTE (A)
            contract.with_context(no_check_write=True).deactivate_legajo_contract(
                second_movement.fecha_vig + datetime.timedelta(days=-1),
                legajo_state='baja',
                eff_date=fields.Date.today(),
            )

            # SI ES UN MOVIMIENTO PARA EL MISMO INCISO Y UE SE DESACTIVA TAMBIEN EL B
            if same_ue:
                incoming_contract.with_context(no_check_write=True).deactivate_legajo_contract(
                    second_movement.fecha_vig + datetime.timedelta(days=-1),
                    legajo_state='baja',
                    eff_date=fields.Date.today()
                )
                incoming_contract.write({
                    'causes_discharge_id': causes_discharge.id,
                })

            contract.write({
                'causes_discharge_id': causes_discharge.id,
                'cs_contract_id': new_contract.id
            })

            if incoming_contract.legajo_state == 'incoming_commission' and new_contract.legajo_state == 'outgoing_commission':
                incoming_contract.write({
                    'eff_date': fields.Date.today(),
                    'cs_contract_id': new_contract.id
                })
        else:
            new_contract = self._get_contract_copy(
                contract,
                second_movement,
                state_square_id=state_square_id.id,
                movement_description=movement_description
            )
            self._copy_jobs(contract, new_contract, operation_dict.get(record.mov))

            if new_contract.operating_unit_id != contract.operating_unit_id:
                # DESACTIVA EL CONTRATO
                contract.with_context(no_check_write=True, is_copy_job=False).deactivate_legajo_contract(
                    second_movement.fecha_vig + datetime.timedelta(days=-1),
                    legajo_state='baja',
                    eff_date=fields.Date.today()
                )
            else:
                # DESACTIVA EL CONTRATO
                contract.with_context(no_check_write=True).deactivate_legajo_contract(
                    second_movement.fecha_vig + datetime.timedelta(days=-1),
                    legajo_state='baja',
                    eff_date=fields.Date.today()
                )
            if record.mov == 'ASCENSO':
                causes_discharge = self.env.user.company_id.ws7_ascenso_causes_discharge_id
            elif record.mov in ['TRANSFORMA', 'TRANSFORMA_REDUE']:
                causes_discharge = self.env.user.company_id.ws7_transforma_causes_discharge_id
            else:
                causes_discharge = self.env.user.company_id.ws7_reestructura_causes_discharge_id

            contract.write({
                'eff_date': fields.Date.today(),
                'cs_contract_id': new_contract.id,
                'causes_discharge_id': causes_discharge.id,
            })

            # FIXME la desactivacion posterior lo saca de manager y por la secuencia de los pasos no sabe volver a ponerlo
            excluded_descriptor1_ids = self.env.company.descriptor1_ids.ids
            for job in new_contract.job_ids:
                cond2 = job.is_uo_manager and job.start_date <= fields.Date.today()
                if cond2 and not job.department_id.manager_id:
                    job.department_id.suspend_security().write({
                        'manager_id': job.employee_id.id,
                        'is_manager_reserved': False
                    })
            # self._check_contract_data(new_contract)

        records |= second_movement
        records.write({'state': 'processed'})

    def set_correccion_ascenso(self, Contract, record):
        records = record
        active_contract = self._get_contract(Contract, record, legajo_state_operator='=', legajo_state='active')
        if len(active_contract) == 0:
            record.write({
                'state': 'error',
                'log': _('Contrato no encontrado')})
            return

        second_movement = self._get_second_movement(record, 'BAJA')
        if not second_movement:
            record.write({
                'state': 'error',
                'log': _('Segundo movimiento no encontrado o en estado Error')})
            return
        records |= second_movement

        if active_contract.cs_contract_id and active_contract.cs_contract_id.legajo_state == 'baja':
            baja_contract = active_contract.cs_contract_id
        else:
            baja_contract = Contract.search([
                ('cs_contract_id', '=', active_contract.id),
                ('legajo_state', '=', 'baja')], limit=1)
        if len(baja_contract) == 0:
            record.write({
                'state': 'error',
                'log': _('Contrato de baja no encontrado')})
            return
        self._check_valid_eff_date(baja_contract, fields.Date.today())
        self._check_valid_eff_date(active_contract, fields.Date.today())
        baja_end_date = baja_contract.date_end
        active_start_date = active_contract.date_start
        baja_contract.write({
            'date_end': second_movement.fecha_vig + datetime.timedelta(days=-1),
            'eff_date': fields.Date.today(),
        })
        active_contract.write({
            'date_start': second_movement.fecha_vig,
            'eff_date': fields.Date.today(),
        })
        baja_contract.job_ids.filtered(lambda x: x.end_date and x.end_date == baja_end_date).write({
            'end_date': second_movement.fecha_vig + datetime.timedelta(days=-1),
        })
        active_contract.job_ids.filtered(
            lambda x: x.start_date and x.start_date == active_start_date).with_context(
            no_check_write=True).update_start_date(second_movement.fecha_vig)
        records.write({'state': 'processed'})

    def set_correccion_alta(self, Contract, record):
        records = record
        second_movement = self._get_second_movement(record, 'BAJA')
        if not second_movement:
            record.write({
                'state': 'error',
                'log': _('Segundo movimiento no encontrado o en estado Error')})
            return
        records |= second_movement

        active_contract = self._get_contract(Contract, second_movement, legajo_state_operator='=',
                                             legajo_state='active')
        if len(active_contract) == 0:
            second_movement.write({
                'state': 'error',
                'log': _('Contrato no encontrado')})
            return
        self._check_valid_eff_date(active_contract, fields.Date.today())
        active_start_date = active_contract.date_start
        active_contract.write({
            'date_start': second_movement.fecha_vig,
            'eff_date': fields.Date.today(),
        })
        active_contract.job_ids.filtered(
            lambda x: x.start_date and x.start_date == active_start_date).with_context(
            no_check_write=True).update_start_date(second_movement.fecha_vig)
        records.write({'state': 'processed'})

    def set_correccion_baja(self, Contract, record):
        records = record
        second_movement = self._get_second_movement(record, 'BAJA')
        if not second_movement:
            record.write({
                'state': 'error',
                'log': _('Segundo movimiento no encontrado o en estado Error')})
            return
        records |= second_movement

        contract = self._get_contract(Contract, second_movement, legajo_state_operator='=', legajo_state='baja')
        if len(contract) == 0:
            second_movement.write({
                'state': 'error',
                'log': _('Contrato no encontrado')})
            return
        self._check_valid_eff_date(contract, fields.Date.today())
        contract.write({
            'date_end': second_movement.fecha_vig,
            'eff_date': fields.Date.today(),
        })
        contract.job_ids.filtered(lambda x: x.end_date and x.end_date == second_movement.fecha_vig).write({
            'end_date': second_movement.fecha_vig,
        })
        records.write({'state': 'processed'})

    def set_reserva(self, Contract, record):
        records = record
        contract = self._get_contract(Contract, record, legajo_state_operator='=', legajo_state='active')
        if len(contract) == 0:
            record.write({
                'state': 'error',
                'log': _('Contrato no encontrado')})
            return
        contract.with_context(no_check_write=True).deactivate_legajo_contract(
            record.fecha_vig + datetime.timedelta(days=-1),
            legajo_state='reserved',
            eff_date=fields.Date.today()
        )
        self._contract_end_role_assignments(
            contract,
            record.fecha_vig + datetime.timedelta(days=-1), operation='Reserva')
        records.write({'state': 'processed'})

    def set_desreserva(self, Contract, record):
        records = record
        contract = self._get_contract(Contract, record, legajo_state_operator='=', legajo_state='reserved')
        if len(contract) == 0:
            record.write({
                'state': 'error',
                'log': _('Contrato no encontrado')})
            return
        contract.with_context(no_check_write=True).activate_legajo_contract(
            legajo_state='active',
            eff_date=fields.Date.today())
        records.write({'state': 'processed'})

    def set_renovacion(self, Contract, record):
        records = record
        contract = self._get_contract(Contract, record, legajo_state_operator='=', legajo_state='active')
        if len(contract) == 0:
            record.write({
                'state': 'error',
                'log': _('Contrato no encontrado')})
            return
        self._check_valid_eff_date(contract, fields.Date.today())
        contract.write({
            'contract_expiration_date': record.fecha_vig,
            'eff_date': fields.Date.today(),
        })
        records.write({'state': 'processed'})

    def set_cambio_jornada(self, Contract, record):
        records = record
        contract = self._get_contract(Contract, record, legajo_state_operator='=', legajo_state='active')
        if len(contract) == 0:
            record.write({
                'state': 'error',
                'log': _('Contrato no encontrado')})
            return
        self._check_valid_eff_date(contract, fields.Date.today())
        contract.write({
            'retributive_day_id': record.retributive_day_id.id,
            'eff_date': fields.Date.today(),
        })
        records.write({'state': 'processed'})

    def set_modif_funcionario(self, Contract, record):
        contract = self._get_contract(Contract, record, legajo_state_operator='!=', legajo_state='baja')
        if len(contract) == 0:
            record.write({
                'state': 'error',
                'log': _('Contrato no encontrado')})
            return
        if not record.aniosInactividad.isdigit():
            record.write({
                'state': 'error',
                'log': _('Valor inválido para aniosInactividad')})
            return
        contract.legajo_id.suspend_security().write({
            'public_admin_inactivity_years_qty': int(record.aniosInactividad),
            'public_admin_entry_date': record.fecha_ing_adm,
        })
        self._check_valid_eff_date(contract, fields.Date.today())
        if record.fechaGraduacion:
            contract.suspend_security().write({
                'eff_date': fields.Date.today(),
                'graduation_date': str(record.fechaGraduacion),
            })
        self._set_modif_funcionario_extras(contract, record)
        record.write({'state': 'processed'})

    def _set_modif_funcionario_extras(self, contract, record):
        return True

    def _get_second_movement(self, operation, tipo_mov):
        """
        Retorna movimiento de contrapartida de la lista de movimientos devueltos por el WS
        :param operation: Recordset de la operacion
        :param response: Listado de recordsets devueltos por el WS
        :param tipo_mov: Tipo de movimiento contra el que se compara
        :return: Recordset secundario O False
        """

        return self.search([
            ('mov', '=', operation.mov),
            ('movimientoPadreId', '=', operation.movimientoPadreId),
            ('tipo_mov', '=', tipo_mov),
            ('doc', '=', operation.doc),
            ('state', '=', 'in_process')
        ], limit=1)

    def _get_contract(
            self,
            Contract,
            record,
            legajo_state_operator=False,
            legajo_state=False,
            use_simple_search=False,
            use_search_count=False):
        """
        Retorna contrato que cumple con los parametros de busqueda del movimiento
        :param Contract: Recomendado: self.env['hr.contract'].sudo()
        :param operation: Recordset de la operacion
        :param legajo_state_operator: Operador para buscar por estado de legajo
        :param legajo_state: Estado de legajo deseado
        :param use_search_count: True si se desea usar search_count  y no search
        :return Contract: Recordset o si el Contrato fue encontrado

        # TODO
        # ('emissor_country_id.code_rve', '=', str(operation.cod_pais)),
        # ('document_type_id.code', '=', str(tipo_doc)),

        no coincide con lo que estamos manejando
        """
        args = [
            ('position', '=', str(record.idPuesto)),
            ('workplace', '=', record.nroPlaza),
            ('sec_position', '=', record.secPlaza),
            ('nro_doc', '=', str(record.doc)),
        ]
        if legajo_state_operator:
            args.append(('legajo_state', legajo_state_operator, legajo_state))
        if not use_simple_search:
            args.extend([
                ('inciso_id', '=', record.inciso_id.id),  #
                ('operating_unit_id', '=', record.operating_unit_id.id),  #
            ])
        if use_search_count:
            return Contract.search_count(args)
        return Contract.search(args, limit=1)

    def _get_contract_copy(self, 
            contract, 
            record, 
            legajo_state='active', 
            link_tocontract=False, 
            state_square_id=False,
            movement_description=False
        ):
        """
        Duplica el contrato aplicando los cambios de la operacion
        :param contract: Recordset de contrato
        :param record: Recordset de la operacion
        :param error: Recordset del log de error
        :return: Recordset de contrato

        # TODO
        si no estan todos los descriptores?
        de todos los juegos cuales pasamos? ej:
        cod_reg : hay que verificarlo?
        inciso?
        ue?
        """
        inciso = record.inciso_id
        operating_unit = record.operating_unit_id
        descriptor1 = record.descriptor1_id
        descriptor2 = record.descriptor2_id
        descriptor3 = record.descriptor3_id
        descriptor4 = record.descriptor4_id
        regime = record.regime_id

        vals = {
            'employee_id': contract.employee_id.id,
            'inciso_id': inciso.id,
            'operating_unit_id': operating_unit.id,
            'date_start': record.fecha_vig,
            'eff_date': fields.Date.today(),
            'date_end': False,
            'legajo_state': legajo_state,
            'descriptor1_id': descriptor1.id,
            'descriptor2_id': descriptor2.id,
            'descriptor3_id': descriptor3.id,
            'descriptor4_id': descriptor4.id,
            'income_mechanism_id': contract.income_mechanism_id.id,
            'retributive_day_id': record.retributive_day_id.id,
            'regime_id': regime.id,
            'position': str(record.idPuesto),
            'workplace': str(record.nroPlaza),
            'sec_position': str(record.secPlaza),
            'program': str(record.programa),
            'project': str(record.proyecto),
            # 'state_square_id': contract.state_square_id.id,
            'legajo_state_id': contract.legajo_state_id.id,
            'wage': contract.wage
        }
        if state_square_id:
            vals['state_square_id'] = state_square_id
        else:
            vals['state_square_id'] = contract.state_square_id.id
        if link_tocontract:
            vals['cs_contract_id'] = contract.id
        if movement_description:
            vals['reason_description'] = movement_description
        new_contract = self.env['hr.contract'].suspend_security().create(vals)
        return new_contract

    def _copy_jobs(self, source_contract, target_contract, operation='ws7'):
        """
        :param source_contract: Recordset de contrato
        :param target_contract: Recordset de contrato
        :param operation: Recordset de la operacion
        :return: Nuevos puestos
        Fecha hasta abierto o Fecha hasta posterior al día de hoy
        O
        Fecha desde anterior a la Fecha de inicio del Contrato
        """
        jobs = self.env['hr.job']
        if target_contract.operating_unit_id != source_contract.operating_unit_id:
            self._contract_end_role_assignments(source_contract, target_contract.date_start, operation=operation)
            return jobs
        for job_id in source_contract.job_ids.filtered(lambda x:
                                                       (x.end_date is False or x.end_date >= fields.Date.today())
                                                       and x.start_date <= target_contract.date_start):
            new_job = self.env['hr.job'].suspend_security().create_job(
                target_contract,
                job_id.department_id,
                target_contract.date_start,
                job_id.security_job_id,
                is_uo_manager=job_id.is_uo_manager,
                extra_security_roles=job_id.role_extra_ids,
                source_job=job_id)

            self._copy_role_assignments(target_contract, job_id, new_job, operation=operation)
            self._copy_jobs_update_new_job_data(job_id, new_job)
            jobs |= new_job
        return jobs

    def _copy_role_assignments(self, target_contract, job, new_job, operation='ws7'):
        RoleAssignment = self.env['onsc.legajo.job.role.assignment'].suspend_security()
        for role_assignment_id in job.role_assignment_ids:
            if role_assignment_id.date_end is False or role_assignment_id.date_end > target_contract.date_start:
                RoleAssignment.with_context(no_check_write=True).create({
                    'job_id': new_job.id,
                    'role_assignment_id': role_assignment_id.role_assignment_id.id,
                    'date_start': target_contract.date_start,
                    'date_end': role_assignment_id.date_end,
                    'role_assignment_file': role_assignment_id.role_assignment_file,
                    'role_assignment_filename': role_assignment_id.role_assignment_filename
                })
                role_assignment_id.suspend_security().with_context(no_check_write=True).write({
                    'date_end': target_contract.date_start,
                })
        job._message_log(body=_('Se finaliza la Asignación de funciones por notificación de %s' % (operation)))

    def _contract_end_role_assignments(self, contract, date_end=False, operation='ws7'):
        TransRoleAssignment = self.env['onsc.legajo.role.assignment'].suspend_security()
        _date_end = date_end or contract.date_end
        for job_id in contract.suspend_security().job_ids:
            role_assignment = job_id.role_assignment_ids.role_assignment_id
            if role_assignment.state == 'confirm':
                role_assignment.with_context(no_check_write=True, ws7_operation=operation).write({
                    'date_end': _date_end,
                })

    def _copy_jobs_update_new_job_data(self, source_job, new_job):
        # THINKING EXTENDABLE
        return True

    def _check_valid_eff_date(self, contract, eff_date):
        if isinstance(eff_date, str):
            _eff_date = fields.Date.from_string(eff_date)
        else:
            _eff_date = eff_date
        if contract.eff_date and contract.eff_date > _eff_date:
            raise ValidationError(_("No se puede modificar la historia del contrato para la fecha enviada."))

    def get_followers_mails(self):
        followers_emails = []
        emails = self.env.user.company_id.ws7_email_list
        for email in emails.split(','):
            try:
                validate_email(email.strip())
                followers_emails.append(email)
            except EmailNotValidError:
                # Si el email no es válido, se captura la excepción
                _logger.info(_("Mail de Contacto no válido: %s") % email)
        return ','.join(followers_emails)

    def _send_ws7_processing_notification(self, records, datetime_start=False, analyze_date_from=False):
        tz_delta = self.env['ir.config_parameter'].sudo().get_param('server_timezone_delta')

        process_qty = len(records.filtered(lambda x: x.state in ['processed']))
        error_qty = len(records.filtered(lambda x: x.state in ['error']))
        na_no_contract_qty = len(records.filtered(lambda x: x.state in ['na'] and x.log == 'Contrato no encontrado'))
        na_qty = len(records.filtered(lambda x: x.state in ['na']))
        in_process_qty = len(records.filtered(lambda x: x.state in ['in_process']))
        total_qty = len(records)
        sorted_records = sorted(records, key=lambda r: (r.fecha_aud))
        date_from = sorted_records[0].fecha_aud if sorted_records else None
        if date_from:
            date_from += datetime.timedelta(hours=int(tz_delta))
        date_to = sorted_records[-1].fecha_aud if sorted_records else None
        if date_to:
            date_to += datetime.timedelta(hours=int(tz_delta))
        datetime_start = datetime_start or fields.Datetime.now()
        datetime_start += datetime.timedelta(hours=int(tz_delta))
        today = fields.Datetime.from_string(fields.Datetime.now())
        today += datetime.timedelta(hours=int(tz_delta))
        process_start_date = datetime_start.strftime('%d-%m-%Y')
        process_start_time = datetime_start.strftime('%H:%M:%S')
        process_end_date = today.strftime('%d-%m-%Y')
        process_end_time = today.strftime('%H:%M:%S')

        email_template_id = self.env.ref('onsc_legajo.email_template_ws7_processing_notification')
        view_context = dict(self._context)
        view_context.update({
            'process_start_date': process_start_date,
            'process_start_time': process_start_time,
            'process_end_date': process_end_date,
            'process_end_time': process_end_time,
            'process_qty': process_qty,
            'in_process_qty': in_process_qty,
            'error_qty': error_qty,
            'na_qty': na_qty,
            'na_no_contract_qty': na_no_contract_qty,
            'total_qty': total_qty,
            'date_from': date_from and date_from.strftime('%d-%m-%Y %H:%M:%S') or None,
            'date_to': date_to and date_to.strftime('%d-%m-%Y %H:%M:%S') or None,
        })

        if analyze_date_from:
            analyze_records = records.filtered(lambda x: x.fecha_aud >= analyze_date_from)
            analyze_process_qty = len(analyze_records.filtered(lambda x: x.state in ['processed']))
            analyze_error_qty = len(analyze_records.filtered(lambda x: x.state in ['error']))
            analyze_na_no_contract_qty = len(
                analyze_records.filtered(lambda x: x.state in ['na'] and x.log == 'Contrato no encontrado'))
            analyze_na_qty = len(analyze_records.filtered(lambda x: x.state in ['na']))
            analyze_in_process_qty = len(analyze_records.filtered(lambda x: x.state in ['in_process']))
            analyze_total_qty = len(analyze_records)

            # analyze_sorted_records = sorted(analyze_records, key=lambda r: (r.fecha_aud))
            # analyze_date_from = analyze_sorted_records[0].fecha_aud if analyze_sorted_records else analyze_date_from
            if analyze_date_from:
                analyze_date_from += datetime.timedelta(hours=int(tz_delta))
            analyze_date_to = self.env.user.company_id.ws7_date_from
            if analyze_date_to:
                analyze_date_to += datetime.timedelta(hours=int(tz_delta))

            view_context.update({
                'has_analyzed_period': True,
                'analyze_process_qty': analyze_process_qty,
                'analyze_error_qty': analyze_error_qty,
                'analyze_na_no_contract_qty': analyze_na_no_contract_qty,
                'analyze_na_qty': analyze_na_qty,
                'analyze_in_process_qty': analyze_in_process_qty,
                'analyze_total_qty': analyze_total_qty,
                'analyze_date_from': analyze_date_from and analyze_date_from.strftime('%d-%m-%Y %H:%M:%S') or None,
                'analyze_date_to': analyze_date_to and analyze_date_to.strftime('%d-%m-%Y %H:%M:%S') or None,
            })

        email_template_id.with_context(view_context).send_mail(self.id)
