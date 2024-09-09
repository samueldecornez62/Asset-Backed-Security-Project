'''
Samuel Decornez
This module contains the derived Car class.
'''




'''====================================
Main Program:
This program will create the Car class.
===================================='''


#Import base class
from asset_base import Asset



#Create the derived Car class
class Car(Asset):
    #Create initialization function
    #This will take model; a dictionary of rates will be defined just below initialization
    #initial_value itself will be inherited from base class (in asset_base.py)
    #Also, invoke superclass __init__ function (initial_value)
    def __init__(self, initial_value, model):
        #Initialize model
        self.model = model
        #Superclass
        super(Car, self).__init__(initial_value)

    #Create some dictionary of predefined depreication rates by car model
    car_depreciation_rates = {'Civic':0.05, 'Lexus':0.10, 'Lambo':0.15, 'Toyota':0.20, 'Ferrari':0.25}


    #Finally, override base class depreciation rate function
    #Correctly overrides yearlyDepreciationRate in base asset class that this one derives from directly
    def yearlyDepreciationRate(self):
        #Return depreciation of given model. If model not found, defaults to a default value
        default_value = 0.30
        return self.car_depreciation_rates.get(self.model, default_value)
