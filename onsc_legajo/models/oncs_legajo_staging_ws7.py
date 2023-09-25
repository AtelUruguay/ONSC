# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, tools, api, _
from odoo.exceptions import ValidationError


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
            record.should_disable_form_edit = record.state in ['na', 'processed']

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
        if self.cod_mecing and not self.income_mechanism_id:
            income_mechanism_id = BaseUtils._get_catalog_id(IncomeMechanism, 'code', self, 'cod_mecing', log_list)
        else:
            income_mechanism_id = self.income_mechanism_id.id
        vals.update({'income_mechanism_id': income_mechanism_id})
        if self.cod_reg and not self.regime_id:
            regime_id = BaseUtils._get_catalog_id(Regime, 'codRegimen', self, 'cod_reg', log_list)
        else:
            regime_id = self.regime_id.id
        vals.update({'regime_id': regime_id})
        if self.cod_desc1 and not self.descriptor1_id:
            descriptor1_id = BaseUtils._get_catalog_id(Descriptor1, 'code', self, 'cod_desc1', log_list)
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
        if self.sexo and not self.gender_id:
            gender_id = BaseUtils._get_catalog_id(Gender, 'code', self, 'sexo', log_list)
        else:
            gender_id = self.gender_id.id
        vals.update({'gender_id': gender_id})
        if self.codigoEstadoCivil and not self.marital_status_id:
            marital_status_id = BaseUtils._get_catalog_id(MaritalStatus, 'code', self, 'codigoEstadoCivil', log_list)
        else:
            marital_status_id = self.marital_status_id.id
        vals.update({'marital_status_id': marital_status_id})
        return vals

    def process_staging(self, ids=False, limit=0):
        Contract = self.env['hr.contract'].sudo()
        args = [('state', 'in', ['in_process', 'na']), ('checked_bysystem', '=', False)]
        if ids:
            args.append(('id', 'in', ids))

        current_pointer = 0
        for record in self.search(args):
            try:
                with self._cr.savepoint():
                    if limit:
                        current_pointer += 1
                    if current_pointer > limit:
                        return
                    if record.mov in ['ALTA', 'BAJA', 'COMISION', 'CAMBIO_DEPTO']:
                        self._check_movement(Contract, record)
                    elif record.mov in ['ASCENSO', 'TRANSFORMA', 'REESTRUCTURA'] and record.tipo_mov == 'BAJA':
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
        if not exist_contract:
            record.write({'checked_bysystem': True, 'log': _('Contrato no encontrado')})

    def set_asc_transf_reest(self, Contract, record):
        records = record
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

        new_contract = self._get_contract_copy(contract, second_movement)
        self._copy_jobs(contract, new_contract)
        contract.with_context(no_check_write=True).deactivate_legajo_contract(
            record.fecha_vig + datetime.timedelta(days=-1),
            legajo_state='baja',
            eff_date=record.fecha_vig
        )
        if record.mov == 'ASCENSO':
            causes_discharge = self.env.user.company_id.ws7_ascenso_causes_discharge_id
        elif record.mov == 'TRANSFORMA':
            causes_discharge = self.env.user.company_id.ws7_transforma_causes_discharge_id
        else:
            causes_discharge = self.env.user.company_id.ws7_reestructura_causes_discharge_id
        contract.write({
            'causes_discharge_id': causes_discharge.id,
            'cs_contract_id': new_contract.id
        })
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

        baja_contract = Contract.search([
            ('cs_contract_id', '=', active_contract.id),
            ('legajo_state', '=', 'baja')], limit=1)
        if len(baja_contract) == 0:
            record.write({
                'state': 'error',
                'log': _('Contrato de baja no encontrado')})
            return
        self._check_valid_eff_date(baja_contract, second_movement.fecha_aud.date())
        self._check_valid_eff_date(active_contract, second_movement.fecha_aud.date())
        baja_end_date = baja_contract.date_end
        active_start_date = active_contract.date_start
        baja_contract.write({
            'date_end': second_movement.fecha_vig + datetime.timedelta(days=-1),
            'eff_date': second_movement.fecha_aud.date(),
        })
        active_contract.write({
            'date_start': second_movement.fecha_vig,
            'eff_date': second_movement.fecha_aud.date(),
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
        self._check_valid_eff_date(active_contract, second_movement.fecha_aud.date())
        active_start_date = active_contract.date_start
        active_contract.write({
            'date_start': second_movement.fecha_vig,
            'eff_date': second_movement.fecha_aud.date(),
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
        self._check_valid_eff_date(contract, second_movement.fecha_aud.date())
        contract.write({
            'date_end': second_movement.fecha_vig,
            'eff_date': second_movement.fecha_aud.date(),
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
            eff_date=record.fecha_vig
        )
        records.write({'state': 'processed'})

    def set_desreserva(self, Contract, record):
        records = record
        contract = self._get_contract(Contract, record, legajo_state_operator='=', legajo_state='reserved')
        if len(contract) == 0:
            record.write({
                'state': 'error',
                'log': _('Contrato no encontrado')})
            return
        contract.with_context(no_check_write=True).activate_legajo_contract(legajo_state='active', eff_date=record.fecha_vig)
        records.write({'state': 'processed'})

    def set_renovacion(self, Contract, record):
        records = record
        contract = self._get_contract(Contract, record, legajo_state_operator='=', legajo_state='active')
        if len(contract) == 0:
            record.write({
                'state': 'error',
                'log': _('Contrato no encontrado')})
            return
        self._check_valid_eff_date(contract, record.fecha_aud.date())
        contract.write({
            'date_end': record.fecha_vig,
            'eff_date': record.fecha_aud.date(),
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
        self._check_valid_eff_date(contract, record.fecha_vig)
        contract.write({
            'retributive_day_id': record.retributive_day_id.id,
            'eff_date': record.fecha_vig,
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
        self._check_valid_eff_date(contract, record.fecha_aud.date())
        contract.suspend_security().write({
            'eff_date': str(record.fecha_aud.date()),
            'graduation_date': str(record.fechaGraduacion),
        })
        self._set_modif_funcionario_extras(contract, record)
        record.write({'state': 'processed'})

    def _set_modif_funcionario_extras(self, contract, recor):
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

    def _get_contract_copy(self, contract, record):
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
        income_mechanism = record.income_mechanism_id
        regime = record.regime_id

        new_contract = self.env['hr.contract'].suspend_security().create({
            'employee_id': contract.employee_id.id,
            'inciso_id': inciso.id,
            'operating_unit_id': operating_unit.id,
            'date_start': record.fecha_vig,
            'eff_date': record.fecha_vig,
            'date_end': False,
            'legajo_state': 'active',
            'descriptor1_id': descriptor1.id,
            'descriptor2_id': descriptor2.id,
            'descriptor3_id': descriptor3.id,
            'descriptor4_id': descriptor4.id,
            'income_mechanism_id': income_mechanism.id,
            'retributive_day_id': record.retributive_day_id.id,
            # 'description_day': record.retributive_day_id.descripcionJornada,
            # 'code_day': record.retributive_day_id.codigoJornada,
            'regime_id': regime.id,
            'position': str(record.idPuesto),
            'workplace': str(record.nroPlaza),
            'sec_position': str(record.secPlaza),
            'program': str(record.programa),
            'project': str(record.proyecto),
            'state_square_id': contract.state_square_id.id,
            #
            'wage': contract.wage
        })
        return new_contract

    def _copy_jobs(self, source_contract, target_contract):
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
            return jobs
        for job_id in source_contract.job_ids.filtered(
                lambda x:
                (x.end_date is False or x.end_date >= fields.Date.today()) and
                x.start_date <= target_contract.date_start):
            jobs |= self.env['hr.job'].suspend_security().create_job(
                target_contract,
                job_id.department_id,
                target_contract.date_start,
                job_id.security_job_id,
                job_id.role_extra_ids
            )
        return jobs

    def _check_valid_eff_date(self, contract, eff_date):
        if isinstance(eff_date, str):
            _eff_date = fields.Date.from_string(eff_date)
        else:
            _eff_date = eff_date
        if contract.eff_date and contract.eff_date > _eff_date:
            raise ValidationError(_("No se puede modificar la historia del contrato para la fecha enviada."))
