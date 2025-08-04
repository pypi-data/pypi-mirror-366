# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _get_applicable_rules_domain(self, products, date, **kwargs):
        res = super()._get_applicable_rules_domain(products, date, **kwargs)
        tags = products.mapped("product_tag_ids")
        if products._name == "product.product":
            tags |= products.mapped("additional_product_tag_ids")
        return res + [
            "|",
            ("product_tag_ids", "=", False),
            ("product_tag_ids", "in", tags.ids),
            # The in acts like an intersects
        ]
