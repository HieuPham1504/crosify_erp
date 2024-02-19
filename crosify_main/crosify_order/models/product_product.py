# -*- coding: utf-8 -*-
import contextlib
import collections

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.models import BaseModel

class ProductProduct(models.Model):
    _inherit = 'product.product'
    _description = 'SKU'

    @api.constrains('default_code')
    def _check_default_code(self):
        for record in self:
            default_code = record.default_code

            duplicate_code = self.sudo().search(
                [('id', '!=', record.id), ('default_code', '=', default_code)])
            if duplicate_code:
                raise ValidationError(_("This SKU already exists."))

    default_code = fields.Char(string='SKU')
    product_tmpl_product_type = fields.Char(string='Product Type', related='product_tmpl_id.product_type', store=True,
                                            index=True)
    weight = fields.Float(string='Weight (Gram)')
    length = fields.Float(string='Length (cm)')
    width = fields.Float(string='Width (cm)')
    height = fields.Float(string='Height (cm)')
    vendor_production_price_ids = fields.One2many('product.vendor.production.price', 'product_id',
                                                  string='Production Price')
    employee_id = fields.Many2one('hr.employee', string='Employee', default=lambda self: self.env.user.employee_id.id, tracking=True)

    @api.depends("product_tmpl_id.write_date")
    def _compute_write_date(self):
        """
        First, the purpose of this computation is to update a product's
        write_date whenever its template's write_date is updated.  Indeed,
        when a template's image is modified, updating its products'
        write_date will invalidate the browser's cache for the products'
        image, which may be the same as the template's.  This guarantees UI
        consistency.

        Second, the field 'write_date' is automatically updated by the
        framework when the product is modified.  The recomputation of the
        field supplements that behavior to keep the product's write_date
        up-to-date with its template's write_date.

        Third, the framework normally prevents us from updating write_date
        because it is a "magic" field.  However, the assignment inside the
        compute method is not subject to this restriction.  It therefore
        works as intended :-)
        """
        for record in self:
            record.write_date = max(record.write_date or self.env.cr.now(),
                                    record.product_tmpl_id.write_date) if record.product_tmpl_id.write_date else False

    def action_select_product_template(self):
        return {
            'name': 'Select Product',
            'view_mode': 'form',
            'res_model': 'select.product.template.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_product_id': self.id}
        }

    def _export_rows(self, fields, *, _is_toplevel_call=True):
        """ Export fields of the records in ``self``.

        :param list fields: list of lists of fields to traverse
        :param bool _is_toplevel_call:
            used when recursing, avoid using when calling from outside
        :return: list of lists of corresponding values
        """
        import_compatible = self.env.context.get('import_compat', True)
        lines = []

        def splittor(rs):
            """ Splits the self recordset in batches of 1000 (to avoid
            entire-recordset-prefetch-effects) & removes the previous batch
            from the cache after it's been iterated in full
            """
            for idx in range(0, len(rs), 1000):
                sub = rs[idx:idx + 1000]
                for rec in sub:
                    yield rec
                sub.invalidate_recordset()

        if not _is_toplevel_call:
            splittor = lambda rs: rs

        # memory stable but ends up prefetching 275 fields (???)
        # if self._name == 'product.template.attribute.value':
        #     lines.append([','.join([rec.display_name for rec in self])])
        attributes = self.env['product.attribute'].sudo().search([], order='id desc')
        for record in splittor(self):
            # main line of record, initially empty
            current = [''] * len(fields)


            if ['product_template_attribute_value_ids'] in fields:
                append_col = [''] * (len(attributes) - 1)
                current += append_col
            lines.append(current)

            # list of primary fields followed by secondary field(s)
            primary_done = []
            i = 0
            # process column by column
            for path in fields:
                if not path:
                    continue

                name = path[0]
                if name in primary_done:
                    continue

                if name == '.id':
                    current[i] = str(record.id)
                elif name == 'id':
                    current[i] = (record._name, record.id)
                else:
                    field = record._fields[name]
                    value = record[name]

                    # this part could be simpler, but it has to be done this way
                    # in order to reproduce the former behavior
                    if not isinstance(value, BaseModel) or value._name != 'product.template.attribute.value':
                        current[i] = field.convert_to_export(value, record)
                    elif not isinstance(value, BaseModel) or value._name == 'product.template.attribute.value':
                        for number, attribute in enumerate(attributes):
                            i = number
                            for att_val in value:
                                if att_val.attribute_id.id == attribute.id:
                                    current[i] = att_val.display_name

                    else:
                        primary_done.append(name)
                        # recursively export the fields that follow name; use
                        # 'display_name' where no subfield is exported
                        fields2 = [(p[1:] or ['display_name'] if p and p[0] == name else [])
                                   for p in fields]

                        # in import_compat mode, m2m should always be exported as
                        # a comma-separated list of xids or names in a single cell
                        if import_compatible and field.type == 'many2many':
                            index = None
                            # find out which subfield the user wants & its
                            # location as we might not get it as the first
                            # column we encounter
                            for name in ['id', 'name', 'display_name']:
                                with contextlib.suppress(ValueError):
                                    index = fields2.index([name])
                                    break
                            if index is None:
                                # not found anything, assume we just want the
                                # display_name in the first column
                                name = None
                                index = i

                            if name == 'id':
                                xml_ids = [xid for _, xid in value.__ensure_xml_id()]
                                current[index] = ','.join(xml_ids)
                            else:
                                current[index] = field.convert_to_export(value, record)
                            continue

                        lines2 = value._export_rows(fields2, _is_toplevel_call=False)
                        if lines2:
                            # merge first line with record's main line
                            for j, val in enumerate(lines2[0]):
                                if val or isinstance(val, (int, float)):
                                    current[j] = val
                            # append the other lines at the end
                            lines += lines2[1:]
                        else:
                            current[i] = ''
                i += 1
                # if record._name == 'product.template.attribute.value':
                #     i += 2

        # if any xid should be exported, only do so at toplevel
        if _is_toplevel_call and any(f[-1] == 'id' for f in fields):
            bymodels = collections.defaultdict(set)
            xidmap = collections.defaultdict(list)
            # collect all the tuples in "lines" (along with their coordinates)
            for i, line in enumerate(lines):
                for j, cell in enumerate(line):
                    if type(cell) is tuple:
                        bymodels[cell[0]].add(cell[1])
                        xidmap[cell].append((i, j))
            # for each model, xid-export everything and inject in matrix
            for model, ids in bymodels.items():
                for record, xid in self.env[model].browse(ids).__ensure_xml_id():
                    for i, j in xidmap.pop((record._name, record.id)):
                        lines[i][j] = xid
            assert not xidmap, "failed to export xids for %s" % ', '.join('{}:{}' % it for it in xidmap.items())

        return lines
