# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrderLineReport(models.Model):
    _name = "sale.order.line.report"
    _description = "Sales Order Line Analysis Report"
    _auto = False
    _rec_name = 'crosify_created_date'
    _order = 'crosify_created_date desc'

    count_order_line = fields.Integer("Count")

    #product
    product_id = fields.Many2one(
        comodel_name='product.product',
        string="SKU")
    product_template_attribute_value_ids = fields.Many2many(related='product_id.product_template_attribute_value_ids')

    #custom
    crosify_created_date = fields.Datetime(string='Create Date', store=True)



    # product custom
    default_code = fields.Char(string='Product Code', related='product_id.default_code', store=True)
    product_tmpl_product_type = fields.Char(string='Product Type',
                               related='product_id.product_tmpl_product_type',
                               store=True,
                               index=True)
    #
    domain = fields.Char('Domain')
    #
    payment_status = fields.Boolean('Payment Status')
    seller_id = fields.Many2one('crosify.seller', string='Seller')
    production_vendor_id = fields.Many2one('res.partner', string='Production Vendor')
    packaging_vendor_id = fields.Many2one('res.partner', string='Packaging Vendor')
    shipping_vendor_id = fields.Many2one('res.partner', string='Shipping Vendor')
    sublevel_id = fields.Many2one('sale.order.line.level', string='Level')


    def _with_sale_order_line(self):
        return ""

    def _select_sale_order_line(self):
        select_ = f"""
            l.id,
            product_id,
            crosify_created_date,
            l.seller_id,
            p.default_code as default_code,
            count(l.id) as count_order_line,
            product_tmpl_product_type,
            s.domain,
            s.payment_status,
            l.production_vendor_id,
            l.packaging_vendor_id,
            l.shipping_vendor_id,
            l.sublevel_id
            
        """

        return select_

    def _from_sale_order_line(self):
        return """
            sale_order_line as l
            LEFT JOIN product_product p ON l.product_id=p.id
            LEFT JOIN sale_order s ON l.order_id=s.id
            JOIN res_partner partner ON l.production_vendor_id = partner.id
            JOIN res_partner partner2 ON l.packaging_vendor_id = partner2.id
            JOIN res_partner partner3 ON l.shipping_vendor_id = partner3.id
            JOIN res_partner sublevel ON l.sublevel_id = sublevel.id 
            
            """

    def _where_sale_order_line(self):
        return """
            """

    def _group_by_sale_order_line(self):
        return """
            l.product_id,
            crosify_created_date,
            l.seller_id,
            default_code,
            l.id,
            product_tmpl_product_type,
            s.domain,
            s.payment_status,
            l.production_vendor_id,
            l.packaging_vendor_id,
            l.shipping_vendor_id,
            l.sublevel_id
            
            """

    def _query(self):
        with_ = self._with_sale_order_line()
        return f"""
            {"WITH" + with_ + "(" if with_ else ""}
            SELECT {self._select_sale_order_line()}
            FROM {self._from_sale_order_line()}
            GROUP BY {self._group_by_sale_order_line()}
            {")" if with_ else ""}
        """

    @property
    def _table_query(self):
        return self._query()








