'''
Samuel Decornez
This module contains the derived HouseBase class.
'''




'''======================================================================================
Main Program:
This program creates the House class. See house_derived_class.py for added functionality. 
======================================================================================'''


#Import base class
from loan.asset_base import Asset


#Create base House class
class HouseBase(Asset):
    # Create initialization function
    def __init__(self, initial_value, home_type):
        # Initialize home type; Primary or Vacation (other types can be added later)
        super(HouseBase, self).__init__(initial_value)


    # Classes derived from this one will be in a separate file, see house_derived_classes.py


