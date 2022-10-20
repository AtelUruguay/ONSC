odoo.define('hr_organizational_chart.view_chart', function (require){
"use strict";
var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var core = require('web.core');
var rpc = require('web.rpc');
var _t = core._t;
var pathNumber = 1;
var allLinks = [];

// scg path params
var strokeWidth = '5px';

var EmployeeOrganizationalChart =  AbstractAction.extend({

    contentTemplate: 'OrganizationalEmployeeChart',
    events: {
        'click .o_employee_border': '_getChild_data',
        'click .employee_name': 'view_employee',
        'click .node': '_onClickNodeText',
    },

    init: function(parent, context) {

        this._super(parent, context);
        const operating_unit_id = context.params.operating_unit_id
        this.renderEmployeeDetails(operating_unit_id);
    },
    getOffset: function(el) {
      const rect = el.getBoundingClientRect();
      return {
        left: rect.left + window.pageXOffset,
        top: rect.top + window.pageYOffset,
        width: rect.width || el.offsetWidth,
        height: rect.height || el.offsetHeight
      };
    },

    connect: function(div1, div2, color, thickness) {
      const off1 = this.getOffset(div1);
      const off2 = this.getOffset(div2);

      const x1 = off1.left + off1.width;
      const y1 = off1.top + off1.height;

      const x2 = off2.left + off2.width;
      const y2 = off2.top;

      const length = Math.sqrt(((x2 - x1) * (x2 - x1)) + ((y2 - y1) * (y2 - y1)));

      const cx = ((x1 + x2) / 2) - (length / 2);
      const cy = ((y1 + y2) / 2) - (thickness / 2);

      const angle = Math.atan2((y1 - y2), (x1 - x2)) * (180 / Math.PI);

      const htmlLine = "<div class='line-path' style='padding:0px; margin:0px; height:" + thickness + "px; background-color:" + color + "; line-height:1px; position:absolute; left:" + cx + "px; top:" + cy + "px; width:" + length + "px; -moz-transform:rotate(" + angle + "deg); -webkit-transform:rotate(" + angle + "deg); -o-transform:rotate(" + angle + "deg); -ms-transform:rotate(" + angle + "deg); transform:rotate(" + angle + "deg);' />";

      document.body.innerHTML += htmlLine;
    },

//    const d1 = document.getElementById('d1')
//    const d2 = document.getElementById('d2')
//    connect(d1, d2, 'green', 5)
    _toggleDisplayNode: function(node){
        let self = this;
        const {id} = node.data();
        const childs = $('*[data-parent="'+id+'"]');
        if (childs.length === 0){
            if($(node).hasClass('d-none')){
            	$(node).removeClass('d-none');
            }
            else{
            	$(node).addClass('d-none');
            }
        }
        $.each(childs, (index, element) => {
//            if($(element).hasClass('d-none')){
//                $(element).removeClass('d-none');
//            }
//            else{
//                $(element).addClass('d-none');
//            }
            self._toggleDisplayNode($(element))
        });


    },
    _onClickNodeText: function(event) {
        let self = this;
        const {parent, id} = $(event.target).data();
        console.log(id, parent);
        const childs = $('*[data-parent="'+id+'"]');
        $.each(childs, (index, element) => {
            if($(element).hasClass('d-none')){
            	$(element).removeClass('d-none');
            }
            else{
            	$(element).addClass('d-none');
            }
            self._toggleDisplayNode($(element));
        });

    },
    iterate: function(tree, start, from) {
        let self = this;
        const strokeColor = Math.floor(Math.random()*16777215).toString(16);
        const svgContainer = document.getElementById('tree__svg-container__svg');
        const treeContainer = document.createElement('div');
        treeContainer.classList.add('tree__container__branch', `from_${from}`);
        document.getElementById(from).after(treeContainer);

        for (const key in tree) {
//            const textCard = treeParams[key] !== undefined && treeParams[key].trad !== undefined ? treeParams[key].trad : key;
//
//            if (!document.getElementById(`card_${key}`)){
//                treeContainer.innerHTML += `<div class="tree__container__step"><div class="tree__container__step__card" id="${key}"><p id="card_${key}" class="tree__container__step__card__p">${textCard}</p></div></div>`;
//                addStyleToCard(treeParams[key], key);
//            }

            if ((from && !start) || start){
                const newPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
                newPath.id = "path" + pathNumber;
                newPath.setAttribute('stroke', "#" + strokeColor);
                newPath.setAttribute('fill', 'none');
                newPath.setAttribute('stroke-width', strokeWidth);
                newPath.setAttribute('color', "red");
                svgContainer.appendChild(newPath);
                allLinks.push(['path' + pathNumber, from ? from : 'tree__container__step__card__first', key]);
                pathNumber++;
            }

            if (Object.keys(tree[key]).length > 0) {
                self.iterate(tree[key], false, key);
            }
        }
    },
    drawPath: function (svg, path, startX, startY, endX, endY) {
        // get the path's stroke width (if one wanted to be  really precize, one could use half the stroke size)
        let stroke = parseFloat(path.getAttribute("stroke-width"));
        // check if the svg is big enough to draw the path, if not, set heigh/width
        if (svg.getAttribute("height") < endY) svg.setAttribute("height", endY);
        if (svg.getAttribute("width") < (startX + stroke)) svg.setAttribute("width", (startX + stroke));
        if (svg.getAttribute("width") < (endX + stroke)) svg.setAttribute("width", (endX + stroke));

        let deltaX = (endX - startX) * 0.15;
        let deltaY = (endY - startY) * 0.15;
        // for further calculations which ever is the shortest distance
        let delta = deltaY < absolute(deltaX)
            ? deltaY
            : absolute(deltaX);

        // set sweep-flag (counter/clock-wise)
        // if start element is closer to the left edge,
        // draw the first arc counter-clockwise, and the second one clock-wise
        let arc1 = 0;
        let arc2 = 1;
        if (startX > endX) {
            arc1 = 1;
            arc2 = 0;
        }
        // draw tha pipe-like path
        // 1. move a bit down, 2. arch,  3. move a bit to the right, 4.arch, 5. move down to the end
        path.setAttribute("d", "M" + startX + " " + startY + " V" + (startY + delta) + " A" + delta + " " + delta + " 0 0 " + arc1 + " " + (startX + delta * signum(deltaX)) + " " + (startY + 2 * delta) + " H" + (endX - delta * signum(deltaX)) + " A" + delta + " " + delta + " 0 0 " + arc2 + " " + endX + " " + (startY + 3 * delta) + " V" + endY);
    },

     connectElements: function(svg, path, startElem, endElem) {
        const svgContainer = document.getElementById('tree__svg-container');

        // if first element is lower than the second, swap!
        if (startElem.offsetTop > endElem.offsetTop) {
            const temp = startElem;
            startElem = endElem;
            endElem = temp;
        }

        // get (top, left) corner coordinates of the svg container
        const svgTop = svgContainer.offsetTop;
        const svgLeft = svgContainer.offsetLeft;

        // calculate path's start (x,y)  coords
        // we want the x coordinate to visually result in the element's mid point
        const startX = startElem.offsetLeft + 0.5 * startElem.offsetWidth - svgLeft;    // x = left offset + 0.5*width - svg's left offset
        const startY = startElem.offsetTop + startElem.offsetHeight - svgTop;        // y = top offset + height - svg's top offset

        // calculate path's end (x,y) coords
        const endX = endElem.offsetLeft + 0.5 * endElem.offsetWidth - svgLeft;
        const endY = endElem.offsetTop - svgTop;

        // call function for drawing the path
        this.drawPath(svg, path, startX, startY, endX, endY);
    },
    connectCard: function () {
        // magic
        const svg = document.getElementById('tree__svg-container__svg');
        for (let i = 0; allLinks.length > i; i++) {
            this.connectElements(svg, document.getElementById(allLinks[i][0]), document.getElementById(allLinks[i][1]), document.getElementById(allLinks[i][2]));
//            this.connect(document.getElementById(allLinks[i][1]), document.getElementById(allLinks[i][2]), 'green', 5);
        }
    },
    renderEmployeeDetails: function (operating_unit_id){
        var employee_id = 1
        var self = this;
        this._rpc({
            route: '/get/organizational/level',
            params: {'operating_unit_id': operating_unit_id}
        }).then(function (result) {
                const svgDiv = document.createElement('div');
                svgDiv.id = 'tree__svg-container';
                $('#o_parent_employee').append(svgDiv);
                const svgContainer = document.createElementNS("http://www.w3.org/2000/svg", "svg");
                svgContainer.id = 'tree__svg-container__svg';
                svgDiv.append(svgContainer);
            const {data, tree} = result;
            const levels = Object.entries(data);
            levels.map((level) => {
                const tr = document.createElement("div");
                tr.className = "row level"

                const div_level = document.createElement('div');
                div_level.className = "div-level";
                const text_level = document.createElement('span');
                text_level.appendChild(document.createTextNode(level[1]['name']));
                text_level.className = "text-level";
                div_level.appendChild(text_level);
                const parents = Object.entries(level[1]['parents']);
                const width = 100 / parents.length;
                parents.forEach((parent) => {
                    const div_parent = document.createElement('div');
                    div_parent.style.width = width + ' %';
                    div_parent.setAttribute('style','max-width:'+width+'%');
                    div_parent.className = "div-parent";
                    div_parent.id = parent[0] === 'false' ? 'tree__container__step__card__first' : '';
                    tr.appendChild(div_parent);
                    parent[1]['nodes'].forEach((node) => {
                        if(node['id'] !== parent[0]){
                        const child = document.createElement("div");
                        child.className = "col node";
                        child.id = node['id'];
                        child.setAttribute("data-id", node['id']);
                        child.setAttribute("data-parent", node['parent_id']);
                        const nodeText = document.createElement("div");
                        nodeText.className = "node-text";

                        nodeText.appendChild(document.createTextNode(node['name']));
                        child.appendChild(nodeText);
                        div_parent.appendChild(child);
                        }
                    });
                });
                const div_content = document.createElement('div');
                div_content.className = "div-content row";
                div_content.appendChild(div_level);
                div_content.appendChild(tr);
                $('#o_parent_employee').append(
                  div_content
                );
            });
            self.iterate(tree[Object.keys(tree)[0]], true, 'tree__container__step__card__first');

            self.connectCard();
            window.onresize = function () {
                $('.line-path').remove();
                svgDiv.setAttribute('height', '0');
                svgDiv.setAttribute('width', '0');
                self.connectCard();
            };

        });

    },

    view_employee: function(ev){
        if (ev.target.parentElement.className){
            var id = parseInt(ev.target.parentElement.parentElement.children[0].id)
            this.do_action({
            name: _t("Employee"),
            type: 'ir.actions.act_window',
            res_model: 'hr.department',
            res_id: id,
            view_mode: 'form',
            views: [[false, 'form']],
            })
        }
    },
});
    core.action_registry.add('organization_dashboard', EmployeeOrganizationalChart);

});
