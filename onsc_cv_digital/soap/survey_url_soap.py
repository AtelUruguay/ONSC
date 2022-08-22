# © 2018 Quanam (ATEL SA., Uruguay)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.addons.ws_int_base.utils.service_registration \
    import register_service
from spyne import ServiceBase, ComplexModelBase
from spyne import Unicode, Array, Integer, Float
from spyne import rpc
from spyne.model.fault import Fault

import odoo
from odoo import _, fields
from odoo import api, SUPERUSER_ID
from odoo.exceptions import UserError as InternalError
from odoo.modules.registry import Registry

_logger = logging.getLogger(__name__)

NAMESPACE_BASE = "http://quanam.com/encuestas/abc/"
NAMESPACE_BASE_V1 = NAMESPACE_BASE


def get_children(env, node):
    HsNode = env['hs.node']
    children_ids = HsNode.search([('parent_id', '=', node.id)])
    no_more_child = False
    if children_ids:
        new_children = children_ids
        while not no_more_child:
            more_child = HsNode.search([('parent_id', 'in', new_children.ids)])
            if not more_child:
                no_more_child = True
            else:
                children_ids |= more_child
                new_children = more_child

    return children_ids


class BaseComplexType(ComplexModelBase):
    __namespace__ = NAMESPACE_BASE_V1


class UsuarioNoAutorizado(Fault):
    __namespace__ = NAMESPACE_BASE_V1
    __type_name__ = 'UsuarioNoAutorizado'

    def __init__(self):
        super(UsuarioNoAutorizado, self). \
            __init__(faultcode='Server.005',
                     detail=_(
                         "Usuario no autorizado para la operacion."))


class ResultSurveyUrl(BaseComplexType):
    _type_info = {
        'url': Unicode(min_occurs=0),
        'fault_code': Integer(),
        'response_code': Integer(),
        'log_table': Integer(),
        'menssages': Array(Unicode)
    }
    _type_info_alt = []


class ResultSurveyGetAverage(BaseComplexType):
    _type_info = {
        'promedio': Float(min_occurs=1),
        'cantidad_respuestas': Integer(),
        'cantidad_no_dada': Integer(),
        'tipo_respuestas': Array(Unicode),
        'max_puntaje': Float(),
        'fault_code': Integer(),
        'response_code': Integer(),
        'messages': Array(Unicode)
    }
    _type_info_alt = []


def build_survey_get_average(promedio, cantidad_respuestas,
                             cantidad_no_dada, tipo_respuestas,
                             max_puntaje, fault_code, response_code, messages):
    return ResultSurveyGetAverage(
        promedio=promedio,
        cantidad_respuestas=cantidad_respuestas,
        cantidad_no_dada=cantidad_no_dada,
        tipo_respuestas=tipo_respuestas,
        max_puntaje=max_puntaje,
        messages=messages,
        fault_code=fault_code,
        response_code=response_code
    )


class WsSurveyUrl(ServiceBase):
    """Survey class to Webservice url"""

    __service_url_path__ = 'devolver_encuesta'
    __target_namespace__ = NAMESPACE_BASE_V1

    uid = 0

    @rpc(Unicode, Unicode, Unicode, Unicode,
         Unicode, _returns=ResultSurveyUrl)
    def devolver_encuesta(
            self, cod_estructura, cod_nodo,
            id_instancia, id_persona, email
    ):
        """WS Devolver encuesta"""
        dbname = list(Registry.registries.d)[0]
        uid = SUPERUSER_ID
        try:
            registry = odoo.registry(dbname)
            cr = registry.cursor()
            env = api.Environment(cr, uid, {})
            Control = env['survey.hierarchical.control']
            UserInput = env['survey.user_input']
            Maintanment = env['hs.node.maintanment']
            base_url = env['ir.config_parameter'].sudo().get_param(
                'survey_extend.survey_url')
            if not cod_estructura or not cod_nodo:
                msg_node = "El código del Nodo es obligatorio"
                msg_hs = "El código de la Estructura Jerárquica es obligatorio"
                msg = cod_estructura and msg_node or msg_hs
                return ResultSurveyUrl(
                    url='',
                    menssages=[msg],
                    fault_code=404,
                    response_code=404,
                    log_table=0
                )

            # # Check if survey was sended with same code and transaction.
            control_id = Control.search(
                [
                    ('hs_code', '=', cod_estructura),
                    ('node_code', '=', cod_nodo),
                    ('node_id', '!=', False),
                    ('transaction', '=', id_instancia),
                ], limit=1
            )
            if control_id:
                in_maintanment = Maintanment.search_count([
                    ('node_id', '=', control_id.node_id.id),
                    ('survey_id', '=', control_id.survey_id.id),
                    ('survey_id.stage_id', 'in', [2, 4]),
                    ('survey_id.abailable', '=', True),
                    ('is_active', '=', True),
                ])
                if in_maintanment:
                    return ResultSurveyUrl(
                        url=control_id.url,
                        menssages=["OK"],
                        fault_code=200,
                        response_code=200,
                        log_table=control_id.id
                    )
            # SI EXISTE EL NODO
            node = env['hs.node'].search(
                [
                    ('code', '=', cod_nodo),
                    ('hierarchical_structure_id.code', '=', cod_estructura)
                ], limit=1
            )
            if node:
                node_maintanment = Maintanment.search([
                    ('node_id', '=', node.id),
                    ('survey_id', '!=', False),
                    ('survey_id.stage_id', 'in', [2, 4]),
                    ('survey_id.abailable', '=', True),
                    ('is_active', '=', True)
                ], limit=1)
                # SI EXISTE EL NODO Y TIENE ENCUESTA ASIGNADA
                if node_maintanment:
                    survey = node_maintanment.survey_id
                    vals = {'survey_id': survey.id, 'state': 'new',
                            'type': 'link'}
                    user_input = UserInput.create(vals)
                    survey_url = base_url + '/survey/fill/%s/%s' % (
                        survey.id, user_input.token
                    )
                    obj = Control.create(
                        {
                            'node_id': node.id,
                            'ok_node_id': node.id,
                            'transaction': id_instancia,
                            'node_code': node.code,
                            'ok_node_code': node.code,
                            'hs_code': node.hierarchical_structure_id.code,
                            'token': user_input.token,
                            'url': survey_url,
                            'survey_id': survey.id,
                            'state': 'sended',
                            'line_ids': [
                                (
                                    0,
                                    0,
                                    {
                                        'state': 'sended',
                                        'date': fields.Datetime.now()
                                    }
                                )
                            ],
                        }
                    )

                    user_input.recompute_control()
                    return ResultSurveyUrl(
                        url=survey_url,
                        menssages=["OK"],
                        fault_code=200,
                        response_code=200,
                        log_table=obj.id
                    )
                # SI EXISTE EL NODO PERO NO TIENE ENCUESTA ASIGNADA
                else:
                    # Busca hacia arriba la primera encuesta genérica
                    current_node = node
                    generic = False
                    while current_node and not generic:
                        gnode_maintanment = Maintanment.search([
                            ('node_id', '=', current_node.id),
                            ('survey_id.generic', '=', True),
                            ('survey_id.stage_id', 'in', [2, 4]),
                            ('survey_id.abailable', '=', True),
                            ('is_active', '=', True)
                        ], limit=1)
                        if gnode_maintanment:
                            survey = gnode_maintanment.survey_id
                            generic = True
                        else:
                            current_node = current_node.parent_id
                    if not generic and node.generic_survey_id:
                        _logger.warning('Devuelve Encuestra genérica de la EJ')
                        survey = node.generic_survey_id
                        generic = True

                    # Si la encuentra
                    if generic:
                        # SI SE CUMPLE QUE EL CONTROL ENCONTRADO:
                        # - Respondió con el mismo nodo padre y
                        # se mantiene la misma encuesta entonces
                        # devolvemos esa misma respuesta
                        if control_id.ok_node_code == current_node.code and \
                                control_id.survey_id.id == survey.id:
                            return ResultSurveyUrl(
                                url=control_id.url,
                                menssages=[
                                    'No hay encuesta asignada al nodo, '
                                    'devuelve encuesta genérica de nodo '
                                    'superior.'],
                                fault_code=200,
                                response_code=301,
                                log_table=control_id.id
                            )
                        else:
                            vals = {'survey_id': survey.id, 'state': 'new',
                                    'type': 'link'}
                            user_input = UserInput.create(vals)
                            survey_url = base_url + '/survey/fill/%s/%s' % (
                                survey.id, user_input.token
                            )
                            obj = Control.create({
                                'node_id': node.id,
                                'ok_node_id': current_node.id,
                                'transaction': id_instancia,
                                'node_code': node.code,
                                'ok_node_code': current_node.code,
                                'hs_code': node.hierarchical_structure_id.code,
                                'token': user_input.token,
                                'url': survey_url,
                                'survey_id': survey.id,
                                'state': 'sended',
                                'line_ids': [
                                    (
                                        0,
                                        0,
                                        {
                                            'state': 'sended',
                                            'date': fields.Datetime.now()
                                        }
                                    )
                                ],
                            })
                            user_input.recompute_control()
                            return ResultSurveyUrl(
                                url=base_url + '/survey/fill/%s/%s' % (
                                    survey.id, user_input.token
                                ),
                                menssages=[
                                    'No hay encuesta asignada al nodo, '
                                    'devuelve encuesta genérica de nodo '
                                    'superior.'],
                                fault_code=200,
                                response_code=301,
                                log_table=obj.id
                            )
                    else:
                        # Si no la encuentra
                        return ResultSurveyUrl(
                            url='',
                            menssages=[
                                'No hay encuesta asignada al nodo ni a nodos '
                                'superiores.'
                            ],
                            fault_code=501,
                            response_code=501,
                            log_table=0
                        )
            else:
                # Si ID de nodo no existe o es vacío
                node_maintanment = Maintanment.search([
                    ('hierarchical_structure_id.code', '=', cod_estructura),
                    ('node_id.parent_id', '=', False),
                    ('survey_id.generic', '=', True),
                    ('survey_id.stage_id', 'in', [2, 4]),
                    ('survey_id.abailable', '=', True),
                    ('is_active', '=', True)
                ], limit=1)
                if node_maintanment:
                    # Si la encuentra se verifica que se haya solicitado
                    # con la misma info
                    control_id = Control.search(
                        [
                            ('hs_code', '=',
                             node_maintanment.hierarchical_structure_id.code),
                            (
                                'ok_node_code', '=',
                                node_maintanment.node_id.code),
                            ('node_id', '=', False),
                            ('transaction', '=', id_instancia),
                        ], limit=1
                    )
                    if control_id:
                        return ResultSurveyUrl(
                            url=control_id.url,
                            menssages=[
                                'Nodo inexistente. '
                                'Se asigna encuesta genérica de nodo raíz.'
                            ],
                            fault_code=200,
                            response_code=302,
                            log_table=control_id.id
                        )
                    else:
                        survey = node_maintanment.survey_id
                        current_node = node_maintanment.node_id
                        vals = {'survey_id': survey.id, 'state': 'new',
                                'type': 'link'}
                        user_input = UserInput.create(vals)
                        survey_url = base_url + '/survey/fill/%s/%s' % (
                            survey.id, user_input.token
                        )
                        Control.create({
                            'node_id': False,
                            'ok_node_id': current_node.id,
                            'transaction': id_instancia,
                            'node_code': cod_nodo,
                            'ok_node_code': current_node.code,
                            'hs_code':
                                current_node.hierarchical_structure_id.code,
                            'token': user_input.token,
                            'url': survey_url,
                            'survey_id': survey.id,
                            'state': 'sended',
                            'line_ids': [
                                (
                                    0,
                                    0,
                                    {
                                        'state': 'sended',
                                        'date': fields.Datetime.now()
                                    }
                                )
                            ],
                        })

                        user_input.recompute_control()
                        return ResultSurveyUrl(
                            url=survey_url,
                            menssages=[
                                'Nodo inexistente. '
                                'Se asigna encuesta genérica de nodo raíz.'
                            ],
                            fault_code=200,
                            response_code=302
                        )
                else:
                    # Si no la encuentra
                    return ResultSurveyUrl(
                        url='',
                        menssages=[
                            'Error: Nodo inexistente y no se encuentra '
                            'encuesta en nodo raíz.'],
                        fault_code=502,
                        response_code=502
                    )
        except Fault as e:
            cr.rollback()
            raise InternalError(e)
        except Exception as e:
            cr.rollback()
            raise InternalError(e)
        finally:
            cr.commit()
            cr.close()

    @rpc(Unicode, Unicode, Unicode,
         Unicode, Array(Unicode),
         Unicode, Unicode, _returns=ResultSurveyGetAverage)
    def promedio_pregunta(self, cod_estructura_jerarquica,
                          cod_prom_pregunta,
                          fecha_inicio,
                          fecha_fin,
                          nodos,
                          cant_minima_resp,
                          considerar_nodos_hijos):
        dbname = list(Registry.registries.d)[0]
        uid = SUPERUSER_ID
        registry = odoo.registry(dbname)
        cr = registry.cursor()
        env = api.Environment(cr, uid, {})
        return env['survey.average.code.test.wizard'].average_service_soap(
            cod_estructura_jerarquica,
            cod_prom_pregunta,
            fecha_inicio,
            fecha_fin,
            nodos,
            cant_minima_resp,
            considerar_nodos_hijos
        )


register_service(WsSurveyUrl)
