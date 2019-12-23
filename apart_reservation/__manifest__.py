# See LICENSE file for full copyright and licensing details.

{
    'name': 'Apartment Reservation Management',
    'version': '13.0.1.0.0',
    'author': 'NDS4IT - Ali Elgarhi',
    'license': 'AGPL-3',
    'summary': 'Manages  Reservation & displays Reservation Summary',
    'depends': ['apart', 'stock', 'mail'],
    'demo': ['data/apart_reservation_data.xml'],
    'data': [
        'security/ir.model.access.csv',
        'data/apart_scheduler.xml',
        'data/apart_reservation_sequence.xml',
        'views/apart_reservation_view.xml',
        'data/email_template_view.xml',
        'report/checkin_report_template.xml',
        'report/checkout_report_template.xml',
        'report/flat_max_report_template.xml',
        'report/apart_reservation_report_template.xml',
        'report/report_view.xml',
        'views/assets.xml',
        'wizards/apart_reservation_wizard.xml',
    ],
    'qweb': ['static/src/xml/apart_flat_summary.xml'],
    'installable': True,
    'auto_install': False,
}
