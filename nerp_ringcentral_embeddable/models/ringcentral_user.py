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
import logging

class RingCentralUser(models.Model):
    _name = 'ringcentral.user'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'RingCentral User'

    ####################
    # DEFAULT FUNCTIONS
    ####################

    ####################
    # FIELDS
    ####################

    name = fields.Char(string='Name', help='User Name in RingCentral Phonebook')
    user_type = fields.Selection([
        ('internal', 'Employee'),
        ('external', 'Customer')
        ], string='User Type', default='external', help='User Type to seperarate between staffs and customers')
    phone = fields.Char(string='Phone', help='Phone Number of the caller')
    extension_id = fields.Char(string='Extension Id', help='User Extension ID on RingCentral')
    extension_number = fields.Char(string='Extension Number', help='User Externsion Number on RingCentral')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State', domain="[('country_id', '=', country_id)]")
    country_id = fields.Many2one('res.country', string='Country')

    ####################
    # ONCHANGE / COMPUTED FUNCTIONS
    ####################

    ####################
    # FUNCTIONS
    ####################

    def _get_or_create_user(self, user_data, force_create=False):
        user_id = self.env['ringcentral.user'].sudo()
        if user_data:
            data = {}
            extension_id = user_data.get('extensionId', '')
            extension_number = user_data.get('extensionNumber', '')
            if extension_id:
                user_id = self.env['ringcentral.user'].sudo().search([('extension_id', '=ilike', str(extension_id))], limit=1)
            if not user_id and extension_number:
                user_id = self.env['ringcentral.user'].sudo().search([('extension_number', '=ilike', str(extension_number))], limit=1)
            phone = user_data.get('phoneNumber', '')
            if not user_id and phone:
                user_id = self.env['ringcentral.user'].sudo().search([('phone','=ilike',phone)], limit=1)
            name = user_data.get('name', 'Guest')
            user_type = 'external'
            if extension_id or extension_number:
                user_type = 'internal'
            data = {
                'extension_id': extension_id,
                'extension_number': extension_number
            }
            location_json = user_data.get('location', '')
            if location_json:
                location = location_json.split(', ')
                city = location[0]
                country_id = self.env.ref('base.us')
                state_id = self.env['res.country.state'].search([('code','=',location[1]), ('country_id','=', country_id.id)], limit=1)
                data.update({
                   'city': city,
                   'country_id': country_id.id,
                   'state_id': state_id and state_id.id or False
                })
            if user_id:
                user_id.write(data)
            elif not user_id and force_create:
                data.update({'name': name, 'phone': phone, 'user_type': user_type})
                user_id = self.create(data)
        return user_id
