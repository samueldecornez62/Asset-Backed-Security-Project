'''
Samuel Decornez
This module contains the Loan pool class.
'''
import random

'''========================================================================================================
Main Program:
This program will create the LoanPool class.
========================================================================================================'''


#We need to import the base loan class to use its functionality
from loan_base import Loan
from loans import FixedRateLoan, VariableRateLoan

#With Level 3 updates, import reduce
from functools import reduce


###Create the LoanPool class
class LoanPool(object):
    #Create initialization function; take some loans
    def __init__(self, loans):
        #Initialize variable
        self._loans = loans

    #Modifying class to be an iterable
    #Create the iter method
    def __iter__(self):
        #For every element of the loan pool, called through self._loans, do something
        for loan in self._loans:
            #Using yield instead of return treats this as a genrator
            yield loan



    #Getter setter properties
    @property
    def loans(self):
        return self._loans

    @loans.setter
    def loans(self, iloans):
        self._loans = iloans



    #Method to get total loan principal
    def total_loan_principal(self):
        #Sum face for all
        return sum(loan.face for loan in self._loans)


    #Method to get the total loan balance for a given period
    def total_loan_balance(self, period):
        #Sum balance_formula for all; call formula from base class
        return sum(loan.balance_formula(period) for loan in self._loans)


    ### Methods to get aggregate principal, interest and total payment due in gievn period

    #First, aggregate principal
    def aggregate_principal(self, period):
        #Sum principalDue_formula for all; call formula from base class
        #Note: in base class, we return a no payment string for period 0.
        # To get around this error when looping through loans, make sure we are reading a number into the sum
        #Check this with isinstance
        return sum(loan.principalDue_formula(period) for loan in self._loans if isinstance(loan.principalDue_formula(period), (int, float)))

    #Second, aggregate interest
    def aggregate_interest(self, period):
        #Note: in base class, we return a string that no payment is made. Hard code period = 0 to deal with it
        #Sum interestDue_formula
        return sum(loan.interestDue_formula(period) for loan in self._loans if isinstance(loan.interestDue_formula(period), (int, float)))

    #Total payment due in given period
    def aggregate_payment(self, period):
        #Sum of principal and interest for each loan
        return self.aggregate_interest(period) + self.aggregate_principal(period)

        ## Only keep one, test both and see if it returns same
        #Alternatively, can calculate monthlyPmt of each one (both should be same)
        # return sum(Loan.monthlyPmt(period) for loan in self._loans)



    #Number of active loans (balance > 0 )
    def active_loans(self):
        #Sum 1 means keep adding 1 if condition is met (condition is positive value)
        return sum(1 for loan in self._loans if loan.balance_formula(0) > 0)


    ### Weighted Average Maturity (WAM) and Weighted Average Rate (WAR)

    ### Now update WAM. Requires regular_func function. Use self parameter since we are now in class
    def regular_func(self, total_sum, mortgage_tuple):
        # Returns product of amount and term based on given tuple format
        return total_sum + mortgage_tuple[0] * mortgage_tuple[2]

    #Create WAM method. Recall that we initialize the loans, each one with given amount, rate, term.
    # For each loan in self.loans, we can call loan.face, loan.rate, loan.term
    # Term is in years from Level 2, so convert to months here. Code will print as months as seen in 3.1.2_main.py
    def WAM(self):
        #Convert the loans into a list of tuples to maintain format
        mortgage_list = [(loan.face, loan.rate(), loan.term) for loan in self._loans]
        #Now that we have mortgage_list, rest of code can be copied from 3.1.2_main.py,
        # except we must call regular_func by self as a class method
        weighted_sum = reduce(self.regular_func, mortgage_list, 0)
        total_amount = sum(mortgage_tuple[0] for mortgage_tuple in mortgage_list)
        return weighted_sum / total_amount



    #For WAR: same except rate instead of term
    def WAR(self):
        #WAR function uses lambda. Reduce already imported.
        #First, as above:
        mortgage_list = [(loan.face, loan.rate(), loan.term) for loan in self._loans]

        # Now define the lambda and copy code in 3.1.2_main.py as in updated WAM function
        lambda_func = lambda total_sum, new_tuple: total_sum + new_tuple[0] * new_tuple[1]
        weighted_sum = reduce(lambda_func, mortgage_list, 0)
        total_amount = sum(mortgage_tuple[0] for mortgage_tuple in mortgage_list)
        return weighted_sum / total_amount



    #Generate random int for each loan. Assume we treat all loans on same, given time period
    #This time period determines range of random integer (starting from 0)
    def checkDefaults(self, period):
        #Get default probability from Loan base class; since it is only based on period, it is fixed here
        #Can read 0th index; we only care about period parameter here so any loan will do
        default_prob = self._loans[0].default_probability(period=period)
        #To make the uniform randint have equal probability of all integers, at probability default prob,
        # we set the range to the reciprocal of default probability
        #We will round the value of this reciprocal, but note that it makes no difference with used table since
        # all the reciprocals of given default probabilites return whole integers
        the_range = int(round(1/default_prob)) #Ensure we get an int

        #Now genereate teh random integers
        #Set to the_range-1 since we start range at 0, which is a possible value
        random_list = [random.randint(0,the_range-1) for loan in self._loans]
        #randint gives uniform random integer in specified range


        #Now, pass this random number into checkDefault in loan base class. Store values in a list as well
        checkedDefaultList = [self._loans[0].checkDefault(number=i, period=period) for i in random_list]

        #We want to also aggregate the recovery values of individual loans, and return it when called in doWaterfall
        #From Loan base method checkDefault: return recovery value for defaulted loans, else return 0. So:
        total_recovery = sum(checkedDefaultList)
        return total_recovery #This returns total recovery value of defaulted loans in the loan pool
        #Now, calling checkDefaults(period) on a loan pool returns the total recovery of defaulted loans in said period


