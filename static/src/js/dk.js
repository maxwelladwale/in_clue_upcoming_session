odoo.define('upcoming_sessions.upcoming_sessions', function (require) {
    'use strict';
    
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _ = core._;
    var rpc = require('web.rpc');
    var options = require('web_editor.snippets.options');
    
    publicWidget.registry.upcomingSessionsSnippet = publicWidget.Widget.extend({
        selector: '.upcoming-sessions-snippet',
        
        start: function () {
            console.log('Snippet initialized');
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                console.log('Starting to load sessions data');
                self._loadSessionsData();
            });
        },
        
        _loadSessionsData: function () {
            var self = this;
            var limit = parseInt(this.$el.data('limit')) || 3;
            
            console.log('Loading sessions with limit:', limit);
            
            // Add a delay to ensure console logs are visible
            setTimeout(function() {
                rpc.query({
                    route: '/upcoming_sessions/data',
                    params: {
                        limit: limit,
                    },
                }).then(function (data) {
                    console.log('RPC Success - Data received:', data);
                    
                    if (data && data.length) {
                        self.$el.find('.sessions-loading').remove();
                        self.$el.find('.table tbody').empty();
                        
                        // Add session rows
                        _.each(data, function (session) {
                            var $row = $('<tr/>');
                            if (session.is_today) {
                                $row.addClass('table-info');
                            }
                            
                            // Session name
                            $row.append($('<td/>').text(session.name));
                            
                            // Date & Time
                            $row.append($('<td/>').text(session.formatted_date));
                            
                            // Location
                            $row.append($('<td/>').text(session.location));
                            
                            // Participants
                            $row.append($('<td/>').text(session.participants));
                            
                            // Client
                            $row.append($('<td/>').text(session.client));
                            
                            // Actions
                            var $actions = $('<td/>');
                            $actions.append(
                                $('<a/>', {
                                    href: session.website_url,
                                    class: 'btn btn-outline-primary btn-sm',
                                    text: 'Details'
                                })
                            );
                            
                            if (session.can_join) {
                                $actions.append(
                                    $('<a/>', {
                                        href: session.meeting_url,
                                        class: 'btn btn-success btn-sm ms-2',
                                        text: 'Join'
                                    })
                                );
                            }
                            
                            $row.append($actions);
                            
                            self.$el.find('.table tbody').append($row);
                        });
                    } else {
                        console.log('No data or empty data received');
                        self.$el.find('.sessions-loading').remove();
                        self.$el.find('.table tbody').html(
                            '<tr><td colspan="6" class="text-center">No upcoming sessions found</td></tr>'
                        );
                    }
                }).guardedCatch(function (error) {
                    console.error('RPC Error:', error);
                    self.$el.find('.sessions-loading').remove();
                    self.$el.find('.table tbody').html(
                        '<tr><td colspan="6" class="text-center">Failed to load session data: ' + (error.message || 'Unknown error') + '</td></tr>'
                    );
                });
            }, 500);
        }
    });
    
    options.registry.upcomingSessionsOptions = options.Class.extend({
        start: function () {
            console.log('Options initialized');
            return this._super.apply(this, arguments);
        },
        
        onBuilt: function () {
            console.log('Options onBuilt triggered');
            this._super.apply(this, arguments);
            this.updateUI();
        },
        
        updateUI: function () {
            console.log('Options updateUI triggered');
            this.$target.find('.upcoming-sessions-snippet').trigger('refresh');
        },
        
        cleanForSave: function () {
            console.log('Options cleanForSave triggered');
            this.$target.addClass('o_snippet_cached');
        }
    });
});