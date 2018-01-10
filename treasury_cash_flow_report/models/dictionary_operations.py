# -*- coding: utf-8 -*-
# Copyright 2017 Giacomo Grasso <giacomo.grasso.82@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _
from odoo.exceptions import UserError
import ast

def sum_dictionary(out, out_weight, cpt, cpt_weight):

    result = {}
    dictionaries = [out, cpt]
    weights = [out_weight, cpt_weight]
    for num in range(2):
        for key, value in dictionaries[num].iteritems():
            if key not in result:
                result[key] = round(value * weights[num], 2)
            else:
                result[key] = round(result[key] + (value * cpt_weight), 2)
    return result

def subtract_dictionary(out, out_weight, cpt, cpt_weight):

    result = {}
    minuend = sum_dictionary(result, 1, out, out_weight)
    for key, value in cpt.iteritems():
        if key not in minuend:
            minuend[key] = round(value * cpt_weight, 2)
        else:
            minuend[key] = round(minuend[key] - (value * cpt_weight), 2)
    return minuend

def check_dict_total(dictionary, rounding):
    """ The sum of all shares of each dictionary shall be equal and not bigger
        than 1. The sum of all shares shall be 1 for summing operations and 0
        for subtractions. The kind of operations is given by the 'round'
        parameter. The remainder will be set in the '' or undefined key

        :param dictionary:  dictionary to be checked and reviewed
        :param round:       1 for sums, 0 for subtractions
        :returns:           dictionary with the remainder in '' key
        """
    if dictionary != {}:
        total = 0
        for key, value in dictionary.iteritems():
            if key != '':
                total += value
        #if abs(total) > 1:
        #    raise UserError(_("""The sum of all shares of a dictionay shall
        #        not be bigger than 1 or smaller than -1"""))
        remainder = round(rounding - total, 2)
        dictionary[''] = remainder

    return dictionary
