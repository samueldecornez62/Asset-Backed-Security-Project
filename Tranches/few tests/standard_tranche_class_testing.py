'''
This file tests some commands in the standard_tranche_class
'''


import sys
import os

# Add the parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from standard_tranche_class import StandardTranche


# Run some testing code in main
def main():
    # Create a StandardTranche object
    tranche = StandardTranche(notional=1000, rate=0.05, subordination='Senior')

    # Test initial state
    print("Initial notional balance:", tranche.notionalBalance())  # Expected: 1000
    print("Initial interest due:", tranche.interestDue())          # Expected: 0

    # Test increasing time periods
    tranche.increaseTimePeriod()
    print("Time period after increase:", tranche._timePeriod)      # Expected: 1

    # Test making principal payments
    tranche.makePrincipalPayment(amount_paid=200)
    print("Principal payments:", tranche._principalPayments)      # Expected: {0: 200}
    print("Total principal paid:", tranche._principalPaid)        # Expected: 200
    print("Notional balance after payment:", tranche.notionalBalance())  # Expected: 800

    # Test making interest payments
    tranche.increaseTimePeriod()
    print("Interest due for period 1:", tranche.interestDue())    # Expected: 40

    tranche.makeInterestPayment(amount_paid=30)
    print("Interest payments:", tranche._interestPayments)        # Expected: {1: 30}
    print("Total interest paid:", tranche._interestPaid)          # Expected: 30
    print("Interest shortfalls:", tranche._interestShortfalls)    # Expected: {1: 10}

    # Test balance with shortfall
    print("Notional balance with shortfall:", tranche.notionalBalance())  # Expected: 800

    # Test supplemental payment period
    tranche.increaseTimePeriod()
    tranche.makePrincipalPayment(amount_paid=600)  # Extra payment, should reduce notional to zero or negative
    print("Principal payments after supplemental payment:", tranche._principalPayments)  # Expected: {0: 200, 2: 600}
    print("Notional balance after supplemental payment:", tranche.notionalBalance())  # Expected: 0 or negative

    # Test reset functionality
    tranche.reset()
    print("Time period after reset:", tranche._timePeriod)          # Expected: 0
    print("Principal payments after reset:", tranche._principalPayments)  # Expected: {}
    print("Interest payments after reset:", tranche._interestPayments)  # Expected: {}
    print("Total principal paid after reset:", tranche._principalPaid)    # Expected: 0
    print("Total interest paid after reset:", tranche._interestPaid)      # Expected: 0
    print("Principal shortfalls after reset:", tranche._principalShortfalls)  # Expected: {}
    print("Interest shortfalls after reset:", tranche._interestShortfalls)  # Expected: {}

    # Additional tests for edge cases
    # Test making principal payment with no remaining notional
    tranche.increaseTimePeriod()
    tranche.makePrincipalPayment(amount_paid=200)  # Should be invalid or ignored
    print("Notional balance after invalid payment:", tranche.notionalBalance())  # Expected: -200 or similar

    try:
        tranche.makePrincipalPayment(amount_paid=100)
    except ValueError as e:
        print("Error on principal payment with no notional:", e)  # Expected error

    # Test making interest payment with no interest due
    try:
        tranche.makeInterestPayment(amount_paid=10)
    except ValueError as e:
        print("Error on interest payment with no interest due:", e)  # Expected error

    # Test manual shortfall handling
    tranche.increaseTimePeriod()
    tranche.makeInterestPayment(amount_paid=5)
    print("Interest shortfall after partial payment:", tranche._interestShortfalls)  # Expected: {3: 35}

if __name__ == '__main__':
    main()
