# -*- coding: utf-8 -*-
from lxml import etree

from odoo import models, fields, api

DOCUMENTARY_VALIDATION_STATES = [('to_validate', 'Para validar'),
                                 ('validated', 'Validado'),
                                 ('rejected', 'Rechazado')]


class ONSCCVAbstractFileValidation(models.AbstractModel):
    _inherit = 'onsc.cv.abstract.documentary.validation'

    def _get_validation_config(self):
        if self._context.get('force_show_validation_section'):
            return self.env["onsc.cv.documentary.validation.config"].get_config()
        return self.env["onsc.cv.documentary.validation.config"].get_config(self._name)

    def _check_todisable_dynamic_fields(self):
        return super(ONSCCVAbstractFileValidation,
                     self)._check_todisable_dynamic_fields() or self.cv_digital_id.is_docket

    def _can_delete_record_if_was_validated(self):
        """
        Determines if a record can be deleted if it has been validated.

        This method overrides the parent class method to add additional checks
        specific to the `ONSCCVAbstractFileValidation` model. It checks if the
        record is part of a digital docket and if it belongs to an employee's
        legajo (employee file). If the record is found in the legajo, it cannot
        be deleted.

        Returns:
            bool: True if the record can be deleted, False otherwise.
        """
        result = super(ONSCCVAbstractFileValidation, self)._can_delete_record_if_was_validated()
        if self.cv_digital_id.is_docket and hasattr(self, '_legajo_model'):
            LegajoModel = self.env[self._legajo_model].suspend_security()
            employee = self.cv_digital_id.employee_id
            is_in_legajo = LegajoModel.search_count([
                ('employee_id', '=', employee.id),
                ('origin_record_id', '=', self.id),
            ])
            if is_in_legajo:
                return False
        return result

    @property
    def widget_call_documentary_button(self):
        if self._context.get('is_legajo') and self._context.get('show_only_status'):
            return etree.XML("""
                            <div>
                                <field name="documentary_validation_state" invisible="1"/>
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
        elif self._context.get('is_legajo'):
            return etree.XML("""
                            <div>
                                <field name="documentary_validation_state" invisible="1"/>
                                <field name="is_validated_seccions_rolleables" invisible="1"/>
                                <button name="button_documentary_approve"
                                    attrs="{'invisible': [('documentary_validation_state', '=', 'validated')]}"
                                    groups="onsc_cv_digital.group_validador_documental_cv,onsc_cv_digital_legajo.group_legajo_validador_doc_inciso,onsc_cv_digital_legajo.group_legajo_validador_doc_ue"
                                    type="object" string="Validar" icon="fa-thumbs-o-up" class="btn btn-sm btn-outline-success"/>
                                <button name="button_documentary_reject"
                                    attrs="{'invisible': ['|',('documentary_validation_state', '=', 'rejected'),'&amp;',('documentary_validation_state', '=', 'validated'),('is_validated_seccions_rolleables', '=', False)]}"
                                    groups="onsc_cv_digital.group_validador_documental_cv,onsc_cv_digital_legajo.group_legajo_validador_doc_inciso,onsc_cv_digital_legajo.group_legajo_validador_doc_ue"
                                    type="object" string="Rechazar" icon="fa-thumbs-o-down" class="btn btn-sm btn-outline-danger"/>
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
        return etree.XML("""
                <div>
                    <field name="documentary_validation_state" invisible="1"/>
                    <field name="is_validated_seccions_rolleables" invisible="1"/>
                    <button name="button_documentary_approve"
                        attrs="{'invisible': [('documentary_validation_state', '=', 'validated')]}"
                        groups="onsc_cv_digital.group_validador_documental_cv,onsc_cv_digital_legajo.group_legajo_validador_doc_inciso,onsc_cv_digital_legajo.group_legajo_validador_doc_ue"
                        type="object" string="Validar" icon="fa-thumbs-o-up" class="btn btn-sm btn-outline-success"/>
                    <button name="button_documentary_reject"
                        attrs="{'invisible': ['|',('documentary_validation_state', '=', 'rejected'),'&amp;',('documentary_validation_state', '=', 'validated'),('is_validated_seccions_rolleables', '=', False)]}"
                        groups="onsc_cv_digital.group_validador_documental_cv,onsc_cv_digital_legajo.group_legajo_validador_doc_inciso,onsc_cv_digital_legajo.group_legajo_validador_doc_ue"
                        type="object" string="Rechazar" icon="fa-thumbs-o-down" class="btn btn-sm btn-outline-danger"/>
                    <button name="button_documentary_tovalidate"
                        attrs="{'invisible': ['|',('documentary_validation_state', '=', 'to_validate'),'&amp;',('documentary_validation_state', '=', 'validated'),('is_validated_seccions_rolleables', '=', False)]}"
                        groups="onsc_cv_digital.group_validador_documental_cv"
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

    @api.model
    def create(self, values):
        result = super(ONSCCVAbstractFileValidation, self).create(values)
        if hasattr(self, 'cv_digital_id'):
            result.cv_digital_id.button_legajo_update_documentary_validation_sections_tovalidate()
        return result

    def write(self, vals):
        result = super(ONSCCVAbstractFileValidation, self).write(vals)
        if hasattr(self, 'cv_digital_id') and not self._context.get('ignore_documentary_status'):
            self.mapped('cv_digital_id').button_legajo_update_documentary_validation_sections_tovalidate()
        return result

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
        _user_id = self._context.get('user_id', self.env.user.id)
        args = {
            'documentary_validation_state': 'validated',
            'documentary_reject_reason': '',
            'documentary_validation_date': fields.Date.today(),
            'documentary_user_id': _user_id,
        }
        self.with_context(updating_call_instances=True).update_call_instances(args)
        result = super(ONSCCVAbstractFileValidation, self).button_documentary_approve()
        if not self._context.get('updating_call_instances') and len(self) == 1 and self.cv_digital_id.type:
            self.with_context(ignore_documentary_status=True).set_legajo_validated_records()
        return result

    def set_legajo_validated_records(self):
        """
        METODO PARA LLENAR ELEMENTOS DEL LEGAJO DESDE LA VALIDACION DOCUMENTAL DEL CV (TANTO EN LLAMADOS COMO EN VDL)
        :return:
        """
        if hasattr(self, '_legajo_model'):
            LegajoModel = self.env[self._legajo_model].suspend_security()
            employee = self.cv_digital_id.employee_id
            legajo = self.env['onsc.legajo'].sudo().search([('employee_id', '=', employee.id)], limit=1)

            if legajo.legajo_state != 'active':
                # SOLO DEBE ACTUALIZAR SECCIONES SI EL LEGAJO ESTA ACTIVO. DE LO CONTRARIO DE LA ACTUALIZACION SE
                # ENCARGA LA ACTIVACION DE LEGAJO MEDIANTE LOS CONTRATOS. EJ: ALTAVL Y ALTACS
                return True

            # SI EXISTE YA UN RECORD ASOCIADO ACTUALIZO
            if self.cv_digital_id.type == 'call' and self.original_instance_identifier:
                origin_record_id = self.original_instance_identifier
            else:
                origin_record_id = self.id
            legajo_record = LegajoModel.search([
                ('employee_id', '=', employee.id),
                ('origin_record_id', '=', origin_record_id),
            ], limit=1)
            # si ya esta el record de legajo actualizo
            if legajo_record:
                legajo_record_vals = self.copy_data()
                legajo_record_vals = self._update_legajo_record_vals(legajo_record_vals[0])
                legajo_record.with_context(is_legajo_record=True).write(legajo_record_vals)
            # sino creo uno nuevo
            else:
                legajo_record_vals = self.copy_data(default={
                    'employee_id': employee.id,
                    'legajo_id': legajo.id,
                    'origin_record_id': origin_record_id
                })
                LegajoModel.with_context(is_legajo_record=True).create(legajo_record_vals)
        return True

    def _update_legajo_record_vals(self, vals):
        """
        METODO PARA EXTENDER EN OTRAS ENTIDADES SI SE PRECISA AJUSTAR INFORMACION A GUARDAR EN EL RECORD DE LEGAJO
        :param vals:
        :return:
        """
        return vals

    def documentary_reject(self, reject_reason):
        args = {
            'documentary_validation_state': 'rejected',
            'documentary_reject_reason': reject_reason,
            'documentary_validation_date': fields.Date.today(),
            'documentary_user_id': self.env.user.id,
        }
        self.update_call_instances(args)
        return super(ONSCCVAbstractFileValidation, self).documentary_reject(reject_reason)

    def update_call_instances(self, args):
        if hasattr(self, 'cv_digital_id'):
            Calls = self.env['onsc.cv.digital.call']
            for record in self.filtered(lambda x: x.original_instance_identifier == 0 and x.cv_digital_id.type == 'cv'):
                # OBTENIENDO LLAMADOS DEL CV
                calls = Calls.with_context(unactive_user_config=True).search([
                    ('cv_digital_origin_id', '=', record.cv_digital_id.id),
                    ('is_zip', '=', False),
                    ('preselected', '!=', 'no'),
                ])
                # OBTENIENDO RECORDSETS ASOCIADOS A LLAMADOS Y QUE TENGAN COMO ORIGEN EL RECORD
                recordsets = self.search([
                    ('original_instance_identifier', '=', record.id),
                    ('cv_digital_id', 'in', calls.mapped('cv_digital_id').ids),
                    ('create_date', '>=', record.custom_write_date)])
                if args.get('documentary_validation_state') == 'rejected':
                    recordsets.documentary_reject(args.get('documentary_reject_reason'))
                elif args.get('documentary_validation_state') == 'to_validate':
                    recordsets.button_documentary_tovalidate()
                else:
                    recordsets.button_documentary_approve()
                calls.button_update_documentary_validation_sections_tovalidate()
            self._update_call_documentary_validation_status()

    def _update_call_documentary_validation_status(self):
        if self._fields.get('cv_digital_id'):
            self.mapped('cv_digital_id').button_legajo_update_documentary_validation_sections_tovalidate()
