# -*- coding: utf-8 -*-

##############################################################################
#
##############################################################################

import base64
import contextlib
import cStringIO
import csv

from openerp import models, fields, api
from openerp import tools
from openerp.osv import osv
from openerp.tools.translate import _
from openerp.tools.misc import get_iso_codes


class partner_complete_export(models.TransientModel):
    _name = "partner.complete.export"

    name = fields.Char('File Name', readonly=True)
    file_format = fields.Selection([('csv', 'CSV File'),
                                    ], 'File Format',
                                       required=True,
                                       default='csv')
    data = fields.Binary('File', readonly=True)
    state = fields.Selection([('choose', 'choose'),   # choos language
                             ('get', 'get')], default='choose')  # get file

    @api.multi
    def act_getfile(self):
        for this in self:

            with contextlib.closing(cStringIO.StringIO()) as buf:
                buf = this.create_excel_file(buf)
                out = base64.encodestring(buf.getvalue())

            filename = 'export_contatti'
            extension = 'csv'

            name = "%s.%s" % (filename, extension)
            this.write({'state': 'get', 'data': out, 'name': name})

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'partner.complete.export',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': this.id,
                'views': [(False, 'form')],
                'target': 'new',
            }

    def create_excel_file(self, buf):
        final_file = csv.writer(buf, delimiter=',', quotechar='"')

        partner_list = self.env['res.partner'].search([('name', '!=', '')])

        """ writing the header"""
        header = ("Nome",
                  "Società di appartenenza",
                  "Tags",

                  "Indirizzo",
                  "Cap",
                  "Località",
                  "Provincia",
                  "Stato",

                  "Telefono",
                  "Cellulare",
                  "Fax",
                  "Email",
                  "Sito",
                 )

        final_file.writerow(header)

        for partner in partner_list:

            name = partner.name or ""
            related_company = partner.parent_id.name or ""

            tags_string = ""
            if partner.category_id:
                tags_string = ""
                for k in partner.category_id:
                    tags_string = tags_string + "," + k.name

            street = partner.street or ""
            zip_code = partner.zip or ""
            city = partner.city or ""
            state_id = partner.state_id.name or ""
            country = partner.country_id.name or ""

            phone = partner.phone or ""
            mobile = partner.mobile or ""
            fax = partner.fax or ""
            email = partner.email or ""
            website = partner.website or ""

            output = name.encode('utf-8'),\
                related_company.encode('utf-8'),\
                tags_string.encode('utf-8'),\
                street.encode('utf-8'),\
                zip_code.encode('utf-8'),\
                city.encode('utf-8'),\
                state_id.encode('utf-8'),\
                country.encode('utf-8'),\
                phone.encode('utf-8'),\
                mobile.encode('utf-8'),\
                fax.encode('utf-8'),\
                email.encode('utf-8'),\
                website.encode('utf-8'),\

            final_file.writerow(output)


        return buf
