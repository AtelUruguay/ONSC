# -*- coding: utf-8 -*-
from lxml import etree

from odoo import fields, models, api, _
from .. import onsc_cv_useful_tools as useful_tools
from .onsc_cv_abstract_config import STATES as CONDITIONAL_VALIDATION_STATES


class ONSCCVAbstractConditionalState(models.AbstractModel):
    _name = 'onsc.cv.abstract.conditional.state'
    _description = 'Modelo abstracto de estado condicional'
    _catalogs2validate = []

    # CATALOGS VALIDATION STATE
    conditional_validation_state = fields.Selection(
        string="Estado valor condicional",
        selection=CONDITIONAL_VALIDATION_STATES,
        compute='_compute_conditional_validation_state',
        store=True
    )
    conditional_validation_reject_reason = fields.Html(
        string="Motivo del rechazo",
        compute='_compute_conditional_validation_state',
        store=True
    )

    @property
    def field_conditional_validation_state(self):
        return etree.XML("""<field name="conditional_validation_state" invisible="1"/>""")

    @property
    def div_info(self):
        return etree.XML("""
                <div class="alert alert-info" role="alert"
                         attrs="{'invisible': [('conditional_validation_state', '!=', 'to_validate')]}">
                        <p class="mb-0">
                            <strong>
                                El registro ingresado está en proceso de validación, se notificará el resultado de este
                                a su e-mail
                            </strong>
                        </p>
                    </div>""")

    @property
    def div_danger(self):
        return etree.XML("""
                <div class="alert alert-danger" role="alert"
                         attrs="{'invisible': [('conditional_validation_state', '!=', 'rejected')]}">
                        <p class="mb-0">
                            <strong>
                                El registro ha sido rechazado por los siguientes motivos:
                                <field name="conditional_validation_reject_reason" readonly="1"/>
                            </strong>
                        </p>
                    </div>""")

    @api.depends(lambda self: ['%s.state' % x for x in self._catalogs2validate])
    def _compute_conditional_validation_state(self):
        for record in self:
            validation_status = useful_tools.get_validation_status(record, self._catalogs2validate)
            record.conditional_validation_state = validation_status.get('state')
            record.conditional_validation_reject_reason = validation_status.get('reject_reason', '')

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ONSCCVAbstractConditionalState, self).fields_view_get(view_id, view_type, toolbar, submenu)
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for node in doc.xpath('//sheet'):
                node.insert(0, self.div_info)
                node.insert(0, self.div_danger)
                node.insert(0, self.field_conditional_validation_state)
            # Replace arch with new definition
            xarch, xfields = self.env['ir.ui.view'].postprocess_and_fields(doc, model=self._name)
            res['arch'] = xarch
            res['fields'] = xfields
        return res
