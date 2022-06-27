#!/usr/bin/env python3

import json, argparse
from monobank import MonobankApi

parser = argparse.ArgumentParser()
parser.add_argument('token')
parser.add_argument('iban')
parser.add_argument('n_days', type=int)
args = parser.parse_args()

client = MonobankApi(args.token)

account_id = client.request_account_id(args.iban)
statements = client.request_statements_for_last_n_days(account_id, args.n_days)

print(json.dumps(statements, indent=2, ensure_ascii=False))
