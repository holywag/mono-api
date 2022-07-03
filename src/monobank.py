import requests
from requests_toolbelt.utils import dump
from datetime import datetime, timedelta

class IbanNotFound(Exception):
    """Account with the specified IBAN not found.
    """
    def __init__(self, iban):
        super().__init__(f'Account with the specified IBAN not found: {iban}')
        self.iban = iban


class MonobankApiErrorResponse(Exception):
    """API returned an error.
    """
    def __init__(self, response):
        super().__init__(f'Monobank API returned an error: {response.text}\nFull response:\n{dump.dump_all(response)}')
        self.response = response


class Monobank:
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
        return requests.get(Monobank.CLIENT_INFO_API_URL, headers=headers).json()


    def request_account_id(self, iban):
        headers =  {'X-Token': self.token}
        response = requests.get(Monobank.CLIENT_INFO_API_URL, headers=headers)
        try:
            for account in response.json()['accounts']:
                if account['iban'] == iban:
                    return account['id']
        except:
            raise MonobankApiErrorResponse(response)
        raise IbanNotFound(iban)


    def request_statements_for_last_n_days(self, account_id, n_days):
        headers =  {'X-Token': self.token}
        url = Monobank.STATEMENT_API_URL.format(
            account=account_id,
            date_from=int((datetime.today() - timedelta(days=n_days)).timestamp()),
            date_to= int(datetime.today().timestamp()))
        return requests.get(url, headers=headers).json()
