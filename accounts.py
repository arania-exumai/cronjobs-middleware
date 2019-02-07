import os, binascii
from models import Account
from db import db_session

unassigned_addresses = []


#base command for all multichain json-rpc commands
base_command = 'sudo /usr/local/bin/multichain-cli auditchain %s'


def create_and_label_wallets():
    unassigned_accounts, unassigned_addresses = validate_account_addresses()
    if unassigned_accounts:
        label_account_wallet_addresses(unassigned_accounts, unassigned_addresses)


def validate_account_addresses():
    active_no_wallet_accounts = db_session.query(Account).filter(Account.active=='true', Account.wallet_address==None).all()
    unassigned_accounts = []
    for acc in active_no_wallet_accounts:
        acct_fqdn = acc.fully_qualified_name
        #append qbo fully qualified account name into unassigned_accounts array
        unassigned_accounts.append(acct_fqdn)
        #generate new address and output it to text file in home directory
        get_new_addr_command = base_command % ('getnewaddress >~/newaddress.txt 2>&1')
        #os.system(get_new_addr_command)

        cur_dir = os.getcwd()
        tmp_folder = cur_dir + '/tmp'
        print(tmp_folder)
        if not os.path.exists(tmp_folder):
            print('not there')
            os.makedirs(tmp_folder)
        path = tmp_folder + '/newaddress.txt'

        #opens text file and extracts new address and adds it to unassigned_addresses array
        with open(path) as fp:
            for j, line in enumerate(fp):
                if j == 2:
                    unassigned_addresses.append(line)

                    #updates the wallet_address column for the account
                    acc.wallet_address = line

                    db_session.add(acc)
                    #saves database changes as permanent
                    db_session.commit()
    #deletes placeholder text file in home directory
    os.system("cd ~ & sudo rm newaddress.txt")
    return unassigned_accounts, unassigned_addresses


def label_account_wallet_addresses(unassigned_accounts, unassigned_addresses):
    #iterates through list of array and assigns the label in root stream
    for acc_name, add in zip(unassigned_accounts, unassigned_addresses):

        #reformat label_name into appropriate hexadecimal format to put into root stream
        hex_label=binascii.hexlify(acc_name.encode('ascii'))
        label_name_hex = hex_label.decode("utf-8")

        #grant send and receive permissions to wallet address
        grant_command = base_command % ('grant "%s" send,receive' % add)
        os.system(grant_command)

        #publishes into root stream the label for the new address
        publish_from_command = base_command % ('publishfrom "%s" root "%s" %s' % (add, label_name, label_name_hex))
        os.system(publish_from_command)

    return True

