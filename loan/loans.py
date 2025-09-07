'''
Samuel Decornez
This module contains derived loan classes.
'''


'''========================================================================================================
Main Program:
This program defines Fixed vs Variable rates for the Loan base class.
========================================================================================================'''


# Import local packages
from loan.loan_base import Loan

class FixedRateLoan(Loan):
    def rate(self, period):
        # Override base Loan class to provide rate functionality
        # print('In the FixedRateLoan rate function')
        return self._rate


class VariableRateLoan(Loan):
    def __init__(self, asset, face, rateDict, term):
        self._rateDict = rateDict
        # Invoke superclass __init__ function
        super(VariableRateLoan, self).__init__(asset, face, None, term)

    ## Overriding rate function; overrides rate function in base Loan class (which currently raises NotImplementedError)
    # Again, periods are months, term is in years
    def rate(self, period):
        # Add code to find rate for given period from given rateDict
        # rateDict contains startPeriod as key, rate as value through next key, first key is always 0
        # print('In the VariableRateLoan rate function')
        if period is None:
            raise ValueError(f"None period is invalid")
        if period < 0:
            raise ValueError(f"Negative period is invalid")

        # Collect sorted list of keys; this will have all period where there is an interest rate change
        key_ranges = sorted(self._rateDict.keys())
        key = key_ranges[0]

        # Loop through sorted list of keys
        for start_period in key_ranges:
            # Keep updating value of "key" until the largest one less or equal to given period
            if start_period <= period:
                key = start_period
            # Break once exceeding key, and continue through loop
            else:
                break

        # Correct key should now be held but this is like a last check
        if key in self._rateDict:
            # Return appropriate rate
            return self._rateDict[key]
        else:
            raise ValueError(f"Invalid period/has no associated rate")