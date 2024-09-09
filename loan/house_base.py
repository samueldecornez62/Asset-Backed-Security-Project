'''
Samuel Decornez
This module contains the derived HouseBase class.
'''




'''======================================
Main Program:
This program will create the House class.
======================================'''


#Import base class
from asset_base import Asset


#Create base House class
class HouseBase(Asset):
    #Initialization function
    def __init__(self, initial_value, home_purpose):
        #Initialize home purpose (vacation or primary)
        self.home_purpose = home_purpose
        #similar to derived car class, superclass
        super(HouseBase, self).__init__(initial_value)

#Create classes derived from this one in separate file (house_derived_classes.py)

#Now with those derived classes created, we can assign meaning to home_purpose through depreciation rates
#As with car depreciation rates in car_class.py, do it here:

#Create some dictionary of predefined depreication rates by car model
    home_depreciation_rates = {'Vacation':0.05, 'Primary':0.25}


    #Finally, override base class depreciation rate function
    #Correctly overrides yearlyDepreciationRate in base asset class that this one derives from directly
    def yearlyDepreciationRate(self):
        #Return depreciation of given model. If model not found, defaults to a default value
        #If refusing to comply with instructions of Primary/Vacation,
        # give user a default revenge depreciation rate of 100%
        default_value = 1.00
        return self.home_depreciation_rates.get(self.home_purpose, default_value)