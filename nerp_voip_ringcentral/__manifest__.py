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
    'name': 'NOVOBI RingCentral Integration',
    'version': '1.0',
    'website': 'https://www.novobi.com',
    'category': '',
    'author': 'Novobi LLC',
    'depends': [
        'base'
    ],
    'description': """Allow to make phone call in Odoo""",
    'data': [
        'views/assets.xml',
        'data/rc_data.xml',
        'views/callback.xml'
        # 'views/res_users_views.xml'
    ],
    'images': [],
    'demo': [],
    'application': False,
    'installable': True,
    'auto_install': False,
    'qweb': ['static/src/xml/*.xml'
    ],
}
