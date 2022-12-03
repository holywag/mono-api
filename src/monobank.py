import requests, random, time
from requests_toolbelt.utils import dump
from datetime import datetime, date, timedelta

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

class ApiClient:
    def __init__(self, token, max_retry_no=1):
        self.token = token
        self.max_retry_no = max_retry_no
    
    def request(self, url):
        for attempt_no in range(self.max_retry_no):
            response = requests.get(url, headers={'X-Token': self.token})
            response_json = response.json()
            if type(response_json) is dict:
                error_description = response_json.get('errorDescription')
                if error_description:
                    if error_description == 'Too many requests' and attempt_no < self.max_retry_no - 1:
                        delay = random.uniform(3, 12)
                        time.sleep(delay)
                        continue
                    raise MonobankApiErrorResponse(response)
            return response

class MonobankApi:
    """Wrapper for monobank REST API (https://api.monobank.ua/docs/)
    Provide functionality:
        - request client information
        - request bank statements for the last N days
    """

    CLIENT_INFO_API_URL = 'https://api.monobank.ua/personal/client-info'
    STATEMENT_API_URL = 'https://api.monobank.ua/personal/statement/{account}/{date_from}/{date_to}'

    def __init__(self, client):
        self.client = client

    def request_client_info(self):
        return self.client.request(MonobankApi.CLIENT_INFO_API_URL).json()

    def request_account_id(self, iban):
        response = self.client.request(MonobankApi.CLIENT_INFO_API_URL)
        for account in response.json()['accounts']:
            if account['iban'] == iban:
                return account['id']
        raise IbanNotFound(iban)

    def request_statements_for_last_n_days(self, account_id, n_days):
        url = MonobankApi.STATEMENT_API_URL.format(
            account=account_id,
            date_from=int((datetime.combine(date.today(), datetime.min.time()) - timedelta(days=n_days)).timestamp()),
            date_to= int(datetime.now().timestamp()))
        return self.client.request(url).json()
    
    def request_statements_for_time_range(self, account_id, datetime_range_start, datetime_range_end):
        url = MonobankApi.STATEMENT_API_URL.format(
            account=account_id,
            date_from=int(datetime_range_start.timestamp()),
            date_to=int(datetime_range_end.timestamp()))
        return self.client.request(url).json()
