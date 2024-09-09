'''
Samuel Decornez
This module contains classes related to Mortgages.
'''


#Import the derived classes that will be called
from loans import VariableRateLoan, FixedRateLoan

#Import House Base class to initialize home , and derived classes being used
from house_base import HouseBase
from house_derived_classes import VacationHome, PrimaryHome

#Import Car
from car_class import Car

#Update loan class to log anytime an exception is thrown
import logging
# Configure lowest logging level to contain ERROR, which is what we are trying to throw
logging.getLogger().setLevel(logging.ERROR)



class MortgageMixin(object):
    # Add asset parameter in input to __init__, and initialize it below
    def __init__(self, face, rate = None, term = None, home = None):
        #MortgageMixin.__init__(self)
        super(MortgageMixin, self).__init__(face, rate, term)
        if not isinstance(home, HouseBase):
            logging.error(f'Invalid asset type {type(home)}. Enter valid house asset type.')
            raise Exception('Enter valid Asset Type')
        #Initialize new variable
        self._home = home

        # First, ensure input asset is Asset object
        #Note: HouseBase is most basic after Asset; any derived version of HouseBase will count here
        if not isinstance(home, HouseBase):
            # Print error message if it is not, after logging error
            logging.error(f'Invalid asset type {type(home)}. Enter valid house asset type.')
            raise Exception('Enter valid Asset Type')
            # Exit
        else:
            return




    #Mortgage-specific functionality goes here
    def PMI(self, period):
        #Mortgage-specific functions and code go here

        #Loan >= 80%  asset value means pay PMI
        #So loan/asset = LTV >= 0.8  means pay PMI
        #Here, assume initial loan = 100% asset value (which is >= 80% asset value, so always pay PMI)

        #Calculate LTV = loan/value ratio; call initial_value from base Asset
        LTV = (self._face) / self._home.initial_value

        #From above logic in commenting, if loan covers more than 80% of asset value
        if LTV >= 0.8:
            #0.0075% is 0.000075 as a decimal; return this multiplied by face value
            return 0.000075 * self._face
        #Else, no PMI and return 0
        else:
            return 0



    #Above code calculates PMI. Next, override Loan base class functions:
    # monthlyPMT(self, period),
    # and principalDue_formula(self, period)

    #Override monthlyPMT
    def monthlyPmt(self, period = None):
        base_payment = super(MortgageMixin, self).monthlyPmt(period)
        #Above duplicated formula + add PMI
        return base_payment + self.PMI(period)

    #Override principalDue_formula
    def principalDue_formula(self, period):
        #Call base class with super
        return super(MortgageMixin, self).principalDue_formula(period)
        #Seeing the base class formula, it does monthly payment minus interest due
        #Since the PMI is included in monthlyPmt (see directly above in this script), it should be OK.





#No code to pass through below classes; they inherit everything necessary from classes described below

#Derive from MortgageMixin, and from VariableRateLoan
#Inherits everything from both classes; __init__ and PMI above,
# as well as __init__ from VariableRateLoan and rate function (see loans.py), as well as ITS base class, Loan.
class VariableMortgage(MortgageMixin, VariableRateLoan):
    pass


#Derive from MortgageMixin, and from FixedRateLoan
#Similar inheritance as VariableMortgage
class FixedMortgage(MortgageMixin, FixedRateLoan):
    pass









#Initialize it with car parameter instead of home, so import Car class at top of file
class AutoLoan(FixedRateLoan):
    #Create initialization function this time, to store car
    def __init__(self, face, rate, loanstart, loanend, car):
        #Call Superclass from base; FixedRateLoan goes to Loan, whose init has these 3
        super(AutoLoan, self).__init__(car, face, rate, loanstart, loanend)

        # First, ensure input asset is Car object
        if not isinstance(car, Car):
            # Print error message if it is not
            logging.error(f'Invalid asset type {type(car)}. Enter valid Car asset.')
            raise TypeError('Enter valid Car asset.')

        # Initialize new    variable
        self._car = car






