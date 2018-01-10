# coding=utf-8

import ast
from erppeek import Client

if False:
    ODOO_URL = "http://localhost:8069"
    ODOO_DB = '10c_treasury'
    ODOO_ACCOUNT = {'user': 'admin', 'pwd': 'admin'}

    # setting erppeek
    client = Client(ODOO_URL,
                    db=ODOO_DB,
                    user=ODOO_ACCOUNT['user'],
                    password=ODOO_ACCOUNT['pwd'])


def sum_dictionary(out, out_weight, cpt, cpt_weight):
    """
    Merges two dictionaries based on their weight.
    :param out:         source dictionary
    :param out_weight:  dictionary to be merged
    :param cpt:         weight of the dictionary to be merged
    :param cpt_weight:  weight of the dictionary to be merged
    :returns:           source dictionary merged with counterpart
    """
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


def compute_dictionary(self):
    aa_share = {}
    coa_share = {}
    for line in self.invoice_line_ids:
        line_share = round(line.price_subtotal / self.amount_untaxed, 2)
        if str(line.account_id.id) not in aa_share:
            aa_share[str(line.account_id.id)] = line_share
        else:
            aa_share[str(line.account_id.id)] += line_share
        if str(line.account_analytic_id.id) not in coa_share:
            coa_share[str(line.account_analytic_id.id)] = line_share
        else:
            coa_share[str(line.account_analytic_id.id)] += line_share
    self.comment = """{'aa_share': %s, coa_share': %s }""" % (
        aa_share, coa_share)
    return

# INVOICE = client.AccountInvoice
# invoice = INVOICE.browse(16)
# compute_dictionary(invoice)

__name__


def compute_initial_final_date(self):
    """Compute initial and final date of the statement"""
    for statement in self:
        if statement.line_ids:
            line_list = statement.line_ids.sorted(key=lambda r: r.date)
            statement.initial_date = line_list[0].date
            statement.final_date = line_list[-1].date

    # WHERE DOES THIS COME FROM??
    for key, value in dictionaries[num].iteritems():
        if key not in result:
            result[key] = round(value * weights[num], 2)
        else:
            result[key] = round(result[key] + (value * cpt_weight), 2)
    # print "Result ", result
    return result


def subtract_dictionary(out, out_weight, cpt, cpt_weight):

    result = {}
    minuend = sum_dictionary(result, 1, out, out_weight)
    # print "Minuend: ", minuend
    for key, value in cpt.iteritems():
        if key not in minuend:
            minuend[key] = round(value * cpt_weight, 2)
        else:
            minuend[key] = round(minuend[key] - (value * cpt_weight), 2)
    return minuend


def check_bank_reconciliation(move_id):
    MOVE = client.AccountMove

    # move = MOVE.search([('id', '=', '22'),])[0]
    move = MOVE.browse(move_id)
    if not move:
        print "Move not found!"
    else:
        print
        print move
        print move.line_ids[1].name
        print"\nFull reconcile id \n"
        print move.line_ids[1].full_reconcile_id

        print"\nFor each LINE of the account move \n"
        print "Matched debit > account.partial.reconcile"
        for ml in move.line_ids:
            counterparts = (ml.matched_credit_ids
                if ml.matched_credit_ids else ml.matched_debit_ids)
            m_share = {}
            for cp in counterparts:
                l_weight = cp.amount / abs(ml.balance)
                print "weight", l_weight
                cp_dict = ast.literal_eval(cp.debit_move_id.aa_account_share)
                if not cp_dict:
                    continue
                for key, value in cp_dict.iteritems():
                    if key not in m_share:
                        m_share[key] = value * l_weight
                    else:
                        m_share[key] = m_share[key] + (value * l_weight)
            print str(m_share)

def check_dict_total(dictionary, rounding):
    """ The sum of all shares of each dictionary shall be equal and not bigger
        than 1. The sum of all shares shall be 1 for summing operations and 0
        for subtractions. The kind of operations is given by the 'round'
        parameter. The remainder will be set in the '' or undefined key

        :param dictionary:  dictionary to be checked and reviewed
        :param round:       1 for sums, 0 for subtractions
        :returns:           dictionary with the remainder in '' key
        """

    total = 0
    for key, value in dictionary.iteritems():
        if key != '':
            total += value
    if abs(total) > 1:
        raise UserError(_("""The sum of all shares of a dictionay shall
            not be bigger than 1 or smaller than -1"""))
    remainder = round(rounding - total, 2)
    dictionary[''] = remainder

    return dictionary

#######################################################à
### TEST DIFFERENCE THREE WEIGHTED DICTIONARIES

esempio_1 = [[{1: 0.4, 4: 0.6}, 1],         # FORECAST
[{1: 0.4, 3: 0.6}, 0.6],          # REAL
[{4: 0.4, 5: 0.6}, 0.4]           # REAL
]

esempio_2 = [[{1: 0.4, 4: 0.6}, 1],         # FORECAST
[{1: 0.4, 3: 0.6}, 1.5],          # REAL
[{4: 0.4, 5: 0.6}, -0.5]           # REAL
]

esempio_3 = [[{"1": 0.6, "2": 0.4},1],         # FORECAST
[{"1": 0.2, "2": 0.2}, 1],          # REAL
[{"1": 0.4, "2": 0.4}, 0.5]           # REAL
]

esempio_4 = [[{}, 0.2],         # FORECAST
[{"": 0.1, "8": 0.15, "4": 0.1, "17": 0.65}, 1],          # REAL
[{}, 1]           # REAL
]


# FOREC {'coa_share': {'1': 0.53, '2': 0.14}, 'aa_share': {'17': 0.67}}
# REAL {"coa_share": {"1": 0.79, "2": 0.21}, "aa_share": {"17": 1.0}}
cp = esempio_4

final_dict = {}
sum0 = check_dict_total(cp[0][0], 1)
sum1 = check_dict_total(cp[1][0], 1)
sum2 = check_dict_total(cp[2][0], 1)

print "\nSum: ", sum1 , " + ", sum2
final_dict = sum_dictionary(sum1, cp[1][1], sum2, cp[2][1])
print "Equal:", final_dict

final_dict = subtract_dictionary(final_dict, 1,
             sum0,cp[0][1])
print "\nThen ",  final_dict, " minus ", cp[0][0]
print "Equal: ", check_dict_total(final_dict, 0)

"""
#######################################################à
### TESTING

bank_statement_line = client.AccountBankStatementLine
bkl = bank_statement_line.browse(8)

bank_coa_account = bkl.statement_id.journal_id.default_debit_account_id
print bank_coa_account
move_debit_lines = []
move_credit_lines = []
for entry in bkl.journal_entry_ids:
    for line in entry.line_ids:
        if line.account_id.finacial_planning:
            print "\nLine: ", line.name
            if line.credit > 0 and line.debit == 0:
                for match in line.matched_debit_ids:
                    print match.debit_move_id
                    move_debit_lines.append(match.debit_move_id.id)

            if line.credit == 0 and line.debit > 0:
                for match in line.matched_credit_ids:
                    print match.credit_move_id
                    move_credit_lines.append(match.credit_move_id.id)

print "debit lines", move_debit_lines
print "credit lines", move_credit_lines


#######################################################à
### TEST DIFFERENCE TWO WEIGHTED DICTIONARIES

cp = [[{1: 0.4, 2: 0.6}, 1], [{1: 0 , 2: 0.6, 3: 0.6}, 0.5]]
final_dict = cp[0][0]
final_dict = subtract_dictionary(final_dict, cp[1][0], cp[1][1])
print final_dict

#######################################################à
### TEST MERGING TWO WEIGHTED DICTIONARIES
# check_bank_reconciliation()

cp = [[{1: 0.4, 2: 0.6}, 1], [{2: 0.6 , 3: 0.4}, 1]]
final_dict = {}
final_dict = merge_dictionary(final_dict, cp[0][0], cp[0][1])
print final_dict
final_dict = merge_dictionary(final_dict, cp[1][0], cp[1][1])
print final_dict


#######NOTES#####

    print line.balance
    for x in move.line_ids[1].matched_debit_ids:
        print x.debit_move_id.amount
        print x.debit_move_id.aa_account_share # itself
        print x.debit_move_id.balance

for line in move.line_ids:
    print"Matched credit > account.partial.reconcile"
    for x in move.line_ids[1].matched_credit_ids:
        print x.amount
        print x.credit_move_id.aa_account_share # itself
        print x.debit_move_id.aa_account_share

    print


print
for line in move.line_ids:
    print line.name

#####################

def subtract_dictionary_old(minuend, subtraend, weight):

for key, value in subtraend.iteritems():
    if key not in minuend:
        minuend[key] = - round(value * weight, 2)
    else:
        minuend[key] = round(minuend[key] - (value * weight), 2)
return minuend

"""
