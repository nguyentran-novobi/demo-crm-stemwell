odoo.define('nerp_voip_ringcentral.WebClient', function (require) {
"use strict";

const DialingPanel = require('nerp_voip_ringcentral.DialingPanel');
const config = require('web.config');
const WebClient = require('web.WebClient');

// As voip is not supported on mobile devices,
// we want to keep the standard phone widget
if (config.device.isMobile) {
    return;
}

WebClient.include({

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------
    /**
     * @private
     * @param {OdooEvent} ev
     * @param {string} ev.data.number
     * @param {string} ev.data.resModel
     * @param {integer} ev.data.resId
     */
    _onVoipCall(ev) {
        return this._dialingPanel.goToPhoneCallDetails(ev.data);
    },

    /**
     * @override
     */
    async show_application() {
        await this._super(...arguments);
        this._dialingPanel = new DialingPanel(this);
        await this._dialingPanel.appendTo(this.$el);
        this.on('voip_call', this, this.proxy('_onVoipCall'));
    },
});

});
