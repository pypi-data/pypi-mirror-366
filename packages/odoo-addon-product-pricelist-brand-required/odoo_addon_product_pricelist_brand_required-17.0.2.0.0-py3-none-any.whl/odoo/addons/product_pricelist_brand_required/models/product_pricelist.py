# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _get_applicable_rules_domain(self, products, date, **kwargs):
        return super()._get_applicable_rules_domain(products, date, **kwargs) + [
            "|",
            ("product_brand_ids", "=", False),
            ("product_brand_ids", "in", products.product_brand_id.ids),
            # The in acts like an intersects
        ]
