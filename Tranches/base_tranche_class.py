'''
This file creates the abstract Tranche class.
'''

#Import packages
import logging
import numpy as np
#Special numpy financial package -- required for IRR/DIRR
import numpy_financial as npf


#Create the base Tranche class (derived classes follow in other python files)


class Tranche(object):
    #Create initialization function
    def __init__(self, notional, rate, subordination):
        self._notional = notional
        self._rate = rate
        #Subordination handled in main functions where class is called
        #Default sorting is standard Python lexicographical sorting (digits --> UPPER --> lower)
        #Treated thoroughly in function calls or can override order if necessary
        self._subordination = subordination


    ###Create getter/setter property functions for above variables
    #Can come in handy if any manual adjustments are required

    # getter/setter for notional
    @property
    def notional(self):
        return self._notional

    @notional.setter
    def notional(self, inotional):
        self._notional = inotional

    # getter/setter for rate
    @property
    def rate(self):
        return self._rate

    @rate.setter
    def rate(self, irate):
        self._rate = irate

    # getter/setter for subordination
    @property
    def subordination(self):
        return self._subordination

    @subordination.setter
    def subordination(self, isubordination):
        self._subordination = isubordination




    ## Add some methods to calculate waterfall metrics

    #First, create the IRR method; simply use in-built numpy function
    def IRR(self, cash_flow_list):
        #Let this method take the ccash_flow_list as a parameter
        #Waterfall method must be updated to build this list from parameters already calculated from loanpool
        #First convert the list to a np array
        monthly_IRR = npf.irr([-self._notional] + cash_flow_list)
        #Return annualized value
        return monthly_IRR * 12


    #Create a method to calculate average life
    #Pass in a list of principal payments (in order by periods) to determine average life
    def AL(self, principalPaymentList):
        #If loan does not get paid down, AL is infinite
        if sum(principalPaymentList) < self._notional:
            logging.debug(f'AL is infinite. Return None type.')
            return None
        #Calculate average life
        else:
            #Calculate numerator of AL formula; divide by sum of payments in return
            numerator = sum(index * value for index, value in enumerate(principalPaymentList))
            #Return result
            return numerator/sum(principalPaymentList)

    #Create a method to calculate reduction in yield, DIRR
    #This invokes a different self method, and needs the same parameter
    def DIRR(self, cash_flow_list):
        #This is the tranche rate minus IRR
        dirr_value = self._rate - self.IRR(cash_flow_list=cash_flow_list)

        #DIRR specifies how much the investor has lost on, so it maxes at 100% + tranche rate
        max_val = 1.00 + self._rate
        #Log a awrning for unexpectedly large value
        if dirr_value > max_val:
            logging.error((f'Calculated DIRR {max_val} is larger than expected maximum {max_val}.'))
            #Not sure if it is better practice to return the maximum or the "incorrect"(?) excessive value
            # return max_val
        return dirr_value

    #Extra method to assign a rating based on the DIRR numerical value
    def DIRR_rating(self, dirr_value):
        #Create categories; only consider positive values, move down the category table (i.e. up in DIRR from 0)
        category_dict = {'Aaa': 0.06, 'Aa1': 0.67, 'Aa2': 1.3, 'Aa3': 2.7, 'A1': 5.2, 'A2': 8.9, 'A3': 13, 'Baa1': 19,
                         'Baa2': 27, 'Baa3': 46, 'Ba1': 72, 'Ba2': 106, 'Ba3': 143, 'B1': 183, 'B2': 231, 'B3': 311,
                         'Caa': 2500, 'Ca': 10000}
        rating = None  # Just initialize none; this should be updated correctly in fololwing loop since dirr_value must be %
        # Use lambda to sort by increasing dict value so we can move upwards in value to assign correct category
        for key, value in sorted(category_dict.items(), key=lambda item: item[1], reverse=False):
            # This finds the first value greater than dirr_BP for the threshold
            # Example: if value is 0.65 < 0.67 threshold
            if dirr_value < value:
                # Once we find the first value that is larger, break before rating can be reassigned
                # Example continued: associated key of 0.67 is Aa1, which is the correct rating assigned. Then break loop
                rating = key
                break

        #Return rating
        return rating