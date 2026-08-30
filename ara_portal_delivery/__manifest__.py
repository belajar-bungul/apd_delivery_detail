# -*- coding: utf-8 -*-
{
    'name': 'Portal Delivery Orders',
    'version': '19.0.2.0.0',
    'category': 'Website',
    'author': 'ARA SOFT SPLIT DEVELOPERS',
    'summary': 'Read-only Delivery Orders on the customer portal, with a fully configurable portal status/reason system',
    'description': """
Portal Delivery Orders
=======================
Adds a "Delivery Orders" section to the customer portal (My Account).

- Lists only the OUTGOING deliveries (stock.picking) belonging to the
  logged in portal user's partner (and its child contacts / delivery addresses).
- Search bar to filter by Delivery Order reference or by the related
  Sales Order reference.
- Detail page is strictly read-only: shows the delivery status, the
  product lines, and (optionally) the full chatter log / attachments.

Configurable Portal Status
---------------------------
- "Portal Delivery Statuses" (Inventory > Configuration, or Settings) is a
  master-data list you fully control: name + color, in any order, add as
  many as you like (Ready, Waiting, Picking, Packing, On Delivery, On Hold,
  Done, ... or your own).
- Any status can be flagged "Requires a Reason". When a delivery carrying
  that status is opened on the portal, an extra field appears below the
  header showing why (drawn from the second master-data list, "Portal
  Delivery Hold Reasons").
- Both lists, and whether the Delivery Log is shown to portal users at all,
  are toggled from Settings > Portal Delivery.
""",
    'depends': ['portal', 'sale_stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/portal_delivery_security.xml',
        'data/portal_delivery_data.xml',
        'views/portal_delivery_master_data_views.xml',
        'views/stock_picking_views.xml',
        'views/res_config_settings_views.xml',
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ara_portal_delivery/static/src/js/color_hex_field.js',
            'ara_portal_delivery/static/src/xml/color_hex_field.xml',
        ],
    },
    'images': ['static/description/banner.png'],
    'price': 42.00,
    'currency': 'USD',
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}