odoo.define('nerp_voip_ringcentral.DialingPanel', function (require) {
    "use strict";
    const core = require('web.core');
    const config = require('web.config');
    const Widget = require('web.Widget');
    const PhoneCallDetails = require('nerp_voip_ringcentral.PhoneCallDetails');
    const RcWebPhone = require('nerp_voip_ringcentral.ringcentral_webphone');
    const _t = core._t;
    // const ajax = require('web.ajax');

// As voip is not supported on mobile devices,
// we want to keep the standard phone widget
    if (config.device.isMobile) {
        return;
    }

    const DialingPanel = Widget.extend({
        template: 'nerp_voip_ringcentral.DialingPanel',
        events: {
            'click .o_dial_window_close': '_onClickWindowClose',
            'click .o_dial_fold': '_onClickFold',
            'click .o_dial_keypad_icon': '_onClickDialKeypadIcon',
            'click .o_dial_call_button': '_onClickCallButton',
            'click .o_dial_number': '_onClickDialNumber',
            'click .o_dial_keypad_backspace': '_onClickBackspace',
        },
        custom_events: {},
        /**
         * @constructor
         */
        init() {
            this.RcWebPhone = undefined
            this._super(...arguments);
            this._isShow = false;
            this._phoneCallTab = undefined;
            this._isInCall = false;
            this._rcSession = undefined
            this._isFold = false;
            this._isMute = false;
            this._isRec = false
            this.title = _t("RINGCENTRAL");
            this._timer = undefined;
        },
        /**
         * @override
         */
        start() {
            if (this.RcWebPhone == undefined) {
                this.RcWebPhone = new RcWebPhone(this)
            }
            this._$phoneDetails = undefined;
            this._$callButton = this.$('.o_dial_call_button');
            this._$tabsPanel = this.$('.o_dial_panel');
            this._$keypad = this.$('.o_dial_keypad');
            this._$keypadInput = this.$('.o_dial_keypad_input');
            this._$keypadInputDiv = this.$('.o_dial_keypad_input_div');
            this._$keypadButton = this.$('.o_dial_keypad_icon');
            this.$el.hide();
            this.$el.css('bottom', 0);
            core.bus.on('voip_onToggleDisplay', this, this._onToggleDisplay);
            core.bus.on('voip_onToggleMute', this, this._toggleMute);
            core.bus.on('voip_onToggleRec', this, this._toggleRec);
        },
        /**
         * @private
         */
        _toggleKeypadInputDiv() {
            if (this._isInCall) {
                this._$keypadInputDiv.hide();
            } else {
                this._$keypadInputDiv.show();
                this._$keypadInput.focus();
            }
        },
        _onToggleDisplay() {
            var self = this
            if (self._isShow) {
                this.RcWebPhone.logOut(function () {
                    self.$el.hide();
                    self.$el.css('height', self._isFold ? 0 : 480);
                    self._isShow = false;
                })

            } else {
                this.RcWebPhone.logIn(function () {
                    self.$el.show();
                    self._isShow = true;
                })
            }
        },

        _toggleMute() {
            if (this._rcSession) {
                if (!this._isMute){
                    this._rcSession.mute()
                    this._isMute = true
                }
                else{
                    this._rcSession.unmute()
                    this._isMute = false
                }
            }
        },

        _toggleRec() {
            if (this._rcSession) {
                if (!this._isRec){
                    this._rcSession.startRecord().then(function(res){
                        this._isRec = true
                        console.log(res)
                    })
                }
                else{
                    this._rcSession.stopRecord().then(function(res){
                        this._isRec = false
                        console.log(res)
                    })
                }
            }
        },

        _onClickWindowClose(ev) {
            ev.preventDefault();
            ev.stopPropagation();
            this.$el.animate({

                height: '0px',
            });
            this.$('.o_dial_fold').css("bottom", "25px");
            this.$('.o_dial_window_close').hide();
            this.$('.o_dial_main_buttons').hide();
            this.$('.o_dial_unfold').show();
            this._isFold = true
        },

        _onClickFold() {
            this.$el.animate({
                height: '480px',
            });
            this.$('.o_dial_fold').css("bottom", 0);
            this.$('.o_dial_window_close').show();
            this.$('.o_dial_main_buttons').show();
            this.$('.o_dial_unfold').hide();
            this._isFold = false
        },

        _onClickDialKeypadIcon(ev) {
            if (this._$tabsPanel.is(":visible")) {
                this._$keypad.show();
                this._toggleKeypadInputDiv();
                if (this._$phoneDetails) {
                    this._removePhoneCallTab()
                }
            }
        },

        _onClickDialNumber(ev) {
            this._$keypadInput.val(this._$keypadInput.val() + $(ev.target).text())
        },

        _onClickBackspace(ev) {
            this._$keypadInput.val(this._$keypadInput.val().slice(0, -1))
        },

        async _removePhoneCallTab() {
            this._$phoneDetails.remove()
            delete this._$phoneDetails;
            delete this._phoneCallTab;
            this._$keypadButton.hide();
        },

        async _onClickCallButton() {
            if (this._phoneCallTab) {
                if (!this._isInCall) {
                    this._phoneCallTab._showActiveButtons()
                    this._$callButton.addClass('o_dial_hangup_button')
                    this._$keypadButton.hide()
                    this._isInCall = true
                    this._cleanUpRCSession()
                    var self = this
                    this._rcSession = this.RcWebPhone.makeCall(this._phoneCallTab.phoneNumber)
                } else {
                    this._phoneCallTab._hideActiveButton()
                    this._$callButton.removeClass('o_dial_hangup_button')
                    this._$keypadButton.show()
                    this._isInCall = false
                    this.RcWebPhone.hangUpCall(this._rcSession)
                }
            } else {
                this.trigger_up('voip_call', {
                    number: this._$keypadInput.val(),
                });
                this._$keypadInput.val('')
            }
        },

        _cleanUpRCSession() {
            if (this._rcSession) {
                this._rcSession.terminate()
                this._rcSession = undefined
            }
        },

        /**
         * Function called when widget phone is clicked.
         *
         * @param {Object} params
         * @param {string} params.number
         * @param {string} params.resModel
         * @param {integer} params.resId
         * @return {Promise}
         */
        async goToPhoneCallDetails(params) {
            if (!this._isInCall) {
                if (this._$phoneDetails) {
                    this._removePhoneCallTab()
                }
                this._phoneCallTab = new PhoneCallDetails(params)
                await this._phoneCallTab.appendTo(this._$tabsPanel)
                this._$keypad.hide();
                this._$phoneDetails = this._phoneCallTab.$el
                if (!this._isShow) {
                    core.bus.trigger('voip_onToggleDisplay');
                }
                this._$keypadButton.show()
            } else {
                this.do_notify('Your are currently in a call');
            }
        },
    });

    return DialingPanel;

});
