from loans.models import Application,ApplicationStatusEnum, Loan
from clients.models import Client, LoanProfile
from datetime import date
from django.conf import settings
from django.core.cache import cache
import requests
from requests.auth import HTTPBasicAuth
from payments.models import Checkout
from funds.models import Fund
# from wallets.models import Cash
from transactions.models import Transaction
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Helpers:
    def create_loan_application(self,client,product,amount,period):
        code = self.get_loan_application_next_code()
        if amount > settings.AUTO_APPROVE_CEILING:
            status = ApplicationStatusEnum.PENDING
        else:
            status = ApplicationStatusEnum.APPROVED

        return Application.objects.create(
                client = client,
                product = product,
                amount = amount,
                duration = period,
                code = code,
                status=status)

    def get_latest_loan_application(self):
        try:
            application = Application.objects.latest('created_at')
        except Application.DoesNotExist:
            return None
        else:
            return application



    def get_loan_application_next_code(self):
        today = date.today().isoformat()
        year, month, day = str(today).split('-')

        today_code = str(year)[2:] +  str(month) + str(day)
        next_code = today_code + '1'

        latest = self.get_latest_loan_application()
        if latest and (today_code == str(latest.code)[:6]):
            next_code = latest.code + 1

        return int(next_code)

    def get_client_product_loan_profile(self,client,product):
        return LoanProfile.objects.filter(client=client,product=product).last()

    def get_client_by_msisdn(self,msisdn):
        msisdn = str(msisdn).strip('+').strip()
        try:
            client = Client.objects.get(msisdn=msisdn)
        except Client.DoesNotExist:
            client = None
        return client
    def generate_token(self):
        # if cache.get('access_token'):
        #     token = cache.get('access_token').encode('utf-8')
        #     return token
        # else:

        consumer_key = settings.VARIABLES.get('CONSUMER_KEY')
        consumer_secret = settings.VARIABLES.get('CONSUMER_SECRET')
        r = requests.get(settings.VARIABLES.get('TOKEN_URL'), auth=HTTPBasicAuth(consumer_key, consumer_secret))
        token=r.json()
        access_token = token.get('access_token')
        cache.set('access_token',access_token,1700)
        return token.get('access_token')
    
    def create_checkout(self,amount,ref_no,msisdn):
        return Checkout.objects.create(amount=amount,ref_no=ref_no,msisdn=msisdn)

    def is_loan_product_fund_sufficient(self,application):
        return application.product.fund.balance > application.amount

    def calculate_interest(self,application):
        interest = (application.amount*application.product.interest_rate*application.duration)//100
        return interest
    # def add_new_client_wallet(self,client):
    #     if not hasattr(client, "cash"):
    #         client.cash = Cash.objects.create(client=client)

    def create_transaction(self,client,type,product,subject,initial_balance,amount,ref):
        Transaction.objects.create(
            client=client,
            type=type,
            product=product,
            subject=subject,
            initial_balance=initial_balance,
            amount=amount,
            ref=ref
            )
    
    def get_loan_by_code(self,code):
        try:
            return Loan.objects.filter(application__code=code,is_disbursed=True).last()
        except Loan.DoesNotExist:
            return None

            

       


helpers = Helpers()

