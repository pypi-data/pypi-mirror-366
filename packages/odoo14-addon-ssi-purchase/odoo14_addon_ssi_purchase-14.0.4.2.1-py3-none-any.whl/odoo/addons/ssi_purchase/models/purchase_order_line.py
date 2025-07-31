# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _name = "purchase.order.line"
    _inherit = [
        "purchase.order.line",
    ]

    percent_invoiced = fields.Float(
        string="Percent Invoiced",
        compute="_compute_percent_invoiced",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "qty_invoiced",
        "product_uom_qty",
    )
    def _compute_percent_invoiced(self):
        for record in self:
            result = 0.0
            if record.product_uom_qty != 0.0:
                try:
                    result = record.qty_invoiced / record.product_uom_qty
                except ZeroDivisionError:
                    result = 0.0
            record.percent_invoiced = result
