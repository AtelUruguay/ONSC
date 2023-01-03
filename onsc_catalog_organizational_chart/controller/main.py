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
        domain = [('operating_unit_id', '=', operating_unit_id)]
        levels = request.env['onsc.catalog.hierarchical.level'].sudo().search(
            [])
        if department_id:
            domain.extend(['|', ('parent_id', '=', int(department_id)), ('id', '=', int(department_id))])
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
        for node in nodes_by_level.filtered(lambda node: node.function_nature not in ('comite', 'commission_project')):
            last_parent = node.parent_id.id
            if node.parent_id and node.hierarchical_level_order - node.parent_id.hierarchical_level_order != 1:
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
                'isVisible': True,
                'short_name': node.short_name,
                'responsible': node.manager_id.name or '',
                'responsibleEmpty': '',
                'title': node.name,
                'templateName': 'contactTemplate'
            }
            items.append(item)
        right_left = 'right'
        assistances = nodes_by_level.filtered(
            lambda node: not root_node.parent_id and node.function_nature in (
                'comite', 'commission_project'))
        dummy_assistance_qty = 0 if len(assistances) <= 2 else len(
            assistances) // 2
        for index, assistant in enumerate(assistances):
            lastparent = root_node.id
            if dummy_assistance_qty >= 1 and index > 0 and (index + 1) % 2 != 0:
                dummy_item = {
                    'id': f'dummy-{lastparent}-{index}',
                    'parent': lastparent,
                    'isVisible': False,
                    'title': "Aggregator",
                    'description': "Invisible aggregator",
                    'childrenPlacementType': 'Horizontal'
                }
                items.append(dummy_item)
                lastparent = dummy_item['id']
            item = {
                'id': assistant.id,
                'parent': lastparent,
                'isVisible': True,
                'short_name': assistant.short_name,
                'responsible': assistant.manager_id.name or '',
                'responsibleEmpty': '',
                'title': assistant.name,
                'itemType': 'Assistant',
                'adviserPlacementType': right_left,
                'templateName': 'contactTemplate'
            }
            items.append(item)
            right_left = 'left' if right_left == 'right' else 'right'
        return {'levels': levels_result, 'items': items, 'responsible': responsible}
