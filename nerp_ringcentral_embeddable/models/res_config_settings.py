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

    ####################
    # DEFAULT FUNCTIONS
    ####################

    ####################
    # FIELDS
    ####################

    module_nerp_ringcentral_embeddable = fields.Boolean(string='RingCentral Integration')
    ringcentral_client_id = fields.Char(string='RingCentral Client ID', config_parameter='ringcentral._client_id')
    ringcentral_client_secret = fields.Char(string='RingCentral Client Secret', config_parameter='ringcentral._client_secret')
    ringcentral_username = fields.Char(string='RingCentral Username', config_parameter='ringcentral._username')
    ringcentral_password = fields.Char(string='RingCentral Password', config_parameter='ringcentral._password')
    ringcentral_environment = fields.Selection([('prod', 'Production'), ('sandbox', 'Sandbox')], default='sandbox',
        string='RingCentral Environment', config_parameter='ringcentral._environment')

    ####################
    # ONCHANGE / COMPUTED FUNCTIONS
    ####################

    ####################
    # FUNCTIONS
    ####################