# See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


def _offset_format_timestamp1(
    src_tstamp_str, src_format, dst_format, ignore_unparsable_time=True, context=None
):
    """
    Convert a source timeStamp string into a destination timeStamp string,
    attempting to apply the correct offset if both the server and local
    timeZone are recognized,or no offset at all if they aren't or if
    tz_offset is false (i.e. assuming they are both in the same TZ).

    @param src_tstamp_str: the STR value containing the timeStamp.
    @param src_format: the format to use when parsing the local timeStamp.
    @param dst_format: the format to use when formatting the resulting
     timeStamp.
    @param server_to_client: specify timeZone offset direction (server=src
                             and client=dest if True, or client=src and
                             server=dest if False)
    @param ignore_unparsable_time: if True, return False if src_tstamp_str
                                   cannot be parsed using src_format or
                                   formatted using dst_format.
    @return: destination formatted timestamp, expressed in the destination
             timezone if possible and if tz_offset is true, or src_tstamp_str
             if timezone offset could not be determined.
    """
    if not src_tstamp_str:
        return False
    res = src_tstamp_str
    if src_format and dst_format:
        try:
            # dt_value needs to be a datetime object\
            # (so notime.struct_time or mx.DateTime.DateTime here!)
            dt_value = datetime.strptime(src_tstamp_str, src_format)
            if context.get("tz", False):
                try:
                    import pytz

                    src_tz = pytz.timezone(context["tz"])
                    dst_tz = pytz.timezone("UTC")
                    src_dt = src_tz.localize(dt_value, is_dst=True)
                    dt_value = src_dt.astimezone(dst_tz)
                except Exception:
                    pass
            res = dt_value.strftime(dst_format)
        except Exception:
            # Normal ways to end up here are if strptime or strftime failed
            if not ignore_unparsable_time:
                return False
            pass
    return res


class apartFloor(models.Model):

    _name = "apart.floor"
    _description = "Floor"

    name = fields.Char("Floor Name", required=True, index=True)
    sequence = fields.Integer(index=True)


class apartflatType(models.Model):

    _name = "apart.flat.type"
    _description = "flat Type"

    name = fields.Char(required=True)
    categ_id = fields.Many2one("apart.flat.type", "Category")
    child_ids = fields.One2many("apart.flat.type", "categ_id", "Child Categories")

    def name_get(self):
        def get_names(cat):
            """ Return the list [cat.name, cat.categ_id.name, ...] """
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.categ_id
            return res

        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if not args:
            args = []
        if name:
            # Be sure name_search is symmetric to name_get
            category_names = name.split(" / ")
            parents = list(category_names)
            child = parents.pop()
            domain = [("name", operator, child)]
            if parents:
                names_ids = self.name_search(
                    " / ".join(parents), args=args, operator="ilike", limit=limit
                )
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    categories = self.search([("id", "not in", category_ids)])
                    domain = expression.OR(
                        [[("categ_id", "in", categories.ids)], domain]
                    )
                else:
                    domain = expression.AND(
                        [[("categ_id", "in", category_ids)], domain]
                    )
                for i in range(1, len(category_names)):
                    domain = [
                        [("name", operator, " / ".join(category_names[-1 - i :]))],
                        domain,
                    ]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            categories = self.search(expression.AND([domain, args]), limit=limit)
        else:
            categories = self.search(args, limit=limit)
        return categories.name_get()


class ProductProduct(models.Model):

    _inherit = "product.product"

    isflat = fields.Boolean("Is flat")
    iscategid = fields.Boolean("Is Categ")
    isservice = fields.Boolean("Is Service")


class apartflatAmenitiesType(models.Model):

    _name = "apart.flat.amenities.type"
    _description = "amenities Type"

    name = fields.Char(required=True)
    amenity_id = fields.Many2one("apart.flat.amenities.type", "Category")
    child_ids = fields.One2many(
        "apart.flat.amenities.type", "amenity_id", "Child Categories"
    )

    def name_get(self):
        def get_names(cat):
            """ Return the list [cat.name, cat.amenity_id.name, ...] """
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.amenity_id
            return res

        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if not args:
            args = []
        if name:
            # Be sure name_search is symetric to name_get
            category_names = name.split(" / ")
            parents = list(category_names)
            child = parents.pop()
            domain = [("name", operator, child)]
            if parents:
                names_ids = self.name_search(
                    " / ".join(parents), args=args, operator="ilike", limit=limit
                )
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    categories = self.search([("id", "not in", category_ids)])
                    domain = expression.OR(
                        [[("amenity_id", "in", categories.ids)], domain]
                    )
                else:
                    domain = expression.AND(
                        [[("amenity_id", "in", category_ids)], domain]
                    )
                for i in range(1, len(category_names)):
                    domain = [
                        [("name", operator, " / ".join(category_names[-1 - i :]))],
                        domain,
                    ]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            categories = self.search(expression.AND([domain, args]), limit=limit)
        else:
            categories = self.search(args, limit=limit)
        return categories.name_get()


class apartflatAmenities(models.Model):

    _name = "apart.flat.amenities"
    _description = "flat amenities"

    product_id = fields.Many2one(
        "product.product",
        "Product Category",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
    categ_id = fields.Many2one(
        "apart.flat.amenities.type", string="Amenities Category", required=True
    )
    product_manager = fields.Many2one("res.users", string="Product Manager")


class FolioflatLine(models.Model):

    _name = "folio.flat.line"
    _description = "apart flat Reservation"
    _rec_name = "flat_id"

    flat_id = fields.Many2one("apart.flat", "flat id")
    check_in = fields.Datetime("Check In Date", required=True)
    check_out = fields.Datetime("Check Out Date", required=True)
    folio_id = fields.Many2one("apart.folio", string="Folio Number")
    status = fields.Selection(string="state", related="folio_id.state")


class apartflat(models.Model):

    _name = "apart.flat"
    _description = "apart flat"

    product_id = fields.Many2one(
        "product.product",
        "Product_id",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
    floor_id = fields.Many2one(
        "apart.floor", "Floor No", help="At which floor the flat is located."
    )
    max_adult = fields.Integer()
    max_child = fields.Integer()
    categ_id = fields.Many2one("apart.flat.type", string="flat Category", required=True)
    flat_amenities = fields.Many2many(
        "apart.flat.amenities",
        "temp_tab",
        "flat_amenities",
        "rcateg_id",
        help="List of flat amenities. ",
    )
    status = fields.Selection(
        [("available", "Available"), ("occupied", "Occupied")],
        "Status",
        default="available",
    )
    capacity = fields.Integer("Capacity", required=True)
    flat_line_ids = fields.One2many(
        "folio.flat.line", "flat_id", string="flat Reservation Line"
    )
    product_manager = fields.Many2one("res.users", "Product Manager")

    @api.constrains("capacity")
    def check_capacity(self):
        for flat in self:
            if flat.capacity <= 0:
                raise ValidationError(_("flat capacity must be more than 0"))

    @api.onchange("isflat")
    def isflat_change(self):
        """
        Based on isflat, status will be updated.
        ----------------------------------------
        @param self: object pointer
        """
        if self.isflat is False:
            self.status = "occupied"
        if self.isflat is True:
            self.status = "available"

    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        if "isflat" in vals and vals["isflat"] is False:
            vals.update({"color": 2, "status": "occupied"})
        if "isflat" in vals and vals["isflat"] is True:
            vals.update({"color": 5, "status": "available"})
        ret_val = super(apartflat, self).write(vals)
        return ret_val

    def set_flat_status_occupied(self):
        """
        This method is used to change the state
        to occupied of the apart flat.
        ---------------------------------------
        @param self: object pointer
        """
        return self.write({"isflat": False, "color": 2})

    def set_flat_status_available(self):
        """
        This method is used to change the state
        to available of the apart flat.
        ---------------------------------------
        @param self: object pointer
        """
        return self.write({"isflat": True, "color": 5})


class apartFolio(models.Model):

    _name = "apart.folio"
    _description = "apart folio new"
    _rec_name = "order_id"
    _order = "id"

    def name_get(self):
        res = []
        disp = ""
        for rec in self:
            if rec.order_id:
                disp = str(rec.name)
                res.append((rec.id, disp))
        return res

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        if args is None:
            args = []
        args += [("name", operator, name)]
        mids = self.search(args, limit=100)
        return mids.name_get()

    @api.model
    def _needaction_count(self, domain=None):
        """
         Show a count of draft state folio on the menu badge.
         @param self: object pointer
        """
        return self.search_count([("state", "=", "draft")])

    @api.model
    def _get_checkin_date(self):
        if self._context.get("tz"):
            to_zone = self._context.get("tz")
        else:
            to_zone = "UTC"
        return _offset_format_timestamp1(
            time.strftime("%Y-%m-%d 12:00:00"),
            DEFAULT_SERVER_DATETIME_FORMAT,
            DEFAULT_SERVER_DATETIME_FORMAT,
            ignore_unparsable_time=True,
            context={"tz": to_zone},
        )

    @api.model
    def _get_checkout_date(self):
        if self._context.get("tz"):
            to_zone = self._context.get("tz")
        else:
            to_zone = "UTC"
        tm_delta = timedelta(days=1)
        return (
            datetime.strptime(
                _offset_format_timestamp1(
                    time.strftime("%Y-%m-%d 12:00:00"),
                    DEFAULT_SERVER_DATETIME_FORMAT,
                    DEFAULT_SERVER_DATETIME_FORMAT,
                    ignore_unparsable_time=True,
                    context={"tz": to_zone},
                ),
                "%Y-%m-%d %H:%M:%S",
            )
            + tm_delta
        )

    def copy(self, default=None):
        """
        @param self: object pointer
        @param default: dict of default values to be set
        """
        return super(apartFolio, self).copy(default=default)

    name = fields.Char("Folio Number", readonly=True, index=True, default="New")
    order_id = fields.Many2one(
        "sale.order", "Order", delegate=True, required=True, ondelete="cascade"
    )
    checkin_date = fields.Datetime(
        "Check In",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=_get_checkin_date,
    )
    checkout_date = fields.Datetime(
        "Check Out",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=_get_checkout_date,
    )
    flat_lines = fields.One2many(
        "apart.folio.line",
        "folio_id",
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
        help="apart flat reservation detail.",
    )
    service_lines = fields.One2many(
        "apart.service.line",
        "folio_id",
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
        help="apart services details provided to"
        "Customer and it will included in "
        "the main Invoice.",
    )
    apart_policy = fields.Selection(
        [
            ("prepaid", "On Booking"),
            ("manual", "On Check In"),
            ("picking", "On Checkout"),
        ],
        "apart Policy",
        default="manual",
        help="apart policy for payment that "
        "either the guest has to payment at "
        "booking time or check-in "
        "check-out time.",
    )
    duration = fields.Float(
        "Duration in Days",
        help="Number of days which will automatically "
        "count from the check-in and check-out date. ",
    )
    apart_invoice_id = fields.Many2one("account.move", "Invoice", copy=False)
    duration_dummy = fields.Float("Duration Dummy")

    @api.constrains("flat_lines")
    def folio_flat_lines(self):
        """
        This method is used to validate the flat_lines.
        ------------------------------------------------
        @param self: object pointer
        @return: raise warning depending on the validation
        """
        folio_flats = []
        for flat in self[0].flat_lines:
            if flat.product_id.id in folio_flats:
                raise ValidationError(_("You Cannot Take Same flat Twice"))
            folio_flats.append(flat.product_id.id)

    @api.onchange("checkout_date", "checkin_date")
    def onchange_dates(self):
        """
        This method gives the duration between check in and checkout
        if customer will leave only for some hour it would be considers
        as a whole day.If customer will check in checkout for more or equal
        hours, which configured in company as additional hours than it would
        be consider as full days
        --------------------------------------------------------------------
        @param self: object pointer
        @return: Duration and checkout_date
        """
        configured_addition_hours = 0
        wid = self.warehouse_id
        whouse_com_id = wid or wid.company_id
        if whouse_com_id:
            configured_addition_hours = wid.company_id.additional_hours
        myduration = 0
        if self.checkout_date and self.checkin_date:
            dur = self.checkin_date - self.checkin_date
            sec_dur = dur.seconds
            if (not dur.days and not sec_dur) or (dur.days and not sec_dur):
                myduration = dur.days
            else:
                myduration = dur.days + 1
            # To calculate additional hours in apart flat as per minutes
            if configured_addition_hours > 0:
                additional_hours = abs((dur.seconds / 60) / 60)
                if additional_hours >= configured_addition_hours:
                    myduration += 1
        self.duration = myduration
        self.duration_dummy = self.duration

    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        @return: new record set for apart folio.
        """
        if not "service_lines" and "folio_id" in vals:
            tmp_flat_lines = vals.get("flat_lines", [])
            vals["order_policy"] = vals.get("apart_policy", "manual")
            vals.update({"flat_lines": []})
            folio_id = super(apartFolio, self).create(vals)
            for line in tmp_flat_lines:
                line[2].update({"folio_id": folio_id.id})
            vals.update({"flat_lines": tmp_flat_lines})
            folio_id.write(vals)
        else:
            if not vals:
                vals = {}
            vals["name"] = self.env["ir.sequence"].next_by_code("apart.folio")
            vals["duration"] = vals.get("duration", 0.0) or vals.get(
                "duration_dummy", 0.0
            )
            folio_id = super(apartFolio, self).create(vals)
            folio_flat_line_obj = self.env["folio.flat.line"]
            h_flat_obj = self.env["apart.flat"]
            try:
                for rec in folio_id:
                    if not rec.reservation_id:
                        for flat_rec in rec.flat_lines:
                            prod = flat_rec.product_id.name
                            flat_obj = h_flat_obj.search([("name", "=", prod)])
                            flat_obj.write({"isflat": False})
                            vals = {
                                "flat_id": flat_obj.id,
                                "check_in": rec.checkin_date,
                                "check_out": rec.checkout_date,
                                "folio_id": rec.id,
                            }
                            folio_flat_line_obj.create(vals)
            except Exception:
                for rec in folio_id:
                    for flat_rec in rec.flat_lines:
                        prod = flat_rec.product_id.name
                        flat_obj = h_flat_obj.search([("name", "=", prod)])
                        flat_obj.write({"isflat": False})
                        vals = {
                            "flat_id": flat_obj.id,
                            "check_in": rec.checkin_date,
                            "check_out": rec.checkout_date,
                            "folio_id": rec.id,
                        }
                        folio_flat_line_obj.create(vals)
        return folio_id

    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        product_obj = self.env["product.product"]
        h_flat_obj = self.env["apart.flat"]
        folio_flat_line_obj = self.env["folio.flat.line"]
        flat_lst = []
        flat_lst1 = []
        for rec in self:
            for res in rec.flat_lines:
                flat_lst1.append(res.product_id.id)
            if vals and vals.get("duration_dummy", False):
                vals["duration"] = vals.get("duration_dummy", 0.0)
            else:
                vals["duration"] = rec.duration
            for folio_rec in rec.flat_lines:
                flat_lst.append(folio_rec.product_id.id)
            new_flats = set(flat_lst).difference(set(flat_lst1))
            if len(list(new_flats)) != 0:
                flat_list = product_obj.browse(list(new_flats))
                for rm in flat_list:
                    flat_obj = h_flat_obj.search([("name", "=", rm.name)])
                    flat_obj.write({"isflat": False})
                    vals = {
                        "flat_id": flat_obj.id,
                        "check_in": rec.checkin_date,
                        "check_out": rec.checkout_date,
                        "folio_id": rec.id,
                    }
                    folio_flat_line_obj.create(vals)
            if len(list(new_flats)) == 0:
                flat_list_obj = product_obj.browse(flat_lst1)
                for rom in flat_list_obj:
                    flat_obj = h_flat_obj.search([("name", "=", rom.name)])
                    flat_obj.write({"isflat": False})
                    flat_vals = {
                        "flat_id": flat_obj.id,
                        "check_in": rec.checkin_date,
                        "check_out": rec.checkout_date,
                        "folio_id": rec.id,
                    }
                    folio_romline_rec = folio_flat_line_obj.search(
                        [("folio_id", "=", rec.id)]
                    )
                    folio_romline_rec.write(flat_vals)
        return super(apartFolio, self).write(vals)

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        """
        When you change partner_id it will update the partner_invoice_id,
        partner_shipping_id and pricelist_id of the apart folio as well
        ---------------------------------------------------------------
        @param self: object pointer
        """
        if self.partner_id:
            partner_rec = self.env["res.partner"].browse(self.partner_id.id)
            order_ids = [folio.order_id.id for folio in self]
            if not order_ids:
                self.partner_invoice_id = partner_rec.id
                self.partner_shipping_id = partner_rec.id
                self.pricelist_id = partner_rec.property_product_pricelist.id
                raise ValidationError(_("Not Any Order For  %s " % (partner_rec.name)))
            else:
                self.partner_invoice_id = partner_rec.id
                self.partner_shipping_id = partner_rec.id
                self.pricelist_id = partner_rec.property_product_pricelist.id

    def action_done(self):
        for rec in self:
            rec.write({"state": "done"})

    def action_invoice_create(self, grouped=False, final=False):
        """
        @param self: object pointer
        """
        flat_lst = []
        invoice_id = self.order_id._create_invoices(grouped=False, final=False)
        for line in self:
            values = {"invoiced": True, "apart_invoice_id": invoice_id}
            line.write(values)
            for rec in line.flat_lines:
                flat_lst.append(rec.product_id)
            for flat in flat_lst:
                flat_rec = self.env["apart.flat"].search([("name", "=", flat.name)])
                flat_rec.write({"isflat": True})
        return invoice_id

    def action_invoice_cancel(self):
        """
        @param self: object pointer
        """
        if not self.order_id:
            raise UserError(_("Order id is not available"))
        for sale in self:
            for line in sale.order_line:
                line.write({"invoiced": "invoiced"})
        self.state = "invoice_except"
        return self.order_id.invoice_ids.action_invoice_cancel()

    def action_cancel(self):
        """
        @param self: object pointer
        """
        if not self.order_id:
            raise UserError(_("Order id is not available"))
        for sale in self:
            for invoice in sale.invoice_ids:
                invoice.state = "cancel"
        return self.order_id.action_cancel()

    def action_confirm(self):
        for order in self.order_id:
            order.state = "sale"
            if not order.analytic_account_id:
                for line in order.order_line:
                    if line.product_id.invoice_policy == "cost":
                        order._create_analytic_account()
                        break
        config_parameter_obj = self.env["ir.config_parameter"]
        if config_parameter_obj.sudo().get_param("sale.auto_done_setting"):
            self.order_id.action_done()

    def test_state(self, mode):
        """
        @param self: object pointer
        @param mode: state of workflow
        """
        write_done_ids = []
        write_cancel_ids = []
        if write_done_ids:
            test_obj = self.env["sale.order.line"].browse(write_done_ids)
            test_obj.write({"state": "done"})
        if write_cancel_ids:
            test_obj = self.env["sale.order.line"].browse(write_cancel_ids)
            test_obj.write({"state": "cancel"})

    def action_cancel_draft(self):
        """
        @param self: object pointer
        """
        if not len(self._ids):
            return False
        query = "select id from sale_order_line \
        where order_id IN %s and state=%s"
        self._cr.execute(query, (tuple(self._ids), "cancel"))
        cr1 = self._cr
        line_ids = map(lambda x: x[0], cr1.fetchall())
        self.write({"state": "draft", "invoice_ids": []})
        sale_line_obj = self.env["sale.order.line"].browse(line_ids)
        sale_line_obj.write(
            {"invoiced": False, "state": "draft", "invoice_lines": [(6, 0, [])]}
        )
        return True


class apartFolioLine(models.Model):

    _name = "apart.folio.line"
    _description = "apart folio1 flat line"

    def copy(self, default=None):
        """
        @param self: object pointer
        @param default: dict of default values to be set
        """
        return super(apartFolioLine, self).copy(default=default)

    @api.model
    def _get_checkin_date(self):
        if "checkin" in self._context:
            return self._context["checkin"]
        return time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    @api.model
    def _get_checkout_date(self):
        if "checkout" in self._context:
            return self._context["checkout"]
        return time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    order_line_id = fields.Many2one(
        "sale.order.line",
        string="Order Line",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
    folio_id = fields.Many2one("apart.folio", string="Folio", ondelete="cascade")
    checkin_date = fields.Datetime(
        string="Check In", required=True, default=_get_checkin_date
    )
    checkout_date = fields.Datetime(
        string="Check Out", required=True, default=_get_checkout_date
    )
    is_reserved = fields.Boolean(
        string="Is Reserved",
        help="True when folio line created from \
                                 Reservation",
    )

    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        @return: new record set for apart folio line.
        """
        if "folio_id" in vals:
            folio = self.env["apart.folio"].browse(vals["folio_id"])
            vals.update({"order_id": folio.order_id.id})
        return super(apartFolioLine, self).create(vals)

    @api.constrains("checkin_date", "checkout_date")
    def check_dates(self):
        """
        This method is used to validate the checkin_date and checkout_date.
        -------------------------------------------------------------------
        @param self: object pointer
        @return: raise warning depending on the validation
        """
        if self.checkin_date >= self.checkout_date:
            raise ValidationError(
                _(
                    "flat line Check In Date Should be \
                less than the Check Out Date!"
                )
            )
        if self.folio_id.date_order and self.checkin_date:
            if self.checkin_date <= self.folio_id.date_order:
                raise ValidationError(
                    _(
                        "flat line check in date should be \
                greater than the current date."
                    )
                )

    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        sale_line_obj = self.env["sale.order.line"]
        fr_obj = self.env["folio.flat.line"]
        for line in self:
            if line.order_line_id:
                sale_unlink_obj = sale_line_obj.browse([line.order_line_id.id])
                for rec in sale_unlink_obj:
                    flat_obj = self.env["apart.flat"].search([("name", "=", rec.name)])
                    if flat_obj.id:
                        folio_arg = [
                            ("folio_id", "=", line.folio_id.id),
                            ("flat_id", "=", flat_obj.id),
                        ]
                        folio_flat_line_myobj = fr_obj.search(folio_arg)
                        if folio_flat_line_myobj.id:
                            folio_flat_line_myobj.unlink()
                            flat_obj.write({"isflat": True, "status": "available"})
                sale_unlink_obj.unlink()
        return super(apartFolioLine, self).unlink()

    @api.onchange("product_id")
    def product_id_change(self):
        """
 -        @param self: object pointer
 -        """
        context = dict(self._context)
        if not context:
            context = {}
        if context.get("folio", False):
            if self.product_id and self.folio_id.partner_id:
                self.name = self.product_id.name
                self.price_unit = self.product_id.list_price
                self.product_uom = self.product_id.uom_id
                tax_obj = self.env["account.tax"]
                pr = self.product_id
                self.price_unit = tax_obj._fix_tax_included_price(
                    pr.price, pr.taxes_id, self.tax_id
                )
        else:
            if not self.product_id:
                return {"domain": {"product_uom": []}}
            val = {}
            pr = self.product_id.with_context(
                lang=self.folio_id.partner_id.lang,
                partner=self.folio_id.partner_id.id,
                quantity=val.get("product_uom_qty") or self.product_uom_qty,
                date=self.folio_id.date_order,
                pricelist=self.folio_id.pricelist_id.id,
                uom=self.product_uom.id,
            )
            p = pr.with_context(pricelist=self.order_id.pricelist_id.id).price
            if self.folio_id.pricelist_id and self.folio_id.partner_id:
                obj = self.env["account.tax"]
                val["price_unit"] = obj._fix_tax_included_price(
                    p, pr.taxes_id, self.tax_id
                )

    @api.onchange("checkin_date", "checkout_date")
    def on_change_checkout(self):
        """
        When you change checkin_date or checkout_date it will checked it
        and update the qty of apart folio line
        -----------------------------------------------------------------
        @param self: object pointer
        """
        configured_addition_hours = 0
        fwhouse_id = self.folio_id.warehouse_id
        fwc_id = fwhouse_id or fwhouse_id.company_id
        if fwc_id:
            configured_addition_hours = fwhouse_id.company_id.additional_hours
        myduration = 0
        if not self.checkin_date:
            self.checkin_date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if not self.checkout_date:
            self.checkout_date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if self.checkin_date and self.checkout_date:
            dur = self.checkout_date - self.checkin_date
            sec_dur = dur.seconds
            if (not dur.days and not sec_dur) or (dur.days and not sec_dur):
                myduration = dur.days
            else:
                myduration = dur.days + 1
            #            To calculate additional hours in apart flat as per minutes
            if configured_addition_hours > 0:
                additional_hours = abs((dur.seconds / 60) / 60)
                if additional_hours >= configured_addition_hours:
                    myduration += 1
        self.product_uom_qty = myduration
        apart_flat_obj = self.env["apart.flat"]
        apart_flat_ids = apart_flat_obj.search([])
        avail_prod_ids = []
        for flat in apart_flat_ids:
            assigned = False
            for rm_line in flat.flat_line_ids:
                if rm_line.status != "cancel":
                    if (
                        self.checkin_date <= rm_line.check_in <= self.checkout_date
                    ) or (self.checkin_date <= rm_line.check_out <= self.checkout_date):
                        assigned = True
                    elif (
                        rm_line.check_in <= self.checkin_date <= rm_line.check_out
                    ) or (rm_line.check_in <= self.checkout_date <= rm_line.check_out):
                        assigned = True
            if not assigned:
                avail_prod_ids.append(flat.product_id.id)
        domain = {"product_id": [("id", "in", avail_prod_ids)]}
        return {"domain": domain}

    def button_confirm(self):
        """
        @param self: object pointer
        """
        for folio in self:
            line = folio.order_line_id
            line.button_confirm()
        return True

    def button_done(self):
        """
        @param self: object pointer
        """
        for rec in self:
            lines = [folio_line.order_line_id for folio_line in rec]
            lines.button_done()
            rec.write({"state": "done"})
        return True

    def copy_data(self, default=None):
        """
        @param self: object pointer
        @param default: dict of default values to be set
        """
        line_id = self.order_line_id.id
        sale_line_obj = self.env["sale.order.line"].browse(line_id)
        return sale_line_obj.copy_data(default=default)


class apartServiceLine(models.Model):

    _name = "apart.service.line"
    _description = "apart Service line"

    def copy(self, default=None):
        """
        @param self: object pointer
        @param default: dict of default values to be set
        """
        return super(apartServiceLine, self).copy(default=default)

    @api.model
    def _service_checkin_date(self):
        if "checkin" in self._context:
            return self._context["checkin"]
        return time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    @api.model
    def _service_checkout_date(self):
        if "checkout" in self._context:
            return self._context["checkout"]
        return time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    service_line_id = fields.Many2one(
        "sale.order.line",
        "Service Line",
        required=True,
        delegate=True,
        ondelete="cascade",
    )
    folio_id = fields.Many2one("apart.folio", "Folio", ondelete="cascade")
    ser_checkin_date = fields.Datetime(
        "From Date", required=True, default=_service_checkin_date
    )
    ser_checkout_date = fields.Datetime(
        "To Date", required=True, default=_service_checkout_date
    )

    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        @return: new record set for apart service line.
        """
        if "folio_id" in vals:
            folio = self.env["apart.folio"].browse(vals["folio_id"])
            vals.update({"order_id": folio.order_id.id})
        return super(apartServiceLine, self).create(vals)

    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        s_line_obj = self.env["sale.order.line"]
        for line in self:
            if line.service_line_id:
                sale_unlink_obj = s_line_obj.browse([line.service_line_id.id])
                sale_unlink_obj.unlink()
        return super(apartServiceLine, self).unlink()

    @api.onchange("product_id")
    def product_id_change(self):
        """
        @param self: object pointer
        """
        if self.product_id and self.folio_id.partner_id:
            self.name = self.product_id.name
            self.price_unit = self.product_id.list_price
            self.product_uom = self.product_id.uom_id
            tax_obj = self.env["account.tax"]
            prod = self.product_id
            self.price_unit = tax_obj._fix_tax_included_price(
                prod.price, prod.taxes_id, self.tax_id
            )

    @api.onchange("ser_checkin_date", "ser_checkout_date")
    def on_change_checkout(self):
        """
        When you change checkin_date or checkout_date it will checked it
        and update the qty of apart service line
        -----------------------------------------------------------------
        @param self: object pointer
        """
        if not self.ser_checkin_date:
            time_a = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            self.ser_checkin_date = time_a
        if not self.ser_checkout_date:
            self.ser_checkout_date = time_a
        if self.ser_checkout_date < self.ser_checkin_date:
            raise ValidationError(_("Checkout must be greater or equal checkin date"))
        if self.ser_checkin_date and self.ser_checkout_date:
            diffDate = self.ser_checkout_date - self.ser_checkin_date
            qty = diffDate.days + 1
            self.product_uom_qty = qty

    def button_confirm(self):
        """
        @param self: object pointer
        """
        for folio in self:
            line = folio.service_line_id
            if line:
                return line.button_confirm()
        return True

    def button_done(self):
        """
        @param self: object pointer
        """
        for folio in self:
            line = folio.service_line_id
            if line:
                return line.button_confirm()
        return True

    def copy_data(self, default=None):
        """
        @param self: object pointer
        @param default: dict of default values to be set
        """
        sale_line_obj = self.env["sale.order.line"].browse(self.service_line_id.id)
        return sale_line_obj.copy_data(default=default)


class apartServiceType(models.Model):

    _name = "apart.service.type"
    _description = "Service Type"

    name = fields.Char("Service Name", size=64, required=True)
    service_id = fields.Many2one("apart.service.type", "Service Category")
    child_ids = fields.One2many("apart.service.type", "service_id", "Child Categories")

    def name_get(self):
        def get_names(cat):
            """ Return the list [cat.name, cat.service_id.name, ...] """
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.service_id
            return res

        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if not args:
            args = []
        if name:
            # Be sure name_search is symetric to name_get
            category_names = name.split(" / ")
            parents = list(category_names)
            child = parents.pop()
            domain = [("name", operator, child)]
            if parents:
                names_ids = self.name_search(
                    " / ".join(parents), args=args, operator="ilike", limit=limit
                )
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    categories = self.search([("id", "not in", category_ids)])
                    domain = expression.OR(
                        [[("service_id", "in", categories.ids)], domain]
                    )
                else:
                    domain = expression.AND(
                        [[("service_id", "in", category_ids)], domain]
                    )
                for i in range(1, len(category_names)):
                    domain = [
                        [("name", operator, " / ".join(category_names[-1 - i :]))],
                        domain,
                    ]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            categories = self.search(expression.AND([domain, args]), limit=limit)
        else:
            categories = self.search(args, limit=limit)
        return categories.name_get()


class apartServices(models.Model):

    _name = "apart.services"
    _description = "apart Services and its charges"

    product_id = fields.Many2one(
        "product.product",
        "Service_id",
        required=True,
        ondelete="cascade",
        delegate=True,
    )
    categ_id = fields.Many2one(
        "apart.service.type", string="Service Category", required=True
    )
    product_manager = fields.Many2one("res.users", string="Product Manager")


class ResCompany(models.Model):

    _inherit = "res.company"

    additional_hours = fields.Integer(
        "Additional Hours",
        help="Provide the min hours value for \
                                      check in, checkout days, whatever the \
                                      hours will be provided here based on \
                                      that extra days will be calculated.",
    )


class AccountMove(models.Model):

    _inherit = "account.move"

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        if self._context.get("folio_id"):
            folio = self.env["apart.folio"].browse(self._context["folio_id"])
            folio.write({"apart_invoice_id": res.id, "invoice_status": "invoiced"})
        return res
