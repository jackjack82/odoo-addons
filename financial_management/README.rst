=========================
Financial Planning
=========================

This module introduces financial planning functionalities to openerp.

Configuration
=============

To configure this module, you need to:

#. create a template and add fixed cost lines             ok
# - select the bank statement for financial planning       ok

#. manage financial planning date in different objects:
 - account.invoice >> date_financial_planning
 - account.move >> financial_date


 (??) - account.move.user_type_id.type => internal_type

NOTES:
- check in invoice no final saldo updated >> ok
- when creating bank.line from forecast set date = financial_date >>0k!
- add financial balance on bank statement lines >> non fattibile
- !! when possible, update all SALDOS!! >> ok

Open Points
=====

- Multi-company
- What if I delete a forecast, links to is still missing.



Credits
=======

Contributors
------------

* Giacomo Grasso <giacomo.grasso.82@gmail.com>
