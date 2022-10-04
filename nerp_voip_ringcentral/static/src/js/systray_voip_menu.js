odoo.define('nerp_voip_ringcentral.SystrayVoipMenu', function (require) {
"use strict";

const config = require('web.config');
const core = require('web.core');
const SystrayMenu = require('web.SystrayMenu');
const Widget = require('web.Widget');
const DialingPanel = require('nerp_voip_ringcentral.DialingPanel');
// As voip is not supported on mobile devices,
// we want to keep the standard phone widget
if (config.device.isMobile) {
    return;
}

const SystrayVoipMenu = Widget.extend({
    name: 'voip',
    template: 'nerp_voip_ringcentral.switch_panel_top_button',
    events: {
        'click': '_onClick',
    },
    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    init(){
        this._super(...arguments);
        this._dialingPanel = new DialingPanel(this);
    },

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClick(ev) {
        ev.preventDefault();
        core.bus.trigger('voip_onToggleDisplay');
    },
});

// Insert the Voip widget button in the systray menu
SystrayMenu.Items.push(SystrayVoipMenu);

return SystrayVoipMenu;

});
