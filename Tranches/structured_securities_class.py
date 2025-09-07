'''
This is the StructuredSecurities class. This will be a composition of Tranche objects.
'''

#Import modules
import logging

from matplotlib.style.core import available

logging.getLogger().setLevel(logging.DEBUG)

#Import other classes in case we need them
from Tranches.base_tranche_class import Tranche
from Tranches.standard_tranche_class import StandardTranche



#Create the class
class StructuredSecurities(object):
    #Create initialization function; this is not a derived class, rather a composition of Tranche objects
    #This composition is similar to how LoanPool is a composition of Loan objects (see loan folder)
    #Since we manually add tranches, this will be handled in addTranche method; not intiailized like loans
    def __init__(self, total_notional_amount):
        #Initialize variables
        self._totalNotionalAmount = total_notional_amount
        # StructuredSecurities object internal list of tranches
        self._tranches = []

        ## Any extra required variables added while creating methods go here
        self._tranchePercentNotional = {}
        self._possibleFlags = ['Sequential', 'Pro Rata']
        self._flagValue = None
        self._reserveAccount = 0



    # Create method to add tranches StructuredSecurities object internal list of tranches, self._tranches
    # Until more classes are added to this project, always default the class to StandardTranche
    def addTranche(self, percent_notional, rate, subordination, tranche_class = StandardTranche):
        # Assign notional amount for specific tranche passed into this method
        added_tranche_notional = percent_notional * self._totalNotionalAmount
        # Add object; see relevant class for format (for now, always StandardTranche)
        added_tranche = tranche_class(notional=added_tranche_notional, rate=rate, subordination=subordination)
        # Append created Tranche object to StructuredSecurities pool object's internal list
        self._tranches.append(added_tranche)
        # To help with Pro Rata payment implementation, store the percent notional of each tranche in a dict (useful later)
        self._tranchePercentNotional[added_tranche] = percent_notional


    # Method to flag payment mode (for now, Sequential or Pro Rata)
    def setMode(self, mode):
        possible_modes = self._possibleFlags
        if mode not in possible_modes:
            raise ValueError(f'Selected payment mode must be in: {possible_modes}')
        else:
            # New flag variable; initialize in __init__ function
            self._flagValue = mode



    # Method to increase current time period for all tranches
    def increaseTime(self, num_increases = 1):
        for tranche in self._tranches:
            # Call time increase method in StandardTranche class
            tranche.increaseTimePeriod(num_increases=num_increases)

    def makePayments(self, cash_amount, principal_received):
        """
        Pay interest first (by seniority), then principal based on mode.
        Any leftover cash goes to the reserve account.
        """
        # 0) Include reserve exactly once, and don't double-count it later.
        available = float(cash_amount) + float(self._reserveAccount)
        self._reserveAccount = 0.0  # prevent geometric growth from adding it again at the end

        # 1) Order tranches by subordination (A senior to B). Adjust attr if yours is different.
        tranches_in_order = sorted(self._tranches, key=lambda t: t.subordination)

        # 2) Interest pass (single call per tranche)
        for tr in tranches_in_order:
            due = float(tr.interestDue())
            pay = min(due, available)
            tr.makeInterestPayment(pay)
            available -= pay
            # any unpaid interest becomes shortfall inside the tranche (your tranche class handles this)

        # 3) Principal pass (single call per tranche, no double loops)
        if getattr(self, "_flagValue", "Sequential") == "Sequential":
            # Pay down A fully, then B, etc., but cap by principal_received and cash available
            principal_left = float(principal_received)
            for tr in tranches_in_order:
                if principal_left <= 1e-9 or available <= 1e-9:
                    break
                bal = float(tr.notionalBalance())
                if bal <= 1e-9:
                    continue
                pay = min(bal, available, principal_left)
                if pay > 0:
                    tr.makePrincipalPayment(pay)  # exactly once per tranche per period
                    available -= pay
                    principal_left -= pay

        else:  # Pro Rata
            # Allocate by percent of notional among ACTIVE tranches, then pay each ONCE
            # Your code tracks percents in self._tranchePercentNotional[tr] (0.0–1.0)
            active = [tr for tr in tranches_in_order if float(tr.notionalBalance()) > 1e-9]
            total_pct = sum(self._tranchePercentNotional.get(tr, 0.0) for tr in active)
            if total_pct <= 0:
                total_pct = 1.0  # safety against divide-by-zero if everything is somehow 0

            for tr in active:
                if available <= 1e-9:
                    break
                bal = float(tr.notionalBalance())
                if bal <= 1e-9:
                    continue
                pct = self._tranchePercentNotional.get(tr, 0.0) / total_pct
                due = float(principal_received) * pct  # (no principal shortfall carry in your current design)
                pay = min(due, available, bal)
                if pay > 0:
                    tr.makePrincipalPayment(pay)  # exactly once per tranche per period
                    available -= pay

        # 4) Leftover goes to reserve (once)
        if available > 0:
            self._reserveAccount += available

    # ### OLDDDD (come back here if it all fails still)
    # # Makes payments for CURRENT TIME PERIOD; can be looped through term
    # def makePayments(self, cash_amount, principal_received):
    #     # Make incoming cash for current
    #     if self._flagValue is None:
    #         raise ValueError("Payment mode not set. Call setMode('Sequential') or setMode('Pro Rata'). ")
    #
    #     #Cash pot = new cash + reserve
    #     available_funds = cash_amount + self._reserveAccount
    #     principal_left = principal_received
    #
    #     # Seniority of tranche subordination: sort by ascending lexicographical standard
    #     tranches = sorted(self._tranches, key=lambda tr:tr.subordination)
    #
    #     ## Interest payments ===============================================================
    #     #Loop through sorted tranches; all payments geet deducted from available_funds
    #     for tr in tranches:
    #         if available_funds <= 0:
    #             break
    #         due = tr.interestDue()
    #         pay = min(due, available_funds) if due > 0 else 0
    #
    #         if pay > 0:
    #             paid = tr.makeInterestPayment(pay)
    #             available_funds -= paid
    #         else:
    #             # Even if nothing paid, record 0
    #             paid = tr.makeInterestPayment(0)
    #     ## Interest payments done ==========================================================
    #
    #     ## ==================================================================================
    #     ## Principal payments ===============================================================
    #     # Uses ONLY principal_received (not whole cash pot)
    #     # Still, cap by amount of cash left (can only pay with available_funds > 0 )
    #     if principal_left > 0 and available_funds > 0:
    #         if self._flagValue == 'Sequential':
    #             for tr in tranches:
    #                 if principal_left <= 0 or  available_funds <= 0:
    #                     break
    #
    #                 bal = tr.notionalBalance()
    #                 if bal <= 0:
    #                     continue
    #                 offer = min(bal, principal_left, available_funds)
    #                 if offer <= 0:
    #                     continue
    #                 paid = tr.makePrincipalPayment(offer)
    #                 principal_left -= paid
    #                 available_funds -= paid
    #         elif self._flagValue == 'Pro Rata':
    #             # Allocate by percent_notional
    #             # Read remaining tranches for positive notionalBalance
    #             remaining = {tr:tr.notionalBalance() for tr in tranches if tr.notionalBalance() > 0}
    #             # Active tranches that can still take principal
    #             active = {tr for tr in tranches if remaining.get(tr, 0) > 0}
    #
    #             # Continue distributions while there is cash and principal, and while tranches exist (not empty dict)
    #             while principal_left > 0 and available_funds > 0 and active:
    #                 # Sum of original percent_notional for active tranches
    #                 percent_sum = sum(self._tranchePercentNotional[tr] for tr in active)
    #                 if percent_sum <= 0:
    #                     break
    #
    #                 progressed = False
    #                 for tr in list(active): # copy to allow mutation
    #                     if principal_left <= 0 or available_funds <= 0:
    #                         break
    #                     bal = remaining.get(tr, 0)
    #                     if bal <= 0:
    #                         active.discard(tr)
    #                         continue
    #
    #                     share = (self._tranchePercentNotional[tr] / percent_sum) * principal_left
    #                     offer = min(bal, share, available_funds)
    #                     if offer <= 0:
    #                         continue
    #
    #                     paid = tr.makePrincipalPayment(offer)
    #                     principal_left -= paid
    #                     available_funds -= paid
    #                     remaining[tr] = bal - paid
    #                     if remaining[tr] <= 0:
    #                         active.discard(tr)
    #                     progressed = True
    #
    #                 if not progressed:
    #                     # Nothing moved this pass (small residuals); kill to avoid loop
    #                     break
    #
    #         # Last flag
    #         else:
    #             raise ValueError(f'Unknown payment mode: {self._flagValue}')
    #
    #     ## Principal payments done ==========================================================
    #     ## ==================================================================================
    #
    #     # Send leftover cash to reserve account
    #     self._reserveAccount += available_funds



    # Create a method that returns a list of lists
    # Pulls all the actual recorded payments from tranche dictionaries that were loaded in at each period
    # Returns a list of lists, one per tranche, in subordination order:
    # [Interest Due, Interest Paid, Interest Shortfall, Principal Paid, Balance]
    def getWaterfall(self, period = None):
        rows = []

        # Sort tranches by subordination
        sorted_tranches = sorted(self._tranches, key=lambda tr:tr.subordination)

        # For each tranche; create the waterfall (they will be printed side by size on period tp)
        for tr in sorted_tranches:
            # Set period
            tp = tr._timePeriod if period is None else int(period)

            # Read the easier waterfall values that are already stored
            interest_paid = tr.interestPayments.get(tp, 0.0)
            interest_shortfall = tr.interestShortfall.get(tp, 0.0)
            principal_paid = tr.principalPayments.get(tp, 0.0)

            # Interest due; waterfall calls timeperiod properly, but this handles manual waterfall retrievals for the curious
            if period is None or tp == tr._timePeriod:
                interest_due = tr.interestDue()
            else:
                interest_due = interest_paid + interest_shortfall

            # Balance at period
            bal = tr.notionalBalance(tp)

            # Combine into the waterfall list
            rows.append([interest_due, interest_paid, interest_shortfall, principal_paid, bal])

        return rows










    ##### BAD VERSION, old one before debug on 8/18
    # def getWaterfall(self):
    #     # Initialize empty list; we will append lists to it to create the list of lists
    #     rows = []
    #
    #     # Sort
    #     sorted_tranches = sorted(self._tranches, key=lambda tr: tr.subordination)
    #
    #     # Loop through tranches
    #     for tranche in sorted_tranches:
    #         tp = tranche._timePeriod #Reads current time period tp of tranche
    #
    #         # Read from dictionaries
    #         interest_due = tranche.interestDue()
    #         interest_paid = tranche.interestPayments.get(tp, 0)
    #         interest_shortfall = tranche.interestShortfall.get(tp, 0)
    #         principal_paid = tranche.principalPayments.get(tp, 0)
    #         balance = tranche.notionalBalance()
    #
    #         # Combine into the list
    #         rows.append([interest_due, interest_paid, interest_shortfall, principal_paid, balance])
    #
    #
    #     return rows









    # To be ignored or archived, deleted later even
    # def badMakePayments(self, cash_amount):
    #     # Available funds to make payments
    #     available_funds = cash_amount + self._reserveAccount
    #     # Sort tranches by order of subordination using a lambda (sorted lexicographically - Python default)
    #     sorted_tranches = sorted(self._tranches, key = lambda tranche:tranche.subordination)
    #
    #
    #     ## Interest payments ===============================================================
    #     #Loop through sorted tranches; all payments geet deducted from available_funds
    #     for tranche in sorted_tranches:
    #         pass
    #     ## Interest payments done ==========================================================
    #
    #
    #     ## Principal payments ===============================================================
    #     #Check if there is cash left over in available funds, and use this to make principal payments
    #     if available_funds <= 0:
    #         print(f'Out of cash. Unable to begin processing principal payments')
    #     #Else, cycle through subordination-sorted tranches to make principal payments
    #     else:
    #         #First though, need to check payment type flag to decide ehow to make payments
    #         #At this point it should be valid or flag method would have raised an error
    #         #Before breaking down by payment method, store total principal received amount
    #         principal_received = sum(tranche.notional for tranche in self._tranches)
    #         if self._flagValue == 'Sequential':
    #             pass
    #
    #         #Now handle Pro Rata payout
    #         elif self._flagValue == 'Pro Rata':
    #             for tranche in sorted_tranches:
    #                 pass
    #     ## Principal payments done ==========================================================
    #
    #
    #     self._reserveAccount += available_funds