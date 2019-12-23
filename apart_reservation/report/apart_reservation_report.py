# See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ReportTestCheckin(models.AbstractModel):
    _name = "report.apart_reservation.report_checkin_qweb"
    _description = 'Auxiliar to get the check in report'

    def _get_flat_type(self, date_start, date_end):
        reservation_obj = self.env['apart.reservation']
        flat_dom = [('checkin', '>=', date_start),
                    ('checkout', '<=', date_end)]
        res = reservation_obj.search(flat_dom)
        return res

    def _get_flat_nos(self, date_start, date_end):
        reservation_obj = self.env['apart.reservation']
        res = reservation_obj.search([('checkin', '>=', date_start),
                                      ('checkout', '<=', date_end)])
        return res

    def get_checkin(self, date_start, date_end):
        reservation_obj = self.env['apart.reservation']
        res = reservation_obj.search([('checkin', '>=', date_start),
                                      ('checkin', '<=', date_end)])
        return res

    @api.model
    def _get_report_values(self, docids, data):
        self.model = self.env.context.get('active_model')
        if data is None:
            data = {}
        if not docids:
            docids = data['form'].get('docids')
        folio_profile = self.env['apart.reservation'].browse(docids)
        date_start = data.get('date_start', fields.Date.today())
        date_end = data['form'].get('date_end', str(datetime.now() +
                                    relativedelta(months=+1,
                                                  day=1, days=-1))[:10])
        rm_act = self.with_context(data['form'].get('used_context', {}))
        _get_flat_type = rm_act._get_flat_type(date_start, date_end)
        _get_flat_nos = rm_act._get_flat_nos(date_start, date_end)
        get_checkin = rm_act.get_checkin(date_start, date_end)
        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': folio_profile,
            'time': time,
            'get_flat_type': _get_flat_type,
            'get_flat_nos': _get_flat_nos,
            'get_checkin': get_checkin,
        }


class ReportTestCheckout(models.AbstractModel):
    _name = "report.apart_reservation.report_checkout_qweb"
    _description = 'Auxiliar to get the check out report'

    def _get_flat_type(self, date_start, date_end):
        reservation_obj = self.env['apart.reservation']
        res = reservation_obj.search([('checkout', '>=', date_start),
                                      ('checkout', '<=', date_end)])
        return res

    def _get_flat_nos(self, date_start, date_end):
        reservation_obj = self.env['apart.reservation']
        res = reservation_obj.search([('checkout', '>=', date_start),
                                      ('checkout', '<=', date_end)])
        return res

    def _get_checkout(self, date_start, date_end):
        reservation_obj = self.env['apart.reservation']
        res = reservation_obj.search([('checkout', '>=', date_start),
                                      ('checkout', '<=', date_end)])
        return res

    @api.model
    def _get_report_values(self, docids, data):
        self.model = self.env.context.get('active_model')
        if data is None:
            data = {}
        if not docids:
            docids = data['form'].get('docids')
        folio_profile = self.env['apart.reservation'].browse(docids)
        date_start = data.get('date_start', fields.Date.today())
        date_end = data['form'].get('date_end', str(datetime.now() +
                                    relativedelta(months=+1,
                                                  day=1, days=-1))[:10])
        rm_act = self.with_context(data['form'].get('used_context', {}))
        _get_flat_type = rm_act._get_flat_type(date_start, date_end)
        _get_flat_nos = rm_act._get_flat_nos(date_start, date_end)
        _get_checkout = rm_act._get_checkout(date_start, date_end)
        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': folio_profile,
            'time': time,
            'get_flat_type': _get_flat_type,
            'get_flat_nos': _get_flat_nos,
            'get_checkout': _get_checkout,
        }


class ReportTestMaxflat(models.AbstractModel):
    _name = "report.apart_reservation.report_maxflat_qweb"
    _description = 'Auxiliar to get the flat report'

    def _get_flat_type(self, date_start, date_end):
        reservation_obj = self.env['apart.reservation']
        tids = reservation_obj.search([('checkin', '>=', date_start),
                                       ('checkout', '<=', date_end)])
        res = reservation_obj.browse(tids)
        return res

    def _get_flat_nos(self, date_start, date_end):
        reservation_obj = self.env['apart.reservation']
        tids = reservation_obj.search([('checkin', '>=', date_start),
                                       ('checkout', '<=', date_end)])
        res = reservation_obj.browse(tids)
        return res

    def _get_data(self, date_start, date_end):
        reservation_obj = self.env['apart.reservation']
        res = reservation_obj.search([('checkin', '>=', date_start),
                                      ('checkout', '<=', date_end)])
        return res

    def _get_flat_used_detail(self, date_start, date_end):
        flat_used_details = []
        apart_flat_obj = self.env['apart.flat']
        flat_ids = apart_flat_obj.search([])
        for flat in apart_flat_obj.browse(flat_ids.ids):
            counter = 0
            details = {}
            if flat.flat_reservation_line_ids:
                end_date = datetime.strptime(date_end,
                                             DEFAULT_SERVER_DATETIME_FORMAT)
                start_date = datetime.strptime(date_start,
                                               DEFAULT_SERVER_DATETIME_FORMAT)
                for flat_resv_line in flat.flat_reservation_line_ids:
                    if(flat_resv_line.check_in >= start_date and
                       flat_resv_line.check_in <= end_date):
                        counter += 1
            if counter >= 1:
                details.update({'name': flat.name or '',
                                'no_of_times_used': counter})
                flat_used_details.append(details)
        return flat_used_details

    @api.model
    def _get_report_values(self, docids, data):
        self.model = self.env.context.get('active_model')
        if data is None:
            data = {}
        if not docids:
            docids = data['form'].get('docids')
        folio_profile = self.env['apart.reservation'].browse(docids)
        date_start = data['form'].get('date_start', fields.Date.today())
        date_end = data['form'].get('date_end', str(datetime.now() +
                                    relativedelta(months=+1,
                                                  day=1, days=-1))[:10])
        rm_act = self.with_context(data['form'].get('used_context', {}))
        _get_flat_type = rm_act._get_flat_type(date_start, date_end)
        _get_flat_nos = rm_act._get_flat_nos(date_start, date_end)
        _get_data = rm_act._get_data(date_start, date_end)
        _get_flat_used_detail = rm_act._get_flat_used_detail(date_start,
                                                             date_end)
        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': folio_profile,
            'time': time,
            'get_flat_type': _get_flat_type,
            'get_flat_nos': _get_flat_nos,
            'get_data': _get_data,
            'get_flat_used_detail': _get_flat_used_detail,
        }


class ReportTestflatres(models.AbstractModel):
    _name = "report.apart_reservation.report_flatres_qweb"
    _description = 'Auxiliar to get the flat report'

    def _get_flat_type(self, date_start, date_end):
        reservation_obj = self.env['apart.reservation']
        tids = reservation_obj.search([('checkin', '>=', date_start),
                                       ('checkout', '<=', date_end)])
        res = reservation_obj.browse(tids)
        return res

    def _get_flat_nos(self, date_start, date_end):
        reservation_obj = self.env['apart.reservation']
        tids = reservation_obj.search([('checkin', '>=', date_start),
                                       ('checkout', '<=', date_end)])
        res = reservation_obj.browse(tids)
        return res

    def _get_data(self, date_start, date_end):
        reservation_obj = self.env['apart.reservation']
        res = reservation_obj.search([('checkin', '>=', date_start),
                                      ('checkout', '<=', date_end)])
        return res

    @api.model
    def _get_report_values(self, docids, data):
        self.model = self.env.context.get('active_model')
        if data is None:
            data = {}
        if not docids:
            docids = data['form'].get('docids')
        folio_profile = self.env['apart.reservation'].browse(docids)
        date_start = data.get('date_start', fields.Date.today())
        date_end = data['form'].get('date_end', str(datetime.now() +
                                    relativedelta(months=+1,
                                                  day=1, days=-1))[:10])
        rm_act = self.with_context(data['form'].get('used_context', {}))
        _get_flat_type = rm_act._get_flat_type(date_start, date_end)
        _get_flat_nos = rm_act._get_flat_nos(date_start, date_end)
        _get_data = rm_act._get_data(date_start, date_end)
        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': folio_profile,
            'time': time,
            'get_flat_type': _get_flat_type,
            'get_flat_nos': _get_flat_nos,
            'get_data': _get_data,
        }
