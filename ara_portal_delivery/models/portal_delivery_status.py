# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PortalDeliveryStatus(models.Model):
    """Master data: the list of statuses shown on the customer portal for
    deliveries (Ready, Waiting, Picking, Packing, On Delivery, On Hold,
    Done, ...). Fully user-managed: add/rename/reorder/recolor freely.

    This is intentionally decoupled from stock.picking.state - it's a
    separate, portal-facing label that a warehouse user sets manually on
    the picking (see stock_picking.py: portal_status_id).
    """
    _name = 'portal.delivery.status'
    _description = 'Portal Delivery Status'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    color = fields.Char(
        string='Color', default='#875A7B',
        help="Hex color (e.g. #3AAED8) used for this status' badge on the customer portal.")
    requires_reason = fields.Boolean(
        string='Requires a Reason',
        help="If enabled, deliveries carrying this status will show an extra "
             "'Reason' field (drawn from Portal Delivery Hold Reasons) to the "
             "customer on the portal, e.g. for an 'On Hold' status.")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'A portal delivery status with this name already exists.'),
    ]
