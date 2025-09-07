'''
Samuel Decornez
This module contains the Loan pool class.
'''

import random

'''========================================================================================================
Main Program:
This program creates the LoanPool class. A LoanPool is a list of Loan objects, with loan group methods.
========================================================================================================'''


#We need to import the base loan class to use its functionality
from loan.loan_base import Loan
from loan.loans import FixedRateLoan, VariableRateLoan

#With Level 3 updates, import reduce
from functools import reduce


###Create the LoanPool class
class LoanPool(object):
    #Create initialization function; take some loans
    def __init__(self, loans):
        #Initialize variable
        self._loans = loans

    #Make the class an iterable
    def __iter__(self):
        return self._loans



    # Getter/setter properties
    @property
    def loans(self):
        return self._loans

    @loans.setter
    # Pass in a new list iloans of loans
    def loans(self, iloans):
        self._loans = iloans


    # Method to get the total loan principal from the pool of loans
    def totalLoanPrincipal(self):
        # Sum all face values
        return sum(loan.face for loan in self._loans)

    #Method to get the total loan balance for a given period
    def totalLoanBalance(self, period):
        #Sum balance_formula for all; call formula from base class
        return sum(loan.balance_formula(period) for loan in self._loans)


    ### Methods to get aggregate principal, interest, and total payment due in a given period

    # First, aggregate principal
    def aggregatePrincipal(self, period):
        return sum(loan.principalDue_formula(period) for loan in self._loans)

    def aggregateInterest(self, period):
        return sum(loan.interestDue_formula(period) for loan in self._loans)

    #Total payment due in given period
    def aggregatePayment(self, period):
        #Sum of principal and interest for each loan
        return self.aggregateInterest(period) + self.aggregatePrincipal(period)

        ## Only keep one, test both and see if it returns same
        #Alternatively, can calculate monthlyPmt of each one (both should be same)
        # return sum(Loan.monthlyPmt(period) for loan in self._loans)


    #Number of active loans (balance > 0 )
    def activeLoans(self, period):
        #Sum 1 means keep adding 1 if condition is met (condition is positive value)
        #Instead of 0, adding a tiny check because of some splicing issues
        return sum(1 for loan in self._loans if loan.balance_formula(period) > 1e-6)


    ## Formulas for Weighted Average Maturity (WAM) and Weighted Average Rate (WAR)

    # WAM method; uses term so is given in years, not months (which corresponds to periods)
    def WAM(self):
        # face_values = [loan.face for loan in self._loans]
        # term_values = [loan.term for loan in self._loans]
        # product = sum([a * b for a, b in zip(face_values, term_values)])
        product = sum(loan.face * loan.term for loan in self._loans)
        return product/self.totalLoanPrincipal()

    # WAR method
    # VariableRateLoans exist, default to 0 period which uses the first value throughout
    def WAR(self, period = 0):
        # face_values = [loan.face for loan in self._loans]
        # rate_values = [loan.rate(period) for loan in self._loans]
        # product = sum([a * b for a, b in zip(face_values, rate_values)])
        product = sum(loan.face * loan.rate(period) for loan in self._loans)
        return product/self.totalLoanPrincipal()

    # Method to calculate remaining WAM on surviving pools
    def WAM_remaining(self, period):
        numer = 0
        for loan in self._loans:
            remaining = max(loan.term * 12 - period, 0)
            numer += loan.face * remaining
        denom = self.totalLoanPrincipal()
        # Return, nback in years
        return (numer / denom / 12 if denom > 1e-6 else 0)