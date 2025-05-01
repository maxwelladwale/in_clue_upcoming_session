odoo.define('upcoming_sessions.basic', function (require) {
    'use strict';
    
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _t = core._t;
    var rpc = require('web.rpc');
    
    publicWidget.registry.upcomingSessionsSnippet = publicWidget.Widget.extend({
        selector: '.upcoming-sessions-snippet',
        
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self._loadSessionsData();
            });
        },
        
        _loadSessionsData: function () {
            var self = this;
            var limit = parseInt(this.$el.data('limit')) || 10;
            
            // Display a loading indicator
            this.$el.find('.sessions-loading').html('<i class="fa fa-spinner fa-spin"></i> ' + _t('Loading your upcoming sessions...'));
            
            // Make the RPC call to load event data
            rpc.query({
                route: '/upcoming_sessions/data',
                params: {
                    limit: limit,
                    published_only: true
                },
            }).then(function (response) {
                self.$el.find('.sessions-loading').remove();
                
                if (response.success && response.data.length) {
                    self.$el.find('.table tbody').empty();
                    
                    _.each(response.data, function (session) {
                        var $row = $('<tr/>');
                        
                        // Mark the row if the event is happening today
                        if (session.is_today) {
                            $row.addClass('table-info');
                        }
                        // Add a border based on the user's relationship with the event
                        if (session.is_creator) {
                            $row.addClass('border-start border-3 border-primary');
                        } else if (session.is_registered) {
                            $row.addClass('border-start border-3 border-success');
                        }
                        
                        // Build the Session Name cell with badges
                        var $nameCell = $('<td/>').text(session.name);
                        if (session.is_creator) {
                            $nameCell.append(' ').append(
                                $('<span/>', {
                                    class: 'badge bg-primary ms-1',
                                    text: _t('Organizer')
                                })
                            );
                        } else if (session.is_registered) {
                            $nameCell.append(' ').append(
                                $('<span/>', {
                                    class: 'badge bg-success ms-1',
                                    text: _t('Registered')
                                })
                            );
                        } else if (session.is_company_event) {
                            $nameCell.append(' ').append(
                                $('<span/>', {
                                    class: 'badge bg-secondary ms-1',
                                    text: _t('Company')
                                })
                            );
                        }
                        $row.append($nameCell);
                        
                        // Date & Time cell
                        $row.append($('<td/>').text(session.formatted_date));
                        // Location cell
                        $row.append($('<td/>').text(session.location));
                        // Participants cell
                        $row.append($('<td/>').text(session.participants));
                        // Client cell
                        $row.append($('<td/>').text(session.client));
                        
                        // Build the Actions cell
                        var $actions = $('<td/>');
                        
                        // View button (always if website_url exists)
                        if (session.website_url) {
                            $actions.append($('<a/>', {
                                href: session.website_url,
                                class: 'btn btn-sm btn-outline-primary me-1',
                                text: _t('View'),
                                target: '_blank'
                            }));
                        }
                        
                        // Register button (if not registered and not creator)
                        if (!session.is_registered && !session.is_creator && session.registration_url) {
                            $actions.append($('<a/>', {
                                href: session.registration_url,
                                class: 'btn btn-sm btn-success me-1',
                                text: _t('Register'),
                                target: '_blank'
                            }));
                        }
                        
                        // Edit button (if the current user is the creator)
                        if (session.edit_url) {
                            $actions.append($('<a/>', {
                                href: session.edit_url,
                                class: 'btn btn-sm btn-outline-secondary',
                                text: _t('Edit'),
                                target: '_blank'
                            }));
                        }
                        
                        $row.append($actions);
                        self.$el.find('.table tbody').append($row);
                    });
                } else {
                    self.$el.find('.table tbody').html(
                        '<tr><td colspan="6" class="text-center text-muted">' +
                        _t('No upcoming sessions found.') + '</td></tr>'
                    );
                }
            }).catch(function (err) {
                console.error("Error fetching sessions:", err);
                self.$el.find('.sessions-loading').remove();
                self.$el.find('.table tbody').html(
                    '<tr><td colspan="6" class="text-center text-danger">' +
                    _t('Failed to load sessions.') + '</td></tr>'
                );
            });
        },
    });
});
