# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderType(models.Model):
    _name = "purchase_order_type"
    _inherit = [
        "mixin.master_data",
    ]
    _description = "Purchase Order Type"
    _field_name_string = "Purchase Order Type"
