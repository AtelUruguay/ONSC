# -*- coding: utf-8 -*-
from odoo import http
from odoo.exceptions import UserError
from odoo.http import request


class EmployeeChart(http.Controller):

    @http.route('/get/organizational/level', type='json', auth='user', method=['POST'], csrf=False)
    def get_parent_child(self, **post):
        operating_unit_id = post.get('operating_unit_id', False)
        department_id = post.get('department_id', False)
        responsible = post.get('responsible')
        # end_date = post.get('end_date', False)
        form_id = request.env.ref('onsc_catalog.onsc_catalog_department_form').id
        domain = [
            ('operating_unit_id', '=', operating_unit_id),
        ]
        # if end_date:
        #     domain.extend(
        #         [
        #             # '|',
        #             ('end_date', '>=', end_date),
        #             # ('end_date', '=', False),
        #
        #         ]
        #     )
        levels = request.env['onsc.catalog.hierarchical.level'].sudo().search([])
        if department_id:
            domain.extend(['|', ('id', 'child_of', int(department_id)), ('id', '=', int(department_id))])
        nodes_by_level = request.env['hr.department'].sudo().search(
            domain, order='id asc, parent_id asc'
        )
        root_node = nodes_by_level.filtered(
            lambda node: not node.parent_id
        ) or (len(nodes_by_level) and nodes_by_level[0] or [])
        if len(root_node) > 1:
            root_node = root_node[0]
        if not root_node:
            raise UserError(
                "No tiene datos para mostrar"
            )
        levels_result = []
        if not root_node.parent_id:
            if root_node.hierarchical_level_order != 1:
                level_ids = []
                for level in levels:
                    if level.order < root_node.hierarchical_level_order:
                        level_ids.append(level.order - 1)
                    else:
                        break
                levels_result = [('', level_ids)]
                levels_result.extend((level.name, [level.order - 1]) for level in levels if
                                     level.order >= root_node.hierarchical_level_order)
            else:
                levels_result.extend((level.name, [level.order - 1]) for level in levels)

        items = []
        for node in nodes_by_level.filtered(
                lambda node: node.function_nature not in ('comite', 'commission_project', 'adviser')):
            last_parent = node.parent_id.id
            if not root_node.parent_id and node.parent_id and node.hierarchical_level_order - node.parent_id.hierarchical_level_order != 1:
                for level_order in range(node.hierarchical_level_order - node.parent_id.hierarchical_level_order - 1):
                    dummy_item = {
                        'id': f'dummy-{level_order}-{node.id}',
                        'parent': last_parent,
                        'isVisible': False,
                        'short_name': node.short_name,
                        'responsible': node.manager_id.name or '',
                        'responsibleEmpty': '',
                        'title': node.name
                    }
                    items.append(dummy_item)
                    last_parent = dummy_item['id']
            item = {
                'id': node.id,
                'parent': last_parent,
                'form_id': form_id,
                'isVisible': True,
                'short_name': node.short_name,
                'responsible': node.manager_id.name or '',
                'responsibleEmpty': '',
                'title': node.name,
                'show_responsible': responsible,
                'templateName': 'contactTemplate' if not responsible or not node.manager_id else 'contactTemplateResponsible',
                'showShortName': node.show_short_name,
            }
            items.append(item)
        right_left = 'right'
        assistances = nodes_by_level.filtered(
            lambda node: not root_node.parent_id and node.function_nature in (
                'comite', 'commission_project', 'adviser'))
        levelOffset = 0
        for assistant in assistances:
            item = {
                'id': assistant.id,
                'parent': root_node.id,
                'isVisible': True,
                'form_id': form_id,
                'short_name': assistant.short_name,
                'responsible': assistant.manager_id.name or '',
                'responsibleEmpty': '',
                'show_responsible': responsible,
                'title': assistant.name,
                'itemType': 'Assistant' if assistant.function_nature == 'adviser' else 'SubAssistant',
                'adviserPlacementType': right_left,
                'templateName': 'contactTemplate' if not responsible or not assistant.manager_id else 'contactTemplateResponsible',
                'levelOffset': levelOffset,
                'showShortName': assistant.show_short_name,
            }
            levelOffset = levelOffset + 1 if levelOffset // 2 == 0 else levelOffset
            items.append(item)
            right_left = 'left' if right_left == 'right' else 'right'
        return {'levels': levels_result, 'items': items, 'responsible': responsible}
