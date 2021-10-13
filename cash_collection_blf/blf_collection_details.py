import datetime
import pytz
import time
from openerp import tools
from openerp.osv import osv
from openerp.report import report_sxw


class blf_collcetion_details(report_sxw.rml_parse):

    def _get_user_names(self, t_dat=None, end_date=None):
        st_dat=t_dat
        end_date= end_date
        result = []

        query_for_blf="select a.name dr,sum(amount), count(a.id),money_receipt.description,money_receipt.address,money_receipt.name from money_receipt,account_account a where  a.id=money_receipt.towards_to and " \
                         "(money_receipt.create_date <= '%s') and (money_receipt.create_date >= '%s') group by a.name,money_receipt.description,money_receipt.address,money_receipt.name"
        self.cr.execute(query_for_blf % (end_date,st_dat))
        blf_info = []
        for items in self.cr.fetchall():
            blf_info.append({
                'acc_name': items[0],
                'total_amount': items[1],
                'count':items[2],
                'd_name':items[3],
                'address':items[4],
                'mr_no':items[5]



            })
        # opd_info.append({'total':total_amount})

        return blf_info

    def _get_context_text(self, t_dat=None, end_date=None):
        txt = "Start Date " + str(t_dat)  + " End Date " + str(end_date)
        return txt

    def __init__(self, cr, uid, name, context):


        super(blf_collcetion_details, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'get_user_names': self._get_user_names,
            'get_user_context': self._get_context_text,
        })


class report_blf_collection(osv.AbstractModel):
    _name = 'report.blf.report_blf_collection'
    _inherit = 'report.abstract_report'
    _template = 'blf.report_blf_collection'
    _wrapped_report_class = blf_collcetion_details
