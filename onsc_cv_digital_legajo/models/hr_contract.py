# -*- coding:utf-8 -*-

from odoo import models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    def activate_legajo_contract(self, legajo_state='active', eff_date=False, clean_destination_info=False):
        """
        LA ACTIVACION DE UN CONTRATO DISPARA LA ACTUALIZACION DE SECCIONES DEL LEGAJO.
        """
        result = super(HrContract, self).activate_legajo_contract(
            legajo_state=legajo_state,
            eff_date=eff_date,
            clean_destination_info=clean_destination_info
        )
        for record in self:
            record.legajo_id.update_all_legajo_sections()
        return result
