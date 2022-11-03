# -*- coding: utf-8 -*-

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request


class EmployeeChart(http.Controller):

    @http.route('/get/parent/colspan', type='json', auth='public', method=['POST'], csrf=False)
    def get_col_span(self, emp_id):
        if emp_id:
            employee = request.env['hr.department'].sudo().browse(int(emp_id))
            if employee.child_ids:
                child_count = len(employee.child_ids) * 2
                return child_count

    @http.route('/get/parent/employee', type='json', auth='public', method=['POST'], csrf=False)
    def get_employee_ids(self):
        parent_id = request.params.get('operating_unit_id')
        operatin_unit = request.env['operating.unit'].sudo().search([('id', '=', parent_id)])
        names = []
        key = []
        if len(operatin_unit) == 1:
            key.append(operatin_unit.id)
            key.append(len(request.env['hr.department'].sudo().search([('operating_unit_id', '=', parent_id), ('parent_id', '=', False)])))
            return key
        elif len(operatin_unit) == 0:
            raise UserError(
                "Should not have manager for the employee in the top of the chart")
        else:
            for emp in operatin_unit:
                names.append(emp.name)
            raise UserError(
                "These Operative unit have no Manager %s" % (names))

    def get_lines(self, loop_count):
        if loop_count:
            lines = """<tr class='lines'><td colspan='""" + str(loop_count) + """'>
                <div class='downLine'></div></td></tr><tr class='lines'>"""
            for i in range(0, loop_count):
                if i % 2 == 0:
                    if i == 0:
                        lines += """<td class="rightLine"></td>"""
                    else:
                        lines += """<td class="rightLine topLine"></td>"""
                else:
                    if i == loop_count-1:
                        lines += """<td class="leftLine"></td>"""
                    else:
                        lines += """<td class="leftLine topLine"></td>"""
            lines += """</tr>"""
            return lines

    def get_hierarchycal_structure(self, root_node, tree):
        if not root_node.child_ids:
            tree[root_node.id] = ''
        else:
            for node in root_node.child_ids:
                tree[root_node.id][node.id] = {}
                self.get_hierarchycal_structure(node, tree[root_node.id])

    def get_hierarchycal_structure2(self, root_node, visited_nodes, presponsible, base_node):
        tree = ''
        if not root_node.parent_id:
            adjunt = ''
            for ajunt_node in root_node.child_ids.filtered(
                    lambda x: x.function_nature in ['comite']
            ):
                visited_nodes.append(ajunt_node.id)
                adjunt_name = ajunt_node.name if not ajunt_node.show_short_name else ajunt_node.short_name
                if presponsible:
                    adjunt_name += f'\n{ajunt_node.manager_id and ajunt_node.manager_id.name or ""}'
                adjunt += f'<adjunct>{adjunt_name}</adjunct>'
            root_name = root_node.name if not root_node.show_short_name else root_node.short_name
            if presponsible:
                responsible = root_node.manager_id and root_node.manager_id.name or ""
                if responsible:
                    responsible = f'<span class="reponsible">{responsible}</span>'
                root_name += f'{responsible}'
            tree += f'<ul id="organisation" class="d-none"><li>{adjunt}<em>{root_name}</em>'
            visited_nodes.append(root_node.id)
        if root_node.parent_id and root_node.function_nature in ['comite'] and root_node.id not in visited_nodes:
            rnode_name = root_node.name if not root_node.show_short_name else root_node.short_name
            if presponsible:
                responsible = root_node.manager_id and root_node.manager_id.name or ""
                if responsible:
                    responsible = f'<span class="reponsible">{responsible}</span>'
                root_name += f'{responsible}'
            return f'<adjunct>{rnode_name}</adjunct>'
        if not root_node.child_ids:
            return ''
        if base_node.id not in visited_nodes:
            root_name = base_node.name if not base_node.show_short_name else base_node.short_name
            if presponsible:
                responsible = base_node.manager_id and base_node.manager_id.name or ""
                if responsible:
                    responsible = f'<span class="reponsible">{responsible}</span>'
                root_name += f'{responsible}'
            tree += f'<ul id="organisation" class="d-none"><li>{root_name}'
        tree += "<ul>"
        for node in root_node.child_ids.filtered(lambda x: x.id not in visited_nodes):
            node_name = node.name if not node.show_short_name else node.short_name
            if presponsible:
                responsible = node.manager_id and node.manager_id.name or ""
                if presponsible:
                    responsible = f'<span class="reponsible">{responsible}</span>'
                node_name += f'{responsible}'
            tree += f'<li>{node_name}' if not node.function_nature == 'program' else f'<li class="program">{node_name}'
            tree += self.get_hierarchycal_structure2(node, visited_nodes, presponsible, base_node)
            visited_nodes.append(node.id)
        tree += "</ul>"
        tree += '</li>'
        return tree

    def get_nodes(self, child_ids):
        # if child_ids:
        #     child_nodes = """<tr>"""
        #     for child in child_ids:
        #         child_table = """<td colspan='""" + str(2) + """'>
        #             <table><tr><td><div>"""
        #         view = """ <div id='""" + str(child.id) + """' class='o_level_1'><a>
        #             <div id='""" + str(child.id) + """' class="o_employee_border">
        #             <div class='img'/></div>
        #             <div class='employee_name'><p>""" + str(child.name) + """</p>
        #             <p>""" + str(child.manager_id.name or "Sin Manager") + """</p></div></a></div>"""
        #         child_nodes += child_table + view + """</div></td></tr></table></td>"""
        #     nodes = child_nodes + """</tr>"""
        #     return nodes
        levels = request.env['onsc.catalog.hierarchical.level'].sudo().search(
            [])
        trs = ''
        for level in levels:
            trs += """
                    <tr style='width:100%;border-top:4px dashed blue;'>
                    A demonstration on how to add a top border. """ + level.name + """
                    </tr>"""
        table = """<table>""" + trs + """</table>"""
        return table

    @http.route('/get/organizational/level', type='json', auth='user', method=['POST'], csrf=False)
    def get_parent_child(self, **post):
        operating_unit_id = post.get('operating_unit_id', False)
        department_id = post.get('department_id', False)
        responsible = post.get('responsible')
        domain = [('operating_unit_id', '=', operating_unit_id)]
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
        organization_data_tree = ''
        visited_nodes = []
        tree = self.get_hierarchycal_structure2(
            root_node, visited_nodes, responsible, root_node
        )
        organization_data_tree += f'{tree}</li></ul>'
        organization_data = {}
        in_organization = []
        # for level in levels:
        #     organization_data[level.id] = {
        #         'name': level.name,
        #         'code': level.code,
        #         'parents': {},
        #     }
        #     nodes_by_level = request.env['hr.department'].sudo().search(
        #         [
        #             ('operating_unit_id', '=', operating_unit_id),
        #             ('hierarchical_level_id', '=', level.id),
        #         ], order='id asc, parent_id asc'
        #     )
        #     parents_groups = [
        #         group['parent_id'] for group in
        #         request.env['hr.department'].read_group(
        #             [
        #                 (
        #                     'parent_id',  'in', nodes_by_level.mapped(
        #                         'parent_id.id'
        #                     )
        #                 ),
        #                 ('id', 'not in', in_organization)
        #             ],
        #             ['parent_id'],
        #             ['parent_id']
        #         )
        #     ] or [False]
        #     for parent in parents_groups:
        #         if not parent:
        #             parent_id = False
        #             nodes = nodes_by_level
        #             if nodes_by_level:
        #                 organization_data[level.id]['parents'].update({False: {
        #                     'name': nodes_by_level[0].name,
        #                     'nodes': []
        #                 }})
        #         else:
        #             parent_id = parent and parent[0] or False
        #             nodes = request.env['hr.department'].search(
        #                 [('parent_id', '=', parent_id)]
        #             )
        #             organization_data[level.id]['parents'][parent_id] = {
        #                 'name': parent[1],
        #                 'nodes': []
        #             }
        #         for node in nodes:
        #             in_organization.append(node.id)
        #             organization_data[level.id]['parents'][parent_id][
        #                 'nodes'
        #             ].append(
        #                 {
        #                     'name': node.name,
        #                     'parent_id': node.parent_id and node.parent_id.id or False,
        #                     'level': level.id,
        #                     'id': node.id,
        #                     'relation': f'ID: {node.id} -> PARENT: {node.parent_id.id}',
        #                     'metadata': {
        #                         'operating_unit_id': node.operating_unit_id.id,
        #                         'code': node.code,
        #                         'inciso_id': node.inciso_id.id,
        #                     }
        #                 }
        #             )
        return {'data': organization_data, 'tree': organization_data_tree}

    @http.route('/get/child/data', type='json', auth='user', method=['POST'], csrf=False)
    def get_child_data(self, click_id):
        if click_id:
            employee = request.env['hr.department'].sudo().browse(int(click_id))
            if employee.child_ids:
                child_count = len(employee.child_ids) * 2
                value = [child_count]
                lines = self.get_lines(child_count)
                nodes = self.get_nodes(employee.child_ids)
                child_table = nodes + lines
                value.append(child_table)
                return child_table

