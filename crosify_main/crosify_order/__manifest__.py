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
        'security/ir.model.access.csv',
        'data/ir_sequence_sku.xml',
        'data/ir_parameter_data.xml',
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
        'views/update_fulfillment_user_config_views.xml',
        'wizard/product_product_select_product_template_wizard_views.xml',
        'wizard/update_fulfillment_wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'module_type': 'official',
    'assets': {
        'web.assets_backend': [
            'crosify_order/static/src/css/sale_order_view_css.css',
            'crosify_order/static/src/xml/tax_totals.xml',
            'crosify_order/static/src/xml/form_status_indicator.xml',
        ],
        'web.assets_frontend': [

        ],
    },
    'license': 'LGPL-3',
}
