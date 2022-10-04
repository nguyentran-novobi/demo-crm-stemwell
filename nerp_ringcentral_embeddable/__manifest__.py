# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Copyright (C) 2015 Novobi LLC (<http://novobi.com>)
#
##############################################################################

{
    'name': 'NOVOBI RingCentral Embeddable',
    'version': '1.0',
    'website': 'https://www.novobi.com',
    'category': '',
    'author': 'Novobi LLC',
    'depends': [
        'base',
        'portal',
	'utm',
    ],
    'description': """RingCentral Embeddable""",
    'data': [
        'data/ir_cron_data.xml',
        'views/assets.xml',
        'views/menuitem_views.xml',
        'views/ringcentral_call_log_views.xml',
        'views/ringcentral_user_views.xml',
        'views/ringcentral_recording_views.xml',
        'views/res_config_settings_views.xml',
        'security/ir.model.access.csv',
    ],
    'images': [],
    'demo': [],
    'application': False,
    'installable': True,
    'auto_install': False,
    'qweb': [
        'static/src/xml/*.xml'
    ],
}
