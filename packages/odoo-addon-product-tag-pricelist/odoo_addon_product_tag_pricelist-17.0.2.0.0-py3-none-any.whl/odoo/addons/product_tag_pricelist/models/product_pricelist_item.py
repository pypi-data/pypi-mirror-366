# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    applied_on = fields.Selection(
        selection_add=[
            ("2a_product_tags", "Product Tags"),
            ("2_product_category",),
            ("1_product",),
            ("0_product_variant",),
        ],
        ondelete={"2a_product_tags": "set default"},
    )
    product_tag_ids = fields.Many2many(
        comodel_name="product.tag", string="Product Tags"
    )

    @api.constrains("applied_on", "product_tag_ids")
    def _check_product_consistency(self):
        inconsistent_lines = self.filtered(
            lambda item: (
                item.applied_on == "2a_product_tags" and not item.product_tag_ids
            )
        )
        if inconsistent_lines:
            raise ValidationError(
                _(
                    "Please specify the product tags"
                    " for which this rule should be applied: {}"
                ).format(", ".join(inconsistent_lines.mapped("name")))
            )
        return super()._check_product_consistency

    @api.depends("product_tag_ids")
    def _compute_name_and_price(self):
        res = super()._compute_name_and_price()
        for item in self.filtered(
            lambda item: (item.product_tag_ids and item.applied_on == "2a_product_tags")
        ):
            tag_names = item.product_tag_ids.mapped("name")
            tag_names_str = ", ".join(tag_names)
            item.name = _("Tags: {}").format(tag_names_str)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if not values.get("applied_on") and values.get("product_tag_ids"):
                values["applied_on"] = "2a_product_tags"
            if values.get("applied_on"):
                # Ensure item consistency for later searches.
                applied_on = values["applied_on"]
                if applied_on == "2a_product_tags":
                    values.update(
                        dict(product_id=None, product_tmpl_id=None, categ_id=None)
                    )
                elif applied_on in [
                    "3_global",
                    "2_product_category",
                    "1_product",
                    "0_product_variant",
                ]:
                    values.update(dict(product_tag_ids=False))
        return super().create(vals_list)

    def write(self, values):
        if values.get("applied_on"):
            applied_on = values["applied_on"]
            if applied_on == "2a_product_tags":
                values.update(
                    dict(product_id=None, product_tmpl_id=None, categ_id=None)
                )
            elif applied_on in [
                "3_global",
                "2_product_category",
                "1_product",
                "0_product_variant",
            ]:
                values.update(dict(product_tag_ids=False))
        return super().write(values)

    def _is_applicable_for(self, product, qty_in_product_uom):
        self.ensure_one()
        product.ensure_one()

        if (
            not (self.min_quantity and qty_in_product_uom < self.min_quantity)
            and self.applied_on == "2a_product_tags"
        ):
            p_tags = product.product_tag_ids
            if product._name == "product.product":
                p_tags = p_tags | product.additional_product_tag_ids
            res = any(self.product_tag_ids & p_tags)
        else:
            res = super()._is_applicable_for(product, qty_in_product_uom)
        return res
