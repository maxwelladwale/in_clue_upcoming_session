# controllers/main.py
from odoo import http, fields
from odoo.http import request
import logging
import json

_logger = logging.getLogger(__name__)

class UpcomingSessionsController(http.Controller):

    @http.route('/upcoming_sessions/data', type='json', auth='user', website=True)
    def get_upcoming_sessions(self, **kw):
        _logger.info("RPC CALLED: /upcoming_sessions/data with params: %s", json.dumps(kw))
        try:
            # Get current user, company, and partner info
            current_user = request.env.user
            user_company = current_user.company_id
            partner = current_user.partner_id

            _logger.info("Current user: %s (ID: %s)", current_user.name, current_user.id)
            group_names = current_user.groups_id.mapped('name')
            _logger.info("Current user group names: %s", group_names)

            # Log group details (name and XML ID if available)
            group_details = []
            for group in current_user.groups_id:
                xml_id = request.env['ir.model.data'].sudo().search([
                    ('model', '=', 'res.groups'),
                    ('res_id', '=', group.id)
                ], limit=1)
                group_details.append(f"{group.name} ({xml_id.complete_name if xml_id else 'No XML ID'})")
            _logger.info("Current user group details: %s", group_details)

            # Determine user type (portal vs internal)
            is_portal = current_user.has_group('base.group_portal')
            is_internal = current_user.has_group('base.group_user') and not is_portal
            _logger.info("User is portal: %s, internal: %s", is_portal, is_internal)

            # Get limit to fetch from parameters
            limit = int(kw.get('limit', 10))

            # Base domain: only upcoming events
            domain = [('date_begin', '>=', fields.Datetime.now())]

            # Set domain based on user type:
            if is_internal:
                # Internal users: show events if one of:
                # - They created the event,
                # - The event belongs to their company or their partner’s company,
                # - They are registered for the event.
                domain += ['|', '|',
                           ('user_id', '=', current_user.id),
                           ('company_id', 'in', [user_company.id, partner.company_id.id]),
                           ('registration_ids.partner_id', '=', partner.id)]
            else:
                # Portal users: show events if one of:
                # - They are registered for the event,
                # - The event belongs to their company or their partner’s company.
                domain += ['|',
                           ('registration_ids.partner_id', '=', partner.id),
                           ('company_id', 'in', [user_company.id, partner.company_id.id])]

            # Optionally include only published events
            if kw.get('published_only', False):
                domain.append(('website_published', '=', True))

            _logger.info("SEARCH DOMAIN: %s", domain)

            # Perform the search for events
            upcoming_events = request.env['event.event'].sudo().search(
                domain, order='date_begin asc', limit=limit
            )
            _logger.info("FOUND %s MATCHING EVENTS", len(upcoming_events))

            # Get today's date for flagging today's events
            today = fields.Date.today()
            result = []
            for event in upcoming_events:
                event_date = fields.Date.from_string(event.date_begin)
                is_today = event_date == today

                result.append({
                    'id': event.id,
                    'name': event.name,
                    'user': user_company.name,
                    'date': event.date_begin,
                    'formatted_date': f"Today, {event.date_begin.strftime('%H:%M')}" 
                                       if is_today else event.date_begin.strftime('%d %b, %H:%M'),
                    'location': event.address_id.name if event.address_id else '',
                    'participants': len(event.registration_ids),
                    'client': event.organizer_id.name if event.organizer_id else '',
                    'is_today': is_today,
                    'website_url': event.website_url,
                    # Flags to show appropriate actions on the frontend:
                    'is_creator': event.user_id.id == current_user.id,
                    'is_registered': partner.id in event.registration_ids.mapped('partner_id.id'),
                    'is_company_event': event.company_id.id in [user_company.id, partner.company_id.id],
                    # Build URLs for actions (adjust these if needed)
                    'registration_url': event.website_url + '#register' 
                                        if (partner.id not in event.registration_ids.mapped('partner_id.id')
                                            and event.website_url) else False,
                    'edit_url': '/web#id=%s&model=event.event&view_type=form' % event.id 
                                if event.user_id.id == current_user.id else False,
                })

            return {
                'success': True,
                'count': len(result),
                'data': result
            }

        except Exception as e:
            _logger.error("ERROR in /upcoming_sessions/data: %s", str(e), exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
# controllers/main.py
from odoo import http, fields
from odoo.http import request
import logging
import json

_logger = logging.getLogger(__name__)

class UpcomingSessionsController(http.Controller):

    @http.route('/upcoming_sessions/data', type='json', auth='user', website=True)
    def get_upcoming_sessions(self, **kw):
        _logger.info("RPC CALLED: /upcoming_sessions/data with params: %s", json.dumps(kw))
        try:
            # Get current user, company, and partner info
            current_user = request.env.user
            user_company = current_user.company_id
            partner = current_user.partner_id

            _logger.info("Current user: %s (ID: %s)", current_user.name, current_user.id)
            group_names = current_user.groups_id.mapped('name')
            _logger.info("Current user group names: %s", group_names)

            # Log group details (name and XML ID if available)
            group_details = []
            for group in current_user.groups_id:
                xml_id = request.env['ir.model.data'].sudo().search([
                    ('model', '=', 'res.groups'),
                    ('res_id', '=', group.id)
                ], limit=1)
                group_details.append(f"{group.name} ({xml_id.complete_name if xml_id else 'No XML ID'})")
            _logger.info("Current user group details: %s", group_details)

            # Determine user type (portal vs internal)
            is_portal = current_user.has_group('base.group_portal')
            is_internal = current_user.has_group('base.group_user') and not is_portal
            _logger.info("User is portal: %s, internal: %s", is_portal, is_internal)

            # Get limit to fetch from parameters
            limit = int(kw.get('limit', 10))

            # Base domain: only upcoming events
            domain = [('date_begin', '>=', fields.Datetime.now())]

            # Set domain based on user type:
            if is_internal:
                # Internal users: show events if one of:
                # - They created the event,
                # - The event belongs to their company or their partner’s company,
                # - They are registered for the event.
                domain += ['|', '|',
                           ('user_id', '=', current_user.id),
                           ('company_id', 'in', [user_company.id, partner.company_id.id]),
                           ('registration_ids.partner_id', '=', partner.id)]
            else:
                # Portal users: show events if one of:
                # - They are registered for the event,
                # - The event belongs to their company or their partner’s company.
                domain += ['|',
                           ('registration_ids.partner_id', '=', partner.id),
                           ('company_id', 'in', [user_company.id, partner.company_id.id])]

            # Optionally include only published events
            if kw.get('published_only', False):
                domain.append(('website_published', '=', True))

            _logger.info("SEARCH DOMAIN: %s", domain)

            # Perform the search for events
            upcoming_events = request.env['event.event'].sudo().search(
                domain, order='date_begin asc', limit=limit
            )
            _logger.info("FOUND %s MATCHING EVENTS", len(upcoming_events))

            # Get today's date for flagging today's events
            today = fields.Date.today()
            result = []
            for event in upcoming_events:
                event_date = fields.Date.from_string(event.date_begin)
                is_today = event_date == today

                result.append({
                    'id': event.id,
                    'name': event.name,
                    'user': user_company.name,
                    'date': event.date_begin,
                    'formatted_date': f"Today, {event.date_begin.strftime('%H:%M')}" 
                                       if is_today else event.date_begin.strftime('%d %b, %H:%M'),
                    'location': event.address_id.name if event.address_id else '',
                    'participants': len(event.registration_ids),
                    'client': event.organizer_id.name if event.organizer_id else '',
                    'is_today': is_today,
                    'website_url': event.website_url,
                    # Flags to show appropriate actions on the frontend:
                    'is_creator': event.user_id.id == current_user.id,
                    'is_registered': partner.id in event.registration_ids.mapped('partner_id.id'),
                    'is_company_event': event.company_id.id in [user_company.id, partner.company_id.id],
                    # Build URLs for actions (adjust these if needed)
                    'registration_url': event.website_url + '#register' 
                                        if (partner.id not in event.registration_ids.mapped('partner_id.id')
                                            and event.website_url) else False,
                    'edit_url': '/web#id=%s&model=event.event&view_type=form' % event.id 
                                if event.user_id.id == current_user.id else False,
                })

            return {
                'success': True,
                'count': len(result),
                'data': result
            }

        except Exception as e:
            _logger.error("ERROR in /upcoming_sessions/data: %s", str(e), exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
# controllers/main.py
from odoo import http, fields
from odoo.http import request
import logging
import json

_logger = logging.getLogger(__name__)

class UpcomingSessionsController(http.Controller):

    @http.route('/upcoming_sessions/data', type='json', auth='user', website=True)
    def get_upcoming_sessions(self, **kw):
        _logger.info("RPC CALLED: /upcoming_sessions/data with params: %s", json.dumps(kw))
        try:
            # Get current user, company, and partner info
            current_user = request.env.user
            user_company = current_user.company_id
            partner = current_user.partner_id

            _logger.info("Current user: %s (ID: %s)", current_user.name, current_user.id)
            group_names = current_user.groups_id.mapped('name')
            _logger.info("Current user group names: %s", group_names)

            # Log group details (name and XML ID if available)
            group_details = []
            for group in current_user.groups_id:
                xml_id = request.env['ir.model.data'].sudo().search([
                    ('model', '=', 'res.groups'),
                    ('res_id', '=', group.id)
                ], limit=1)
                group_details.append(f"{group.name} ({xml_id.complete_name if xml_id else 'No XML ID'})")
            _logger.info("Current user group details: %s", group_details)

            # Determine user type (portal vs internal)
            is_portal = current_user.has_group('base.group_portal')
            is_internal = current_user.has_group('base.group_user') and not is_portal
            _logger.info("User is portal: %s, internal: %s", is_portal, is_internal)

            # Get limit to fetch from parameters
            limit = int(kw.get('limit', 10))

            # Base domain: only upcoming events
            domain = [('date_begin', '>=', fields.Datetime.now())]

            # Set domain based on user type:
            if is_internal:
                # Internal users: show events if one of:
                # - They created the event,
                # - The event belongs to their company or their partner’s company,
                # - They are registered for the event.
                domain += ['|', '|',
                           ('user_id', '=', current_user.id),
                           ('company_id', 'in', [user_company.id, partner.company_id.id]),
                           ('registration_ids.partner_id', '=', partner.id)]
            else:
                # Portal users: show events if one of:
                # - They are registered for the event,
                # - The event belongs to their company or their partner’s company.
                domain += ['|',
                           ('registration_ids.partner_id', '=', partner.id),
                           ('company_id', 'in', [user_company.id, partner.company_id.id])]

            # Optionally include only published events
            if kw.get('published_only', False):
                domain.append(('website_published', '=', True))

            _logger.info("SEARCH DOMAIN: %s", domain)

            # Perform the search for events
            upcoming_events = request.env['event.event'].sudo().search(
                domain, order='date_begin asc', limit=limit
            )
            _logger.info("FOUND %s MATCHING EVENTS", len(upcoming_events))

            # Get today's date for flagging today's events
            today = fields.Date.today()
            result = []
            for event in upcoming_events:
                event_date = fields.Date.from_string(event.date_begin)
                is_today = event_date == today

                result.append({
                    'id': event.id,
                    'name': event.name,
                    'user': user_company.name,
                    'date': event.date_begin,
                    'formatted_date': f"Today, {event.date_begin.strftime('%H:%M')}" 
                                       if is_today else event.date_begin.strftime('%d %b, %H:%M'),
                    'location': event.address_id.name if event.address_id else '',
                    'participants': len(event.registration_ids),
                    'client': event.organizer_id.name if event.organizer_id else '',
                    'is_today': is_today,
                    'website_url': event.website_url,
                    # Flags to show appropriate actions on the frontend:
                    'is_creator': event.user_id.id == current_user.id,
                    'is_registered': partner.id in event.registration_ids.mapped('partner_id.id'),
                    'is_company_event': event.company_id.id in [user_company.id, partner.company_id.id],
                    # Build URLs for actions (adjust these if needed)
                    'registration_url': event.website_url + '#register' 
                                        if (partner.id not in event.registration_ids.mapped('partner_id.id')
                                            and event.website_url) else False,
                    'edit_url': '/web#id=%s&model=event.event&view_type=form' % event.id 
                                if event.user_id.id == current_user.id else False,
                })

            return {
                'success': True,
                'count': len(result),
                'data': result
            }

        except Exception as e:
            _logger.error("ERROR in /upcoming_sessions/data: %s", str(e), exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
