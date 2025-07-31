# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Purchase",
    "version": "14.0.4.2.1",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "application": True,
    "depends": [
        "purchase",
        "ssi_policy_mixin",
        "ssi_master_data_mixin",
        "ssi_sequence_mixin",
        "ssi_policy_mixin",
        "ssi_multiple_approval_mixin",
    ],
    "data": [
        "security/ir_module_category_data.xml",
        "security/res_group_data.xml",
        "security/ir.model.access.csv",
        "security/ir_rule_data.xml",
        "data/purchase_order_type.xml",
        "data/approval_template_data.xml",
        "data/policy_template_data.xml",
        "data/ir_sequence_data.xml",
        "data/sequence_template_data.xml",
        "views/res_partner_views.xml",
        "views/purchase_order_views.xml",
        "views/product_product_views.xml",
        "views/purchase_order_type_views.xml",
    ],
    "demo": [],
}
