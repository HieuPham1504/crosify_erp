# -*- coding: utf-8 -*-
{
    'name': 'Crosify Sale',
    'version': '1.8',
    'website': 'https://www.odoo.com/app/events',
    'summary': 'Trainings, Conferences, Meetings, Exhibitions, Registrations',
    'description': """
Organization and management of Events.
======================================

The event module allows you to efficiently organize events and all related tasks: planning, registration tracking,
attendances, etc.

Key Features
------------
* Manage your Events and Registrations
* Use emails to automatically confirm and send acknowledgments for any event registration
""",
    'depends': ['sale_management', 'sale', 'account', 'stock', 'hr'],
    'data': [
        'security/sale_operator_security.xml',
        'security/designer_security.xml',
        'security/producer_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_sku.xml',
        'data/ir_sequence_production_transfer.xml',
        'data/ir_sequence_mo_production.xml',
        'data/fail_product_data.xml',
        'data/ir_parameter_data.xml',
        'report/item_barcode_template.xml',
        'report/export_ready_packing_item_pdf.xml',
        'data/ir_sequence_partner_code.xml',
        'views/sale_order_views.xml',
        'views/sale_order_line_views.xml',
        'views/sale_order_line_level_views.xml',
        'views/product_template_views.xml',
        'views/product_category_views.xml',
        'views/product_product_views.xml',
        'views/product_type_fulfill_views.xml',
        'views/fulfill_shelf_type_views.xml',
        'views/fulfill_shelf_views.xml',
        'views/product_type_shelf_type_views.xml',
        'views/sale_order_type_views.xml',
        'views/fulfill_error_views.xml',
        'views/mo_production_views.xml',
        'views/res_partner_views.xml',
        'views/fulfill_cancel_item_views.xml',
        'views/production_transfer_views.xml',
        'views/res_country_state_views.xml',
        'views/hs_product_config_views.xml',
        'wizard/product_product_select_product_template_wizard_views.xml',
        'wizard/update_fulfillment_wizard_views.xml',
        'wizard/update_item_design_wizard_views.xml',
        'wizard/raise_information_wizard_views.xml',
        'wizard/qc_check_item_wizard_views.xml',
        'wizard/pack_on_shelf_wizard_views.xml',
        'wizard/ready_to_pack_item_wizard_views.xml',
        'wizard/checking_packed_item_wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'module_type': 'official',
    'assets': {
        'web.assets_backend': [
            'crosify_order/static/src/css/sale_order_view_css.css',
            'crosify_order/static/src/xml/form_status_indicator.xml',
            'crosify_order/static/src/xml/list_renderer.xml',
        ],
        'web.assets_frontend': [

        ],
    },
    'license': 'LGPL-3',
}
