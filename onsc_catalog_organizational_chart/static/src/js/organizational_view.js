odoo.define('onsc_catalog_organizational_chart.view_chart', function (require){
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
        'click .btn-downloadpdf': 'DownloadPDF',
        'click .button-hamb': 'toogleSideBar',
        'click #basicdiagram': 'closeSideBar',
        'click #slide-zoomout': 'onClickZoomOut',
        'click #slide-zoomin': 'onClickZoomIn',
        'click #goto-org-uo': 'onClickGotoUO',
        'change #myRange': 'onScale',
    },

    init: function(parent, context) {

        this._super(parent, context);
        const operating_unit_id = context.params.operating_unit_id;
        const department_id = context.params.department_id;
        const short_name = context.params.short_name;
        const end_date = context.params.end_date;
        const responsible = context.params.responsible || false;
        const inciso = context.params.inciso || '';
        const ue = context.params.ue || '';
        this.control = null;
        this.scale = 1;
        this.btnst = true;
        this.contentBtns = true;
        this.renderEmployeeDetails(
        operating_unit_id,
        department_id,
        short_name,
        responsible,
        end_date,
        inciso,
        ue
        );
    },
    onClickGotoUO: function(event) {
        var id = parseInt(event.currentTarget?.dataset?.id);
        var formId = parseInt(event.currentTarget?.dataset?.form);
        this.do_action({
            name: _t("Organigrama"),
            type: 'ir.actions.act_window',
            res_model: 'hr.department',
            res_id: id,
            view_mode: 'form',
            target: 'new',
            views: [[formId, 'form']],
            context: {edit: false, form_view_initial_mode: 'view'},
        });
    },
    closeSideBar: function(ev){
//        if(ev.target.nodeName !== 'svg'){
//            this.btnst = false;
//            this.contentBtns = false;
//            this.toogleSideBar();
//            this.toogleSideBarDetail();
//        }
//        else{
//            this.btnst = false;
//            this.contentBtns = false;
//            this.toogleSideBar();
//            this.toogleSideBarDetail();
//        }
    },
    toogleSideBarDetail: function(ev){
        if(this.contentBtns === true) {
            document.querySelector('.toggle span').classList.add('toggle');
            document.getElementById('sidebar-node-details').classList.add('sidebarshow');
            this.contentBtns = false;
            this.btnst = false;
        }else if(this.contentBtns === false) {
            document.querySelector('.toggle span').classList.remove('toggle');
            document.getElementById('sidebar-node-details').classList.remove('sidebarshow');
            this.contentBtns = true;
            this.btnst = false;
          }
    },
    toogleSideBar: function(ev){
        if(this.btnst === true) {
            document.querySelector('.toggle span').classList.add('toggle');
            document.getElementById('sidebar-legend').classList.add('sidebarshow');
            this.btnst = false;
        }else if(this.btnst === false) {
            document.querySelector('.toggle span').classList.remove('toggle');
            document.getElementById('sidebar-legend').classList.remove('sidebarshow');
            document.getElementById('sidebar-node-details').classList.remove('sidebarshow');
            this.contentBtns = true;
            this.btnst = true;
          }
    },
    onClickZoomOut: function(ev) {
        let slide = document.querySelector('#myRange');
        slide.value = parseInt(slide.value) - 1;
        let scale = parseFloat(slide.value);
        this.control.setOption("scale", scale/10);
        this.control.update(primitives.UpdateMode.Refresh);
    },
    onClickZoomIn: function(ev) {
        let slide = document.querySelector('#myRange');
        slide.value = parseInt(slide.value)  + 1;
        let scale = parseFloat(slide.value);
        this.control.setOption("scale", scale/10);
        this.control.update(primitives.UpdateMode.Refresh);
    },
    onScale: function(ev) {
        const scale = parseFloat(ev.target?.value || 1);
        this.scale = scale/10;
        this.control.setOption("scale", scale/10);
        this.control.update(primitives.UpdateMode.Refresh);
    },
    DownloadPDF: function() {
      // create a document and pipe to a blob
        var doc = new pdfkitsamples.PDFDocument({size: 'LEGAL', layout : 'landscape'});
        var blobStream = pdfkitsamples.blobStream;
        var saveAs = pdfkitsamples.saveAs;
        var stream = doc.pipe(blobStream());

//      doc.fontSize(25)
//        .text('First Organizational Chart', 30, 30);

      var newItems = [];
      const items = this.control.getOptions().items;
      for (var index = 0; index < items.length; index += 1) {
        var item = items[index];
        newItems.push({
          id: item.id,
          parent: item.parent,
          title: item.title,
          description: item.description,
        })
      }
      var sampleChart = primitives.OrgDiagramPdfkit({
        items: items,
        cursorItem: null,
        hasSelectorCheckbox: primitives.Enabled.False
      });
      var sample3size = sampleChart.getSize();
      var size = sampleChart.draw(doc, 50, 100);
      var legalSize = { width: 612.00, height: 1008.00 } // See http://pdfkit.org/docs/paper_sizes.html
      var scale = Math.min(legalSize.width / (sample3size.width + 100), legalSize.height / (sample3size.height + 100))
      doc.save();
      doc.scale(scale);
      doc.restore();

      doc.end();

      if (typeof stream !== 'undefined') {
        stream.on('finish', function () {
          var string = stream.toBlob('application/pdf');
          window.saveAs(string, 'sample.pdf');
        });
      } else {
        alert('Error: Failed to create file stream.');
      }
    },
    getDummyTemplate: function(responsible) {
        var result = new primitives.TemplateConfig();
        result.name = "dummyTemplateItem";
        result.itemSize = new primitives.Size(0, 0);

        result.itemTemplate =[
        "div",
            {
                "style": {
                    "width": result.itemSize.width + "px",
                    "height": result.itemSize.height + "px"
                },
                "class": ["dummyTemplateItem"]
            }

        ];
        return result;
    },
    getContactTemplate: function(responsible) {
        var result = new primitives.TemplateConfig();
        result.name = "contactTemplate";
        result.itemSize = new primitives.Size(150, 75);
        result.minimizedItemSize = new primitives.Size(3, 3);

        result.itemTemplate =[
        "div",
            {
                "style": {
                    "width": result.itemSize.width + "px",
                    "height": result.itemSize.height + "px"
                },
                "class": ["contactTemplate"]
            },
            ["div",
                    {
                        "name": "title",
                        "class": ["ContactTitle"],
                    }
            ],

        ];
        return result;
    },
    getContactTemplateResponsible: function(responsible) {
        var result = new primitives.TemplateConfig();
        result.name = "contactTemplateResponsible";
        result.itemSize = new primitives.Size(150, 75);
        result.minimizedItemSize = new primitives.Size(3, 3);

        result.itemTemplate =

        ["div",
            {
                "style": {
                    "width": result.itemSize.width + "px",
                    "height": result.itemSize.height + "px"
                },
                "class": ["contactTemplateResponsible"]
            },
            ["div",
                    {
                        "name": "title",
                        "class": ["ContactTitle"],
                    }
            ],

        ];
        if(responsible){
            result.itemTemplate.push(
                ["div",
                    {
                        "name": "responsible",
                        "class": ["responsabletTag"],
                    }
                ]
            )
        }
        else{
        result.itemTemplate.push(
                ["div",
                    {
                        "name": "responsibleEmpty",
                        "class": ["responsabletEmptyTag"],
                    }
                ]
            )
        }
        return result;
    },
    getcontactTemplateDashed: function(responsible) {
        var result = new primitives.TemplateConfig();
        result.name = "contactTemplateDashed";
        result.itemSize = new primitives.Size(150, 75);
        result.minimizedItemSize = new primitives.Size(3, 3);

        result.itemTemplate =[
        "div",
            {
                "style": {
                    "width": result.itemSize.width + "px",
                    "height": result.itemSize.height + "px"
                },
                "class": ["contactTemplateDashed"]
            },
            ["div",
                    {
                        "name": "title",
                        "class": ["ContactTitle"],
                    }
            ],

        ];
        return result;
    },
    getcontactTemplateDashedResponsible: function(responsible) {
        var result = new primitives.TemplateConfig();
        result.name = "contactTemplateDashedResponsible";
        result.itemSize = new primitives.Size(150, 75);
        result.minimizedItemSize = new primitives.Size(3, 3);
        result.itemTemplate = ["div",
            {
                "style": {
                    "width": result.itemSize.width + "px",
                    "height": result.itemSize.height + "px"
                },
                "class": ["contactTemplateDashedResponsible"]
            },
            ["div",
                    {
                        "name": "title",
                        "class": ["ContactTitle"],
                    }
            ],
        ];
        if(responsible){
            result.itemTemplate.push(
                ["div",
                    {
                        "name": "responsible",
                        "class": ["responsabletTag"],
                    }
                ]
            )
        }
        else{
            result.itemTemplate.push(
                ["div",
                    {
                        "name": "responsibleEmpty",
                        "class": ["responsabletEmptyTag"],
                    }
                ]
            )
        }
        return result;
    },
    onTemplateRender: function(event, data) {
        switch (data.renderingMode) {
            case primitives.RenderingMode.Create:
                /* Initialize template content here */
                break;
            case primitives.RenderingMode.Update:
                /* Update template content here */
                break;
        }

        var itemConfig = data.context;

        if (data.templateName === "contactTemplateDashed") {
            var title = data.element.firstChild;
            title.textContent = itemConfig.title;
        } else if (data.templateName === "contactTemplate") {

            var title = data.element.firstChild;
            title.textContent = itemConfig.title;

        }else if (data.templateName === "contactTemplateResponsible") {

            var title = data.element.firstChild;
            title.textContent = itemConfig.title;
            var responsible = data.element.childNodes[1];
            if(responsible)
                responsible.textContent = itemConfig?.responsible;

        }else if (data.templateName === "contactTemplateDashedResponsible") {

            var title = data.element.firstChild;
            title.textContent = itemConfig.title;
            var responsible = data.element.childNodes[1];
            if(responsible)
                responsible.textContent = itemConfig?.responsible;

        }
    },
    renderEmployeeDetails: function (operating_unit_id,
        department_id,
        short_name,
        responsible,
        end_date,
        inciso,
        ue
    ){
        var employee_id = 1
        var self = this;
        this._rpc({
            route: '/get/organizational/level',
            params: {'operating_unit_id': operating_unit_id, 'department_id': department_id, 'responsible': responsible, 'end_date': end_date}
        }).then(function (result) {
            var orgRoute = '';
            if(inciso){
                orgRoute += `<span><strong>INCISO: </strong>${inciso}</span>`;
            }
            if(ue){
                orgRoute += ` <span style="margin-left: 2rem"><strong>UE: </strong>${ue}</span>`;
            }
            if(orgRoute.length){
                document.querySelector('.org-route').innerHTML = `<span>${orgRoute}</span>`;
            }
            let annotations = []
            const {levels, items, responsible} = result;
            let allShortNames = [];
            items.map((item) => {
                if(item.itemType === 'Assistant'){
                    item.itemType = primitives.ItemType.Assistant;
                    item.adviserPlacementType = item.adviserPlacementType === 'right' ? primitives.AdviserPlacementType.Right : primitives.AdviserPlacementType.Left;
                    annotations.push({
						annotationType: primitives.AnnotationType.HighlightPath,
						items: [item.parent, item.id],
						color: primitives.Colors.Black,
						lineWidth: 2,
						lineType: primitives.LineType.Solid,
						opacity: 1,
						showArrows: false
					});
                }
                else if(item.itemType === 'SubAssistant'){
                    item.itemType = primitives.ItemType.SubAssistant;
                    item.adviserPlacementType = item.adviserPlacementType === 'right' ? primitives.AdviserPlacementType.Right : primitives.AdviserPlacementType.Left;
                }
                else if(item.itemType === 'SubAdviser'){
                    item.itemType = primitives.ItemType.Comite;
                    item.adviserPlacementType = item.adviserPlacementType === 'right' ? primitives.AdviserPlacementType.Right : primitives.AdviserPlacementType.Left;
                    annotations.push({
						annotationType: primitives.AnnotationType.HighlightPath,
						items: [item.parent, item.id],
						color: primitives.Colors.Black,
						lineWidth: 2,
						lineType: primitives.LineType.Solid,
						opacity: 1,
						showArrows: false
					});
                }
                else if(item.title === 'Aggregator'){
                    item.childrenPlacementType = item.childrenPlacementType === 'Horizontal' ? primitives.ChildrenPlacementType.Horizontal : primitives.ChildrenPlacementType.Auto;
                    annotations.push({
						annotationType: primitives.AnnotationType.HighlightPath,
						items: [item.parent, item.id],
						color: primitives.Colors.Black,
						lineWidth: 2,
						lineType: primitives.LineType.Solid,
						opacity: 1,
						showArrows: false
					});
                }
                else{
                    annotations.push({
						annotationType: primitives.AnnotationType.HighlightPath,
						items: [item.parent, item.id],
						color: primitives.Colors.Black,
						lineWidth: 2,
						lineType: primitives.LineType.Solid,
						opacity: 1,
						showArrows: false
					});
                }
                if(item.showShortName === true){
                    allShortNames.push({name: item.title, short_name: item.short_name});
                    var legengItem = document.createElement('div')
                    legengItem.className = 'legendItem';
                    legengItem.innerHTML = `<span class="legendItemTitle"><strong>${item.short_name}:</strong> ${item.title}</span>`;
                    document.querySelector('#org-legend').appendChild(
                        legengItem
                    );
                    item.title = item.short_name;
                }
            });

            levels.map((level) => {
                annotations.push(new primitives.LevelAnnotationConfig({
                  levels: level[1],
                  title: level[0],
                  titleFontColor: primitives.Colors.Black,
                  titleColor: "#F2F2F2",
                  offset: new primitives.Thickness(0, 0, 0, -5),
                  lineWidth: new primitives.Thickness(0, 0, 0, 2),
                  opacity: 1,
                  borderColor: "#318CDA",
                  fillColor: "#F2F2F2",
                  lineType: primitives.LineType.Dashed
                }))
            });
            self.control = primitives.OrgDiagram(document.getElementById('basicdiagram'), {
                pageFitMode: primitives.PageFitMode.AutoSize,
                autoSizeMinimum: { width: 1800, height: 800 },
//                cursorItem: 0,
                levelTitleOrientation: primitives.TextOrientationType.RotateLeft,
                levelTitleFontWeight: 'bold',
                levelTitleFontSize: '14px',
                linesColor: primitives.Colors.Black,
                lineLevelShift: 40,
                onMouseClick: function (e, data) {
//                    console.log( data);
                    self.contentBtns = true;
                    self.toogleSideBarDetail();
                    const itemId = data.context.id;
                    self._rpc({
                    route: '/get/organizational/operating_unit',
                        params: {'id': itemId}
                    }).then(function (result) {
                        document.querySelector('#ue-code').innerHTML = result.code;
                        document.querySelector('#ue-code').innerHTML = result.code;
                        document.querySelector('#ue-parentName').innerHTML = result.parentName;
                        document.querySelector('#ue-inciso').innerHTML = result.inciso;
                        document.querySelector('#ue-OU').innerHTML = result.OU;
                        document.querySelector('#ue-hierarchy').innerHTML = result.hierarchy;
                        document.querySelector('#ue-responsible').innerHTML = result.responsible;
                        document.querySelector('#ue-function_nature').innerHTML = result.function_nature;
                        document.querySelector('#ue-name').innerHTML = data.context.title;
                        document.querySelector('#ue-observations').innerHTML = result.observations;
//                        document.querySelector('#goto-org-uo').setAttribute("data-id", itemId);
//                        document.querySelector('#goto-org-uo').setAttribute("data-form", data.context.form_id);
                    });
//                    var id = data.context.id;
//                    self.do_action({
//                        name: _t("Organigrama"),
//                        type: 'ir.actions.act_window',
//                        res_model: 'hr.department',
//                        res_id: id,
//                        view_mode: 'form',
//                        views: [[data.context.form_id, 'form']],
////                        context: {edit: false, form_view_initial_mode: 'view'},
//                    })
                },
                alignBranches: true,
                lineItemsInterval: 20,
                normalLevelShift: 40,
                scale: 1,
                hasSelectorCheckbox: primitives.Enabled.False,
                defaultTemplateName: "contactTemplate",
                templates: [
                    self.getContactTemplate(responsible),
                    self.getDummyTemplate(responsible),
                    self.getcontactTemplateDashed(responsible),
                    self.getContactTemplateResponsible(responsible),
                    self.getcontactTemplateDashedResponsible(responsible)
                  ],
                onItemRender: self.onTemplateRender,
                items: items,
                linesType: primitives.LineType.Dashed,
                annotations: annotations,
                onLevelTitleRender: function(data) {
                  var title = data.context.title;
                  var titleColor = data.context.titleColor;
                  var width = data.width;
                  var height = data.height;
                  var element = data.element;
                  element.innerHTML = "";
                  element.appendChild(primitives.JsonML.toHTML(["table",
                    {
                      "style": {
                        fontSize: "12px",
                        fontFamily: "Arial, Helvetica, sans-serif",
                        fontWeight: "normal",
                        fontStyle: "normal",
                        color: "black",
                        position: "absolute",
                        padding: 0,
                        margin: 0,
                        textAlign: "center",
                        lineHeight: 1,
                        transformOrigin: "center center",
                        transform: "rotate(-90deg)",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        tableLayout: "fixed",
                        maxWidth: height + "px",
                        maxHeight: width + "px",
                        width: height + "px",
                        height: width + "px",
                        left: (Math.round(width / 2.0 - height / 2.0)) + "px",
                        top: (Math.round(height / 2.0 - width / 2.0)) + "px",
                        background: titleColor,
                        borderRadius: "4px"
                      },
                    },
                    ["tbody",
                      ["tr",
                        ["td",
                          {
                          "style": {
                            "verticalAlign": "middle",
                            "padding": 0,
                            "textOverflow": "ellipsis",
                            "whiteSpace": "nowrap",
                            "overflow": "hidden"
                          }
                          },
                          title
                        ]
                      ]
                    ]
                  ]));
                },
              });

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
            views: [['onsc_catalog.onsc_catalog_department_form', 'form']],
            })
        }
    },
});
    core.action_registry.add('organization_dashboard', EmployeeOrganizationalChart);

});
