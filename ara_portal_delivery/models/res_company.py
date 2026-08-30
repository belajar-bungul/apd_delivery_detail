# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    portal_delivery_status_map_draft_id = fields.Many2one(
        'portal.delivery.status', string='Portal Status for "Draft"')
    portal_delivery_status_map_waiting_id = fields.Many2one(
        'portal.delivery.status', string='Portal Status for "Waiting Another Move"')
    portal_delivery_status_map_confirmed_id = fields.Many2one(
        'portal.delivery.status', string='Portal Status for "Waiting"')
    portal_delivery_status_map_assigned_id = fields.Many2one(
        'portal.delivery.status', string='Portal Status for "Ready"')
    portal_delivery_status_map_done_id = fields.Many2one(
        'portal.delivery.status', string='Portal Status for "Done"')
    portal_delivery_status_map_cancel_id = fields.Many2one(
        'portal.delivery.status', string='Portal Status for "Cancelled"')

    def _get_portal_status_for_picking_state(self, state):
        """Return the portal.delivery.status configured for a given technical
        stock.picking state on this company, or an empty recordset if none
        is configured (in which case the caller should leave the picking's
        portal_status_id untouched)."""
        self.ensure_one()
        field_by_state = {
            'draft': 'portal_delivery_status_map_draft_id',
            'waiting': 'portal_delivery_status_map_waiting_id',
            'confirmed': 'portal_delivery_status_map_confirmed_id',
            'assigned': 'portal_delivery_status_map_assigned_id',
            'done': 'portal_delivery_status_map_done_id',
            'cancel': 'portal_delivery_status_map_cancel_id',
        }
        field_name = field_by_state.get(state)
        return self[field_name] if field_name else self.env['portal.delivery.status']
