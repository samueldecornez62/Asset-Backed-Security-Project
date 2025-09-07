'''
This is the Standard Tranche class derived from base Tranche class.
'''

#Import modules
import logging
# logging.getLogger().setLevel(logging.DEBUG)


#Import base tranche
from Tranches.base_tranche_class import Tranche


#Create the derived Standard Tranche class
class StandardTranche(Tranche):
    # Initialization function
    # Use annual rate
    def __init__(self, notional, rate, subordination):
        super().__init__(notional, rate, subordination)

        # Initialize 0 time period at object instantiation; see increaseTimePeriod method
        self._timePeriod = 0

        # Initialize an object to track if Principal Payment has been made at this period already
        # Also a way to keep track of payments
        self._principalPayments = {}

        # Interest Payment tracker
        self._interestPayments = {}
        # Interest Shortfall tracker
        self._interestShortfall = {}

        # Excess payment trackers (excess is blocked, and stored here: only amount due is paid)
        self._principalExcess = {}
        self._interestExcess = {}



    # Method to increase time period of the object, default increase i 1
    # Pushes everything forward by num_increases periods
    def increaseTimePeriod(self, num_increases = 1):
        # No check for positive integer; assume user uses this correctly or might even want to subtract time
        # Default use of 1 period is the primary use anyway
        self._timePeriod += num_increases


    # Method to make principal payments
    def makePrincipalPayment(self, payment_amount):
        # Make sure payment has not yet been recorded
        if self._timePeriod in self._principalPayments:
            raise ValueError(f'Principal payment already recorded for (current) period {self._timePeriod}.')

        bal = self.notionalBalance()
        if bal == 0:
            raise ValueError(f'Notional balance is 0. Payment not accepted.')

        if payment_amount <= 0:
            raise ValueError(f'Principal payment must be positive.')

        amount_paid = min(payment_amount, bal)
        # excess = max(0, payment_amount - amount_paid)
        excess = payment_amount - amount_paid


        self._principalPayments[self._timePeriod] = amount_paid
        # self._principalExcess[self._timePeriod] = excess
        if excess > 0:
            self._principalExcess[self._timePeriod] = excess

        # Return statement if function needs amount paid
        return amount_paid


    def makeInterestPayment(self, payment_amount):
        # Make sure payment has not yet been recorded
        if self._timePeriod in self._interestPayments:
            raise ValueError(f'Interest payment already recorded for (current) period {self._timePeriod}.')

        due = self.interestDue()
        ## Cut this to allow 0 interest payments to be recorded as edge cases
        # if due == 0:
        #     raise ValueError('Interest due is 0. Payment not accepted.')
        if payment_amount < 0:
            raise ValueError(f'Interest payment must be positive.')

        amount_paid = min(payment_amount, due)
        shortfall = due - amount_paid

        self._interestPayments[self._timePeriod] = amount_paid
        self._interestShortfall[self._timePeriod] = shortfall

        # excess = max(0, payment_amount - amount_paid)
        excess = payment_amount - amount_paid
        if excess > 0:
            self._interestExcess[self._timePeriod] = excess

        # Return statement if function needs amount paid
        return amount_paid









    def notionalBalance(self, period = None):
        # Default to current period; useful for some other logic (i.e. see interestDue method below)
        if period == None:
            period = self._timePeriod
        # notionalBalance calculated as original notional minus cumulative principal
        # Interest shortfall not added to prevent compounding in calculations (working without compounding shortfall)
        cum_principal = sum(self._principalPayments.get(period,0) for period in range(1, 1 + period))

        ## Making shortfall NOT compound
        # cum_int_shortfall = sum(self._interestShortfall.get(period,0) for period in range(1, 1 + period))

        #Return notional balance at current time period
        return self._notional - cum_principal  #  + cum_int_shortfall

    def interestDue(self):
        ## Previous notional balance times rate; plus carry over prior shortfall
        prev_bal = self.notionalBalance(self._timePeriod - 1)
        monthly_rate = self._rate / 12

        prior_shortfall = self._interestShortfall.get(self._timePeriod - 1, 0)
        return prev_bal * monthly_rate + prior_shortfall




    # Useful for calling
    @property
    def timePeriod(self):
        return self._timePeriod

    @property
    def interestPayments(self):
        return self._interestPayments

    @property
    def interestShortfall(self):
        return self._interestShortfall

    @property
    def principalPayments(self):
        return self._principalPayments



    # Create a reset method to reset the entire Tranche
    def reset(self):
        self._timePeriod = 0
        self._principalPayments.clear()
        self._interestPayments.clear()
        self._interestShortfall.clear()
        self._principalExcess.clear()
        self._interestExcess.clear()





