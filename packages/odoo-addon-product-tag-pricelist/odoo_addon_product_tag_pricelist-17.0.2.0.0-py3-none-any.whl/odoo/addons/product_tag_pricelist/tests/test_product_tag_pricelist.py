# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import datetime

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProductTagPricelist(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create products, pricelist, partner and empty sale
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.categ = cls.env["product.category"].create({"name": "Test Categ"})
        cls.tag = cls.env["product.tag"].create({"name": "Test Tag"})
        cls.tag2 = cls.env["product.tag"].create({"name": "Test Tag 2"})
        cls.tag3 = cls.env["product.tag"].create({"name": "Test Tag 3"})
        cls.product1 = cls.env["product.product"].create(
            {"name": "Test Product 1", "additional_product_tag_ids": [(4, cls.tag.id)]}
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Test Product 2",
                "categ_id": cls.categ.id,
            }
        )
        cls.product3 = cls.env["product.product"].create(
            {
                "name": "Test Product 3",
            }
        )
        cls.product_multi_tags = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "additional_product_tag_ids": [(4, cls.tag.id)],
                "product_tag_ids": [(4, cls.tag2.id)],
            }
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test Pricelist",
            }
        )
        cls.line_global = cls.pricelist.item_ids.create(
            {
                "compute_price": "fixed",
                "fixed_price": 1.0,
                "applied_on": "3_global",
            }
        )
        cls.line_tags = cls.pricelist.item_ids.create(
            {
                "compute_price": "fixed",
                "fixed_price": 10.0,
                "applied_on": "2a_product_tags",
                "product_tag_ids": [(4, cls.tag.id)],
            }
        )
        cls.line_categ = cls.pricelist.item_ids.create(
            {
                "compute_price": "fixed",
                "fixed_price": 100.0,
                "applied_on": "2_product_category",
                "categ_id": cls.categ.id,
            }
        )
        cls.line_multi_tags = cls.pricelist.item_ids.create(
            {
                "compute_price": "fixed",
                "fixed_price": 10.0,
                "applied_on": "2a_product_tags",
                "product_tag_ids": [(4, cls.tag2.id), (4, cls.tag3.id)],
            }
        )

    def test_pricelist(self):
        price1 = self.pricelist._get_product_price(self.product1, quantity=1.0)
        price2 = self.pricelist._get_product_price(self.product2, quantity=1.0)
        price3 = self.pricelist._get_product_price(self.product3, quantity=1.0)

        self.assertEqual(price1, 10)
        self.assertEqual(price2, 100)
        self.assertEqual(price3, 1)

    def test_check_product_consistency(self):
        with self.assertRaises(ValidationError):
            self.pricelist.item_ids.create(
                {
                    "compute_price": "fixed",
                    "fixed_price": 10.0,
                    "applied_on": "2a_product_tags",
                }
            )

    def test_name(self):
        self.line_tags._compute_name_and_price()
        self.assertEqual(self.line_tags.name, f"Tags: {self.tag.name}")

    def test_write_create(self):
        self.line_tags.write(
            {
                "applied_on": "3_global",
            }
        )
        self.assertEqual(len(self.line_tags.product_tag_ids), 0)
        self.line_categ.write(
            {
                "applied_on": "2a_product_tags",
                "product_tag_ids": [(4, self.tag.id)],
            }
        )
        self.assertEqual(len(self.line_categ.categ_id), 0)
        line4 = self.pricelist.item_ids.create(
            {
                "compute_price": "fixed",
                "fixed_price": 1.0,
                "applied_on": "3_global",
                "product_tag_ids": [(4, self.tag.id)],
            }
        )
        self.assertEqual(len(line4.product_tag_ids), 0)
        line5 = self.pricelist.item_ids.create(
            {
                "compute_price": "fixed",
                "fixed_price": 1.0,
                "applied_on": "2a_product_tags",
                "product_tag_ids": [(4, self.tag.id)],
                "categ_id": self.categ.id,
            }
        )
        self.assertEqual(len(line5.categ_id), 0)
        line6 = self.pricelist.item_ids.create(
            {
                "compute_price": "fixed",
                "fixed_price": 1.0,
                "product_tag_ids": [(4, self.tag.id)],
            }
        )
        self.assertEqual(line6.applied_on, "2a_product_tags")

    def test_onchange(self):
        tag4 = self.env["product.tag"].create({"name": "Test Tag 4"})
        self.product1.product_tag_ids = tag4
        res = self.product1._onchange_tag_ids()
        self.assertEqual(type(res), dict)
        self.assertTrue(res["warning"])

        self.product1.product_tmpl_id.product_tag_ids = tag4
        res = self.product1.product_tmpl_id._onchange_tag_ids()
        self.assertEqual(type(res), dict)
        self.assertTrue(res["warning"])

    def test_get_applicable_rules(self):
        tag_rules = self.pricelist._get_applicable_rules(
            self.product_multi_tags, datetime.date.today()
        )
        self.assertIn(self.line_global, tag_rules)
        self.assertIn(self.line_tags, tag_rules)
        self.assertNotIn(self.line_categ, tag_rules)
        self.assertIn(self.line_multi_tags, tag_rules)

        categ_rules = self.pricelist._get_applicable_rules(
            self.product2, datetime.date.today()
        )
        self.assertNotIn(self.line_tags, categ_rules)
