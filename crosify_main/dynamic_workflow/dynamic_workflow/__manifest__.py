{
    'name': 'Dynamic Workflow',
    'version': '17.0.1.0.0',
    'author': 'Cuong.ntt',
    'depends': ['hr'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'wizard/wizard_assign_task_view.xml',
        'wizard/wizard_back_stage_view.xml',
        'wizard/wizard_fail_reason_view.xml',
        'views/dynamic_workflow_view.xml',
        'views/dynamic_workflow_task_view.xml',
        'views/dynamic_workflow_stage_view.xml',
        'views/menu.xml',
    ],
    'assets': {
            'web.assets_backend': [
                'dynamic_workflow/static/css/main.css',
            ],
        },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': -100
}
