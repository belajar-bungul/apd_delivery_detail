# -*- coding: utf-8 -*-
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    portal_status_id = fields.Many2one(
        'portal.delivery.status', string='Portal Status', tracking=True,
        help="Status shown to the customer on the portal delivery page/list. "
             "Independent from the internal Odoo status above, so you can "
             "communicate whatever wording/color makes sense to the customer "
             "(Ready, Waiting, Picking, Packing, On Delivery, On Hold, Done, ...).")
    portal_hold_reason_id = fields.Many2one(
        'portal.delivery.status.reason', string='Portal Hold Reason',
        help="Only shown to the customer when the Portal Status above is "
             "flagged 'Requires a Reason' (e.g. On Hold).")
    portal_status_requires_reason = fields.Boolean(
        related='portal_status_id.requires_reason', string='Status Requires Reason')

    @api.onchange('portal_status_id')
    def _onchange_portal_status_id(self):
        if not self.portal_status_id or not self.portal_status_id.requires_reason:
            self.portal_hold_reason_id = False

    # ------------------------------------------------------------
    # Automatic sync: technical state -> configurable Portal Status
    # (Settings > Portal Delivery > Automatic Status Mapping)
    # ------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        pickings = super().create(vals_list)
        for picking in pickings:
            picking._sync_portal_status_from_state()
        return pickings

    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals:
            for picking in self:
                picking._sync_portal_status_from_state()
        return res

    def _sync_portal_status_from_state(self):
        """Apply the company-configured mapping (Settings > Portal Delivery)
        for this picking's current technical state, if one is configured.
        Uses a bypassing write (not self.write(...)) so this never
        re-triggers the write() override above / recurses."""
        for picking in self:
            mapped_status = picking.company_id._get_portal_status_for_picking_state(picking.state)
            if mapped_status and picking.portal_status_id != mapped_status:
                super(StockPicking, picking).write({'portal_status_id': mapped_status.id})
