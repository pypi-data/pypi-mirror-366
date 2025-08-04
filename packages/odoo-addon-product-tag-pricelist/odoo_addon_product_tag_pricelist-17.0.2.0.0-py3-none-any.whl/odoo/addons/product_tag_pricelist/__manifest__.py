# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Tag Pricelist",
    "summary": "Use tags in pricelists",
    "version": "17.0.2.0.0",
    "category": "Stock",
    "website": "https://github.com/sygel-technology/sy-product-attribute",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "product",
    ],
    "data": [
        "views/product_pricelist_views.xml",
    ],
}
