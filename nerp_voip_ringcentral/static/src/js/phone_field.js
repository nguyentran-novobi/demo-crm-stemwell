odoo.define('nerp_voip_ringcentral.PhoneField', function (require) {
"use strict";

const basicFields = require('web.basic_fields');
const core = require('web.core');
const config = require('web.config');

const Phone = basicFields.FieldPhone;
const _t = core._t;

// As voip is not supported on mobile devices,
// we want to keep the standard phone widget
if (config.device.isMobile) {
    return;
}

/**
 * Override of FieldPhone to use the DialingPanel to perform calls on clicks.
 */
Phone.include({
    events: Object.assign({}, Phone.prototype.events, {
        'click': '_onClick',
    }),

    /**
     * Called when the phone number is clicked.
     *
     * @private
     * @param {MouseEvent} ev
     */
    _onClick(ev) {
        if (this.mode !== 'readonly') {
            return;
        }
        this.trigger_up('voip_call', {
            number: this.value,
            resId: this.res_id,
            resModel: this.model,
        });
        ev.preventDefault();
        core.bus.trigger('');
    },
});

});
