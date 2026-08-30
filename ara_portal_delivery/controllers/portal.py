# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.osv.expression import AND, OR

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class PortalDelivery(CustomerPortal):

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------
    def _delivery_base_domain(self):
        """Domain restricting stock.picking to OUTGOING deliveries that
        belong to the logged in portal partner (or one of its child
        contacts / delivery addresses). This mirrors the ir.rule defined
        in security/portal_delivery_security.xml so the list and the
        record-access check always agree."""
        partner = request.env.user.partner_id
        return [
            ('partner_id', 'child_of', partner.commercial_partner_id.id),
            ('picking_type_id.code', '=', 'outgoing'),
        ]

    def _delivery_get_page_view_values(self, delivery, **kwargs):
        values = {
            'delivery': delivery,
            'page_name': 'delivery',
            'user': request.env.user,
            'show_delivery_log': request.env['ir.config_parameter'].sudo().get_param(
                'portal_delivery.hide_log', default='False') != 'True',
        }
        return self._get_page_view_values(
            delivery, kwargs.get('access_token'), values, 'my_deliveries_history', False, **kwargs
        )

    def _get_delivery_sudo(self, delivery_id):
        """Fetch a stock.picking, enforcing that the current user actually
        has read access to it (own outgoing deliveries only, per the
        ir.rule in security/portal_delivery_security.xml).

        Unlike the generic ``_document_check_access`` helper, this does
        not assume the model has an ``access_token`` field (stock.picking
        doesn't), which avoids an AttributeError on access-denied."""
        Picking = request.env['stock.picking']
        picking = Picking.browse(delivery_id)
        picking_sudo = picking.sudo().exists()
        if not picking_sudo:
            raise MissingError(_("This delivery order does not exist."))
        picking.check_access('read')
        return picking_sudo

    def _get_delivery_attachments(self, delivery_sudo):
        """Attachments (delivery photos, signed proof of delivery, ...)
        posted on this picking. Fetched with sudo() since the current
        portal user's access to the *picking* itself has already been
        enforced by _get_delivery_sudo() before this is ever called; we
        serve the actual bytes ourselves via portal_delivery_attachment()
        below rather than relying on /web/content, whose own ir.attachment
        access check can disagree with the picking-level check."""
        Attachment = request.env['ir.attachment'].sudo()
        return Attachment.search([
            ('res_model', '=', 'stock.picking'),
            ('res_id', '=', delivery_sudo.id),
        ], order='create_date desc')

    # ------------------------------------------------------------
    # Home page counter ("Delivery Orders" card on /my/home)
    # ------------------------------------------------------------
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'delivery_count' in counters:
            Picking = request.env['stock.picking']
            if Picking.check_access_rights('read', raise_exception=False):
                values['delivery_count'] = Picking.search_count(self._delivery_base_domain())
            else:
                values['delivery_count'] = 0
        return values

    # ------------------------------------------------------------
    # List view
    # ------------------------------------------------------------
    @http.route(['/my/deliveries', '/my/deliveries/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_deliveries(self, page=1, sortby=None, search=None, search_in='all', **kw):
        values = self._prepare_portal_layout_values()
        Picking = request.env['stock.picking']

        domain = self._delivery_base_domain()

        searchbar_sortings = {
            'date': {'label': _('Scheduled Date'), 'order': 'scheduled_date desc'},
            'name': {'label': _('Delivery Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state desc'},
        }
        if not sortby or sortby not in searchbar_sortings:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
            'do': {'input': 'do', 'label': _('Search in Delivery Order')},
            'so': {'input': 'so', 'label': _('Search in Sales Order')},
        }
        if search_in not in searchbar_inputs:
            search_in = 'all'

        if search:
            search_domains = []
            if search_in in ('do', 'all'):
                search_domains.append([('name', 'ilike', search)])
            if search_in in ('so', 'all'):
                search_domains.append([('sale_id.name', 'ilike', search)])
                search_domains.append([('origin', 'ilike', search)])
            search_domain = search_domains[0]
            for d in search_domains[1:]:
                search_domain = OR([search_domain, d])
            domain = AND([domain, search_domain])

        deliveries_count = Picking.search_count(domain)

        pager = portal_pager(
            url="/my/deliveries",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search},
            total=deliveries_count,
            page=page,
            step=self._items_per_page,
        )

        deliveries = Picking.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_deliveries_history'] = deliveries.ids[:100]

        values.update({
            'deliveries': deliveries,
            'page_name': 'delivery',
            'pager': pager,
            'default_url': '/my/deliveries',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
        })
        return request.render("portal_delivery.portal_my_deliveries", values)

    # ------------------------------------------------------------
    # Detail view (strictly read-only)
    # ------------------------------------------------------------
    @http.route(['/my/deliveries/<int:delivery_id>'], type='http', auth='user', website=True)
    def portal_delivery_page(self, delivery_id, **kw):
        try:
            # Enforces stock_picking_portal_rule (ir.rule): only own,
            # outgoing deliveries are readable by the portal user. This is
            # a strictly read-only check; no write/unlink rights exist.
            delivery_sudo = self._get_delivery_sudo(delivery_id)
        except (AccessError, MissingError):
            return request.redirect('/my/deliveries')

        values = self._delivery_get_page_view_values(delivery_sudo, **kw)
        values.update({
            'delivery_attachments': self._get_delivery_attachments(delivery_sudo),
        })
        return request.render("portal_delivery.portal_delivery_page", values)

    # ------------------------------------------------------------
    # Attachment streaming (photos, signed proof of delivery, ...)
    # ------------------------------------------------------------
    @http.route(['/my/deliveries/<int:delivery_id>/attachment/<int:attachment_id>'],
                type='http', auth='user', website=True)
    def portal_delivery_attachment(self, delivery_id, attachment_id, download=None, width=0, height=0, **kw):
        """Serve an attachment that belongs to one of the portal user's own
        deliveries. Access is enforced the exact same way as the detail
        page itself (_get_delivery_sudo), then we double-check the
        attachment actually belongs to that specific picking before
        streaming it - this sidesteps ir.attachment's own (stricter/
        inconsistent for this use case) access check on /web/content.

        Also gated on the 'Show Delivery Log to Customers' setting: even if
        a portal user guesses/bookmarks a direct attachment URL, nothing is
        served once the setting is turned off.
        """
        show_log = request.env['ir.config_parameter'].sudo().get_param(
            'portal_delivery.hide_log', default='False') != 'True'
        if not show_log:
            return request.not_found()

        try:
            delivery_sudo = self._get_delivery_sudo(delivery_id)
        except (AccessError, MissingError):
            return request.not_found()

        attachment_sudo = request.env['ir.attachment'].sudo().browse(attachment_id).exists()
        if not attachment_sudo or attachment_sudo.res_model != 'stock.picking' or attachment_sudo.res_id != delivery_sudo.id:
            return request.not_found()

        Binary = request.env['ir.binary']
        is_image = bool(attachment_sudo.mimetype and attachment_sudo.mimetype.startswith('image/'))
        if is_image and (int(width) or int(height)):
            stream = Binary._get_image_stream_from(attachment_sudo, 'raw', width=int(width), height=int(height))
        else:
            stream = Binary._get_stream_from(attachment_sudo, 'raw')
        return stream.get_response(as_attachment=bool(download))
