# See LICENSE file for full copyright and licensing details.

{
    "name": "Flats Rent Management",
    "version": "13.0.1.0.0",
    "author": "NDS4IT - Ali Elgarhi",
    "category": "Flat Rent Management",
    "website": "https://nds4it.com",
    "depends": ["sale_stock", "point_of_sale"],
    "license": "AGPL-3",
    "summary": "Flat Rent Management to Manage Folio and Flats Configuration",
    "demo": ["data/Flat_data.xml"],
    "data": [
        "security/apart_security.xml",
        "security/ir.model.access.csv",
        "data/apart_sequence.xml",
        "report/report_view.xml",
        "report/apart_folio_report_template.xml",
        "views/apart_view.xml",
        "wizard/apart_wizard.xml",
    ],
    "css": ["static/src/css/room_kanban.css"],
    "images": ["static/description/logo.png"],
    "application": True,
}
