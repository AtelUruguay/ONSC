# -*- coding: utf-8 -*-
from odoo import http
from odoo.exceptions import UserError
from odoo.http import request


class EmployeeChart(http.Controller):

    def get_hierarchy_trees(self, root_node, nodes_by_level, form_id, responsible):

        items = []
        for node in nodes_by_level.filtered(
                lambda node: node.function_nature not in (
                'comite', 'commission_project', 'adviser', 'program')):
            last_parent = node.parent_id.id
            if node.hierarchical_level_order - node.parent_id.hierarchical_level_order != 1:
                for level_order in range(
                        node.hierarchical_level_order - node.parent_id.hierarchical_level_order - 1):
                    dummy_item = {
                        'id': f'dummy-{level_order}-{node.id}',
                        'parent': last_parent,
                        'isVisible': True,
                        'isActive': False,
                        'short_name': node.short_name,
                        'responsible': node.manager_id.name or '',
                        'responsibleEmpty': '',
                        'title': node.name,
                        'templateName': 'dummyTemplateItem'
                    }
                    items.append(dummy_item)
                    last_parent = dummy_item['id']
            item = {
                'id': node.id,
                'parent': last_parent,
                'form_id': form_id,
                'isVisible': True,
                'short_name': node.name,
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
                'comite', 'adviser', 'program'))
        levelOffset = 0
        for assistant in assistances:
            template = 'contactTemplate' if not responsible or not assistant.manager_id else 'contactTemplateResponsible'
            itemType = 'Assistant'
            if assistant.function_nature == 'comite':
                template = 'contactTemplateDashed' if not responsible or not assistant.manager_id else 'contactTemplateDashedResponsible'
                itemType = 'SubAdviser'
            elif assistant.function_nature == 'program':
                itemType = 'SubAssistant'
            item = {
                'id': assistant.id,
                'parent': root_node.id,
                'isVisible': True,
                'form_id': form_id,
                'short_name': assistant.name,
                'responsible': assistant.manager_id.name or '',
                'responsibleEmpty': '',
                'show_responsible': responsible,
                'title': assistant.name,
                'itemType': itemType,
                'adviserPlacementType': right_left,
                'templateName': template,
                'levelOffset': levelOffset,
                'showShortName': assistant.show_short_name,
            }
            levelOffset = levelOffset + 1 if levelOffset // 2 == 0 else levelOffset
            items.append(item)
            right_left = 'left' if right_left == 'right' else 'right'
        return items, responsible

    @http.route('/get/organizational/operating_unit', type='json', auth='user',
                method=['POST'], csrf=False)
    def get_operating_unit(self, **post):
        operating_unit_id = post.get('id', False)
        ou_id = request.env['hr.department'].browse(operating_unit_id)
        if not ou_id:
            return {}
        return {
            'code': ou_id.code or '',
            'parentName': ou_id.parent_id.name or '',
            'inciso': ou_id.inciso_id.name or '',
            'OU': ou_id.operating_unit_id.name or '',
            'hierarchy': ou_id.hierarchical_level_id.name or '',
            'responsible': ou_id.manager_id.name or '',
            'function_nature': dict(ou_id._fields['function_nature'].selection).get(ou_id.function_nature) or '',
        }

    @http.route('/get/organizational/level', type='json', auth='user', method=['POST'], csrf=False)
    def get_parent_child(self, **post):
        operating_unit_id = post.get('operating_unit_id', False)
        department_id = post.get('department_id', False)
        responsible = post.get('responsible')
        end_date = post.get('end_date', False)
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
        nodes_by_level = request.env['hr.department'].sudo().with_context(as_of_date=end_date).search(
            domain, order='id asc, parent_id asc'
        )
        root_nodes = nodes_by_level.filtered(
            lambda node: not node.parent_id
        ) or (len(nodes_by_level) and nodes_by_level[0] or [])
        if not root_nodes:
            raise UserError(
                "No tiene datos para mostrar"
            )
        levels_result = []
        items_joined = []

        for root_node in root_nodes:
            parents = list(map(lambda r: int(r), filter(lambda c: c != '', root_node.parent_path.split('/'))))
            nodes_parent = request.env['hr.department'].sudo().with_context(
                as_of_date=end_date).search(
                ['|', ('id', 'child_of', root_node.id), ('id', 'in', parents)], order='id asc, parent_id asc'
            )
            # if not root_node.parent_id:
            # if root_node.hierarchical_level_order != 1:
            #     level_ids = [level.order - 1 for level in levels if level.order < root_node.hierarchical_level_order]
            #
            #     levels_result = [('', level_ids)]
            #     levels_result.extend(
            #         (level.name, [level.order - 1]) for level in levels if
            #         level.order >= root_node.hierarchical_level_order)
            # else:
            levels_result.extend(
                (level.name, [level.order - 1]) for level in levels if (level.name, [level.order - 1]) not in levels_result)
            items, responsible = self.get_hierarchy_trees(root_node, nodes_parent, form_id, responsible)
            items_joined.extend(items)
        return {'levels': levels_result, 'items': items_joined,
                'responsible': responsible}
