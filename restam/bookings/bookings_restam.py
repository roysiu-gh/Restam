#!/bin/env/python3
# coding: utf8

"""I'm a neglected docstring!!"""

__version__ = ""
__author__ = "Roy Siu"
__credits = []

from pathlib import Path
from typing import Dict, Tuple, List, Any, Callable
from copy import copy, deepcopy
from collections import OrderedDict
import sys

## Create type signatures
#meal_config_typing = Dict[ str, Any ]
#meals_config_typing = Dict[ str, meal_config_typing ]

meals_data_typing = Dict[ str, int ]

### Exeption classes

class IdentityError(Exception):
    """Raise when check_iden_exists() is passed a bad id"""
    def __init( self, message, func:Callable=None ):
        self.message = message
        self.func = func

### Decorators

def check_iden_exists( func:Callable, *args, **kwargs ):
    """Check that variable 'iden' exists within self.transactions"""
    def _inner( self, *args, **kwargs ):
        try:
            if not ( "iden" in kwargs ):
                raise IdentityError( "identity not keyword arg in form 'iden=...'", func )
            if not ( isinstance(kwargs["iden"], int) ):
                raise IdentityError( "iden is not str", func )
            if not ( kwargs["iden"] in self.transactions ):
                raise IdentityError( "iden does not exist", func )
        except IdentityError as e:  # Catch-all
            print( "Error in {0}: {1}".format( func, e.args ) )
            raise  # Re-raise error for handling
        else:
            return func( self, **kwargs )
    return _inner

### Classes

class Transaction( object ):
    """Handle transaction operations"""
    def __init__( self ):
        self._transactions = OrderedDict()
        self.__next_transaction_no = 0
    
    def __str__(self):
        pass
    
    def __repr__(self):
        pass
    
    def __iter__(self):
        for val in self._transactions:
            yield val
    
    @property
    def transactions(self):
        return self._transactions
    
    @property
    def pending_transcations(self) -> dict:
        pending = {}
        for transaction in self._transactions:
            if self._transactions[transaction].pending:
                pending[transaction] = self._transactions[transaction]
        return pending
    
    @property
    def completed_transcations(self) -> dict:
        completed = {}
        for transaction in self._transactions:
            if self._transactions[transaction].complete:
                completed[transaction] = self._transactions[transaction]
        return completed
    
    @property
    def cancelled_transcations(self) -> dict:
        cancelled = {}
        for transaction in self._transactions:
            if self._transactions[transaction].cancelled:
                cancelled[transaction] = self._transactions[transaction]
        return cancelled
    
    def add( self, party ):
        self._transactions[ self.__next_transaction_no ] = party
        self.__next_transaction_no += 1
    
    #@check_iden_exists
    def get( self, iden ):
        return self._transactions[ iden ]

class Timetable( object ):
    """Handle timetable operations"""
    def __init__( self, opening_time:int, closing_time:int, timing_interval_mins:int, floors_and_tables_config:dict ):
        self.opening_time = opening_time
        self.closing_time = closing_time
        self.timing_interval_mins = timing_interval_mins
        self.floors_and_tables_config = floors_and_tables_config
        
        self._timetable = OrderedDict()
        
        self._floors = OrderedDict()
        for floor_no, table_list in self.floors_and_tables_config.items():
            self._floors[floor_no] = Floor( table_list )
        
        open_hour, open_min = divmod( self.opening_time, 100 )
        close_hour, close_min = divmod( self.closing_time, 100 )
        total_open_time_mins = ( close_hour - open_hour ) * 60  +  ( close_min - open_min )
        for momentxinterval in range( 0, total_open_time_mins, self.timing_interval_mins ):
            self._timetable[ int(momentxinterval/self.timing_interval_mins) ] = deepcopy(self._floors)
    
    def __str__(self):
        ## Retrieve all floors
        counter = 1  # Set to 1 to compensate for zero-indexing
        to_return = bytearray("", "utf-8")  # Use bytearray
        for key, item in self._floors.items():
            to_add = "{}: [{}]".format(str(key), str(item))
            to_return += bytearray(to_add, "utf-8")  # Append Floor
            if not ( counter == len(self._floors) ):  # Only append comma and space if not end #not efficient
                to_return += bytearray(", ", "utf-8")
            counter += 1
        to_return = to_return.decode(encoding='UTF-8')
        all_floors = "{{{0}}}".format(to_return)
        #return "{{{0}}}".format(to_return)  # Double curly brackets to escape
        
        ## Put all floors into each time in timetable
        counter = 1  # Set to 1 to compensate for zero-indexing
        to_return = bytearray("", "utf-8")  # Use bytearray
        for key, item in self._timetable.items():
            to_add = "{}: [{}]".format(str(key), all_floors)
            to_return += bytearray(to_add, "utf-8")  # Append Floors
            if not ( counter == len(self._timetable) ):  # Only append comma and space if not end #not efficient
                to_return += bytearray(", ", "utf-8")
            counter += 1
        to_return = to_return.decode(encoding='UTF-8')
        timetable_print = "{{{0}}}".format(to_return)
        return timetable_print
    
    def __repr__(self):
        pass

class Restaurant( object ):
    
    def __init__( self, *args ) -> None:
        """Initiate restaurant object with config_files (args)"""
        
        self.timing_interval_mins = 1
        
        self.restaurant_name = "NAME"
        
        self.opening_time = [00, 00]
        self.final_orders = [00, 00]
        self.closing_time = [00, 00]
        self.max_stay = 0
        
        self.floors_and_tables_config = {}
        self.common_table_joins_config = {}
        
        self.meals = {}
        
        for config_file in args:
            with config_file.open() as f:
                exec( f.read() )
        
        try:
            ## Main configs
            if not (type(self.timing_interval_mins) is int):
                raise TypeError("self.timing_interval_mins is not int")
            
            if not (type(self.restaurant_name) is str):
                raise TypeError("self.restaurant_name is not str")
            
            for times in (self.opening_time, self.final_orders, self.closing_time):
                if not (type(times) is int):
                    raise TypeError("'{}' not integer".format(times))
            
            if not (type(self.floors_and_tables_config) is dict):
                if not (type(self.floors_and_tables_config) is OrderedDict):
                    raise TypeError("self.floors_and_tables is not dict")
            for floor_key in self.floors_and_tables_config.keys():  # Check valid floor and table config format
                if not (type( self.floors_and_tables_config[floor_key] ) is list):
                    raise TypeError("floor index {0} is not a list".format( floor_key ))
                for table_key, table in enumerate( self.floors_and_tables_config[floor_key] ):
                    kt = frozenset((floor_key, table_key))
                    for to_check, type_, error_message in zip(
                            [type(table), len(table), type(table[0]), type(table[1]),],
                            [list, 2, int, int,],
                            ["floor index '{1}', table index '{0}': is not a list".format(*kt),
                            "floor index '{1}', table index '{0}': list length not 2".format(*kt),
                            "floor index '{1}', table index '{0}': table number (index 0) not int".format(*kt),
                            "floor index '{1}', table index '{0}': seat count (index 0) not int".format(*kt),
                            ] ):
                        if not (to_check is type_):
                            raise TypeError(error_message)
            
            if not (type(self.common_table_joins_config) is dict):
                if not (type(self.common_table_joins_config) is OrderedDict):
                    raise TypeError("self.common_table_joins is not dict")
                
            ## Meals
            if not (type(self.meals) is dict):
                raise TypeError("self.meals is not dict")
            for meal_key, meal_details in self.meals.items():
                if not (type(meal_key) is str):
                    raise TypeError("meal key {0} not str".format( meal_key ))
                if not (type(meal_details) is dict):
                    raise TypeError("meal key '{0}': details not dict".format( meal_key ))
                for i in ( "name", "price", "veg", "egg_free", "dairy_free", "nut_free" ):
                    if not (i in meal_details):
                        raise TypeError("meal key '{0}': does not specify {1}".format( meal_key, i ))
                
                if not (type(meal_details["name"]) is str):
                    raise TypeError("meal key '{0}', detail key '{1}': {2} is not str".format( meal_key, "name", meal_details["name"] ))
                if not (type(meal_details["price"]) is float):
                    raise TypeError("meal key '{0}', detail key '{1}': {2} is not int".format( meal_key, "price", meal_details["price"] ))
                if not (meal_details["veg"] in ( 0, 1, 2, None )):
                    raise TypeError("meal key '{0}', detail key '{1}': {2} not in ( 0, 1, 2, None )".format( meal_key, "veg", meal_details["veg"] ))
                if not (meal_details["egg_free"] in ( True, False, None )):
                    raise TypeError("meal key '{0}', detail key '{1}': {2} is not bool or None".format( meal_key, "egg_free", meal_details["egg_free"] ))
                if not (meal_details["dairy_free"] in ( True, False, None )):
                    raise TypeError("meal key '{0}', detail key '{1}': {2} is not bool or None".format( meal_key, "dairy_free", meal_details["dairy_free"] ))
                if not (meal_details["nut_free"] in ( True, False, None )):
                    raise TypeError("meal key '{0}', detail key '{1}': {2} is not bool or None".format( meal_key, "nut_free", meal_details["nut_free"] ))
            
        except TypeError as e:
            print( "Error in {0}: {1}".format( sys._getframe().f_code.co_name, e.args ) )
            raise  # Re-raise error for handling
        
        else:
            self.transactions = Transaction()
            self.timetable = Timetable( opening_time=self.opening_time, closing_time=self.closing_time, timing_interval_mins=self.timing_interval_mins, 
            floors_and_tables_config=self.floors_and_tables_config)
    
    def __str__(self):
        pass
    
    def __repr__(self):
        pass
    
    def time_to_moment( self, time ):
        try:
            if not ( ( time >= self.opening_time ) and ( time <= self.closing_time ) ):
                raise ValueError( "time ({2}) not between opening times: {0} and {1}".format( self.opening_time, self.closing_time, time ) )
            if not ( ( time - self.opening_time ) % self.timing_interval_mins == 0 ):
                raise ValueError( "time ({2}) is not at an interval of {0} mins from opening time ({1})".format( self.timing_interval_mins, self.opening_time, time ) )
        except ValueError as e:
            print( "Error in {0}: {1}".format( sys._getframe().f_code.co_name, e.args ) )
            raise # Re-raise error for handling
        else:
            open_hour, open_min = divmod( self.opening_time, 100 )
            time_hour, time_min = divmod( time, 100 )
            return int(  ( ( time_hour - open_hour ) * 60  +  ( time_min - open_min ) ) / self.timing_interval_mins  )
    
    def moment_to_time( self, moment ):
        hour_add, min_add = divmod( moment * self.timing_interval_mins, 60 )
        to_add = hour_add * 100 + min_add
        return int( self.opening_time + to_add )
    
    def add_party( self, time_start:int, meals:dict, booked:bool,
            name:str="anon", caravan_no:int=-1, telephone_no:int=-1, additional_notes:str="" ) -> "Restaurant":
        time_length = self.max_stay  # Need error check in init
        try:
            if not (type(meals) is dict):
                raise TypeError("meals is not dict")
            for key, value in meals.items():
                if not (type(key) is str):
                    raise TypeError("meals key '{0}' not str".format( key ))
                if not (type(value) is int):
                    raise TypeError("meals key '{0}': value not int".format( key ))
            
            if not (type(booked) is bool):
                raise TypeError("booked not int")
            if not (type(name) is str):
                raise TypeError("name not str")
            if not (type(caravan_no) is int):
                raise TypeError("caravan_no not int")
            if not (type(telephone_no) is int):
                raise TypeError("telephone_no not int")
            if not (type(additional_notes) is str):
                raise TypeError("additional_notes not str")
        except TypeError as e:
            print( "Error in {}".format(sys._getframe().f_code.co_name), e.args )
            raise  # Re-raise error for handling
        else:
            party_add = Party( time_start=time_start, time_length=time_length,
                    meals=meals, booked=booked, name=name,
                    caravan_no=caravan_no, telephone_no=telephone_no, additional_notes=additional_notes )
            self.transactions.add( party_add )
    
    def __add_party_to_timetable( self, iden:str ) -> bool: # move to own class
        pass
        #start_moment = self.time_to_moment( self.transactions.get(iden).time_start )
        #start_timeframe = self.timetable[start_moment]
        #self.timetable.get(start_moment) = self.transactions[iden] #testing
    
    @check_iden_exists
    def modify_meals( self, iden:str, meals_add:Dict[ str, int ] ) -> None:
        """ modify amount of meals in a party/booking order
        iden -- the party that the prices should be added to
        meals_add -- dictionary where key is the meal (normally a number), and the value is the amount to be added (to remove, use negative value)
        """
        try:
            self.transactions.get(iden).modify_meals(meals_add)
        except TypeError as e:
            print( "Error in {}".format(sys._getframe().f_code.co_name), e.args )
            raise  # Re-raise error for handling
    
    @check_iden_exists
    def overwrite_additional_party_notes( self, iden:int, notes:str, mode:str="w" ) -> None:
        try:
            if not ( mode in ( "w", "a" ) ):
                raise ValueError( "invalid mode: '{}'".format(mode) )
        except ( TypeError, KeyError, ValueError ) as e:
            print( "Error in {}".format(sys._getframe().f_code.co_name), e.args )
            raise  # Re-raise error for handling
        else:
            self.transactions.get(iden).overwrite_additional_party_notes( notes=notes, mode=mode )
    
    @check_iden_exists
    def modify_past_meals( self, iden:str, meals_add:meals_data_typing ) -> None:
        """Modify meals on a completed transaction"""
        pass
    
    ## Status manipulation
    @check_iden_exists
    def get_party( self, iden:int ) -> dict:
        return self.transactions.get(iden)
    
    def search_parties( self, category, search_term ):
        pass
    
    @check_iden_exists
    def complete_party( self, iden:int ) -> None:
        self.transactions.get(iden).complete = True
    @check_iden_exists
    def cancel_party( self, iden ):
        self.transactions.get(iden).cancelled = True
    @check_iden_exists
    def reactivate_party( self, iden ):
        self.transactions.get(iden).pending = True
    
    def hcf( self ): # Halt and Catch Fire
        pass

class Party( object ):
    
    def __init__( self, time_start:int, time_length:int, meals:dict, booked:bool,
            name:str="anon", caravan_no:int=-1, telephone_no:int=-1, additional_notes:str="", status:int=0 ) -> None:
        self.time_start = time_start
        self.time_length = time_length
        self.meals = meals
        self.name = name
        self.caravan_no = caravan_no
        self.telephone_no = telephone_no
        self.additional_notes = additional_notes
        self.status = status
        self.status_log = [status]
    
    def __str__(self):
        pass
    
    def __repr__(self):
        pass
    
    ## Status properties
    
    @property
    def time_end(self):
        return self.time_start + self.time_length
    
    @property
    def pending(self):
        return ( self.status == 0 )
    @pending.setter
    def pending( self, value ):
        if value:
            self.status = 0
            self.status_log.append(0)
        else:
            raise ValueError
    
    @property
    def complete(self):
        return ( self.status == 1 )
    @complete.setter
    def complete( self, value ):
        if value:
            self.status = 1
            self.status_log.append(1)
        else:
            raise ValueError
    
    @property
    def cancelled(self):
        return ( self.status == 2 )
    @cancelled.setter
    def cancelled( self, value ):
        if value:
            self.status = 2
            self.status_log.append(2)
        else:
            raise ValueError
    
    def modify_meals( self, meals_add:meals_data_typing ) -> None:
        """ modify amount of meals in a party/booking order
        iden -- the party that the prices should be added to
        meals_add -- dictionary where key is the meal (normally a number), and the value is the amount to be added (to remove, use negative value)
        """
        for meal, amount in meals_add.items():
            self.meals[meal] = self.meals.get( meal, 0 ) + amount
    
    def overwrite_additional_party_notes( self, notes:str, mode:str="w" ) -> None:
        if mode == "w": self.additional_notes = notes
        elif mode == "a": self.additional_notes += notes

class Floor( object ):
    
    def __init__( self, tables ) -> None:
        self.tables = OrderedDict()
        for table in tables:
            self.tables[ table[0] ] = Table( table[1] )
    
    def __str__(self):
        counter = 1  # Set to 1 to compensate for zero-indexing
        to_return = bytearray("", "utf-8") # use bytearray
        for key, item in self.tables.items():
            to_add = "[{}, {}]".format(str(key), str(item))
            to_return += bytearray(to_add, "utf-8")  # Append Table
            if not ( counter == len(self.tables) ):  # Only append comma and space if not end #not efficient
                to_return += bytearray(", ", "utf-8")
            counter += 1
        to_return = to_return.decode(encoding='UTF-8')
        return to_return
    
    def __repr__(self):
        pass

class Table( object ):
    
    def __init__( self, seats:int ) -> None:
        self.seats = seats
    
    def __str__(self):
        return str(self.seats)
    
    def __repr__(self):
        pass

if __name__ == "__main__":
    from pprint import pprint
    
    # Instantiate
    main = Path('../haggerston_main.cfg')
    meals = Path('../haggerston_meals.cfg')
    drinks = Path('../haggerston_drinks.cfg')
    takeaways = Path('../haggerston_takeaways.cfg')
    
    # Add bookings
    test = Restaurant( main, meals, drinks, takeaways )
    
    test.add_party( meals={ "1":3, "2":1 }, time_start=1830, booked=True, name="the first 3 guys and a kid" )
    test.add_party( meals={ "1":1 }, booked=True, time_start=1845, name="a lonely guy" )
    
    #print( test.timetable )
    
    import doctest
    doctest.testfile("bookings_restam.doctest")