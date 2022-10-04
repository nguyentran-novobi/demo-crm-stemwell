# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Copyright (C) 2015 Novobi LLC (<http://novobi.com>)
#
##############################################################################

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_nerp_voip_ringcentral = fields.Boolean('RingCentral Integration')
    rc_client_id = fields.Char('RingCentral Client ID', config_parameter='rc._client_id')
    rc_client_secret = fields.Char('RingCentral Client Secret', config_parameter='rc._client_secret')
    rc_api_server = fields.Char('RingCentral API Server URL', config_parameter='rc._api_server')
