'''
This file tests the doWaterfall standalone function.
NOTE: this has some importing issue that needs fixing after some edits
The asset type is showing incorrect since it is <class 'loan.asset_base.Asset'> rather than <class 'asset_base.Asset'>
'''

import sys
import os

# Add the loan and tranche folders to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../loan')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Tranches')))

# Import required classes
# Import loan files
from loan.loan_base import Loan
from loan.loan_pool import LoanPool
from loan.loans import FixedRateLoan, VariableRateLoan
from loan.asset_base import Asset
from loan.car_class import Car

# Import tranche files
from Tranches.standard_tranche_class import StandardTranche
from Tranches.structured_securities_class import StructuredSecurities

# Import waterfall function
from Tranches.waterfall_function import doWaterfall

# Define asset
my_asset = Asset(initial_value=100000)

# Define sample loans
loan1 = FixedRateLoan(asset=my_asset, face=500000, rate=0.05, loanstart='2024-01-01', loanend='2027-01-01')
rate_dict = {0: 0.04, 12: 0.045, 24: 0.05}
loan2 = VariableRateLoan(asset=my_asset, face=300000, rateDict=rate_dict, loanstart='2024-01-01', loanend='2027-01-01')

# Create a LoanPool with these loans
loan_pool = LoanPool([loan1, loan2])

# Create a StructuredSecurities instance
ss = StructuredSecurities(totalNotionalAmount=800000)

# Add tranches to StructuredSecurities
ss.addTranche(percent_notional=0.5, rate=0.06, subordination=1)
ss.addTranche(percent_notional=0.5, rate=0.05, subordination=2)

# Set the payment flag (make sure 'Sequential' is a valid mode)
ss.flag('Sequential')

# Call the doWaterfall function with the loan pool and StructuredSecurities instance
results = doWaterfall(loan_pool, ss)

# Print the results
for period, waterfall in enumerate(results, start=1):
    print(f"Waterfall for Period {period}: {waterfall}")
