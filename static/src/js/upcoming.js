odoo.define('upcoming_sessions.basic', function (require) {
    'use strict';
    
    $(document).ready(function() {
        // Add a visible indicator to the page
        $('body').append(
            $('<div/>', {
                id: 'rpc-debug-indicator',
                css: {
                    position: 'fixed',
                    bottom: '10px',
                    right: '10px',
                    padding: '10px',
                    background: 'rgba(0,0,0,0.7)',
                    color: 'white',
                    'z-index': 9999,
                    'border-radius': '5px'
                },
                text: 'RPC Debug: Initializing...'
            })
        );
        
        function updateIndicator(text) {
            $('#rpc-debug-indicator').text('RPC Debug: ' + text);
        }
        
        // Find all snippets on the page
        var $snippets = $('.upcoming-sessions-snippet');
        updateIndicator('Found ' + $snippets.length + ' snippets');
        
        if ($snippets.length > 0) {
            // Direct Ajax call instead of using odoo.jsonRpc
            updateIndicator('Making Ajax call...');
            
            $.ajax({
                url: '/upcoming_sessions/data',
                method: 'POST',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: { limit: 10 },
                    id: Math.floor(Math.random() * 1000000000)
                }),
                success: function(response) {
                    updateIndicator('Success! Found ' + (response.result ? response.result.length : 0) + ' events');
                    
                    if (response.result && response.result.length) {
                        // Process each snippet
                        $snippets.each(function() {
                            var $snippet = $(this);
                            $snippet.find('.sessions-loading').remove();
                            
                            var $tbody = $snippet.find('.table tbody').empty();
                            
                            // Add each event to the table
                            $.each(response.result, function(i, session) {
                                var $row = $('<tr/>');
                                if (session.is_today) {
                                    $row.addClass('table-info');
                                }
                                
                                $row.append($('<td/>').text(session.name));
                                $row.append($('<td/>').text(session.formatted_date));
                                $row.append($('<td/>').text(session.location));
                                $row.append($('<td/>').text(session.participants));
                                $row.append($('<td/>').text(session.client));
                                
                                var $actions = $('<td/>');
                                $actions.append(
                                    $('<a/>', {
                                        href: session.website_url,
                                        class: 'btn btn-outline-primary btn-sm',
                                        text: 'Details'
                                    })
                                );
                                
                                $row.append($actions);
                                $tbody.append($row);
                            });
                        });
                    } else {
                        $snippets.each(function() {
                            var $snippet = $(this);
                            $snippet.find('.sessions-loading').remove();
                            $snippet.find('.table tbody').html(
                                '<tr><td colspan="6" class="text-center">No upcoming sessions found</td></tr>'
                            );
                        });
                    }
                },
                error: function(xhr, status, error) {
                    updateIndicator('Error: ' + status + ' - ' + error);
                    $snippets.each(function() {
                        var $snippet = $(this);
                        $snippet.find('.sessions-loading').remove();
                        $snippet.find('.table tbody').html(
                            '<tr><td colspan="6" class="text-center">Error loading sessions</td></tr>'
                        );
                    });
                }
            });
        }
    });
});