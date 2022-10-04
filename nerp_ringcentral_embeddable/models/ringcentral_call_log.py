# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Copyright (C) 2018 Novobi LLC (<http://novobi.com>)
#
##############################################################################

from odoo import api, fields, models
from odoo.addons.nerp_ringcentral_embeddable.services.ringcentral.ringcentral_service import RingCentralService
import dateutil.parser
import logging

class RingCentralCallLog(models.Model):
    _name = 'ringcentral.call.log'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'RingCentral Call Log'

    ####################
    # DEFAULT FUNCTIONS
    ####################

    ####################
    # FIELDS
    ####################

    name = fields.Char(string='Name', compute='_compute_call_name', store=True)
    ringcentral_call_log_id = fields.Char(string='RingCentral Call Log ID', help='Call Log ID on RingCentral, unique, used to create and update record', index=True)
    start_time = fields.Datetime(string='Start Time', help='Start Time of the call')
    duration = fields.Integer(string='Time in Sec', help='Call duration in second')
    call_type = fields.Char(string='Call Type', help='Showing type of the call. Ex: VoIP Call, Voice')
    direction = fields.Char(string='Direction', help='Call direction. Ex: Inbound or Outbound')
    action = fields.Char(string='Action', help='Showing type of the call. Ex: VoIP Call, Phone Call')
    result = fields.Char(string='Result', help='Call Status. Ex: Call connected, Missed...etc')
    from_user_id = fields.Many2one('ringcentral.user', string='From User', help='User who made the call from RingCentral. Guest if he is not in the RingCentral phonebook')
    to_user_id = fields.Many2one('ringcentral.user', string='To User', help='User who received the call from RingCentral. Guest if he is not in the RingCentral phonebook')
    from_phone_number = fields.Char(string='From Phone Number', help='From Phone Number of the call log, in case users change their phone number in future')
    to_phone_number = fields.Char(string='To Phone Number', help='To Phone Number of the call log, in case users change their phone number in future')
    recording_ids = fields.One2many('ringcentral.recording', 'call_id', string='Recordings')

    ####################
    # ONCHANGE / COMPUTED FUNCTIONS
    ####################

    @api.depends('from_user_id', 'from_user_id.name', 'to_user_id', 'to_user_id')
    def _compute_call_name(self):
        for record in self:
            from_user_id = record.from_user_id
            to_user_id = record.to_user_id
            name = 'From %s To %s' % (from_user_id and from_user_id.name or '', to_user_id and to_user_id.name or False)
            record.name = name

    ####################
    # FUNCTIONS
    ####################


    ############################################################
    # Created by Van Tran
    #   @Params: From Date, string date with format YYYY-MM-DD
    #   @Return:
    #   @Functionality:
    #       - Pull Call Log from RingCentral to Odoo
    #       - Create Call Log record and related information
    #           Ex: user and recording
    #############################################################
    def get_ringcentral_call_log(self, from_date=None):
        RingCentralObject = RingCentralService()
        RingCentralObject._get_call_log(from_date)

    ############################################################
    # Created by Van Tran
    #   @Params:
    #       - call_log_data: Dict, record data from RingCentral
    #   @Return:
    #       - call_id: RingCentral Call Log object
    #   @Functionality:
    #       - Get RingCentral Call Log object, or create a new call log record
    #############################################################
    def _get_or_create_call_log(self, call_log_data):
        call_id = self
        ringcentral_call_log_id = call_log_data.get('id','')
        if ringcentral_call_log_id and not self.env['ringcentral.call.log'].sudo().search_count([('ringcentral_call_log_id', '=', ringcentral_call_log_id)]):
            RingCentralUserObject = self.env['ringcentral.user'].sudo()
            RingCentralRecordingObject = self.env['ringcentral.recording'].sudo()
            from_user_id = RingCentralUserObject._get_or_create_user(call_log_data.get('from', {}), force_create=True)
            to_user_id = RingCentralUserObject._get_or_create_user(call_log_data.get('to', {}), force_create=True)
            data = {
                'ringcentral_call_log_id': ringcentral_call_log_id,
                #The call start datetime in (ISO 8601)[https://en.wikipedia.org/wiki/ISO_8601] format including timezone, 
                # for example 2016-03-10T18:07:52.534Z
                'start_time': fields.Datetime.from_string(dateutil.parser.parse(call_log_data.get('startTime')).strftime('%Y-%m-%d %H:%M:%S')),
                'duration': call_log_data.get('duration'),
                'call_type': call_log_data.get('type'),
                'direction': call_log_data.get('direction'),
                'action': call_log_data.get('action'),
                'result': call_log_data.get('result'),
                'from_phone_number': call_log_data.get('from').get('phoneNumber'),
                'to_phone_number': call_log_data.get('to').get('phoneNumber'),
                'from_user_id': from_user_id and from_user_id.id or False,
                'to_user_id': to_user_id and to_user_id.id or False,
            }
            call_id = self.env['ringcentral.call.log'].sudo().create(data)
            recording_id = RingCentralRecordingObject._create_recording(call_id, call_log_data)
        return call_id

