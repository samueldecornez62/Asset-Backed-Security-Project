'''
This file tests some commands in the structured_securities_class (again)
'''

import sys
import os

# Add the parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from structured_securities_class import StructuredSecurities, StandardTranche

# Initialize Structured Securities with a total notional amount
total_notional_amount = 1_000_000
ss = StructuredSecurities(total_notional_amount)

# Add tranches to the Structured Securities
ss.addTranche(percent_notional=0.4, rate=0.05, subordination=1)  # 400,000
ss.addTranche(percent_notional=0.3, rate=0.04, subordination=2)  # 300,000
ss.addTranche(percent_notional=0.3, rate=0.03, subordination=3)  # 300,000

# Set the payout flag
ss.flag('Sequential')

# Increase time period
ss.increaseTime()

# Test payments with different cash amounts
cash_amounts = [30_000, 50_000] #If using multiple, use reset method to clear dictionaries
cash_amounts = [30_000]

for cash_amount in cash_amounts:
    print(f"\nMaking payments with cash amount {cash_amount}")
    ss.makePayments(cash_amount)

    # Print tranche details after payment
    for tranche in ss._tranches:
        print(f"Tranche: {tranche}, Notional: {tranche.notional}, Balance: {tranche.notionalBalance()}")
        print(f"Interest Shortfalls: {tranche._interestShortfalls}")
        print(f"Principal Shortfalls: {tranche._principalShortfalls}")


