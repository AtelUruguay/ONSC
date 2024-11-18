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

    document_identity_file = fields.Binary(string="Documento digitalizado del documento de identidad", copy=False)
    document_identity_filename = fields.Char('Nombre del documento digital - Documento digitalizado del documento de identidad', copy=False)
    country_of_birth_id = fields.Many2one("res.country", string="País de nacimiento", copy=False)
    marital_status_id = fields.Many2one("onsc.cv.status.civil", string="Estado civil", copy=False)
    uy_citizenship = fields.Selection(string="Ciudadanía uruguaya", copy=False,
                                      selection=[('legal', 'Legal'), ('natural', 'Natural'),
                                                 ('extranjero', 'Extranjero')])
    crendencial_serie = fields.Char(string="Serie de la credencial", size=3, copy=False)
    credential_number = fields.Char(string="Numero de la credencial", size=6, copy=False)
    civical_credential_file = fields.Binary(string="Documento digitalizado credencial cívica", copy=False)
    civical_credential_filename = fields.Char('Nombre del documento digital - Documento digitalizado credencial cívica', copy=False)
    cjppu_affiliate_number = fields.Integer(string="Numero de afiliado a la CJPPU", copy=False)
    professional_resume = fields.Text(string="Resumen profesional", copy=False)
    user_linkedIn = fields.Char(string="Usuario en LinkedIn", copy=False)
    is_driver_license = fields.Boolean(string="¿Tiene licencia de conducir?", copy=False)

    # Genero
    cv_gender_id = fields.Many2one("onsc.cv.gender", string=u"Género", copy=False)
    is_cv_gender_option_other_enable = fields.Boolean(
        u'¿Permitir opción otra/o?',
        related='cv_gender_id.is_option_other_enable',
        store=True)
    cv_gender2 = fields.Char(string=u"Otro género", copy=False)
    cv_gender_record_file = fields.Binary(string="Constancia de identidad de género", copy=False)
    cv_gender_record_filename = fields.Char('Nombre del documento digital - Constancia de identidad de género', copy=False)
    is_cv_gender_public = fields.Boolean(
        string="¿Desea que esta información se incluya en la versión impresa de su CV?", copy=False)
    is_cv_gender_record = fields.Boolean(u'Constancia', related='cv_gender_id.record')

    # RAZA
    cv_race2 = fields.Char(string=u"Otra identidad étnico-racial", copy=False)
    is_cv_race_public = fields.Boolean(string="¿Permite que su identidad étnico-racial se visualice en su CV?",
                                       copy=False)

    # ETNICO RACIAL
    is_afro_descendants = fields.Boolean(string="Afrodescendientes (Art. 4 Ley N°19.122)", copy=False)
    afro_descendants_file = fields.Binary(
        string='Documento digitalizado "Declaración de afrodescendencia (Art. 4 Ley N°19.122)"', copy=False)
    afro_descendants_filename = fields.Char('Nombre del documento digital - "Declaración de afrodescendencia (Art. 4 Ley N°19.122)"', copy=False)

    # SALUD LABORAL
    is_occupational_health_card = fields.Boolean(string="¿Tiene carné de salud laboral?", copy=False)
    occupational_health_card_date = fields.Date(string="Fecha de vencimiento del carné de salud laboral", copy=False)
    occupational_health_card_file = fields.Binary(
        string="Documento digitalizado del carné de salud laboral", copy=False)
    occupational_health_card_filename = fields.Char('Nombre del documento digital - Carné de salud laboral', copy=False)

    is_medical_aptitude_certificate_status = fields.Boolean(
        string="¿Tiene certificado de aptitud médico-deportiva?", copy=False)
    medical_aptitude_certificate_date = fields.Date(
        string="Fecha de vencimiento del certificado de aptitud médico-deportiva", copy=False)
    medical_aptitude_certificate_file = fields.Binary(
        string="Documento digitalizado del certificado de aptitud médico-deportiva", copy=False)
    medical_aptitude_certificate_filename = fields.Char('Nombre del documento digital - Certificado de aptitud médico-deportiva', copy=False)

    # Víctima de delitos violentos
    is_victim_violent = fields.Boolean(string="Persona víctima de delitos violentos (Art. 105 Ley Nº 19.889)",
                                       copy=False)
    relationship_victim_violent_file = fields.Binary(
        string="Documento digitalizado: Comprobante de parentesco con persona víctima de delito violento",
        copy=False)
    relationship_victim_violent_filename = fields.Char('Nombre del documento digital - Comprobante de parentesco con persona víctima de delito violento', copy=False)
    is_public_information_victim_violent = fields.Boolean(
        string="¿Desea que esta información se incluya en la versión impresa de su CV?", copy=False)

    # Domicilio
    cv_address_street_id = fields.Many2one('onsc.cv.street', string="Calle (Nacional)", copy=False)
    cv_address_street2_id = fields.Many2one('onsc.cv.street', string="Entre calle", copy=False)
    cv_address_street3_id = fields.Many2one('onsc.cv.street', string=u'Y calle', copy=False)

    # Discapacidad
    allow_content_public = fields.Selection(selection=[('si', u'Si'), ('no', u'No')], default='no',
                                            string=u'¿Permite que el contenido de esta sección se visualice en su CV?',
                                            copy=False)
    situation_disability = fields.Selection(selection=[('si', u'Si'), ('no', u'No')], string=SITUATION, copy=False)
    people_disabilitie = fields.Selection(selection=[('si', u'Si'), ('no', u'No')], string=DISABILITE, copy=False)
    document_certificate_file = fields.Binary(
        string=u'Documento digitalizado constancia de inscripción en el RNPcD',
        copy=False
    )
    document_certificate_filename = fields.Char('Nombre del documento Digitalizado - Constancia de inscripción en el RNPcD', copy=False)
    certificate_date = fields.Date(string=u'Fecha de certificado', copy=False)
    to_date = fields.Date(string=u'Fecha hasta', copy=False)
    see = fields.Selection(selection=SELECTION_RADIO, string=u'Ver, aún si usa anteojos o lentes', copy=False)
    hear = fields.Selection(selection=SELECTION_RADIO, string=u'Oír, aún si usa audífono', copy=False)
    walk = fields.Selection(selection=SELECTION_RADIO, string=u'Caminar o subir escalones', copy=False)
    speak = fields.Selection(selection=SELECTION_RADIO, string=u'Hablar o comunicarse aún usando lengua de señas',
                             copy=False)
    realize = fields.Selection(selection=SELECTION_RADIO,
                               string=u'Realizar tareas de cuidado personal como comer, bañarse o vestirse solo',
                               copy=False)
    lear = fields.Selection(
        selection=SELECTION_RADIO,
        string=u'Entender y/o aprender',
        copy=False)
    interaction = fields.Selection(
        selection=SELECTION_RADIO,
        string=u'Interactuar y/o relacionarse con otras personas',
        copy=False)
    need_other_support = fields.Text(string=u"¿Necesita otro apoyo?", copy=False)
