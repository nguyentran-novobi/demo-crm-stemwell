# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Copyright (C) 2018 Novobi LLC (<http://novobi.com>)
#
##############################################################################

from odoo import api, fields, models, _
from odoo.addons.nerp_ringcentral_embeddable.services.ringcentral.ringcentral_service import RingCentralService
import base64
import logging

class RingCentralRecording(models.Model):
    _name = 'ringcentral.recording'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'RingCentral Recording'

    ####################
    # DEFAULT FUNCTIONS
    ####################

    ####################
    # FIELDS
    ####################

    name = fields.Char(string='Recording ID', index=True)
    call_id = fields.Many2one('ringcentral.call.log', string='Related Call Log', help='Related Call in Odoo')
    from_user_id = fields.Many2one('ringcentral.user', related='call_id.from_user_id')
    to_user_id = fields.Many2one('ringcentral.user', related='call_id.to_user_id')
    start_time = fields.Datetime(string='Start Time', related='call_id.start_time', help='Start Time of the call')
    content_type = fields.Char(string='Content Type', default='audio/mpeg')
    content_url = fields.Char(string='Content Url')
    duration = fields.Integer(string='Duration', help='Duration In Sec')
    content = fields.Binary(string='Content', attachment=False)
    filename = fields.Char(string='Filename', size=256, readonly=True)

    ####################
    # ONCHANGE / COMPUTED FUNCTIONS
    ####################

    ####################
    # FUNCTIONS
    ####################

    def _create_recording(self, call_id, call_log_data):
        record_id = self
        if call_id and call_log_data:
            recording_data = call_log_data.get('recording', {})
            if recording_data:
                name = recording_data.get('id')
                data = {
                    'name': name,
                    'call_id': call_id.id,
                }
                RingCentralObjet = RingCentralService()
                recording_detail = RingCentralObjet._get_recording_by_id(name)
                if recording_detail.status_code == 200:
                    recording_detail_json = recording_detail.json()
                    content_type = recording_detail_json.get('contentType')
                    content_url = recording_detail_json.get('contentUri')
                    duration = recording_detail_json.get('duration')
                    content = RingCentralObjet._get_recording_content_by_id(name)
                    data.update({
                        'content_type': content_type,
                        'duration': duration,
                        'content': base64.b64encode(content),
                        'content_url': content_url,
                        'filename': '%s.mp4' % name
                    })
                record_id = self.env['ringcentral.recording'].sudo().create(data)
        return record_id