{
    'name': 'Upcoming Sessions Snippet',
    'summary': 'Website snippet to display upcoming sessions from events',
    'description': 'Adds a customizable snippet to display upcoming sessions from the events module',
    'author': 'Your Name',
    'website': 'https://yourwebsite.com',
    'category': 'Website',
    'version': '16.0.1.0.0',
    'depends': ['website', 'event'],
    'data': [
        'views/upcoming_sessions_snippets.xml',
        'views/upcoming_sessions_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'upcoming_sessions/static/src/js/upcoming_sessions.js',
            # '/upcoming_sessions/static/src/js/simplified.js', 
            'upcoming_sessions/static/src/scss/upcoming_sessions.scss',
        ],
    },
    'installable': True,
    'application': False,
}