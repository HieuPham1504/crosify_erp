# -*- coding: utf-8 -*-
import itertools
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Product Type'

    product_type = fields.Char(string="Product Type", compute="compute_product_type", store=True, index=True)
    design_number = fields.Char(string='Design Number', require=True, trim=True)
    detailed_type = fields.Selection(string="Detailed Type")

    # def _create_variant_ids(self):
    #     return

    def create_variants(self):
        self._create_variant_ids()

    def _create_variant_ids(self):
        if not self:
            return
        self.env.flush_all()
        Product = self.env["product.product"]

        variants_to_create = []
        variants_to_activate = Product
        variants_to_unlink = Product

        for tmpl_id in self:
            lines_without_no_variants = tmpl_id.valid_product_template_attribute_line_ids._without_no_variant_attributes()

            all_variants = tmpl_id.with_context(active_test=False).product_variant_ids.sorted(
                lambda p: (p.active, -p.id))

            current_variants_to_create = []
            current_variants_to_activate = Product

            # adding an attribute with only one value should not recreate product
            # write this attribute on every product to make sure we don't lose them
            # single_value_lines = lines_without_no_variants.filtered(
            #     lambda ptal: len(ptal.product_template_value_ids._only_active()) == 1)
            # if single_value_lines:
            #     for variant in all_variants:
            #         combination = variant.product_template_attribute_value_ids | single_value_lines.product_template_value_ids._only_active()
            #         # Do not add single value if the resulting combination would
            #         # be invalid anyway.
            #         if (
            #                 len(combination) == len(lines_without_no_variants) and
            #                 combination.attribute_line_id == lines_without_no_variants
            #         ):
            #             variant.product_template_attribute_value_ids = combination

            # Set containing existing `product.template.attribute.value` combination
            existing_variants = {
                variant.product_template_attribute_value_ids: variant for variant in all_variants
            }

            # Determine which product variants need to be created based on the attribute
            # configuration. If any attribute is set to generate variants dynamically, skip the
            # process.
            # Technical note: if there is no attribute, a variant is still created because
            # 'not any([])' and 'set([]) not in set([])' are True.
            if not tmpl_id.has_dynamic_attributes():
                # Iterator containing all possible `product.template.attribute.value` combination
                # The iterator is used to avoid MemoryError in case of a huge number of combination.
                all_combinations = itertools.product(*[
                    ptal.product_template_value_ids._only_active() for ptal in lines_without_no_variants
                ])
                # For each possible variant, create if it doesn't exist yet.
                for combination_tuple in all_combinations:
                    combination = self.env['product.template.attribute.value'].concat(*combination_tuple)
                    is_combination_possible = tmpl_id._is_combination_possible_by_config(combination,
                                                                                         ignore_no_variant=True)
                    if not is_combination_possible:
                        continue

                    for variant in existing_variants:
                        if len(combination) > len(variant) and existing_variants[
                            variant] not in current_variants_to_activate:
                            current_variants_to_activate += existing_variants[variant]

                    if combination in existing_variants:
                        current_variants_to_activate += existing_variants[combination]
                    else:
                        current_variants_to_create.append(tmpl_id._prepare_variant_values(combination))
                        variant_limit = self.env['ir.config_parameter'].sudo().get_param(
                            'product.dynamic_variant_limit', 1000)
                        if len(current_variants_to_create) > int(variant_limit):
                            raise UserError(_(
                                'The number of variants to generate is above allowed limit. '
                                'You should either not generate variants for each combination or generate them on demand from the sales order. '
                                'To do so, open the form view of attributes and change the mode of *Create Variants*.'))
                variants_to_create += current_variants_to_create
                variants_to_activate += current_variants_to_activate

            else:
                for variant in existing_variants.values():
                    is_combination_possible = self._is_combination_possible_by_config(
                        combination=variant.product_template_attribute_value_ids,
                        ignore_no_variant=True,
                    )
                    if is_combination_possible:
                        current_variants_to_activate += variant
                variants_to_activate += current_variants_to_activate

            variants_to_unlink += all_variants - current_variants_to_activate

        if variants_to_activate:
            variants_to_activate.write({'active': True})
        if variants_to_unlink:
            variants_to_unlink._unlink_or_archive()
            # prevent change if exclusion deleted template by deleting last variant
            if self.exists() != self:
                raise UserError(
                    _("This configuration of product attributes, values, and exclusions would lead to no possible variant. Please archive or delete your product directly if intended."))
        if variants_to_create:
            Product.create(variants_to_create)

        # prefetched o2m have to be reloaded (because of active_test)
        # (eg. product.template: product_variant_ids)
        # We can't rely on existing invalidate because of the savepoint
        # in _unlink_or_archive.
        self.env.flush_all()
        self.env.invalidate_all()
        return True

    @api.constrains('product_type')
    def _check_product_type(self):
        for record in self:
            product_type = record.product_type

            duplicate_code = self.sudo().search(
                [('id', '!=', record.id), ('product_type', '=', product_type)])
            if duplicate_code:
                raise ValidationError(_("This Product Type already exists."))

    @api.depends('design_number', 'categ_id')
    def compute_product_type(self):
        for rec in self:
            categ_id = rec.categ_id
            design_number = rec.design_number
            if design_number and categ_id and categ_id.product_category_code:
                rec.product_type = f'{categ_id.product_category_code}{design_number}'
            else:
                rec.product_type = False

    @api.depends('name', 'product_type')
    @api.depends_context('product_type', 'name')
    def _compute_display_name(self):

        def get_display_name(name, code):
            if self._context.get('display_product_type', True) and code:
                return f'[{code}] {name}'
            return name
        for rec in self.sudo():
                rec.display_name = get_display_name(rec.name, rec.product_type)

    def _prepare_variant_values(self, combination):
        variant_dict = super()._prepare_variant_values(combination)
        sku_suffix = self.env['ir.sequence'].sudo().next_by_code('product.product.sku') or '_Undefined'
        variant_dict['default_code'] = f'{self.product_type}{sku_suffix}'
        return variant_dict
        
