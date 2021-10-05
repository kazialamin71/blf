# Author Mufti Muntasir Ahmed 11-05-2019


from openerp.osv import osv, fields
from openerp import SUPERUSER_ID, api
from openerp.tools.translate import _
from datetime import datetime



class  MoneyReceipt(osv.osv):
    _name = 'money.receipt'
    _description = "Money Receipt List"


    def _get_period(self, cr, uid, context=None):
        ctx = dict(context or {})
        period_ids = self.pool.get('account.period').find(cr, uid, context=ctx)
        # import pdb
        # pdb.set_trace()
        return period_ids[0]


    _columns = {
        'date': fields.date('Date', required=True, select=True, copy=False),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True),
        'period_id': fields.many2one('account.period', 'Period', required=True),
        'move_id': fields.many2one('account.move', 'Journal Entries', required=False,readonly=True),
        'description': fields.char('Received With Thanks From'),
        'address': fields.char('Of'),
        'name': fields.char('Name'),
        'deposit_to': fields.many2one('account.account', 'Deposit To/DR', required=True),
        'towards_to': fields.many2one('account.account', 'Towards To/CR', required=True),
        'amount': fields.float('Amount', required=True),
        'create_date': fields.datetime('Creation Date', readonly=True, select=True,
                                       help="Date on which Receipt is created."),

        'date_confirm': fields.datetime('Confirmation Date', readonly=True, select=True,
                                    help="Date on which sales order is confirmed.", copy=False),
        'user_id': fields.many2one('res.users', 'Assigned to', select=True, track_visibility='onchange'),

        'state': fields.selection([
            ('pending', 'Pending'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),

        ], 'Status', readonly=True, copy=False, help="Gives the status of the Money Receipt", select=True),

    }

    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'state': 'pending',
        'date': fields.date.context_today,
        'period_id': _get_period,


    }


    def make_confirm(self, cr, uid, ids, context=None):

        id_list = ids

        for element in id_list:
            journal_vals={}

            ids = [element]
            res = self.browse(cr, uid, [element], context=context)[0]
            # import pdb
            # pdb.set_trace()

            journal_vals["journal_id"]=res.journal_id.id
            journal_vals["period_id"]=res.period_id.id
            journal_vals["date"]=res.date

            debit_temp_dict={'analytic_account_id': False,
                       'tax_code_id': False,
                       'tax_amount': 0,
                       'name': res.description,
                       'currency_id': False,
                       'credit': 0,
                       'date_maturity': False,
                       'debit': res.amount,
                       'amount_currency': 0,
                       'partner_id': False,
                       'account_id': res.deposit_to.id}
            credit_temp_dict={'analytic_account_id': False,
                       'tax_code_id': False,
                       'tax_amount': 0,
                       'name': res.description,
                       'currency_id': False,
                       'credit': res.amount,
                       'date_maturity': False,
                       'debit': 0,
                       'amount_currency': 0,
                       'partner_id': False,
                       'account_id': res.towards_to.id}
            journal_vals["line_id"] = [[0,False,debit_temp_dict],[0,False,credit_temp_dict]]
            account_obj = self.pool.get('account.move')
            move_id = account_obj.create(cr, uid, journal_vals, context=context)
            account_obj = self.pool.get('account.move').button_validate(cr, uid, [move_id], context=context)
            
            
            if ids is not None and move_id is not None:
                cr.execute("update money_receipt set state='done' where id=%s", (ids))
                cr.commit()
                cr.execute("update money_receipt set move_id='%s' where id=%s", (move_id,ids[0]))
                cr.commit()

        return 'True'

    def make_cancel(self, cr, uid, ids, context=None):
        id_list = ids
        for element in id_list:
            ids = [element]

            if ids is not None:
                cr.execute("update money_receipt set state='cancel' where id=%s", (ids))
                cr.commit()

        return 'True'

    def write(self, cr, uid, ids, vals, context=None):
        cr.execute("select state from  money_receipt where id=%s", (ids))
        result_list = cr.fetchall()

        for item in result_list:
            if str(item[0]) == 'done' or str(item[0]) == 'cancel':
                raise osv.except_osv(_('Message'), _("Sorry You Can not Edit it. Because it is already confirmed/Cancelled."))
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = super(MoneyReceipt, self).write(cr, uid, ids, vals, context=context)
        return res

    def create(self, cr, uid, vals, context=None):
        receipt_id = super(MoneyReceipt, self).create(cr, uid, vals, context) # return ID int object

        if receipt_id is not None:
            name_text = 'MR-100' + str(receipt_id)
            cr.execute('update money_receipt set name=%s where id=%s', (name_text, receipt_id))
            cr.commit()
        return receipt_id


