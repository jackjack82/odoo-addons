# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from itertools import groupby
from datetime import datetime, timedelta
import base64
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools import html2plaintext
import odoo.addons.decimal_precision as dp

class PosOrderInherit(models.Model):
    _inherit = "pos.order"

    attachment_receipt = fields.Many2one("ir.attachment",'pos order')

    def update_partner_emails(self , client , email):
        client = self.env['res.partner'].browse(int(client))
        client.write({'email':email})
        return True

    @api.model
    def create_from_ui(self, orders):
        res = super(PosOrderInherit , self).create_from_ui(orders)

        if res:
            for i in res:
                order_id  = self.browse(i)
                ref_order = [o['data'] for o in orders if o['data'].get('name') == order_id.pos_reference]
                for order in ref_order:
                    if order.get('email_receipt')== True:
                        template_id = self.env['ir.model.data'].get_object_reference(
                                                                  'bi_pos_email_receipt',
                                                                  'email_template_pos_ticket')[1]
                        email_template_obj = self.env['mail.template'].browse(template_id)
                        result, format = self.env.ref('bi_pos_email_receipt.pos_emails').render_qweb_pdf(order_id.id) 
                        data = base64.b64encode(result) 
                        attachment_obj = self.env['ir.attachment'] 
                        attachment = attachment_obj.create({'name' : "POS Receipts",
                                                             'type' : 'binary', 
                                                             'datas' : data,
                                                             'datas_fname':'POS_receipt'})
                        if template_id:
                            values = email_template_obj.generate_email(order_id.id, fields=None)
                            values['email_from'] = self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.email
                            if order.get('new_email') == None:
                                values['email_to'] = order_id.partner_id.email
                            else:
                                values['email_to'] = order.get('new_email')
                            values['author_id'] = self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.id
                            values['res_id'] = False
                            mail_mail_obj = self.env['mail.mail']
                            values['attachment_ids'] = [(6,0,[attachment.id])]
                            #request.env.uid = 1
                            msg_id = mail_mail_obj.sudo().create(values)
                            if msg_id:
                                mail_mail_obj.send([msg_id])
        return res

    @api.multi
    def attachment_create_action(self):
        self.ensure_one()
        return {
            'name': 'POS Attachment Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'ir.attachment',
            'domain': [('pos_order_recepit_id', '=', self.id)],
        }
