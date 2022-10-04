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


class ResUsers(models.Model):
    _inherit = 'res.users'

    rc_access_token = fields.Char('RingCentral Access Token')
    rc_refresh_token = fields.Char('RingCentral Refresh Token')
    rc_endpoint_id = fields.Char('Endpoint ID')
    rc_owner_id = fields.Char('Owner ID')
    rc_ac_expires_in = fields.Integer('Access Token Expires In')
    rc_ref_expires_in = fields.Integer('Refresh Token Expires In')
    rc_scope = fields.Char('Scope')
    rc_token_type = fields.Char('Token Type')
    rc_expire_time = fields.Char('Expire Time')
    rc_refresh_token_expire_time = fields.Char('Refresh Token Expire Time')

    def save_rc_auth_data(self, token_obj):
        self.ensure_one()
        return self.write({
            'rc_access_token': token_obj['access_token'],
            'rc_endpoint_id': token_obj['endpoint_id'],
            'rc_ac_expires_in': token_obj['expires_in'],
            'rc_owner_id': token_obj['owner_id'],
            'rc_refresh_token': token_obj['refresh_token'],
            'rc_ref_expires_in': token_obj['refresh_token_expires_in'],
            'rc_scope':  token_obj['scope'],
            'rc_token_type': token_obj['token_type'],
            'rc_expire_time': token_obj['expire_time'],
            'rc_refresh_token_expire_time': token_obj['refresh_token_expire_time']
        })

    def get_rc_auth_data(self):
        self.ensure_one()
        return {
            'access_token': self.rc_access_token,
            'endpoint_id': self.rc_endpoint_id,
            'expires_in': self.rc_ac_expires_in,
            'owner_id': self.rc_owner_id,
            'refresh_token': self.rc_refresh_token,
            'refresh_token_expires_in': self.rc_ref_expires_in,
            'scope': self.rc_scope,
            'token_type': self.rc_token_type,
            'refresh_token_expire_time': int(self.rc_refresh_token_expire_time),
            'expire_time': int(self.rc_expire_time)
        }
