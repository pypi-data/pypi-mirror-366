# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.onchange("product_tag_ids", "additional_product_tag_ids")
    def _onchange_tag_ids(self):
        if self.product_tag_ids:
            return {
                "warning": {
                    "title": _("Product tags have been modified."),
                    "message": _(
                        "Be aware that sale pricelists will be applied if a "
                        "product tag matches a tag selected in the pricelist."
                    ),
                }
            }
