'''
This file tests some commands in the structured_securities_class
'''


import sys
import os

# Add the parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from structured_securities_class import StructuredSecurities



### TESTTTTT

# Create a StructuredSecurities instance with a total notional amount
ss = StructuredSecurities(totalNotionalAmount=1000000)  # Example total notional amount

# Add tranches with various parameters
ss.addTranche(percent_notional=0.4, rate=0.05, subordination=1)  # Tranche A
ss.addTranche(percent_notional=0.3, rate=0.04, subordination=2)  # Tranche B
ss.addTranche(percent_notional=0.3, rate=0.03, subordination=3)  # Tranche C

# Set the payment method to 'Sequential'
ss.flag('Sequential')

# Increase the time period to simulate passage of time
ss.increaseTime(num_increases=1)

# Perform payments with a specific cash amount
print("Performing payments with cash amount 200000:")
ss.makePayments(cash_amount=10000001)

# Output results for verification
for i, tranche in enumerate(ss._tranches):
    print(f"Tranche {i+1}:")
    print(f"  Notional Balance: {tranche.notionalBalance()}")
    print(f"  Interest Shortfalls: {tranche._interestShortfalls}")
    print(f"  Principal Shortfalls: {tranche._principalShortfalls}")

