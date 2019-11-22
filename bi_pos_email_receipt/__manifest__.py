# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "POS Email Receipt in Odoo ",
    "version" : "12.0.0.2",
    "category" : "",
    'summary': 'This module used to send POS order receipt to customer by email. you can update customers mail id from POS',
    "description": """
    
   This module used to send POS order receipt to customer by email. you can update customers mail id from POS
    email pos receipt
    pos order email receipt
    pos email
    pos order email
    POS Order Email Receipt
    pos receipt email
    point of sales email
    point of sales order email
    email pos receipt
    email pos order
    pos email
    POS Order Email Receipt
    POS Email Receipt
    POS Receipt email 
    pos order mail
    send pos email
    pos mail

    pos order mail
    

    
    """,
    "author": "BrowseInfo",
    "website" : "www.browseinfo.in",
    "price": 19,
    "currency": 'EUR',
    "depends" : ['base','point_of_sale'],
    "data": [

        'data/data.xml',
       'report/pos_email_receipt_report.xml',
       'views/pos_email_backend.xml',

    ],
    'qweb': [
    'static/src/xml/pos_payment_widget.xml'
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/orsnxLbCtWs',
    "images":["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
