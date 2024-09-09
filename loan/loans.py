'''
Samuel Decornez
This module contains derived Loan classes.
'''

#Import loan base class
from loan_base import Loan

#Import logging
import logging
logging.getLogger().setLevel(logging.INFO)



#FixedRateLoan class, deriving from Loan base class
class FixedRateLoan(Loan):
    def rate(self, period):
        #Overrides base class
        #Also, these print statements were initially put in track the rate calling
        #We can update these with debug logs, which are not captured by our lowest setting being INFO
        logging.debug('In the FixedRateLoan rate function')
        return self._rate


#VariableRateLoan class, deriving from Loan base class
class VariableRateLoan(Loan):
    #Update the initialization function given Loan base class changes
    def __init__(self, asset, face, rateDict, loanstart, loanend):
        #Invoke superclass __init__ function
        super(VariableRateLoan, self).__init__(asset, face, None, loanstart, loanend)
        #Sets _rateDict attribute on self object
        self._rateDict = rateDict

    def rate(self, period):
        #Some error checking
        logging.debug(f'Rate function called with period: {period}')
        if period is None:
            raise ValueError('None period is invalid.')
        #Write code to return rate regardless of input period
        # Assume rateDict is given, defined in __init__ above

        #Collect sorted list of keys; this will have all period where there is an interest rate change
        key_ranges = sorted(list(self._rateDict.keys()))

        #Iinitialize first key value to the first rate of the dict
        key = key_ranges[0]
        #Loop through the sorted list of keys; these keys correspond to
        for i in key_ranges:
            #Keep updating value of "key" until the largest one less or equal to given period
            if i <= period:
                #Returns largest index smaller or equal to period
                key = i
        #The above loop finds the rate of the given period, based on a rate dictionary.
        # and re-described above at start of function


        #Throw error for negative period input, which means key is still kept at None and was never updated
        if key in self._rateDict:
            # Return the appropriate rate
            logging.debug('In the VariableRateLoan rate function')
            return self._rateDict[key]

        #Else no valid rate found
        else:
            raise ValueError('Invalid period/has no associated rate.')







