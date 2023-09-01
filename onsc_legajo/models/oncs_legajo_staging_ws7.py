# -*- coding: utf-8 -*-

from odoo import models, fields


class ONSCLegajoStagingWS7(models.Model):
    _name = 'onsc.legajo.staging.ws7'
    _description = 'Staging WS7'

    inciso_id = fields.Many2one('onsc.catalog.inciso', string='Inciso')
    operating_unit_id = fields.Many2one("operating.unit", string="Unidad ejecutora")

    primer_nombre = fields.Char(string='primer_nombre')
    segundo_nombre = fields.Char(string='segundo_nombre')
    primer_ap = fields.Char(string='primer_ap')
    segundo_ap = fields.Char(string='segundo_ap')
    fecha_nac = fields.Date(string='fecha_nac')
    fecha_ing_adm = fields.Date(string='fecha_ing_adm')
    cod_mot_baja = fields.Char(string='cod_mot_baja')
    fecha_vig = fields.Date(string='fecha_vig')
    fecha_aud = fields.Datetime(string='fecha_aud')
    mov = fields.Char(string='mov')
    tipo_mov = fields.Char(string='tipo_mov')
    pdaId = fields.Char(string='pdaId')
    movimientoPadreId = fields.Char(string='movimientoPadreId')
    fecha_desde_vinc = fields.Char(string='fecha_desde_vinc')
    idPuesto = fields.Char(string='idPuesto')
    nroPlaza = fields.Char(string='nroPlaza')
    secPlaza = fields.Char(string='secPlaza')
    programa = fields.Char(string='programa')
    proyecto = fields.Char(string='proyecto')
    aniosInactividad = fields.Char(string='aniosInactividad')
    fechaGraduacion = fields.Date(string='fechaGraduacion')

    cv_document_type_id = fields.Many2one('onsc.cv.document.type', u'Tipo de documento') #tipo_doc
    country_id = fields.Many2one('res.country', u'País') #cod_pais
    race_id = fields.Many2one("onsc.cv.race", string=u"Raza")  # raza
    income_mechanism_id = fields.Many2one('onsc.legajo.income.mechanism', string='Mecanismo de ingreso')  # cod_mecing
    regime_id = fields.Many2one('onsc.legajo.regime', string='Régimen', history=True)  # cod_reg
    descriptor1_id = fields.Many2one('onsc.catalog.descriptor1', string='Descriptor1', history=True)  # cod_desc1
    descriptor2_id = fields.Many2one('onsc.catalog.descriptor2', string='Descriptor2', history=True)  # cod_desc2
    descriptor3_id = fields.Many2one('onsc.catalog.descriptor3', string='Descriptor3', history=True)  # cod_desc3
    descriptor4_id = fields.Many2one('onsc.catalog.descriptor4', string='Descriptor4', history=True)  # cod_desc4

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

    # TODO
    program_project_id = fields.Many2one('onsc.legajo.office', string='Programa - Proyecto')  # programa - proyecto

    # CV
    gender_id = fields.Many2one("onsc.cv.gender", string=u"Género")  # sexo
    marital_status_id = fields.Many2one("onsc.cv.status.civil", string="Estado civil")  # codigoEstadoCivil
