'''
Samuel Decornez
This module contains the loan base class.
'''
import logging

from loan.asset_base import Asset

from functools import wraps


'''========================================================================================================
Main Program:
This program contains the base Loan class. 
Multiple types of loans will be derived from this class with their own specific functionality.
========================================================================================================'''



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


# Create the Loan base class
class Loan(object):
    # Define initialization function with required Loan inputs
    # Added asset parameter with further class development
    # Assuming given rate in Loan initialization is annual rate, and term is given in years
    def __init__(self, asset, face, rate, term):
        # First, ensure that the passed asset parameters is in fact an Asset object
        # Note: an Asset object is the most basic level; derived version are included
        if not isinstance(asset, Asset):
            # Raise exception for incorrect Asset type and log error beforehand
            logging.error(f'Invalid Asset Type: {type(asset)}')
            # Adjusted from generic exception to Type error
            # print(f'Enter Valid Asset Type')
            raise TypeError(f'Invalid Asset Type: asset must be an instance of Asset or any of its subclasses')
            # Exits function

        else:
            self._asset = asset
            self._face = face
            self._rate = rate
            self._term = term
            logging.info(f'Loan created: Asset={asset}, Face={face}, Rate={rate}, Term={self.term}')
            # return







    # Getter and Setter properties for adjusting defined Loan object parameters
    # =========================================================================
    # =========================================================================
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
    def annual_rate(self):
        return self._rate
    @annual_rate.setter
    def rate(self, value):
        self._rate = value

    @property
    def term(self):
        return self._term

    @term.setter
    def term(self, iterm):
        self._term = iterm
    # =========================================================================
    # =========================================================================




    ## Rate function that delegates to derived subclasses
    def rate(self, period):
        # Overriden by derived classes (see loans.py)
        raise NotImplementedError()


    ## Function that returns monthlyPayment, amount paid for given period (currently constant)
    # Define dummy None for period; current formula has no period-dependent monthly payment
    def monthlyPayment(self, period = None):
        # Class-level method delegation; also use rate methods for Fixed or Variable
        rate_to_use = self.rate(period if period is not None else 0)
        return Loan.calcMonthlyPmt(self._face, rate_to_use, self._term)



        # # Old version -- before class delegation
        # # Convert annual rate to monthly rate, and term in years to number of months
        # monthly_rate = self._rate/12
        # num_payments = self._term * 12
        # # Apply formula after conversion
        # pmt = (monthly_rate * self._face) / (1 - (1+monthly_rate)**(-num_payments))
        # return pmt



    ## Calculates total payments of the entire Loan; principal + interest
    def totalPayments(self):
        # Sum of each of the monthly payments throughout the life of the loan
        # Counts period 1 through N, for N the final term in months --> must convert term in years to months
        total_payment = sum(self.monthlyPayment(period) for period in range(1, 1 + int(self._term * 12)))
        return total_payment

    ## Calculates total interest paid over life of the entire loan, given that totalPayments = face + totalInterest
    def totalInterest(self):
        return self.totalPayments() - self._face



    ## Calculates interest due at given period
    def interestDue_formula(self, period):
        annual_rate = self.rate(period)
        monthly_rate = Loan.monthlyRate(annual_rate)
        # No interest due at period 0:
        if period == 0:
            # Return 0 value for interest due at time loan is taken out
            return 0
        # Call previous period's balance; balance exists at period 0 and is equal to face
        interest_due = monthly_rate * self.balance_formula(period-1)
        return interest_due

    ## Calculates principal payment due at given period
    def principalDue_formula(self, period):
        # Principal due calculated as monthly payment minus the interest due
        principal_due = self.monthlyPayment(period) - self.interestDue_formula(period)
        return principal_due

    ## Calculates remaining balance at given period using annuity  formula
    def balance_formula(self, period):
        annual_rate = self.rate(period)
        return Loan.calcBalance(self._face, annual_rate, self._term, period)
        # # Rate conversion, and payments made up to this period (not inclusive)
        # monthly_rate = self._rate/12
        # # Assuming constant monthly payment
        # balance = self._face * (1 + monthly_rate)**period - self.monthlyPayment()*( ((1+monthly_rate)**period - 1)/(monthly_rate) )
        # return balance



    # Class-level method to calculate monthly payment based on face, rate and term
    # Use cls, not self, since we refer to class and not object
    # Annual rate, term in years
    @classmethod
    def calcMonthlyPmt(cls, face, rate, term):
        # Convert annual rate to monthly rate, and term in years to number of months
        monthly_rate = Loan.monthlyRate(rate)
        num_payments = term * 12
        # Off chance of 0 interest rate for weird loan or some unforeseen circumstance
        if monthly_rate == 0:
            monthly_payment = face / term
        # Else, apply formula
        else:
            monthly_payment = (monthly_rate * face) / (1 - (1 + monthly_rate) ** (-num_payments))
        return monthly_payment

    # Class-level method to calcualte remaining loan balance
    @classmethod
    def calcBalance(cls, face, rate, term, period):
        monthly_rate = Loan.monthlyRate(rate)
        num_payments = term * 12
        # Monthly payment, refer to class method
        monthly_payment = Loan.calcMonthlyPmt(face, rate, term)

        # Calculate balance
        if monthly_rate == 0:  # Again handle 0 rate
            balance = face - (monthly_payment * period)
        else:
            balance = face * (1 + monthly_rate) ** (period) - monthly_payment * (
                        (1 + monthly_rate) ** (period) - 1) / monthly_rate
        return balance


    ## Static methods to convert between rates more easily
    # Static does not need an initialization function (no member data). Also does not use self or cls.
    @staticmethod
    def monthlyRate(annual_rate):
        monthly_rate = annual_rate / 12
        # logging.debug(f'Converting annual rate {annual_rate} to monthly rate {monthly_rate}')
        return monthly_rate

    # Static method to convert monthly rate to annual rate
    @staticmethod
    def annualRate(monthly_rate):
        annual_rate = monthly_rate * 12
        # logging.debug(f'Converting monthly rate {monthly_rate} to annual rate {annual_rate}')
        return annual_rate



    # Create recoveryValue method; returns 60% of current asset value for given period
    def recoveryValue(self, period):
        # Info log for period exceeding term
        if period > self.term * 12:
            logging.info(f'Period {period} is greater than total loan term')

        # Normal code
        # Depreciation accounted for by other methods
        current_value = self._asset.currentAssetValue(period)
        recovery_value = 0.6 * current_value
        logging.debug(f'Storing recovery value of asset at period {period} as {recovery_value}')
        return recovery_value

    # Create equity method; asset value minus the loan balance
    def equity(self, period):
        # Info log for period exceeding term
        if period > self.term * 12:
            logging.info(f'Period {period} is greater than total loan term')

        # Normal code
        # Call current value, from asset class, and loan balance from this base class
        equity_amount = self._asset.currentAssetValue(period) - self.balance_formula(period)
        logging.debug(f'Current equity amount at period {period} is {equity_amount}')
        return equity_amount







    ## Implements recursive versions of earlier formulas for interest due, principal due, and balance;
    ## Only one set of three is needed, recursive set becomes more time intensive as term increases
    @memoize
    def interestDue_recursive(self, period):
        # Base case for recursion
        if period == 0:
            return 0
        # Convert to monthly rate
        monthly_rate = self._rate/12
        return monthly_rate * self.balance_recursive(period-1)

    @memoize
    def principalDue_recursive(self, period):
        return self.monthlyPayment(period) - self.interestDue_recursive(period)

    @memoize
    def balance_recursive(self, period):
        # Base case; plus handles invalid negative inputs
        if period <= 0:
            return self._face
        # Remaining cases
        else:
            return self.balance_recursive(period - 1) - self.principalDue_recursive(period)