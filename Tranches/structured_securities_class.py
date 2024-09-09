'''
This is the StructuredSecurities class. This will be a composition of Tranche objects.
'''

#Import modules
import logging

from matplotlib.style.core import available

logging.getLogger().setLevel(logging.DEBUG)

#Import oother classes in case we need them
from base_tranche_class import Tranche
from standard_tranche_class import StandardTranche


#Create the class
class StructuredSecurities(object):
    #Create initialization function; this is not a derived class, rather a composition of Tranche objects
    #This composition is similar to how LoanPool is a composition of Loan objects (see loan folder)
    #Since we manually add tranches, this will be handled in addTranche method; not intiailized like loans
    def __init__(self, totalNotionalAmount):
        #Initialize variables
        self._totalNotionalAmount = totalNotionalAmount
        ## Any extra required variables added while creating methods go here
        #StructuredSecurities object internal list of tranches
        self._tranches = []
        #Initialize flag for tranche payout type, and list of possible flags
        self._flagValue = None
        self._possibleFlags = ['Sequential', 'Pro Rata']
        #Percent notional per tranche; built in addTranche method to help with Pro Rata method
        self._tranchePercentNotional = {}
        #Initialize a reserve account for leftover cash after payments
        self._reserveAccount = 0


    # Modifying class to be an iterable
    # Create the iter method
    def __iter__(self):
        # For every element of the loan pool, called through self._loans, do something
        for tranche in self._tranches:
            # Using yield instead of return treats this as a genrator
            yield tranche



    #Create method to add tranches StructuredSecurities object internal list of tranches
    #Until more classes are added to this project, always default the class to StandardTranche
    def addTranche(self, percent_notional, rate, subordination, tranche_class = StandardTranche):
        #Calculate tranche notional from percent notional
        added_tranche_notional = percent_notional * self._totalNotionalAmount
        #Add object; see relevant class for format (for now, always StandardTranche)
        added_tranche = tranche_class(notional=added_tranche_notional, rate=rate, subordination=subordination)
        #Appened created Tranche object to StructuredSecurities pool object's internal list
        self._tranches.append(added_tranche)
        #To help with Pro Rata payment implementation, store the percent notional of each tranche in a dict
        self._tranchePercentNotional[added_tranche] = percent_notional


    #Create a method to flag 'Sequential' or 'Pro Rata'
    #More payout methods can be implemented into this model; each time we add one the flag method must be updated
    def flag(self, mode):
        possible_modes = self._possibleFlags
        if mode not in possible_modes:
            raise ValueError(f'Selected mode must be in: {possible_modes}')
        else:
            #New flag variable; initialize in __init__ function
            self._flagValue = mode


    #Create a method to increase current time period of all tranches in StructuredSecurities object by 1 (default)
    def increaseTime(self, num_increases = 1):
        for tranche in self._tranches:
            #Call time increase method in StandardTranche class
            tranche.increaseTimePeriod(num_increases=num_increases)


    #Create a method that rolls out payments
    #Take a cash_amount parameter, and cycle in order of tranche subordination
    def makePayments(self, cash_amount):
        #Available funds to make payments
        available_funds = cash_amount + self._reserveAccount
        #Sort tranches by order of subordination using a lambda (sorted lexicographically - Python default)
        sorted_tranches = sorted(self._tranches, key = lambda tranche:tranche._subordination)

        ## Interest payments ===============================================================
        #Loop through sorted tranches; all payments geet deducted from available_funds
        for tranche in sorted_tranches:
            #First, do interest payments. Must ask tranche how much interest is owed
            #Use interestDue method, but also add any shortfall from prior period
            interest_owed = tranche.interestDue() + tranche._interestShortfallToPay.get(tranche._timePeriod, 0)
            #Make the payment using StandardTranche method
            #This method already handles shortfalls; must just make sure there are enough funds to make payment
            #Store this in payment tuple, which contains (amount_paid, shortfall)
            payment_tuple = tranche.makeInterestPayment(amount_paid=interest_owed)
            #Read first value of tuple, the amount paid, and subtract it from available funds
            available_funds -= payment_tuple[0]
            #Shortfall from this period must be added to next period
            #No index error since this is a dictionary. We will just get an extra value of unpaid interest
            # on lastperiod+1
            tranche._interestShortfallToPay[tranche._timePeriod+1] = (
                    tranche._interestShortfalls.get(tranche._timePeriod, 0) + payment_tuple[1]
                                                                    )
        ## Interest payments done ==========================================================



        ## Principal payments ===============================================================
        #Check if there is cash left over in avilable funds, and use this to make principal payments
        if available_funds <= 0:
            print(f'Out of cash. Unable to begin processing principal payments')
        #Else, cycle through subordination-sorted tranches to make principal payments
        else:
            #First though, need to check payment type flag to decide ehow to make payments
            #At this point it should be valid or flag method would have raised an error
            #Before breaking down by payment method, store total principal received amount
            principal_received = sum(tranche.notional for tranche in self._tranches)
            if self._flagValue == 'Sequential':
                for i, tranche in enumerate(sorted_tranches):
                    #Calculate payment due for this period + shortfall
                    principal_due = principal_received + tranche._principalShortfalls.get(i, 0)
                    #Principal payment for tranche
                    principal_payment = min(principal_due, available_funds, tranche.notionalBalance())
                    # Make payment
                    tranche.makePrincipalPayment(amount_paid=principal_payment)
                    #Update shortfall
                    shortfall_remaining = principal_due - principal_payment
                    tranche._principalShortfalls[i+1] = shortfall_remaining
                    #After making the payment, deduct from funds
                    available_funds -= principal_payment
                    #If any funds remain, go back through loop, else break
                    if available_funds <= 0:
                        print(f'Out of funds. Last payment to tranche {tranche} for period {tranche._timePeriod}. ')
                        # print(available_funds)
                        break

            #Now handale Pro Rata payout
            elif self._flagValue == 'Pro Rata':
                for tranche in sorted_tranches:
                    #Read percent notional of current tranche
                    percent_notional = self._tranchePercentNotional[tranche]
                    #Store index for easy calling
                    tranche_index = self._tranches.index(tranche)
                    #Calculate principal payment due for this period
                    principal_due = principal_received * percent_notional + tranche._principalShortfalls.get(tranche_index, 0)
                    #Calculate principal payment we can make
                    principal_payment = min(principal_due, available_funds, tranche.notionalBalance())
                    #Make the payment using Tranche type class
                    tranche.makePrincipalPayment(amount_paid=principal_payment)
                    #Update shortfall
                    shortfall_remaining = principal_due - principal_payment
                    #Update shortfall lists
                    tranche._principalShortfalls[tranche_index + 1] = shortfall_remaining
                    #Deduct from funds
                    available_funds -= principal_payment
                    #If funds remain, loop again else break
                    if available_funds <= 0:
                        print(f'Out of funds. Last payment to tranche {tranche} for period {tranche._timePeriod}. ')
                        # print(available_funds)
                        break
        ## Principal payments done ==========================================================

        #If cash is leftover, store it in the reserve account
        #For now, assume no interest is earned on the reserve account (pending implementation)
        #Override completely, not +=, since previous reserves (if there were any) contributed to cash_amount
        self._reserveAccount = available_funds

        #Return available funds (could be useful for future methods)
        #Main point is to register payments, which is done on function call without needing a return parameter
        return available_funds


    #Create a method that returns a list of lists
    #Each sublist is [Interest Due, Interest Paid, Interest Shortfall, Principal Paid, Balance]
    #One sublist for every tranche, in order of subordination
    #Using -1 as a flag for debugging and testing; this should default to 0 (no payment) after testing is done
    def getWaterfall(self, period):
        #Initialize empty list; we will append lists to it to create the list of lists
        return_list = []
        #Loop through tranches
        for tranche in self._tranches:
            ## Calculate parameters
            #Interest due at period, with shortfall
            interest_due = tranche.interestDue() + tranche._interestShortfallToPay.get(period, 0)
            #Interest paid, including shortfall
            interest_paid = tranche._interestPayments.get(period,0)
            #Shortfall contribution from this period
            interest_shortfall = tranche._interestShortfalls.get(period, 0)
            principal_paid = tranche._principalPayments.get(period, 0)
            balance = tranche.notionalBalance()
            tranche_list = [interest_due, interest_paid, interest_shortfall, principal_paid, balance]
            #Append this list to the list of lists to reteurn
            return_list.append(tranche_list)
        return return_list
