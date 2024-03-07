# -*- coding: utf-8 -*-


{
    'name': 'Crosify web',
    'version': '1.0',
    'website': '',
    'summary': """ Crosify web""",
    'depends': ['web'],
    'data': [
    ],
    'demo': [],
    'installable': True,
    'module_type': 'official',
    "category": "Crosify/Crosify",
    'assets': {
        'web.assets_backend': [
            'crosify_web/static/src/search/**/*',
            'crosify_web/static/src/views/**/*',
        ],
    },
    'license': 'LGPL-3',
}
