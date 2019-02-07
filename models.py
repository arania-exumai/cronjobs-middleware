from sqlalchemy import BIGINT, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB


from db import Base

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    tx_date = Column(DateTime)
    txn_type = Column(String(50))
    intuit_id = Column(Integer)
    doc_num = Column(String)
    is_no_post = Column(Boolean)
    name = Column(String(50))
    memo = Column(String(50))
    credit_account_id = Column(BIGINT, ForeignKey("accounts.id"))
    credit_account = relationship("Account", foreign_keys=[credit_account_id])
    debit_account_id = Column(BIGINT, ForeignKey("accounts.id"))
    debit_account = relationship("Account", foreign_keys=[debit_account_id])
    company_id = Column(BIGINT, ForeignKey("companies.id"))
    company = relationship("Company", foreign_keys=[company_id])
    amount = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fully_qualified_name = Column(String)
    balance = Column(Float)
    company_id = Column(BIGINT, ForeignKey("companies.id"))
    intuit_id = Column(Integer)
    company = relationship("Company", foreign_keys=[company_id])
    account_type = Column(String)
    wallet_address = Column(String)
    active = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __repr__(self):
        return '<Account %s> %s' % (str(self.id), self.name)

class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    symbol = Column(String)
    legalType = Column(String)
    logo = Column(String)
    isDCARPE = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    has_intuit_connection = Column(Boolean)
    tokens = relationship("OAuth2Token")
    crypto_wallets = relationship("CryptoWallet")

    def __repr__(self):
        return '<Company %s> %s' % (str(self.id), self.name)

class OAuth2Token(Base):
    __tablename__ = 'o_auth2_tokens'
    id = Column(Integer, primary_key=True)
    service_name = Column(String)
    token_type = Column(String)
    refresh_token = Column(String)
    access_token = Column(String)
    x_refresh_token_expires_in = Column(Integer)
    expires_in = Column(Integer)
    company_id = Column(BIGINT, ForeignKey("companies.id"))
    company = relationship("Company", foreign_keys=[company_id])
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __repr__(self):
        return '<OAuth2Token %s> %s' % (str(self.id), self.service_name)

class CryptoWallet(Base):
    __tablename__ = 'crypto_wallets'
    id = Column(Integer, primary_key=True)
    company_id = Column(BIGINT, ForeignKey("companies.id"))
    company = relationship("Company", foreign_keys=[company_id])
    coin_type = Column(String)
    address = Column(String)
    crypto_transactions = relationship("CryptoTransaction")

    def __repr__(self):
        return '<CryptoWallet %s> %s, %s' % (str(self.id), self.coin_type, self.address)

class CryptoTransaction(Base):
    __tablename__ = 'crypto_transactions'
    id = Column(Integer, primary_key=True)
    crypto_wallet_id = Column(BIGINT, ForeignKey("crypto_wallets.id"))
    crypto_wallet = relationship("CryptoWallet", foreign_keys=[crypto_wallet_id])
    tx_hash = Column(String)
    timestamp = Column(DateTime)
    amount = Column(Float)
    usd_amount = Column(Float)
    out = Column(Boolean)
    to_account = Column(String)
    from_account = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    block_num = Column(Integer)
    tx_cost = Column(Float)

    def purchase_cost(self):
        #need to include the tx_cost, gas price for ether, in the full cost of transaction
        return self.usd_amount + (self.amount / self.usd_amount) * self.tx_cost

    def __repr__(self):
        return '<CryptoTransaction %s>' % (str(self.id))

class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    start_period = Column(Date)
    end_period = Column(Date)
    body = Column(JSONB)
    gathered_at = Column(DateTime)
    company_id = Column(BIGINT, ForeignKey("companies.id"))
    company = relationship("Company", foreign_keys=[company_id])
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __repr__(self):
        return '<Report %s> %s' % (str(self.id), self.name)



if __name__ == '__main__':
    from db import db_session
    print(db_session.query(Transaction).count())
    print(db_session.query(Company).count())
    print(db_session.query(OAuth2Token).count())
    print(db_session.query(CryptoWallet).count())
    print(db_session.query(CryptoTransaction).count())
