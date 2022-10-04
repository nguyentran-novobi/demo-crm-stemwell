odoo.define('nerp_voip_ringcentral.ringcentral_webphone', function (require) {
    "use strict";
    const core = require('web.core');
    const config = require('web.config');
    const Widget = require('web.Widget');
    const _t = core._t;
    const ajax = require('web.ajax');
    require('web.dom_ready')
// As voip is not supported on mobile devices,
// we want to keep the standard phone widget
    if (config.device.isMobile) {
        return;
    }

    // The writer himself isn't fully understand how the following code works, so I wish you luck mate
    const RcWebPhone = Widget.extend({
        init() {
            var self = this
            this.api_credentials = undefined
            this.authData = undefined
            this.loggedIn = undefined
            this.WebPhone = undefined
            this.tokenRefreshed = false

            // The below variables are needed for SIP.js, ref the orginal SIP document for details
            this.remoteVideoElement = document.getElementById('remoteVideo');
            this.localVideoElement = document.getElementById('localVideo');

            this._getApiCredentials(function (result) {
                self.rcsdk = new RingCentral.SDK({
                    server: result['server'],
                    clientId: result['appKey'],
                    clientSecret: result['appSecret'],
                    redirectUri: result['redirect_uri'] // optional, but is required for Implicit Grant and Authorization Code OAuth Flows (see below)
                });
                self.api_credentials = result
                self.platform = self.rcsdk.platform()
                self.platform.on(self.platform.events.refreshError, function (e) {
                    console.log(e)
                    // do something, usually open a login page
                });
                self.platform.on(self.platform.events.refreshSuccess, function (e) {
                    console.log(e)
                    var self = this
                    res.json().then(function (res) {
                        if (res['access_token']) {
                            self.tokenRefreshed = true
                            console.log(e)
                        }
                    })
                });
            })
        },

        _getApiCredentials(callback) {
            ajax.jsonRpc(
                '/api_creds', 'call', {}, {
                    success: function (result) {
                        return callback(result.result)
                    }
                }
            )
        },

        _saveAuthData(authData, callback = undefined) {
            var self = this
            ajax.jsonRpc(
                '/save_auth_data', 'call', authData, {
                    success: function (result) {
                        if (result.result['success']) {
                            if (callback != undefined) {
                                callback()
                            }
                            self.tokenRefreshed = false
                            return true
                        } else {
                            console.log(result.result['server_error'])
                        }
                        return false
                    }
                }
            )
        },

        _authorize(showDialPane) {
            var self = this
            var loginUrl = this.platform.loginUrl(); // implicit set to True for implicit grant flow
            self.platform
                .loginWindow({url: loginUrl}) // this method also allows to supply more options to control window position
                .then(function (res) {
                    return self.platform.login(res).then(function (res) {
                        return res.json()
                    })
                })
                .then(function (res) {
                    self.loggedIn = true
                    self.platform.auth().data().then(function (authData) {
                        self.authData = authData
                        self._saveAuthData(authData, function () {
                            self._postLogin(showDialPane)
                        })
                    })
                })
                .catch(function (e) {
                    console.error(e.stack || e);
                });
        },

        async logIn(showDialPane) {
            // var $redirectUri = decodeURIComponent(window.location.href.split('login', 1) + 'callback.html');
            //
            // console.log('The redirect uri value :', $redirectUri);
            var self = this
            if (!self.authData) {
                ajax.jsonRpc(
                    '/get_auth_data', 'call', {}, {
                        success: function (result) {
                            if (!result.result['access_token']) {
                                self._authorize(showDialPane)
                            } else {
                                self._reApplyAuthData(result.result, showDialPane)
                            }
                        }
                    }
                )
            }
            else{
                self._reApplyAuthData()
            }
        },

        logOut(hideDialPane){
            var self = this
            self.WebPhone.userAgent.unregister();
            hideDialPane();
            e.preventDefault();
        },

        _reApplyAuthData(authData, showDialPane) {
            var self = this
            self.platform.auth().setData(authData, false).then(function () {
                self.platform.auth().refreshTokenValid().then(function (isValid) {
                        if (!isValid) {
                            console.log('The refresh token is expired')
                        } else {
                            self.platform.loggedIn().then(function (isLoggedIn) {
                                if (!isLoggedIn) {
                                    self.loggedIn = false
                                } else {
                                    self.loggedIn = true
                                    self.platform.auth().data().then(function (authData) {
                                        self.authData = authData
                                        if (self.tokenRefreshed) {
                                            return self._saveAuthData(authData)
                                        } else return true
                                    }).then(function (value) {
                                            return value ? self._postLogin(showDialPane) : undefined
                                        }
                                    )
                                }
                            })
                        }
                    }
                )
            })
        },

        _createWebPhone(res) {
            var self = this
            var webPhone = new RingCentral.WebPhone(res, { // optional
                appKey: self.api_credentials.appKey,
                appName: self.api_credentials.appName,
                appVersion: self.api_credentials.appVersion,
                uuid: self.authData.endpoint_id,
                logLevel: 1, // error 0, warn 1, log: 2, debug: 3
                audioHelper: {
                    enabled: true, // enables audio feedback when web phone is ringing or making a call
                    incoming: '/nerp_voip_ringcentral/static/src/audio/incoming.ogg', // path to audio file for incoming call
                    outgoing: '/nerp_voip_ringcentral/static/src/audio/incoming.ogg' // path to aduotfile for outgoing call
                },
                media: {
                    remote: self.remoteVideoElement,
                    local: self.localVideoElement
                },
                //to enable QoS Analytics Feature
                enableQos: false
            });
            // The following code will need to callback a function when a specific event happen
            webPhone.userAgent.on('connecting', function () {
                console.log('UA connecting');
            });
            webPhone.userAgent.on('connected', function () {
                console.log('UA Connected');
            });
            webPhone.userAgent.on('disconnected', function () {
                console.log('UA Disconnected');
            });
            webPhone.userAgent.on('registered', function () {
                console.log('UA Registered');
            });
            webPhone.userAgent.on('unregistered', function () {
                console.log('UA Unregistered');
            });
            webPhone.userAgent.on('registrationFailed', function () {
                console.log('UA RegistrationFailed', arguments);
            });
            webPhone.userAgent.on('message', function () {
                console.log('UA Message', arguments);
            });
            webPhone.userAgent.transport.on('switchBackProxy', function () {
                console.log('switching back to primary outbound proxy');
                webPhone.userAgent.transport.reconnect(true);
            });
            webPhone.userAgent.transport.on('closed', function () {
                console.log('WebSocket closed.');
            });
            webPhone.userAgent.transport.on('transportError', function () {
                console.log('WebSocket transportError occured');
            });
            webPhone.userAgent.transport.on('wsConnectionError', function () {
                console.log('WebSocket wsConnectionError occured');
            });
            return webPhone
        },

        _postLogin(showDialPane) {
            var self = this
            return self.platform
                .get('/restapi/v1.0/account/~/extension/~')
                .then(function (res) {
                    res.json().then(function (result) {
                        var extension = result
                        console.log('Extension info', extension);
                    });

                    // Fetch the SIP provisioning if the app is authenticated
                    return self.platform.post('/restapi/v1.0/client-info/sip-provision', {
                        sipInfo: [
                            {
                                transport: 'WSS'
                            }
                        ]
                    });
                })
                .then(function (res) {
                    // Set up WebPhone
                    res.json().then(function (res) {
                        self.WebPhone = self._createWebPhone(res)
                        // Show Pane
                        showDialPane()
                    })
                })
                .catch(function (e) {
                    console.error('Error in main promise chain');
                    console.error(e.stack || e);
                });
        },

        makeCall(toNumber) {
            var session = this.WebPhone.userAgent.invite(toNumber, {
                fromNumber: '', // Optional, Company Number will be used as default
                homeCountryId: '1' // Optional, the value of
            });
            return session
        },

        hangUpCall(session) {
            session.terminate()
        }
    });

    return RcWebPhone;

});
