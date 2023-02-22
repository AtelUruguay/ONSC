# -*- coding: utf-8 -*-

from odoo import fields, models, api

SELECTION_RADIO = [('1', 'Si, no puede hacerlo'), ('2', 'Si, mucha dificultad'),
                   ('3', 'Si, alguna dificultad '), ('4', 'No tiene dificultad')]
SITUATION = u'¿Está en situación de discapacidad y/o requiere algún apoyo para cumplir con sus actividades laborales?'
DISABILITE = u'¿Está inscripto en el registro de personas con discapacidad del Ministerio de Desarrollo Social?'


class ONSCCVAbstractCommon(models.AbstractModel):
    _name = 'onsc.cv.abstract.common'
    _description = 'Modelo abstracto común para todas las entidades de CV(NO CV)'

    # CAMPOS PARA ALMACENAR EL ORIGEN EN LAS ENTIDADES DEL LLAMADO
    original_instance_identifier = fields.Integer(string="Id del documento origen en el CV")

    @api.returns(None, lambda value: value[0])
    def copy_data(self, default=None):
        res = super(ONSCCVAbstractCommon, self).copy_data(default=default)
        if hasattr(self, 'original_instance_identifier') and len(self) == 1:
            for data in res:
                data['original_instance_identifier'] = self.id
        return res


class ONSCCVCommonData(models.AbstractModel):
    _name = 'onsc.cv.common.data'
    _description = 'Modelo abstracto común para los datos de tipo CV'

    document_identity_file = fields.Binary(string="Documento digitalizado del documento de identidad")
    document_identity_filename = fields.Char('Nombre del documento digital')
    country_of_birth_id = fields.Many2one("res.country", string="País de nacimiento")
    marital_status_id = fields.Many2one("onsc.cv.status.civil", string="Estado civil")
    uy_citizenship = fields.Selection(string="Ciudadanía uruguaya",
                                      selection=[('legal', 'Legal'), ('natural', 'Natural'),
                                                 ('extranjero', 'Extranjero')])
    crendencial_serie = fields.Char(string="Serie de la credencial", size=3)
    credential_number = fields.Char(string="Numero de la credencial", size=6)
    civical_credential_file = fields.Binary(string="Documento digitalizado credencial cívica")
    civical_credential_filename = fields.Char('Nombre del documento digital')
    cjppu_affiliate_number = fields.Integer(string="Numero de afiliado a la CJPPU")
    professional_resume = fields.Text(string="Resumen profesional")
    user_linkedIn = fields.Char(string="Usuario en LinkedIn")
    is_driver_license = fields.Boolean(string="¿Tiene licencia de conducir?")

    # Genero
    cv_gender_id = fields.Many2one("onsc.cv.gender", string=u"Género")
    is_cv_gender_option_other_enable = fields.Boolean(
        u'¿Permitir opción otra/o?',
        related='cv_gender_id.is_option_other_enable',
        store=True)
    cv_gender2 = fields.Char(string=u"Otro género")
    cv_gender_record_file = fields.Binary(string="Constancia de identidad de género")
    cv_gender_record_filename = fields.Char('Nombre del documento digital')
    is_cv_gender_public = fields.Boolean(
        string="¿Desea que esta información se incluya en la versión impresa de su CV?")
    is_cv_gender_record = fields.Boolean(u'Constancia', related='cv_gender_id.record')

    # RAZA
    cv_race2 = fields.Char(string=u"Otra identidad étnico-racial")
    is_cv_race_public = fields.Boolean(string="¿Permite que su identidad étnico-racial se visualice en su CV?")

    # ETNICO RACIAL
    is_afro_descendants = fields.Boolean(string="Afrodescendientes (Art. 4 Ley N°19.122)")
    afro_descendants_file = fields.Binary(
        string='Documento digitalizado "Declaración de afrodescendencia (Art. 4 Ley N°19.122)"')
    afro_descendants_filename = fields.Char('Nombre del documento digital')

    # SALUD LABORAL
    is_occupational_health_card = fields.Boolean(string="¿Tiene carné de salud laboral?")
    occupational_health_card_date = fields.Date(string="Fecha de vencimiento del carné de salud laboral")
    occupational_health_card_file = fields.Binary(
        string="Documento digitalizado del carné de salud laboral")
    occupational_health_card_filename = fields.Char('Nombre del documento digital')

    is_medical_aptitude_certificate_status = fields.Boolean(
        string="¿Tiene certificado de aptitud médico-deportiva?")
    medical_aptitude_certificate_date = fields.Date(
        string="Fecha de vencimiento del certificado de aptitud médico-deportiva")
    medical_aptitude_certificate_file = fields.Binary(
        string="Documento digitalizado del certificado de aptitud médico-deportiva")
    medical_aptitude_certificate_filename = fields.Char('Nombre del documento digital')

    # Víctima de delitos violentos
    is_victim_violent = fields.Boolean(string="Persona víctima de delitos violentos (Art. 105 Ley Nº 19.889)", )
    relationship_victim_violent_file = fields.Binary(
        string="Documento digitalizado: Comprobante de parentesco con persona víctima de delito violento")
    relationship_victim_violent_filename = fields.Char('Nombre del documento digital')
    is_public_information_victim_violent = fields.Boolean(
        string="¿Desea que esta información se incluya en la versión impresa de su CV?", )

    # Domicilio
    cv_address_street_id = fields.Many2one('onsc.cv.street', string="Calle")
    cv_address_street2_id = fields.Many2one('onsc.cv.street', string="Entre calle")
    cv_address_street3_id = fields.Many2one('onsc.cv.street', string=u'Y calle')

    # Discapacidad
    allow_content_public = fields.Selection(selection=[('si', u'Si'), ('no', u'No')], default='no',
                                            string=u'¿Permite que el contenido de esta sección se visualice en su CV?')
    situation_disability = fields.Selection(selection=[('si', u'Si'), ('no', u'No')], string=SITUATION)
    people_disabilitie = fields.Selection(selection=[('si', u'Si'), ('no', u'No')], string=DISABILITE)
    document_certificate_file = fields.Binary(string=u'Documento digitalizado constancia de inscripción en el RNPcD')
    document_certificate_filename = fields.Char('Nombre del documento Digitalizado')
    certificate_date = fields.Date(string=u'Fecha de certificado')
    to_date = fields.Date(string=u'Fecha hasta')
    see = fields.Selection(selection=SELECTION_RADIO, string=u'Ver, aún si usa anteojos o lentes')
    hear = fields.Selection(selection=SELECTION_RADIO, string=u'Oír, aún si usa audífono')
    walk = fields.Selection(selection=SELECTION_RADIO, string=u'Caminar o subir escalones')
    speak = fields.Selection(selection=SELECTION_RADIO, string=u'Hablar o comunicarse aún usando lengua de señas')
    realize = fields.Selection(selection=SELECTION_RADIO,
                               string=u'Realizar tareas de cuidado personal como comer, bañarse o vestirse solo')
    lear = fields.Selection(selection=SELECTION_RADIO, string=u'Entender y/o aprender')
    interaction = fields.Selection(selection=SELECTION_RADIO, string=u'Interactuar y/o relacionarse con otras personas')
    need_other_support = fields.Text(string=u"¿Necesita otro apoyo?")
