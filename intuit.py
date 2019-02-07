import requests
import oauth2 as oauth
import base64
import datetime
import os
from urllib import parse as urlparse

from db import db_session
from models import Company, Transaction, OAuth2Token, Account

INTUIT_CLIENT_ID = os.environ.get('INTUIT_CLIENT_ID')
INTUIT_CLIENT_SECRET = os.environ.get('INTUIT_CLIENT_SECRET')
INTUIT_REALM_ID = os.environ.get('INTUIT_REALM_ID')
TOKEN_ENDPOINT = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

def quickbooks_headers(token):
    auth_header = 'Bearer ' + token.access_token
    headers = {'Authorization': auth_header, 'accept': 'application/json'}
    return headers

def get_refresh_token(company):
    token = db_session.query(OAuth2Token).filter(OAuth2Token.company_id==company.id).order_by('id desc').first()
    header_value = "Basic " + base64.b64encode((INTUIT_CLIENT_ID + ':' + INTUIT_CLIENT_SECRET).encode()).decode()
    headers = {
            'Content-type': "application/x-www-form-urlencoded",
            'Accept': "application/json",
            'Authorization': header_value
    }
    params = { 'refresh_token': token.refresh_token, 'grant_type': 'refresh_token' }
    res = requests.post(TOKEN_ENDPOINT, data=params, headers=headers)
    token_values = res.json()
    if 'errors' not in token_values:
        print('Gathered access and refresh token with values:')
        print(token_values)
        new_token = OAuth2Token(**token_values)
        new_token.service_name = 'Intuit'
        new_token.company = company
        new_token.created_at = datetime.datetime.now()
        new_token.updated_at = datetime.datetime.now()
        db_session.add(new_token)
        db_session.commit()
        return new_token
    else:
        raise Exception('Error in attempt to get new access_token.')
    return

def ask_quickbooks(company, endpoint, token=None, params=None):
    if not token:
        token = get_refresh_token(company)
    headers = quickbooks_headers(token)
    res = requests.get(endpoint, headers=headers, params=params)
    return res

def tell_quickbooks(company, endpoint, data, token=None):
    '''
    Function to go and tell quickbooks about something.
    '''
    if not token:
        token = get_refresh_token(company)
    headers = quickbooks_headers(token)
    res = requests.post(endpoint, headers=headers, json=data)
    return res

def transaction_endpoint(start_date=None, end_date=None):
    retval = 'https://quickbooks.api.intuit.com/v3/company/%s/reports/TransactionList?' % INTUIT_REALM_ID
    if start_date:
        retval += "start_date=%s&" % start_date
    if end_date:
        retval += "end_date=%s&" % end_date
    retval += "minorversion=4"
    return retval

def purchase_endpoint():
    return 'https://quickbooks.api.intuit.com/v3/company/%s/purchase?minorversion=4' % INTUIT_REALM_ID

def report_endpoint(report_type, start_date=None, end_date=None):
    retval = 'https://quickbooks.api.intuit.com/v3/company/%s/reports/%s?' % (INTUIT_REALM_ID, report_type)
    if start_date:
        retval += "start_date=%s&" % start_date
    if end_date:
        retval += "end_date=%s&" % end_date
    retval += "minorversion=4"
    return retval

def query_endpoint(company, statement):
    "select count(*) from transaction where docnumber='3'"
    statement_quote = urlparse.quote(statement)
    return 'https://quickbooks.api.intuit.com/v3/company/%s/query?query=%s&minorversion=4' % (INTUIT_REALM_ID, statement_quote)

