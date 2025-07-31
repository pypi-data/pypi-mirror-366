# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = [
        "purchase.order",
        "mixin.policy",
        "mixin.sequence",
        "mixin.print_document",
        "mixin.multiple_approval",
    ]
    _document_number_field = "name"
    _automatically_insert_print_button = True
    _approval_state_field = "state"
    _approval_from_state = "draft"
    _approval_to_state = "purchase"
    _approval_cancel_state = "cancel"
    _approval_reject_state = "reject"
    _approval_state = "confirm"
    _after_approved_method = "button_approve"
    _automatically_insert_multiple_approval_page = True
    _multiple_approval_xpath_reference = "//page[last()]"

    def _compute_policy(self):
        _super = super()
        _super._compute_policy()

    type_id = fields.Many2one(
        comodel_name="purchase_order_type",
        string="Type",
        required=True,
        readonly=True,
        states={
            "draft": [("readonly", False)],
        },
        default=lambda r: r._default_type_id(),
    )
    state = fields.Selection(
        selection_add=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("reject", "Rejected"),
            ("purchase",),
        ],
        ondelete={
            "confirm": "set default",
            "reject": "set default",
        },
    )
    total_qty = fields.Float(
        string="Total Qty",
        compute="_compute_total_qty",
        store=True,
    )
    qty_invoiced = fields.Float(
        string="Qty Invoiced",
        compute="_compute_qty_invoice",
        store=True,
    )
    percent_invoiced = fields.Float(
        string="Percent Invoiced",
        compute="_compute_qty_invoice",
        store=True,
    )
    approve_ok = fields.Boolean(
        string="Can Approve",
        compute="_compute_policy",
        compute_sudo=True,
    )
    reject_ok = fields.Boolean(
        string="Can Reject",
        compute="_compute_policy",
        compute_sudo=True,
    )
    restart_approval_ok = fields.Boolean(
        string="Can Restart Approval",
        compute="_compute_policy",
        compute_sudo=True,
    )
    email_ok = fields.Boolean(
        string="Can Send by Email",
        compute="_compute_policy",
        compute_sudo=True,
    )
    resend_email_ok = fields.Boolean(
        string="Can Re-Send by Email",
        compute="_compute_policy",
        compute_sudo=True,
    )
    email_po_ok = fields.Boolean(
        string="Can Send PO by Email",
        compute="_compute_policy",
        compute_sudo=True,
    )
    print_ok = fields.Boolean(
        string="Can Print RFQ",
        compute="_compute_policy",
        compute_sudo=True,
    )
    confirm_ok = fields.Boolean(
        string="Can Confirm Order",
        compute="_compute_policy",
        compute_sudo=True,
    )
    approve_ok = fields.Boolean(
        string="Can Approve Order",
        compute="_compute_policy",
        compute_sudo=True,
    )
    invoice_ok = fields.Boolean(
        string="Can Create Bill",
        compute="_compute_policy",
        compute_sudo=True,
    )
    reminder_mail_ok = fields.Boolean(
        string="Can Confirm Receipt Date",
        compute="_compute_policy",
        compute_sudo=True,
    )
    draft_ok = fields.Boolean(
        string="Can Set to Draft",
        compute="_compute_policy",
        compute_sudo=True,
    )
    cancel_ok = fields.Boolean(
        string="Can Cancel",
        compute="_compute_policy",
        compute_sudo=True,
    )
    done_ok = fields.Boolean(
        string="Can Lock",
        compute="_compute_policy",
        compute_sudo=True,
    )
    unlock_ok = fields.Boolean(
        string="Can Unlock",
        compute="_compute_policy",
        compute_sudo=True,
    )
    manual_number_ok = fields.Boolean(
        string="Can Input Manual Document Number",
        compute="_compute_policy",
        compute_sudo=True,
    )

    @api.model
    def _default_type_id(self):
        Ptype = self.env["purchase_order_type"]
        result = False
        results = Ptype.search([])
        if len(results) > 0:
            result = results[0]
        return result

    @api.depends(
        "order_line",
        "order_line.product_uom_qty",
        "order_line.qty_invoiced",
        "total_qty",
    )
    def _compute_qty_invoice(self):
        for record in self:
            qty_invoiced = percent_invoiced = 0.0
            for line in record.order_line:
                qty_invoiced += line.qty_invoiced
            if record.total_qty != 0.0:
                try:
                    percent_invoiced = qty_invoiced / record.total_qty
                except ZeroDivisionError:
                    percent_invoiced = 0.0
            record.qty_invoiced = qty_invoiced
            record.percent_invoiced = percent_invoiced

    @api.model
    def default_get(self, fields):
        _super = super()
        res = _super.default_get(fields)

        res["name"] = "/"

        return res

    @api.depends(
        "order_line",
        "order_line.product_uom_qty",
    )
    def _compute_total_qty(self):
        for record in self:
            result = 0.0
            for line in record.order_line:
                result += line.product_uom_qty
            record.total_qty = result

    @api.model
    def create(self, vals):
        vals["name"] = "/"
        _super = super()
        res = _super.create(vals)
        return res

    def action_confirm(self):
        for record in self.sudo():
            record.write(
                {
                    "state": "confirm",
                }
            )
            record._add_supplier_to_product()
            record.action_request_approval()

    def button_approve(self, force=False):
        _super = super()
        for record in self:
            record._create_sequence()
        res = _super.button_approve(force=force)
        return res

    @api.model
    def _get_policy_field(self):
        res = super()._get_policy_field()
        policy_field = [
            "email_ok",
            "resend_email_ok",
            "email_po_ok",
            "print_ok",
            "confirm_ok",
            "approve_ok",
            "invoice_ok",
            "reminder_mail_ok",
            "draft_ok",
            "cancel_ok",
            "done_ok",
            "unlock_ok",
            "manual_number_ok",
            "approve_ok",
            "reject_ok",
            "restart_approval_ok",
        ]
        res += policy_field
        return res

    def name_get(self):
        result = []
        for record in self:
            if getattr(record, self._document_number_field) == "/":
                name = "*" + str(record.id)
            else:
                name = record.name
            result.append((record.id, name))
        return result
