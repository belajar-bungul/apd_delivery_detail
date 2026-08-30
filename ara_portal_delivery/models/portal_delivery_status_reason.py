# -*- coding: utf-8 -*-
from odoo import fields, models


class PortalDeliveryStatusReason(models.Model):
    """Master data: reasons a delivery can be put on a status that
    'requires a reason' (typically 'On Hold'). Fully user-managed."""
    _name = 'portal.delivery.status.reason'
    _description = 'Portal Delivery Status Reason'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'A reason with this name already exists.'),
    ]
