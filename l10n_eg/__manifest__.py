# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (C) 2018 Mahmoud Abdel Latif (<http://mah007.com>) 01002688172

{
    'name': 'Egypt - Accounting',
    'version': '13.0',
    'author': 'Ali Elgarhi',
    'website': 'http://www.nds4it.com',
    'category': 'Localization',
    'license': 'AGPL-3',
    'description': """
Arab Republic of Egypt accounting chart and localization. 
=======================================================

    """,
    'depends': ['base', 'account'],
    'data': [
             'data/account_data.xml',
             'data/l10n_eg_chart_data.xml',
             'data/account_chart_template_data.yml',
    ],
}
