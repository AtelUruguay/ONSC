# -*- coding: utf-8 -*-
from lxml import etree

from odoo import models, fields

DOCUMENTARY_VALIDATION_STATES = [('to_validate', 'Para validar'),
                                 ('validated', 'Validado'),
                                 ('rejected', 'Rechazado')]


class ONSCCVAbstractFileValidation(models.AbstractModel):
    _inherit = 'onsc.cv.abstract.documentary.validation'

    def _check_todisable_dynamic_fields(self):
        return super(ONSCCVAbstractFileValidation,
                     self)._check_todisable_dynamic_fields() or self.cv_digital_id.is_docket

    @property
    def widget_call_documentary_button(self):
        return etree.XML("""
                <div>
                    <field name="documentary_validation_state" invisible="1"/>
                    <button name="button_documentary_approve"
                        attrs="{'invisible': [('documentary_validation_state', '=', 'validated')]}"
                        groups="onsc_cv_digital.group_validador_documental_cv,onsc_cv_digital_legajo.group_legajo_validador_doc_inciso,onsc_cv_digital_legajo.group_legajo_validador_doc_ue,onsc_cv_digital_legajo.group_legajo_validador_doc_consulta"
                        type="object" string="Validar" icon="fa-thumbs-o-up" class="btn btn-sm btn-outline-success"/>
                    <button name="button_documentary_reject"
                        attrs="{'invisible': [('documentary_validation_state', '=', 'rejected')]}"
                        groups="onsc_cv_digital.group_validador_documental_cv,onsc_cv_digital_legajo.group_legajo_validador_doc_inciso,onsc_cv_digital_legajo.group_legajo_validador_doc_ue,onsc_cv_digital_legajo.group_legajo_validador_doc_consulta"
                        type="object" string="Rechazar" icon="fa-thumbs-o-down" class="btn btn-sm btn-outline-danger"/>
                    <button name="button_documentary_tovalidate"
                        attrs="{'invisible': [('documentary_validation_state', '=', 'to_validate')]}"
                        groups="onsc_cv_digital.group_validador_documental_cv,onsc_cv_digital_legajo.group_legajo_validador_doc_inciso,onsc_cv_digital_legajo.group_legajo_validador_doc_ue,onsc_cv_digital_legajo.group_legajo_validador_doc_consulta"
                        type="object" string="Para validar" icon="fa-thumb-tack" class="btn btn-sm btn-outline-info"/>
                    <div class="alert alert-danger" role="alert"
                        attrs="{'invisible': [('documentary_validation_state', '!=', 'rejected')]}">
                        <p class="mb-0">
                            <strong>
                                El registro ha sido rechazado. Motivo del rechazo: <field name="documentary_reject_reason" class="oe_inline" readonly="1"/>
                                <p/>
                                Fecha: <field name="documentary_validation_date" class="oe_inline" readonly="1"/> Usuario: <field name="documentary_user_id" class="oe_inline" options="{'no_open': True, 'no_quick_create': True, 'no_create': True}" readonly="1"/>
                            </strong>
                        </p>
                    </div>
                    <div class="alert alert-success" role="alert"
                        attrs="{'invisible': [('documentary_validation_state', '!=', 'validated')]}">
                        <p class="mb-0">
                            <strong>
                                El registro ha sido validado
                                <p/>
                                Fecha: <field name="documentary_validation_date" class="oe_inline" readonly="1"/> Usuario: <field name="documentary_user_id" class="oe_inline" options="{'no_open': True, 'no_quick_create': True, 'no_create': True}" readonly="1"/>
                            </strong>
                        </p>
                    </div>
                </div>""")

    def button_documentary_tovalidate(self):
        args = {
            'documentary_validation_state': 'to_validate',
            'documentary_reject_reason': '',
            'documentary_validation_date': fields.Date.today(),
            'documentary_user_id': self.env.user.id,
        }
        self.update_call_instances(args)
        return super(ONSCCVAbstractFileValidation, self).button_documentary_tovalidate()

    def button_documentary_approve(self):
        args = {
            'documentary_validation_state': 'validated',
            'documentary_reject_reason': '',
            'documentary_validation_date': fields.Date.today(),
            'documentary_user_id': self.env.user.id,
        }
        self.update_call_instances(args)
        return super(ONSCCVAbstractFileValidation, self).button_documentary_approve()

    def documentary_reject(self, reject_reason):
        args = {
            'documentary_validation_state': 'rejected',
            'documentary_reject_reason': reject_reason,
            'documentary_validation_date': fields.Date.today(),
            'documentary_user_id': self.env.user.id,
        }
        self.update_call_instances(args)
        return super(ONSCCVAbstractFileValidation, self).documentary_reject()

    def update_call_instances(self, args):
        if hasattr(self, 'cv_digital_id'):
            Calls = self.env['onsc.cv.digital.call']
            for record in self.filtered(lambda x: x.original_instance_identifier == 0 and x.cv_digital_id.type == 'cv'):
                # OBTENIENDO LLAMADOS DEL CV
                calls = Calls.search([
                    ('cv_digital_origin_id', '=', record.cv_digital_id.id),
                    ('is_zip', '=', False),
                    ('preselected', '!=', 'no'),
                ])
                # OBTENIENDO RECORDSETS ASOCIADOS A LLAMADOS Y QUE TENGAN COMO ORIGEN EL RECORD
                self.search([
                    ('original_instance_identifier', '=', record.id),
                    ('cv_digital_id', 'in', calls.mapped('cv_digital_id').ids),
                    ('create_date', '>=', record.custom_write_date)]).write(args)
