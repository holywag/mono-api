import requests
from datetime import datetime, timedelta

class IbanNotFound(Exception):
    """Account with the specified IBAN not found.
    """
    def __init__(self, iban):
        super().__init__(f'Account with the specified IBAN not found: {iban}')
        self.iban = iban

class MonobankApi:
    """Wrapper for monobank REST API (https://api.monobank.ua/docs/)
    Provide functionality:
        - request client information
        - request bank statements for the last N days
    """

    CLIENT_INFO_API_URL = 'https://api.monobank.ua/personal/client-info'
    STATEMENT_API_URL = 'https://api.monobank.ua/personal/statement/{account}/{date_from}/{date_to}'

    def __init__(self, token):
        self.token = token

    def request_client_info(self):
        headers =  {'X-Token': self.token}
        return requests.get(MonobankApi.CLIENT_INFO_API_URL, headers=headers).json()

    def request_account_id(self, iban):
        headers =  {'X-Token': self.token}
        response = requests.get(MonobankApi.CLIENT_INFO_API_URL, headers=headers)
        for account in response.json()['accounts']:
            if account["iban"] == iban:
                return account["id"]
        raise IbanNotFound(iban)

    def request_statements_for_last_n_days(self, account_id, n_days):
        headers =  {'X-Token': self.token}
        url = MonobankApi.STATEMENT_API_URL.format(
            account=account_id,
            date_from=int((datetime.today() - timedelta(days=n_days)).timestamp()),
            date_to= int(datetime.today().timestamp()))
        return requests.get(url, headers=headers).json()
