# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "POS Bag Charges in Odoo",
    "version" : "13.0.0.0",
    "category" : "Point of Sale",
    "depends" : ['base','sale','point_of_sale'],
    "author": "BrowseInfo",
    'summary': 'This apps helps to add POS bag changes on POS order',
    "description": """
    
    Purpose :- 
This Module allow us to add bag charges on particular order.
    POS bag changes
    POS carry bag
    POS bag amount
    POS bag extra changes
    POS bag extra payment
    Point of sale  bag changes
    Point of sale  carry bag
    Point of sale  bag amount
    Point of sale  bag extra changes
    Point of sale  bag extra payment
    
    """,
    "website" : "www.browseinfo.in",
   
    "currency": "EUR",
    "data": [
        'data/data.xml',
        'views/custom_pos_view.xml',
    ],
    'qweb': [
        'static/src/xml/pos_bag_charges.xml',
    ],
    "auto_install": False,
    "installable": True,
    "images":['static/description/Banner.png'],
    "live_test_url":'https://youtu.be/sH8p2Id64fk',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
