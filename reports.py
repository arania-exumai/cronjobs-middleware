import datetime

from db import db_session
from models import Company, Report
from helpers.intuit import ask_quickbooks, report_endpoint

def parse_report(company, jres, start_date=None, end_date=None):
    print('Parsing report')
    #create statement, or find statement
    report_name = jres["Header"]["ReportName"]
    start_period = jres["Header"]["StartPeriod"]
    end_period = jres["Header"]["EndPeriod"]
    gathered_at = jres["Header"]["Time"]
    current_time = datetime.datetime.now()
    report = Report(company_id=company.id, start_period=start_date, end_period=end_date, gathered_at=gathered_at, name=report_name, body=jres, created_at=current_time, updated_at=current_time)
    db_session.add(report)
    db_session.commit()

def gather_reports(company_id, report_type, start_date=None, end_date=None, token=None):
    company = db_session.query(Company).filter(Company.id==company_id).first()
    endpoint = report_endpoint(report_type, start_date=start_date, end_date=end_date)
    print(endpoint)
    res = ask_quickbooks(company, endpoint, token=token)
    jres = res.json()
    parse_report(company, jres, start_date=start_date, end_date=end_date)

