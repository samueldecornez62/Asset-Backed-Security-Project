'''
Samuel Decornez
This module contains classes derived from HouseBase.
'''




'''============================================
Main Program:
This program creates the derived House classes.
============================================'''


#Import class we are deriving this from
from loan.house_base import HouseBase
from loan.asset_base import Asset


#Create PrimaryHome class, derived from HouseBase
class PrimaryHome(HouseBase):
    #Initialization function
    def __init__(self, initial_value):
        #Call superclass; must inherit initial value from asset, home_purpose from house base
        super(PrimaryHome, self).__init__(initial_value, home_type='Primary')

    # Define rate method, which overrides base version in Asset class
    def yearlyDepreciationRate(self):
        return 0.025


#Repeat exact same as above, for VacationHome
class VacationHome(HouseBase):
    #Initialization function
    def __init__(self, initial_value):
        #Call superclass; must inherit initial value from asset, home_purpose from house base
        super(VacationHome, self).__init__(initial_value, home_type='Vacation')

    # Define rate method, which overrides base version in Asset class
    def yearlyDepreciationRate(self):
            return 0.015