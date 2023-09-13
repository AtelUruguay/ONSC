# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, tools, _


class ONSCLegajoStagingWS7(models.Model):
    _name = 'onsc.legajo.staging.ws7'
    _description = 'Staging WS7'

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
    comi_reg = fields.Char(string='comi_reg')
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
    program_project_id = fields.Many2one('onsc.legajo.office', string='Programa - Proyecto')  # programa - proyecto

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

    def _compute_should_disable_form_edit(self):
        for record in self:
            record.should_disable_form_edit = record.state in ['na', 'processed']

    def button_in_process(self):
        self._set_mapped_vals()
        if not self.log:
            self.state = 'in_process'

    def _set_mapped_vals(self):
        RetributiveDay = self.env['onsc.legajo.jornada.retributiva'].suspend_security()
        BudgetItem = self.env['onsc.legajo.budget.item'].suspend_security()

        log_list = self._set_mapped_vals_get_logs()

        budget_item_args = []
        if self.descriptor1_id:
            budget_item_args.append(('dsc1Id', '=', self.descriptor1_id.id))
        if self.descriptor2_id:
            budget_item_args.append(('dsc1Id', '=', self.descriptor1_id.id))
        if self.descriptor3_id:
            budget_item_args.append(('dsc1Id', '=', self.descriptor1_id.id))
        if self.descriptor4_id:
            budget_item_args.append(('dsc1Id', '=', self.descriptor1_id.id))

        budget_item = BudgetItem.search(budget_item_args, limit=1)
        if not budget_item:
            log_list.append(_('No se encontró una Partida para la combinación de descriptores'))

        # OFICINA Y JORNADA RETRIBUTIVA
        retributive_day = RetributiveDay.search([
            ('codigoJornada', '=', self.jornada_ret),
            ('office_id.proyecto', '=', self.proyecto),
            ('office_id.programa', '=', self.programa),
        ], limit=1)
        retributive_day_id = retributive_day.id
        office_id = retributive_day.office_id.id

        if not retributive_day_id:
            log_list.append(
                _('No se encontró la Jornada retributiva para la combinación de jornada_ret, proyecto y programa')
            )

        if len(log_list) > 0:
            log_str = ', '.join(log_list)
            self.write({'log': log_str, 'state': 'error'})
        else:
            self.write({
                'state': 'in_process',
                'log': False,
                'budget_item_id': budget_item.id,
                'retributive_day_id': retributive_day_id,
                'program_project_id': office_id,
            })

    def _set_mapped_vals_get_logs(self):
        log_list = []
        if self.inciso and not self.inciso_id:
            log_list.append(_('Hay establecido un inciso pero no está cargado el catálogo correspondiente'))
        if self.ue and not self.operating_unit_id:
            log_list.append(_('Hay establecido una ue pero no está cargado el catálogo correspondiente'))
        if self.tipo_doc and not self.cv_document_type_id:
            log_list.append(_('Hay establecido un tipo_doc pero no está cargado el catálogo correspondiente'))
        if self.cod_pais and not self.country_id:
            log_list.append(_('Hay establecido un cod_pais pero no está cargado el catálogo correspondiente'))
        if self.raza and not self.race_id:
            log_list.append(_('Hay establecido un raza pero no está cargado el catálogo correspondiente'))
        if self.cod_mecing and not self.income_mechanism_id:
            log_list.append(_('Hay establecido un cod_mecing pero no está cargado el catálogo correspondiente'))
        if self.cod_reg and not self.regime_id:
            log_list.append(_('Hay establecido un cod_reg pero no está cargado el catálogo correspondiente'))
        if self.cod_desc1 and not self.descriptor1_id:
            log_list.append(_('Hay establecido un cod_desc1 pero no está cargado el catálogo correspondiente'))
        if self.cod_desc2 and not self.descriptor2_id:
            log_list.append(_('Hay establecido un cod_desc2 pero no está cargado el catálogo correspondiente'))
        if self.cod_desc3 and not self.descriptor3_id:
            log_list.append(_('Hay establecido un cod_desc3 pero no está cargado el catálogo correspondiente'))
        if self.cod_desc4 and not self.descriptor4_id:
            log_list.append(_('Hay establecido un cod_desc4 pero no está cargado el catálogo correspondiente'))

        if self.sexo and not self.gender_id:
            log_list.append(_('Hay establecido un sexo pero no está cargado el catálogo correspondiente'))
        if self.codigoEstadoCivil and not self.marital_status_id:
            log_list.append(_('Hay establecido un codigoEstadoCivil pero no está cargado el catálogo correspondiente'))
        if self.cod_desc4 and not self.descriptor4_id:
            log_list.append(_('Hay establecido un cod_desc4 pero no está cargado el catálogo correspondiente'))
        return log_list

    def process_staging(self, ids=[]):
        Contract = self.env['hr.contract'].sudo()
        args = [('state', 'in', ['in_process', 'na']), ('checked_bysystem', '=', False)]
        if len(ids) > 0:
            args.append(('id', 'in', ids))
        for record in self.search(args):
            try:
                if record.mov in ['ALTA', 'BAJA']:
                    self._check_movement(Contract, record)
                elif record.mov in ['ASCENSO', 'TRANSFORMA'] and record.tipo_mov == 'BAJA':
                    self.set_ascenso_transformacion(Contract, record)
                self.env.cr.commit()
            except Exception as e:
                self.env.cr.rollback()
                record.write({
                    'state': 'error',
                    'log': 'Error: %s' % tools.ustr(e)})
                self.env.cr.commit()

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
            record.write({'checked_bysystem': True, 'log': _('No se encontró el contrato')})

    def set_ascenso_transformacion(self, Contract, record):
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
                'log': _('Segundo movimiento no encontrado')})
            return

        new_contract = self._get_contract_copy(contract, second_movement)
        contract.deactivate_legajo_contract(record.fecha_vig + datetime.timedelta(days=-1))
        if record.mov == 'ASCENSO':
            causes_discharge = self.env.user.company_id.ws7_ascenso_causes_discharge_id
        else:
            causes_discharge = self.env.user.company_id.ws7_transforma_causes_discharge_id
        contract.write({
            'causes_discharge_id': causes_discharge.id,
            'cs_contract_id': new_contract.id
        })
        self._copy_jobs(contract, new_contract)
        records |= second_movement
        records.write({'state': 'processed'})

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

        new_contract = contract.copy({
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
            'description_day': record.retributive_day_id.descripcionJornada,
            'code_day': record.retributive_day_id.codigoJornada,
            'regime_id': regime.id,
            'position': str(record.idPuesto),
            'workplace': str(record.nroPlaza),
            'sec_position': str(record.secPlaza),
            'program': str(record.programa),
            'project': str(record.proyecto),
        })
        return new_contract

    def _copy_jobs(self, source_contract, target_contract):
        """
        :param source_contract: Recordset de contrato
        :param target_contract: Recordset de contrato
        :param operation: Recordset de la operacion
        :return: Nuevos puestos
        """
        if target_contract.operating_unit_id != source_contract.operating_unit_id:
            return self.env['hr.job']
        return source_contract.job_ids.filtered(
            lambda x: x.end_date is False or x.end_date >= target_contract.date_start).copy(
            {'contract_id': target_contract.id})
