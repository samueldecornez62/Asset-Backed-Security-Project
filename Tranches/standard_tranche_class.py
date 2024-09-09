'''
This is the Standard Tranche class derived from base Tranche class.
'''

#Import modules
import logging
logging.getLogger().setLevel(logging.DEBUG)


#Import base tranche
from Tranches.base_tranche_class import Tranche


#Create the derived Standard Tranche class
class StandardTranche(Tranche):
    #Initialization function
    def __init__(self, notional, rate, subordination):
        #Invoke superclass of Tranche base; it already initializes notional, rate and subordination
        super().__init__(notional, rate, subordination)
        ## Initialize any supplemental parameters we define in future methods
        #Time period; add to this in a method
        self._timePeriod = 0
        #----------------------------------------------------------------------------------------------------
        ## Tranche must keep track of all interest/principal payments; use dictionary to track periods as key
        #Store payments (key = period, value = payment)
        self._principalPayments = {}
        self._interestPayments = {}
        #Store total payments to avoid having to sum through dictionaries repeatedly
        self._principalPaid = 0
        self._interestPaid = 0
        #Store shortfalls (key = period, value = shortfall)
        self._principalShortfalls = {}
        self._interestShortfalls = {}
        #Shortfalls can carry over; the above dict holds shortfall contribution per period
        # This one is shortfall to pay at any period (which includes carry over)
        self._interestShortfallToPay = {}
        self._principalShortfallToPay = {} #This is mainly for tranche payout in makePayments method
        #----------------------------------------------------------------------------------------------------



    #Create a method to increase the time period of current StandardTranche object
    # Defaults to 1; variable is included in case we must jump multiple periods for whatever raeson
    def increaseTimePeriod(self, num_increases = 1):
        #No check for positive integer; assume user uses this correctly or might even want to subtract time
        #Default use of 1 period is the primary use anyways
        self._timePeriod += num_increases


    #Principal Payment method
    def makePrincipalPayment(self, amount_paid, period = None):
        #In case we want to read balance at any period, we default it to None and set to current time period
        #This way, it can be called purely as self method on current time period as its default input
        if period == None:
            period = self._timePeriod
        #If current notional balance is 0, reject payment
        if self.notionalBalance() <= 0:
            logging.warning(f'Notional balance is 0: principal payment rejected for tranche {self}.')
            # raise ValueError(f'Notional balance is 0: payment rejected.')
            return (0, 'Notional balance 0')
        #Can only record a payment once per period; so reject payment if the dictionary has a value at key
        elif period in self._principalPayments:
            logging.warning(f'Principal payment already recorded for period {self._timePeriod} for tranche {self}.')
            # raise ValueError(f'Principal payment already recorded for (current) period {self._timePeriod}.')
            return (0, 'Principal already recorded')
        #If no payment recorded for this period yet, record it in this Tranche object's dictionary
        else:
            #Record principal payment
            self._principalPayments[period] = amount_paid
            #Add to total principal payment value of tranche
            self._principalPaid += amount_paid


    #Interest Payment method
    def makeInterestPayment(self, amount_paid, period = None):
        #Default to current period
        if period == None:
            period = self._timePeriod
        #If current interest due is 0, reject payment (method to calculate this follows)
        interest_due = self.interestDue()
        if interest_due == 0:
            logging.warning(f'Interest due is 0: payment rejected for tranche {self} in period {period}.')
            # raise ValueError(f'Interest due is 0: payment rejected.')
            return (0, 'Interest due 0')
        #Can only record a payment once per period; so reject payment if the dictionary has a value at key
        elif period in self._interestPayments:
            logging.warning(f'Interest payment already recorded for period {period} for tranche {self}.')
            # raise ValueError(f'Interest payment already recorded for (current) period {period}.')
            return (0, 'Interest already recorded')
        #If no payment recorded for this period yet, record it in this Tranche object's dictionary
        #Note: if amount paid is less than amount due, pay what you can, and record difference as shortfall
        else:
            #Record the amount being paid
            self._interestPayments[period] = amount_paid
            #Add to total interest payment value of tranche
            self._interestPaid += amount_paid
            #Calculate shortfall; if it exists it is positive, else set it to 0
            shortfall = max(0, interest_due - amount_paid)
            #Cumulative shortfall dictionary may contain a value (see later files)
            #So, use .get function to ensure we add shortfall (if it exists), else add nothing
            self._interestShortfalls[period] = shortfall
            self._interestShortfallToPay[period] = (self._interestShortfalls.get(period, 0) + shortfall)
            #Return amount paid, and shortfall as a tuple
            return (amount_paid, shortfall)


    #Create a method to calculate the notional balance (amount still owed to tranche) for current time period
    #This returns amount owed after payments of input period, defaults to current time period
    def notionalBalance(self, period = None):
        #Handle period; default to current
        if period == None:
            period = self._timePeriod
        #At period 0, balance is initial balance
        if period == 0:
            balance = self._notional
        else:
            ## Can calculate this as original notional, minus all principal payments so far, plus any shortfalls
            #Principal payments up to and including current time period
            principal_so_far = sum(value for key, value in self._principalPayments.items() if key <= period)
            # Interest shortfalls up to and including current time period
            int_shortfalls_so_far = sum(value for key, value in self._interestShortfalls.items() if key <= period)
            #Calculate and return the balance from this method
            balance = self._notional - principal_so_far + int_shortfalls_so_far
        return balance



    #Create a method to return amount of interest due at a period, default to current period
    def interestDue(self, period = None):
        if period == None:
            period = self._timePeriod
        #Manually handle first period
        if period == 0:
            logging.debug(f'Period 0: no interest due.')
            return 0
        try:
            previous_balance = self.notionalBalance(period=period-1)
            #Multiply previous balance by interest rate to get interest due
            interest_due = previous_balance * self.rate
            return interest_due
        except Exception as ex:
            logging.error(f'Error occurred computing interest for period {period}: {ex}')
            # raise Exception(f'Unknown error: {ex}')
            return 0

    #Create a method to reset the tranche to its original state (time 0)
    def reset(self):
        #Set time back to 0 and clear dictionaries/values
        self._timePeriod = 0
        self._principalPayments.clear()
        self._interestPayments.clear()
        self._principalPaid = 0
        self._interestPaid = 0
        self._principalShortfalls.clear()
        self._interestShortfalls.clear()
        self._interestShortfallToPay.clear()


