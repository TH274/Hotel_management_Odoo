{
    'name': 'Hotel Management',
    'version': '1.0',
    'summary': 'Manage hotel operations including reservations and billing',
    'description': """
        Hotel Management Module:
        -------------------------
        - Manage hotel rooms, reservations, and services.
        - Track customer check-ins and check-outs.
        - Generate billing and maintain customer records.
    """,
    'author': 'Odoo S.A.',
    'category': 'Services/Hotel Management',
    'depends': [
        'base',
        'mail',
        'product',
        ],
    'data': [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/room_tag_views.xml",
        "views/customer_views.xml",
        "views/customer_readonly_views.xml",
        "views/hotel_views.xml",
        "views/service_views.xml",
        "views/sales_views.xml",
        "views/room_views.xml",
        "views/customer_tag_views.xml",
        "views/menu.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
