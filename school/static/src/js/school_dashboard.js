odoo.define('school.dashboard', function(require) {
    "use strict";

    var core = require('web.core');
    var formats = require('web.formats');
    var Model = require('web.Model');
    var session = require('web.session');
    var KanbanView = require('web_kanban.KanbanView');
    var ajax = require('web.ajax');
    var ActionManager = require('web.ActionManager');

    var QWeb = core.qweb;
    var _t = core._t;
    var _lt = core._lt;

    var SchoolDashboardView = KanbanView.extend({
        display_name: _lt('Dashboard'),
        icon: 'fa-plus',
        view_type: "school_dashboard_view",
        searchview_hidden: true,
        events: {
            'click .o_dashboard_action': 'on_dashboard_action_clicked',
            'click .o_target_to_set': 'on_dashboard_target_clicked',
            'click .school_dashboard_tree_table tbody tr': 'on_tree_action_clicked',
            'click .school_news div': 'on_news_action_clicked',
        },

        fetch_data: function() {
            // Overwrite this function with useful data
            return $.Deferred().resolve();
        },

        render: function() {
            var super_render = this._super;
            var self = this;
            super_render.call(self);
            return this.fetch_data().then(function(result) {
                ajax.jsonRpc('get_school_dash_board_details', 'call', {}).done(function(details) {
                    var s_dashboard = QWeb.render('school.SchoolDashboard', {
                        widget: self,
                        values: result,
                        payment_details: details[0],
                        tree_details: details[1],
                        group_details: details[2],
                        news_details: details[3],
                        reminders_details: details[4],
                        user_id: details[5],
                    });
                    super_render.call(self);
                    $(s_dashboard).prependTo(self.$el);
                });
            });
        },

        on_tree_action_clicked: function(e) {
            e.preventDefault();
            this.do_action_form($(e.currentTarget));
        },

        on_news_action_clicked: function(e) {
            e.preventDefault();
            this.do_action_form($(e.currentTarget));
        },

        do_action_form: function(action) {
            var model = action.attr('model');
            var id = parseInt(action.attr('id'));
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: model,
                res_id: id,
                views: [
                    [false, 'form']
                ],
                target: 'current',
                context: {},
            });

        },

        on_dashboard_action_clicked: function(ev) {
            ev.preventDefault();

            var self = this;
            var $action = $(ev.currentTarget);
            var action_name = $action.attr('name');
            var action_extra = $action.attr('id');
            var additional_context = {};

            // TODO: find a better way to add defaults to search view
            if (action_name === 'school.action_school_parent_form') {
                this.do_action_form($(e.currentTarget));
            }
            if (action_name === 'school_fees.action_student_payslip_form') {
                additional_context.view_student_payslip_search = 1;
                if (action_extra === 'paid') {
                    additional_context.search_default_paid = 1;
                } else if (action_extra === 'open') {
                    additional_context.search_default_submit = 1;
                } else if (action_extra === 'total') {
                    additional_context.search_default_submit = 1;
                    additional_context.search_default_paid = 1;
                }
            } else if (action_name === 'school_canteen.action_canteen') {
                additional_context.canteen_canteen_search_view = 1;
                if (action_extra === 'paid') {
                    additional_context.search_default_done = 1;
                } else if (action_extra === 'open') {
                    additional_context.search_default_invoiced = 1;
                } else if (action_extra === 'total') {
                    additional_context.search_default_invoiced = 1;
                    additional_context.search_default_done = 1;
                }
            } else if (action_name === 'school_transport.action_student_transport_registration_form') {
                additional_context.view_transport_registration_search = 1;
                if (action_extra === 'paid') {
                    additional_context.search_default_paid = 1;
                } else if (action_extra === 'open') {
                    additional_context.search_default_validate = 1;
                } else if (action_extra === 'total') {
                    additional_context.search_default_validate = 1;
                    additional_context.search_default_paid = 1;
                }
            } else if (action_name === 'accommodation.action_accommodation_accommodation') {
                additional_context.accommodation_accommodation_search_view = 1;
                if (action_extra === 'paid') {
                    additional_context.search_default_paid = 1;
                } else if (action_extra === 'open') {
                    additional_context.search_default_invoice = 1;
                } else if (action_extra === 'total') {
                    additional_context.search_default_invoice = 1;
                    additional_context.search_default_paid = 1;
                }
            }
            new Model("ir.model.data")
                .call("xmlid_to_res_id", [action_name])
                .then(function(data) {
                    if (data) {
                        self.do_action(data, {
                            additional_context: additional_context
                        });
                    }
                });
        },
    });

    core.view_registry.add('school_dashboard_view', SchoolDashboardView);

    return SchoolDashboardView;

});