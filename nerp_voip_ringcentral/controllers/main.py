# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Copyright (C) 2015 Novobi LLC (<http://novobi.com>)
#
##############################################################################

from odoo import http, _, fields
import urllib
from ringcentral import SDK
from odoo.http import request
from datetime import datetime
from datetime import timedelta
import json

class RingCentralSDK:
    RINGCENTRAL_CLIENT_ID = 'tT2gvd0-QoW5uvTKRhAHdQ'
    RINGCENTRAL_CLIENT_SECRET = '0D5ly4gBQ9a1fbsG2ksViQQ34OE0D3RpuRYbXf0_OrjA'
    RINGCENTRAL_SERVER_URL = 'https://platform.devtest.ringcentral.com'
    RINGCENTRAL_REDIRECT_URL = '/ringcentral_oauth2callback'
    rcsdk = SDK(RINGCENTRAL_CLIENT_ID, RINGCENTRAL_CLIENT_SECRET, RINGCENTRAL_SERVER_URL)


class RingCentral(http.Controller):
    @http.route([
        '/api_creds',
    ], type='json', auth='user')
    def _getApiCredentials(self):
        IR_Config = request.env['ir.config_parameter'].sudo()
        return_vals = {
            'appKey': IR_Config.get_param('rc._client_id'),
            'appSecret': IR_Config.get_param('rc._client_secret'),
            'server': IR_Config.get_param('rc._api_server'),
            'redirect_uri': self._getAbsoluteRedirectUrl(),
        }
        return return_vals

    @http.route(['/save_auth_data'], type='json', auth='user')
    def _saveAuthData(self, **kwargs):
        current_user = request.env['res.users'].browse(request.uid)
        try:
            current_user.save_rc_auth_data(kwargs)
        except Exception as e:
            return {
                'success': False,
                'server_error': e
            }
        return {
            'success': True,
        }

    @http.route(['/get_auth_data'], type='json', auth='user')
    def _getAuthData(self, **kwargs):
        current_user = request.env['res.users'].browse(request.uid)
        return current_user.get_rc_auth_data()

    #
    # @http.route([
    #     '/ringcentral_authen_url',
    # ], type='json', auth='user')
    # def login(self):
    #     current_user = request.env['res.users'].browse(request.uid)
    #     if current_user.rc_last_authen_date and timedelta(minutes=45) + current_user.rc_last_authen_date > datetime.now():
    #         return {
    #             'access_token': current_user.rc_access_token
    #         }
    #     elif not current_user.rc_last_authen_date or timedelta(days=6) + current_user.rc_last_authen_date > datetime.now():
    #         base_url = RingCentralSDK.RINGCENTRAL_SERVER_URL + '/restapi/oauth/authorize'
    #         params = (
    #             ('response_type', 'code'),
    #             ('redirect_uri', self._getAbsoluteRedirectUrl()),
    #             ('client_id', RingCentralSDK.RINGCENTRAL_CLIENT_ID),
    #             ('state', 'initialState')
    #         )
    #         auth_url = base_url + '?' + urllib.parse.urlencode(params)
    #         return {
    #             'auth_url': auth_url
    #         }

    @http.route([
        '/ringcentral_oauth2callback',
    ], type='http', auth='public', method=['POST'])
    def oauth2callback(self, **kwargs):
            return request.render('nerp_voip_ringcentral.callback')

    def _getAbsoluteRedirectUrl(self):
        return request.env['ir.config_parameter'].sudo().get_param(
            'web.base.url') + RingCentralSDK.RINGCENTRAL_REDIRECT_URL
