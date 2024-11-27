# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, _, api
from odoo.exceptions import ValidationError
from ..soap import dnic_client

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """INFORMACION Y COMPORTAMIENTO PROPIO DE INTEGRACIONES DNIC E IDUY"""
    _inherit = 'res.partner'

    cv_dnic_full_name = fields.Char(u'Nombre en cédula')
    cv_dnic_name_1 = fields.Char(u'Primer nombre CI')
    cv_dnic_name_2 = fields.Char(u'Segundo nombre CI')
    cv_dnic_lastname_1 = fields.Char(u'Primer apellido CI')
    cv_dnic_lastname_2 = fields.Char(u'Segundo apellido CI')
    cv_last_name_adoptive_1 = fields.Char(u'Primer apellido adoptivo')
    cv_last_name_adoptive_2 = fields.Char(u'Segundo apellido adoptivo')

    # def get_cv_main_values(self, response):
    #     "Metodo a extender para adicionar valores al diccionario"
    #     return response

    def update_dnic_values(self, jump_error=False):
        """
        Actualiza los valores del partner consultando al servicio de dnic
        (Si el flag is_dnic_integrated está activo)
        :param jump_error: Si está en true se realiza un commit antes de consultar el servicio para no perder datos
        si el mismo da error
        :return: boolean
        """
        if self.env.company.is_dnic_integrated:
            self = self.filtered(lambda x: x.is_cv_uruguay)
            if self:
                # Preservamos desde este punto por si falla el servicio
                with self._cr.savepoint():
                    try:
                        client_obj = dnic_client.DNICClient(self.env.company)
                        for rec in self:
                            response = client_obj.ObtPersonaPorDoc(rec.cv_nro_doc)
                            response = self.map_cv_sex(response)
                            return rec.with_context(can_update_contact_cv=True).write(response)
                    except Exception as e:
                        _logger.error(_('Ha ocurrido un error al tratar de consultar el servicio de DNIC'))
                        _logger.error(_('Error encontrado: %s' % e))
                        if not jump_error:
                            raise ValidationError(
                                _('Ha ocurrido un error al consultar el servicio de DNIC. %s' % e))

        return False

    @api.model
    def map_cv_sex(self, response):
        """Actualmente tenemos 2 sexos 1: Masculino 2: Femenino
        Se utiliza esta función para reusar los códigos definidos para el selection y no fijar valores"""
        cv_sex = self.fields_get(['cv_sex'])['cv_sex']['selection']
        cv_sex_map = {cont + 1: cv_sex[cont][0] for cont in range(len(cv_sex))}

        response.update({'cv_sex': cv_sex_map.get(response.get('cv_sex'))})
        return response

    @api.model
    def _run_retry_dnic_cron(self):
        """
        Cron que identifica los partner de Uruguay que no
        :return:
        """
        if self.env.company.is_dnic_integrated:
            partner_to_fix = self.env['res.partner'].search([
                ('is_partner_cv', '=', True),
                ('cv_dnic_name_1', '=', False),
            ]).filtered(lambda x: x.is_cv_uruguay)
            partner_to_fix.update_dnic_values()
            _logger.info("Se procesaron los siguientes Partner de CV: %s" % partner_to_fix.ids)
