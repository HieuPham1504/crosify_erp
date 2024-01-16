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
    'depends': ['sale'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'demo': [],
    'installable': True,
    'module_type': 'official',
    'assets': {
        'web.assets_backend': [
            'crosify_order/static/src/css/sale_order_view_css.css',
        ],
    },
    'license': 'LGPL-3',
}
