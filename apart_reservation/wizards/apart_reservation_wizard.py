# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class apartReservationWizard(models.TransientModel):
    _name = 'apart.reservation.wizard'
    _description = 'Allow to generate a reservation'

    date_start = fields.Datetime('Start Date', required=True)
    date_end = fields.Datetime('End Date', required=True)

    
    def report_reservation_detail(self):
        data = {
            'ids': self.ids,
            'model': 'apart.reservation',
            'form': self.read(['date_start', 'date_end'])[0]
        }
        return self.env.ref('apart_reservation.apart_flatres_details'
                            ).report_action(self, data=data)

    
    def report_checkin_detail(self):
        data = {
            'ids': self.ids,
            'model': 'apart.reservation',
            'form': self.read(['date_start', 'date_end'])[0],
        }
        return self.env.ref('apart_reservation.apart_checkin_details'
                            ).report_action(self, data=data)

    
    def report_checkout_detail(self):
        data = {
            'ids': self.ids,
            'model': 'apart.reservation',
            'form': self.read(['date_start', 'date_end'])[0]
        }
        return self.env.ref('apart_reservation.apart_checkout_details'
                            ).report_action(self, data=data)

    
    def report_maxflat_detail(self):
        data = {
            'ids': self.ids,
            'model': 'apart.reservation',
            'form': self.read(['date_start', 'date_end'])[0]
        }
        return self.env.ref('apart_reservation.apart_maxflat_details'
                            ).report_action(self, data=data)


class MakeFolioWizard(models.TransientModel):
    _name = 'wizard.make.folio'
    _description = 'Allow to generate the folio'

    grouped = fields.Boolean('Group the Folios')

    
    def makeFolios(self):
        order_obj = self.env['apart.reservation']
        newinv = []
        for order in order_obj.browse(self.env.context.get('active_ids', [])):
            for folio in order.folio_id:
                newinv.append(folio.id)
        return {
            'domain': "[('id','in', [" + ','.join(map(str, newinv)) + "])]",
            'name': 'Folios',
            'view_mode': 'tree,form',
            'res_model': 'apart.folio',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }
