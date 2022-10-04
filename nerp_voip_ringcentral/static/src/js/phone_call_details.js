odoo.define('nerp_voip_ringcentral.PhoneCallDetails', function (require) {
"use strict";

const core = require('web.core');
const Widget = require('web.Widget');

const PhoneCallDetails = Widget.extend({
    template: 'nerp_voip_ringcentral.PhoneCallDetails',
    events: {
        'click .o_dial_mute_button': '_onClickMute',
        'click .o_dial_rec_button': '_onClickRec',
    },

    init(params) {
        this._super(...arguments);
        this.phoneNumber = params.number;
    },

    start() {
        this._super(...arguments);
        this._$activeButton = this.$('.o_phonecall_in_call');

    },

    async _showActiveButtons(){
        this._$activeButton.removeClass('o_phonecall_in_call')
    },

    _onClickMute(){
        core.bus.trigger('voip_onToggleMute');
    },

    _onClickRec(){
        core.bus.trigger('voip_onToggleRec');
    },

    async _hideActiveButton(){
        this._$activeButton.addClass('o_phonecall_in_call')
    }
    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

});

return PhoneCallDetails;

});
