# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    portal_delivery_hide_log = fields.Boolean(
        string='Hide Delivery Log from Customers',
        config_parameter='portal_delivery.hide_log',
        default=False,
        help="If enabled, the 'Delivery Log' section (attachments, delivery "
             "photos, signed proof of delivery, ...) is hidden from the "
             "customer portal delivery page. The internal chatter is never "
             "affected.")

    portal_delivery_status_map_draft_id = fields.Many2one(
        related='company_id.portal_delivery_status_map_draft_id', readonly=False,
        string='Draft')
    portal_delivery_status_map_waiting_id = fields.Many2one(
        related='company_id.portal_delivery_status_map_waiting_id', readonly=False,
        string='Waiting Another Move')
    portal_delivery_status_map_confirmed_id = fields.Many2one(
        related='company_id.portal_delivery_status_map_confirmed_id', readonly=False,
        string='Waiting')
    portal_delivery_status_map_assigned_id = fields.Many2one(
        related='company_id.portal_delivery_status_map_assigned_id', readonly=False,
        string='Ready')
    portal_delivery_status_map_done_id = fields.Many2one(
        related='company_id.portal_delivery_status_map_done_id', readonly=False,
        string='Done')
    portal_delivery_status_map_cancel_id = fields.Many2one(
        related='company_id.portal_delivery_status_map_cancel_id', readonly=False,
        string='Cancelled')

    def action_open_portal_delivery_statuses(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Portal Delivery Statuses',
            'res_model': 'portal.delivery.status',
            'view_mode': 'list,form',
            'target': 'current',
        }

    def action_open_portal_delivery_hold_reasons(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Portal Delivery Hold Reasons',
            'res_model': 'portal.delivery.status.reason',
            'view_mode': 'list,form',
            'target': 'current',
        }
