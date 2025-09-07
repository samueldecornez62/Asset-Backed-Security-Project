'''
Samuel Decornez
This module contains classes related to Mortgages.
'''



'''========================================================================================================
Main Program:
This program defines Mortgage functionality. 
It includes a MortgageMixin for standard loans, and assigns Fixed or Variable rates.
========================================================================================================'''


# Import the derived classes that will be called
from loan.loans import VariableRateLoan, FixedRateLoan
from loan.house_base import HouseBase
# from loan.asset_base import Asset
from loan.car_class import Car


### ADJUSTED VERSION
class MortgageMixin(object):
    def __init__(self, *args, **kwargs):
        # MortgageMixin.__init__(self)
        super(MortgageMixin, self).__init__(*args, **kwargs)


    # Mortgage-specific functionality for Private Mortgage Insurance (required by law on mortgages exceeding 80% asset value)
    def PMI(self, period):
        #Mortgage-specific functions and code go here

        #Loan >= 80%  asset value means pay PMI
        #So loan/asset = LTV >= 0.8  means pay PMI
        #Here, assume initial loan = 100% asset value (which is >= 80% asset value, so always pay PMI)

        #Calculate LTV = loan/value ratio; call initial_value from base Asset
        LTV = (self._face) / self._asset.initial_value

        #From above logic in commenting, if loan covers more than 80% of asset value
        if LTV >= 0.8:
            #0.0075% is 0.000075 as a decimal; return this multiplied by face value
            return 0.000075 * self._face
        #Else, no PMI and return 0
        else:
            return 0



# ### OLD VERSION
# class MortgageMixin(object):
#     def __init__(self, notional, rate, term, home):
#         # MortgageMixin.__init__(self)
#         super(MortgageMixin, self).__init__()
#
#         # Validate that home is in fact a HouseBase or further derived class
#         if not isinstance(home, HouseBase):
#             raise TypeError(f'home must be an instance of HouseBase or its subclasses')
#
#         # Set object-level attribute
#         self._home = home
#
#     # Mortgage-specific functionality for Private Mortgage Insurance (required by law on mortgages exceeding 80% asset value)
#     def PMI(self, period):
#         #Mortgage-specific functions and code go here
#
#         #Loan >= 80%  asset value means pay PMI
#         #So loan/asset = LTV >= 0.8  means pay PMI
#         #Here, assume initial loan = 100% asset value (which is >= 80% asset value, so always pay PMI)
#
#         #Calculate LTV = loan/value ratio; call initial_value from base Asset
#         LTV = (self._face) / self._home.initial_value
#
#         #From above logic in commenting, if loan covers more than 80% of asset value
#         if LTV >= 0.8:
#             #0.0075% is 0.000075 as a decimal; return this multiplied by face value
#             return 0.000075 * self._face
#         #Else, no PMI and return 0
#         else:
#             return 0


# Double inheritance; Mixin for mortgage functionality, Fixed which itself inherits Loan functionality
class FixedMortgage(FixedRateLoan, MortgageMixin):
    def __init__(self, asset, face, rate, term):
        if not isinstance(asset, HouseBase):
            raise TypeError(f'FixedMortgage asset must be a HouseBase or subclass')
        super().__init__(asset, face, rate, term)



# Double inheritance; Mixin for mortgage functionality, Variable which itself inherits Loan functionality
class VariableMortgage(VariableRateLoan, MortgageMixin):
    def __init__(self, asset, face, rateDict, term):
        if not isinstance(asset, HouseBase):
            raise TypeError(f'VariableMortgage asset must be a HouseBase or subclass')
        super().__init__(asset, face, rateDict, term)



# Single inheritance; Fixed car loan
# Functionality to be added later 
class AutoLoan(FixedRateLoan):
    def __init__(self, asset, face, rate, term):
        if not isinstance(asset, Car):
            raise TypeError(f'AutoLoan must have asset of type Car')
        super().__init__(asset, face, rate, term)
    pass

