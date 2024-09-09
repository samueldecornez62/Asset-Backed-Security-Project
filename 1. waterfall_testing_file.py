'''
This file will test the doWaterfall function.
'''

import logging
import sys
import os

# Set the system path to include loan and Tranches folders
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'loan')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Tranches')))

# Import loan files
from asset_base import Asset  # Assuming this works correctly from the loan folder
from loan_base import Loan
from loan_pool import LoanPool
from loans import FixedRateLoan, VariableRateLoan
from car_class import Car

# Import tranche files
from base_tranche_class import Tranche
from standard_tranche_class import StandardTranche
from structured_securities_class import StructuredSecurities
from waterfall_function import doWaterfall

# Set logger
logging.basicConfig(level=logging.ERROR)

# Begin testing in main function
def main():
    # Initialize an Asset object
    my_asset = Asset(initial_value=100000)

    # Create a FixedRateLoan instance
    loan_face_value = 50000
    fixed_rate = 0.05
    loan_start = '2024-01-01'
    loan_end = '2027-01-01'

    fixed_loan_1 = FixedRateLoan(asset=my_asset, face=loan_face_value, rate=fixed_rate,
                                      loanstart=loan_start, loanend=loan_end)


    rate_dict = {0:0.04, 12:0.045, 24:0.05}
    variable_loan_1 = VariableRateLoan(asset=my_asset, face= loan_face_value, rateDict=rate_dict,
                                       loanstart=loan_start, loanend = loan_end)

    # Initialize LoanPool obect
    loan_pool = LoanPool([fixed_loan_1, variable_loan_1])

    #Initialize StructuredSecurities object
    ss = StructuredSecurities(totalNotionalAmount = 1_000_000)

    # Add Tranches to StructuredSecurities, wiwth different subordination flags
    ss.addTranche(percent_notional=0.2, rate=0.03, subordination='1')
    ss.addTranche(percent_notional=0.3, rate=0.04, subordination='2')
    ss.addTranche(percent_notional=0.5, rate=0.05, subordination='3')

    #Call the doWaterfall function
    waterfall_results = doWaterfall(loan_pool, ss)





    ## Count defaulted loans by end of waterfall
    ## Note that not all loans will default at same time
    ## The calculated recovery value we return in the function call is based on the default period of each loan
    # Count the number of defaulted loans
    defaulted_count = sum(1 for loan in loan_pool if getattr(loan, '_defaultFlag', None) == 'Defaulted')
    print(f"Number of defaulted loans: {defaulted_count}")






if __name__ == '__main__':
    main()
