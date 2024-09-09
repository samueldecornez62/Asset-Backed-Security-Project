'''
Samuel Decornez
This module contains the Loan base class.
'''


'''========================================================================================================
Main Program:
This program will create the basic Loan class and create functions for monthly payments, 
total payments and total interest. 
Afterwards, this implements the recursive and formula-based computation of interest, principal and balance.
========================================================================================================'''

#Import required modules
import datetime
from functools import wraps
#We have both Loan and Asset classes. Import Asset class into here as it is needed
from asset_base import Asset
#Update loan class to log anytime an exception is thrown
import logging
# Configure lowest logging level to contain DEBUG, which is lowest level log we want to catch
logging.getLogger().setLevel(logging.INFO)
#Import random module
import random







#Create memoize decorator, might come in handy
def memoize(f):
    # This dict will memoize/cache the result for every unique set of parameter values args and kwargs
    memoize_dict = {}
    #Use wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        #Create some unique dictionary key for unique passed in arguments to function
        #Args is a tuple already, kwargs is a dictionary (so sort its keys then make tuple of sorted keys)
        # keys = kwargs.items()
        # sorted_keys = sorted(kwargs.items())
        # tuple_keys = tuple(sorted(kwargs.items()))

        key = (args, tuple(sorted(kwargs.items())))

        #If passed in key of inputs has not been memoized...
        if key not in memoize_dict:
            #... memoize the key and its value through function f
            memoize_dict[key] = f(*args, **kwargs)
        #Return the value of newly memoized value
        return memoize_dict[key]
    #Return wrapped function
    return wrapped




#Create the Loan base class
class Loan(object):
    #Define initalization function with inputs
    # Add asset parameter in input to __init__, and initialize it below
    def __init__(self, asset, face, rate, loanstart, loanend):
        #First, ensure input asset is Asset object
        #Note: asset is most basic level
        if not isinstance(asset, Asset):
            #Raise exception if it is not (and log the error beforehand)
            logging.error(f'Invalid Asset Type: {type(asset)}')
            #Adjusted from generic exception to Type error
            raise TypeError('Enter valid Asset Type')
            #Exit
        #In case of valid asset, do normal stuff
        else:
            # Initialize
            self._asset = asset
            self._face = face
            self._rate = rate
            #Initialize a default flag
            self._defaultFlag = None
            #Assume loan start and end are entered as YYYY-MM-DD; convert input to datetimes, to date
            self._loanstart = datetime.datetime.strptime(loanstart, '%Y-%m-%d').date()
            self._loanend = datetime.datetime.strptime(loanend, '%Y-%m-%d').date()
            logging.info(f'Loan created: Asset={asset}, Face={face}, Rate={rate}, Term={self.term()}')
            return

    #New term method, collects date difference between initialized date objects
    def term(self):
        days_difference = (self._loanend - self._loanstart).days
        #Assume a month is 30 days exactly, round to nearest whole term
        term = round(days_difference/30)
        return term


    #Create getter/setter property functions for above variables
    #getter/setter for asset
    @property
    def asset(self):
        return self._asset
    @asset.setter
    def asset(self, iasset):
        self._asset = iasset


    #getter/setter for face
    @property
    def face(self):
        return self._face
    @face.setter
    def face(self, iface):
        self._face = iface

    #getter/setter for rate
    @property
    def rate(self):
        return self._rate
    @rate.setter
    def rate(self, irate):
        self._rate = irate



    ...

    #Define rate method
    def rate(self, period):
        ##Debug messages
        logging.debug(f'Calling rate method for this loan.')
        # Should be overridden by derived classes
        raise NotImplementedError()

    # Implement formula to calculate monthly payment based on:
    # monthly interest rate, term of loan (period in months), principal
    #Define monthly payment with dummy period paramater; default it to None (change code later if given formula)
    def monthlyPmt(self, period):
        ### Class delegation; see calcMonthlyPmt lower in class
        logging.debug(f'Monthly payment calculated for period {period}.')

        #info logging for invalid period greater than term in months (recall term is entered in years)
        if period is not None and period > self.term():
            logging.info(f'Period {period} is greater than total loan term.')

        return Loan.calcMonthlyPmt(self._face, self.rate(period), self._loanstart, self._loanend)




    #Calculates total payments, no need for extra parameter since we assume it is taken care of in
    # monthlyPmt (assuming the monthly payment even depends on period)
    def totalPayments(self):
        #Total payments is this monthly payment (possibly dependent on period) for number of payments
        #Had to come back to edit this formula once variable rate dicts were added;
        # Note that for fixed rates this sums the value for the number of periods which yields same answer
        # Generator expression on such small numbers has no real processing speed downside
        total_payment = sum(self.monthlyPmt(period) for period in range(self.term()))
        logging.debug(f'Total Payment made calculated for this loan {total_payment}.')
        return total_payment


    #Now calculate the total interest on the loan
    def totalInterest(self):
        #Total interest is total payment minus principal
        #Call totalPayments function and subtract the principal, which is given
        total_interest = self.totalPayments() - self._face
        logging.debug(f'Total interest paid is {total_interest}.')
        return total_interest



    #Formula based solutions are grouped below
    #Interest amount due at a given period (in months) (formula)
    def interestDue_formula(self, period):
        ## Add extra info log for inpupt period greater than term - fits cleanest here in code logic
        if period > self.term():
            logging.info(f'Period {period} is greater than total loan term.')

        #Normal code
        #At time 0, no interest
        if period <= 0:
            logging.debug(f'Interest Due called at period 0. No payment made. ')
            logging.info(f'No payment made at period 0; return is a string.')
            return 'No payment made yet'
        #Else, compute formula
        else:
            #Convert to monthly rate as standard
            monthly_rate = Loan.monthlyRate(self.rate(period))
            logging.debug(f'Calculated monthly rate of {monthly_rate} for period {period}.')
            #Here, we can actually call balance_formula defined right below
            interest_due = monthly_rate * self.balance_formula(period-1)
            logging.debug(f'Interest due is {interest_due} at period {period}.')
            return interest_due

    #Principal amount due at a given period (formula)
    def principalDue_formula(self, period):
        #Info log for period too big
        if period > self.term():
            logging.info(f'Period {period} is greater than total loan term.')

        #Normal code
        #At time 0, no principal due
        if period <= 0:
            logging.debug(f'Principal Due called at period 0. No payment made. ')
            logging.info(f'No payment made at period 0; return is a string.')
            return 'No payment made yet'
        else:
            principal_due = self.monthlyPmt(period) - self.interestDue_formula(period)
            logging.debug(f'Principal due is {principal_due} at period {period}.')
            return principal_due

    #Balance of the loan at a given period (formula)
    def balance_formula(self, period):
        #Info log for period too big
        if period > self.term():
            logging.info(f'Period {period} is greater than total loan term.')
            return 0
        elif period < 0:
            raise ValueError(f'Negative period is invalid. Can not calculate balance_formula.')

        #Normal code
        #Class delegation; see calcBalance lower in class
        balance = Loan.calcBalance(self._face, self.rate(period), self._loanstart, self._loanend, period)
        logging.debug(f'Current balance at period {period} is {balance}.')
        return balance




    # Class-level method to calculate monthly payment based on face, rate and term
    #Use cls, not self, since we refer to class and not object
    @classmethod
    def calcMonthlyPmt(cls, face, rate, loanstart, loanend):
        logging.debug('Calling Monthly Payment calculator formula....')

        #Date
        days_difference = (loanend - loanstart).days
        # Assume a month is 30 days exactly, round to nearest whole term
        term = round(days_difference / 30)

        # Assume monthly rate is given as yearly rate in decimal form. Divide by 12 to make monthly rate
        monthly_rate = cls.monthlyRate(rate)
        logging.debug(f'Monthly rate is {monthly_rate}.')
        # Updated term from new methods
        num_payments = term
        ## Now apply formula in slides
        #Off chance of 0 interest rate for weird loan or some unforeseen circumstance
        if monthly_rate == 0:
            monthly_payment = face/term
        else:
            monthly_payment = (monthly_rate * face) / (1 - (1 + monthly_rate) ** (-num_payments))
        logging.debug(f'Monthly Payment is {monthly_payment}')
        logging.debug('...Finished calling Monthly Payment calculator formula.')
        return monthly_payment


    # Class-level to calculate remaining loan balance
    @classmethod
    def calcBalance(cls, face, rate, loanstart, loanend, period):
        # Date
        days_difference = (loanend - loanstart).days
        # Assume a month is 30 days exactly, round to nearest whole term
        term = round(days_difference / 30)
        #Convert to monthly rate
        monthly_rate = Loan.monthlyRate(rate)
        logging.debug(f'Collecting rate as {monthly_rate}. ')
        #Number of periods from year
        num_payments = term
        # Calculate the monthly payment, refer to class method
        monthly_payment = cls.calcMonthlyPmt(face, rate, loanstart, loanend)

        #Calculate balance
        if monthly_rate == 0: #Again handle 0 rate
            balance = face - (monthly_payment*period)
        else:
            balance = face * (1 + monthly_rate)**(period) - monthly_payment*((1 + monthly_rate)**(period) - 1)/monthly_rate
        logging.debug(f'Class-level method to calculate remaining loan balance returns {balance}. ')
        return balance



    #As instructed, this static-level method is created in Loan, but
    # Static does not need an initialization function (no member data). Also does not use self or cls.
    @staticmethod
    def monthlyRate(annual_rate):
        monthly_rate = annual_rate/12
        logging.debug(f'Converting annual rate {annual_rate} to monthly rate {monthly_rate}')
        return monthly_rate

    #Static method to convert monthly rate to annual rate
    @staticmethod
    def annualRate(monthly_rate):
        annual_rate = monthly_rate*12
        logging.debug(f'Converting monthly rate {monthly_rate} to annual rate {annual_rate}')
        return annual_rate



    #Create recovery value method; returns 60% of current asset value for given period
    def recoveryValue(self, period):
        #Info log for period too big
        if period > self.term():
            logging.info(f'Period {period} is greater than total loan term.')

        #Normal code
        #Call current value after depreciation; see asset_base.py
        # Depreciation accounted for by our methods
        current_value = self._asset.current_asset_value(period)
        recovery_value = current_value * 0.6
        logging.debug(f'Storing recovery value of asset at period {period} as {recovery_value}')
        return recovery_value



    #Create equity method; asset_value at current period, minus loan balance
    def equity(self, period):
        #Info log for period too big
        if period > self.term():
            logging.info(f'Period {period} is greater than total loan term.')

        #Normal code
        #Call current value, from asset class, and loan balance from this base class
        equity_amount = self._asset.current_asset_value(period) - self.balance_formula(period)
        logging.debug(f'Current equity amount at period {period} is {equity_amount}')
        return equity_amount




    #### =============== Part e ===============

    ##### Interest, Principal, Balance recursive definitions
    ### Recursive interest
    #Add memoize decorator (5.2.3)
    @memoize
    def interestDue_recursive(self, period):
        #Warn log to state that this is an inefficient method
        logging.warning('Recursive method is expected to take longer than formula based method. ')

        # At time 0, no interest
        if period <= 0:
            return 'No payment made yet'
        #Base case
        elif period == 1:
            #Convert to monthly rate, and use initial face value since this is first payment
            return Loan.monthlyRate(self._rate) * self._face
        else:
            return Loan.monthlyRate(self._rate) * self.balance_recursive(period - 1)

    ### Recursive principal
    @memoize
    def principalDue_recursive(self, period):
        #Warn log to state that this is an inefficient method
        logging.warning('Recursive method is expected to take longer than formula based method. ')

        # At time 0, no interest
        if period <= 0:
            return 'No payment made yet'
        return self.monthlyPmt() - self.interestDue_recursive(period)

    ### Recursive balance
    @memoize
    def balance_recursive(self, period):
        #Warn log to state that this is an inefficient method
        logging.warning('Recursive method is expected to take longer than formula based method. ')

        # At time 0, hard code balance to face
        if period <= 0:
            return float(self._face)
        #Create base case for recursion
        elif period == 1:
            return self._face - self.principalDue_recursive(period)
        else:
            return self.balance_recursive(period - 1) - self.principalDue_recursive(period)



    #This method returns probability of default for a loan for a given tmie period
    def default_probability(self, period):
        #Create a dictionary that stores the ranges of default probabilities
        #A dummy value is added as a bandaid to process payments with negative IRR
        #Need more research to determine how to handle this potential case
        default_dict = {-10:0.0003, 1:0.0005, 11:0.001, 60:0.002, 121:0.004, 181:0.002, 211:0.001}
        #For above dictionary: periods 1 through 10 have default chance 0.0005, periods 11 through 59 are 0.001, etc...
        try:
            #Loop through, sorting by decreasing key
            for key, value in sorted(default_dict.items(), key=lambda item: item[0], reverse=True):
                #Find first key threshold above the period
                #Similar to logic in basis point rating, but the boundary is on opposite side,
                # so sort reverse and reverse inequality
                if period > key:
                    default_prob = default_dict[key]
                    # break
                    return default_prob #Return default probability if try block executes successfully
        except ValueError as ex:
            print('Invalid Values.')
        except Exception as ex:
            print(f'Unknown error: {ex}')




    #This method takes a number. This method is called with the number in LoanPool method checkDefaults
    #Also pass in a period to handle recoveryValue method which requires it
    def checkDefault(self, number, period):
        #If we get 0 as the random int, of probability default probability
        if number == 0:
            #Then, flag loan as defaulted and return recovery value after setting balance to 0
            self.face = 0
            self.defaultFlag = 'Defaulted' #This will stay None, as initialized if not defaulted with tag number = 0
            logging.debug(f'Defaulted loan')
            return self.recoveryValue(period=period)
        #Else do nothing
        else:
            return 0







    #Other loan functions go here





