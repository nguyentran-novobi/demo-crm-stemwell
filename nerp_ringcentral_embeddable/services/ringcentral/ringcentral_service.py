# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Copyright (C) 2015 Novobi LLC (<http://novobi.com>)
#
##############################################################################

import requests
import time
from odoo.http import request
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta
from odoo.tools.translate import _
import json
import base64

import logging
_logger = logging.getLogger(__name__)


class RingCentralService:
    """
    :param _ringcentral_client_id: api key of RingCentral App
    :param _ringcentral_client_secret: api secret of RingCentral App
    :param _ringcentral_api_server: The service server based on the environment
    """
    _ringcentral_client_id = None
    _ringcentral_client_secret = None
    _ringcentral_api_server = None
    _ringcentral_username = None
    _ringcentral_password = None

    def __init__(self):

        IR_Config = request.env['ir.config_parameter'].sudo()
        ringcentral_client_id = IR_Config.get_param('ringcentral._client_id')
        ringcentral_client_secret = IR_Config.get_param('ringcentral._client_secret')
        ringcentral_username = IR_Config.get_param('ringcentral._username')
        ringcentral_password = IR_Config.get_param('ringcentral._password')
        ringcentral_environment = IR_Config.get_param('ringcentral._environment')

        if ringcentral_environment == 'prod':
            ringcentral_api_server = 'https://platform.ringcentral.com/restapi'
        else:
            ringcentral_api_server = 'https://platform.devtest.ringcentral.com/restapi'
        
        self._ringcentral_client_id = ringcentral_client_id
        self._ringcentral_client_secret = ringcentral_client_secret
        self._ringcentral_username = ringcentral_username
        self._ringcentral_password = ringcentral_password
        self._ringcentral_api_server = ringcentral_api_server

    def _get_access_token(self):
        """
        Get Access Token from RingCentral
        :return access_token: string
        """
        content = self._ringcentral_client_id + ':' + self._ringcentral_client_secret
        authorization_code = base64.b64encode(bytes(content, 'utf-8')).decode('utf-8')
        url = self._ringcentral_api_server + '/oauth/token'
        headers = {
            'Accept': 'application/json ',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic {}'.format(authorization_code),
        }

        data = {
            'grant_type': 'password',
            'username': self._ringcentral_username,
            'password': self._ringcentral_password
        }

        response = requests.post(url, headers=headers, data=data)
        response_json = response.json()
        if response.status_code != 200:
            _logger.exception(_("RingCentral auth issue : %s"), response.content)
            raise UserError(_(
                "Sorry, your credentials were setup incorrectly. You may try to authenticate again."))
        return response_json.get('access_token','')

    def _get_ringcentral_header(self):
        """
        Generate Header which will be used in all requests
        :return headers: Dict
        """
        token = self._get_access_token()
        headers = {
            'Content-Type': "application/json",
            'Authorization': 'Bearer {}'.format(token)
        }
        return headers

    def _get_call_log(self, from_date=None):
        headers = self._get_ringcentral_header()
        url = self._ringcentral_api_server + '/v1.0/account/~/extension/~/call-log'
        to_date = date.today()
        if not from_date:
            from_date = to_date - timedelta(days=1)
        params = {
            'dateFrom': from_date,
            'dateTo': to_date,
            'perPage': 20,
        }
        
        RingCentralCallLogObject = request.env['ringcentral.call.log'].sudo()
        while url:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                break
            response_json = response.json()
            navigation = response_json.get('navigation', '')
            next_page = navigation.get('nextPage', '')
            if next_page:
                # I dont even know why RingCentral named that param as uri, not url
                url = next_page.get('uri','')
            else:
                url = None
            for record in response_json.get('records', []):
                call_id = RingCentralCallLogObject._get_or_create_call_log(record)

    def _get_recording_by_id(self, recording_id):
        headers = self._get_ringcentral_header()
        url = self._ringcentral_api_server + '/v1.0/account/~/recording/' + recording_id
        response = requests.get(url, headers=headers)
        return response

    def _get_recording_content_by_id(self, recording_id):
        headers = self._get_ringcentral_header()
        url = self._ringcentral_api_server + '/v1.0/account/~/recording/' + recording_id + '/content'
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.content
        return None