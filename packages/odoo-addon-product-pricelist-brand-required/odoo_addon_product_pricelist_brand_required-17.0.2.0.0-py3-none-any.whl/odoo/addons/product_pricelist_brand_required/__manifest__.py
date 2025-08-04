# Copyright 2025 Angel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Product Pricelist Brand Required",
    "summary": """
        Check if the product's brand matches any selected brand in the
        pricelist item.""",
    "version": "17.0.2.0.0",
    "license": "AGPL-3",
    "author": "Sygel,Odoo Community Association (OCA)",
    "website": "https://github.com/sygel-technology/sy-product-attribute",
    "depends": [
        "product_brand",
    ],
    "data": [
        "views/product_pricelist_views.xml",
    ],
}
