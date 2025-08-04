# Copyright 2025 Angel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    product_brand_ids = fields.Many2many("product.brand", string="Brands")

    def _is_applicable_for(self, product, qty_in_product_uom):
        self.ensure_one()
        product.ensure_one()

        res = False
        if (
            not self.product_brand_ids
            or product.product_brand_id in self.product_brand_ids
        ):
            res = super()._is_applicable_for(product, qty_in_product_uom)
        return res
