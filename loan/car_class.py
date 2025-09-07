'''
Samuel Decornez
This module contains the derived Car class.
'''




'''==============================================
Main Program:
This program creates the Asset-derived Car class.
=============================================='''


#Import base class
from loan.asset_base import Asset



#Create the derived Car class
class Car(Asset):
    # Create initialization function
    #This will take model; a dictionary of rates will be defined just below initialization with some associated rates
    #initial_value itself will be inherited from base class (in asset_base.py)
    def __init__(self, initial_value, model):
        # Initialize model
        self._model = model
        # Invoke Asset Superclass initialization
        super(Car, self).__init__(initial_value)


    #Create some dictionary of predefined depreciation rates by car model
    car_depreciation_rates = {'Civic':0.05, 'Lexus':0.10, 'Lambo':0.15, 'Toyota':0.20, 'Ferrari':0.25}


    # Override base Asset class depreciation method
    def yearlyDepreciationRate(self):
        # Return pre-defined depreciation rate of specified model
        # Default to a blanket value if specified model is not in above list
        default_value = 0.30
        return self.car_depreciation_rates.get(self._model, default_value)