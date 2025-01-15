{
    'name': 'Hotel Management',
    'version': '1.0',
    'summary': 'Manage hotel operations including reservations and billing',
    'license': 'LGPL-3',
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
        'web',
        'hr'
        ],
    'data': [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "data/cron.xml",
        "data/mail_template_data.xml",
        "views/room_tag_views.xml",
        "views/customer_tag_views.xml",
        "views/product_views.xml",
        "views/customer_views.xml",
        "views/customer_pending.xml",
        "views/room_views.xml",
        "views/hotel_views.xml",
        "views/menu.xml",
        "reports/report_customer.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
