=========================
Treasury Planning
=========================

This module introduces treasury planning functionalities to Odoo.

Treasury management is based on account moves and on bank statement lines
(for forecasting other costs and revenues not yet invoiced or not invoiceable).


Configuration
=============

To configure this module, you need to:

#. selects accounts for treasury planning

This module forecasting is based on account moves, which are in turn related to
accounts. At the menu "Accounting > Adviser > Chart of Accounts", select
the accounts for planning and flag the field "Treasury Planning".

#. Create treasury forecast journal

Create a Treasury Planning journal, which shall be of type "Bank".
Select the flag "Treasury Planning".

#. Create a bank statements for Treasury Planning

Create a bank statements related to the Treasury Planning. You can call it
"Virtual Bank 2017", it might be useful to use one statement for a determined
period. Link it to the treasury planning journal.


Usage
=============

#. Payables and receivables

At the menu "Treasury > Others > Payables and Receivables" we see all account moves
we flagged initially for treasury planning

#. create a template and add fixed cost lines

At the menu "Treasury > Treasury Planning > Templates" create a template, link it
to the "Virtual bank 2017" and cost lines.

 # - select the bank statement for treasury planning


Open Points
=====

- The boolean Treasury Planning on journal not very useful
- Link the virtual bank not to template but on each forecast?
- take recurrent costs from previous month
- compute bank balance and print on note field (e.g)


Credits
=======

Contributors
------------

* Giacomo Grasso <giacomo.grasso.82@gmail.com>
