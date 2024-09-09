'''
This file tests the getWaterfall method in the StructuredSecurities class.
'''

import sys
import os

# Add the parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from structured_securities_class import StructuredSecurities
from standard_tranche_class import StandardTranche





# Create a StructuredSecurities instance
ss = StructuredSecurities(totalNotionalAmount=1000000)

# Add tranches
ss.addTranche(percent_notional=0.6, rate=0.05, subordination=1)
ss.addTranche(percent_notional=0.4, rate=0.04, subordination=2)

# Set flag
ss.flag('Sequential')

# Increase time periods
ss.increaseTime(1)

# Make interest and principal payments
ss.makePayments(cash_amount=700000)

# Print waterfall for current period
waterfall = ss.getWaterfall(period=1)
print(waterfall)

# Test invalid mode
try:
    ss.flag('InvalidMode')
#This is to try the newly added debugging and error handling
except ValueError as ex:
    print(f'Caught expected exception: {ex}')




















# # Initialize StructuredSecurities object with total notional amount
# total_notional = 1000000
# ss = StructuredSecurities(totalNotionalAmount=total_notional)
#
# # Add some tranches to the StructuredSecurities object
# ss.addTranche(percent_notional=0.4, rate=0.05, subordination='A')
# ss.addTranche(percent_notional=0.3, rate=0.06, subordination='B')
# ss.addTranche(percent_notional=0.3, rate=0.07, subordination='C')
#
# # Flag payment method as 'Sequential'
# ss.flag('Sequential')
#
# # Make payments (arbitrary amounts for testing)
# ss.makePayments(30000)  # First period payment
# ss.increaseTime()       # Move to next period
# ss.makePayments(50000)  # Second period payment
#
# # Test getWaterfall for period 1
# period = 1
# waterfall_period_1 = ss.getWaterfall(period=period)
# print(f'Waterfall for Period {period}:')
# for i, tranche_data in enumerate(waterfall_period_1):
#     print(f"Tranche {i + 1}: Interest Due = {tranche_data[0]}, Interest Paid = {tranche_data[1]}, "
#           f"Interest Shortfall = {tranche_data[2]}, Principal Paid = {tranche_data[3]}, "
#           f"Balance = {tranche_data[4]}")
#
# # Test getWaterfall for period 2
# period = 2
# waterfall_period_2 = ss.getWaterfall(period=period)
# print(f'\nWaterfall for Period {period}:')
# for i, tranche_data in enumerate(waterfall_period_2):
#     print(f"Tranche {i + 1}: Interest Due = {tranche_data[0]}, Interest Paid = {tranche_data[1]}, "
#           f"Interest Shortfall = {tranche_data[2]}, Principal Paid = {tranche_data[3]}, "
#           f"Balance = {tranche_data[4]}")
