/* 
 * This is a simplified version of the upcoming sessions JS that uses
 * direct jQuery instead of the Odoo widget system for debugging
 */
odoo.define('upcoming_sessions.simplified', function (require) {
    'use strict';
    
    // Use jQuery directly for simplicity during debugging
    $(document).ready(function() {
        console.log("Document ready - looking for upcoming sessions snippet");
        
        // Find the snippet on the page
        var $snippet = $('.upcoming-sessions-snippet');
        
        if ($snippet.length) {
            console.log("Found the upcoming sessions snippet!");
            
            // Directly call the RPC endpoint
            odoo.jsonRpc("/upcoming_sessions/data", 'call', {
                limit: 5
            }).then(function(data) {
                console.log("RPC success!", data);
                
                $snippet.find('.sessions-loading').remove();
                
                if (data && data.length) {
                    $snippet.find('.table tbody').empty();
                    
                    // Add session rows
                    data.forEach(function(session) {
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
                        
                        $snippet.find('.table tbody').append($row);
                    });
                } else {
                    $snippet.find('.table tbody').html(
                        '<tr><td colspan="6" class="text-center">No upcoming sessions found</td></tr>'
                    );
                }
            }).guardedCatch(function(error) {
                console.error("RPC error:", error);
                $snippet.find('.sessions-loading').remove();
                $snippet.find('.table tbody').html(
                    '<tr><td colspan="6" class="text-center">Error loading sessions: ' + JSON.stringify(error) + '</td></tr>'
                );
            });
        } else {
            console.log("No upcoming sessions snippet found on the page");
        }
    });
});