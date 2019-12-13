# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "POS Loyalty and Rewards Program in Odoo",
    "version" : "12.0.1.6",
    "category" : "Point of Sale",
    "depends" : ['base','sale','point_of_sale'],
    "author": "BrowseInfo",
    'summary': 'This apps allows your customers to provide POS loyalty management.',
    "description": """
    
    Purpose :- 
This apps allows your cutomers to provide POS loyalty management. 
customer loyalty programs, loyalty points and reward programs
    pos loyalty program
    pos loyalty and redeem program
    POS Loyalty and Rewards Program
    pos loyalty redeem
    pos loyalty points reward and redeem
    pos redeem loyalty
    pos loyalty rewards
    pos rewards program
    pos loyalty redeem
	pos loyalty programs
	pos loyalty cards
	pos loyalty discount

    point of sale loyalty program
    point of sale loyalty and redeem program
    point of sale Loyalty and Rewards Program
    point of sale loyalty redeem
    point of sale loyalty points reward and redeem
    point of sale redeem loyalty
    point of sale loyalty rewards
    point of sale rewards program
    point of sale loyalty redeem
    

    point of sales loyalty program
    point of sales loyalty and redeem program
    point of sales Loyalty and Rewards Program
    point of sales loyalty redeem
    point of sales loyalty points reward and redeem
    point of sales redeem loyalty
    point of sales loyalty rewards
    point of sales rewards program
    point of sales loyalty redeem
    
    
    """,
    "website" : "www.browseinfo.in",
    "price": 29,
    "currency": "EUR",
    "data": [
        'security/ir.model.access.csv',
        'views/custom_pos_view.xml',
        'views/pos_loyalty.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    "auto_install": False,
    "installable": True,
    "images":['static/description/Banner.png'],
    "live_test_url":'https://youtu.be/rXqA4irplrE',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
