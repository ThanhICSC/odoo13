# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2017-Today Ascetic Business Solution <www.nds4it.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    regno = fields.Char(string='Registration number' )
    genname = fields.Char(string='Generic Name')
    dossage = fields.Char    (string='Dosage Form' )
    routadm = fields.Char(string='Route of Administration' )        
    shelflife = fields.Char(string='Shelf-life (mon)')        
    storagecon = fields.Char(string='Storage Condition')        
    manufature = fields.Char(string='Manufacturer') 
    agent = fields.Char  (string='Agent')                           
    authstatu = fields.Char(string='Authorization status' )        
