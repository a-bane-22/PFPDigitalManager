from app.models import Quarter, Group, Account, AccountSnapshot
from app import db
from datetime import date


# Pre:  groups is a dictionary of format {group_name: market_value}
# Post: tda_group_value.csv has been written with each key-value pair
#        on a line
def write_tda_group_value(groups):
    with open('tda_group_value.csv', 'w') as group_file:
        for group in groups:
            market_value = str(groups[group])
            group_line = '{},{}\n'.format(group, market_value)
            group_file.write(group_line)


# Pre:  accounts is a dictionary of format {account_number: data}
#        where data is a dictionary of format {client_name, group_name,
#        account_type, group_market_value, account_market_value,
#        weight_of_account, group_fee, account_fee}
# Post: tda_fees_by_account.csv has been written with each key-value pair
#        on a line
def write_tda_fee_by_account(accounts):
    with open('tda_fees_by_account.csv') as account_file:
        header = '{},{},{},{},{},{},{},{},{}\n'.format('Client Name',
                                                       'Group Name',
                                                       'Account Number',
                                                       'Account Type',
                                                       'Group Market Value',
                                                       'Account Market Value',
                                                       'Weight of Account',
                                                       'Group Fee',
                                                       'Account Fee')
        account_file.write(header)
        for account_number in accounts:
            account = accounts[account_number]
            account_line = '{},{},{},{},{},{},{},{},{}\n'.format(account['client_name'],
                                                                 account['group_name'],
                                                                 account_number,
                                                                 account['account_type'],
                                                                 account['group_market_value'],
                                                                 account['account_market_value'],
                                                                 account['weight_of_account'],
                                                                 account['group_fee'],
                                                                 account['account_fee'])
            account_file.write(account_line)