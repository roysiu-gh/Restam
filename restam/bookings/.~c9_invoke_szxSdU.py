from pathlib import Path
from typing import Dict, Tuple, List, Any, NewType
import sys

# get func name: sys._getframe().f_code.co_name

# Create type signatures
meal_config_typing = Dict[ str, Any ]
meals_config_typing = Dict[ str, meal_config_typing ]

meals_data_typing = Dict[ str, int ]

class Restaurant(object):
    
    def __init__( self, *args ) -> None:
        """Initiate restaurant object with config_files (args)"""
        
        self.timing_interval_mins = 1
    
        self.restaurant_name = "NAME"
        
        self.opening_time = [00, 00]
        self.final_orders = [00, 00]
        self.closing_time = [00, 00]
        
        self.floors_and_tables = []
        self.common_table_joins = []
        
        self.meals = {}
        
        for config_file in args:
            with config_file.open() as f:
                exec( f.read() )
        
        try:
            # Main configs
            assert type(self.timing_interval_mins) is int , "self.timing_interval_mins is not int"
            
            assert type(self.restaurant_name) is str , "self.restaurant_name is not str"
            
            for item in ( self.opening_time, self.final_orders, self.closing_time ): # Check valid timings
                assert type(item) is list
                assert len(item) == 2
                
                assert type( item[0] ) is int , "hour in '{0}' not integer".format( item )
                assert type( item[1] ) is int , "minute in '{0}' not integer".format( item )
            
            assert type(self.floors_and_tables) is list , "self.floors_and_tables is not list"
            for floor_index, floor in enumerate(self.floors_and_tables): # Check valid floor and table config format
                assert type(floor) is list , "floor index {0} is not a list".format( floor_index )
                for table_index, table in enumerate(floor):
                    assert type(table) is list , "table index '{1}', floor index '{0}': is not a list".format( floor_index, table_index )
                    assert len(table) == 2 , "table index '{1}', floor index '{0}': list length not 2".format( floor_index, table_index )
                    
                    assert type( table[0] ) is int , "table index '{1}', floor index '{0}': table number (index 0) not int".format( floor_index, table_index )
                    assert type( table[1] ) is int , "table index '{1}', floor index '{0}': seat count (index 0) not int".format( floor_index, table_index )
            
            assert type(self.common_table_joins) is list , "self.common_table_joins is not list"
            
            # Meals
            assert type(self.meals) is dict , "self.meals is not dict"
            for meal_key, meal_details in self.meals.items():
                assert type(meal_key) is str , "meal key {0} not str".format( meal_key )
                assert type(meal_details) is dict , "meal key '{0}': details not dict".format( meal_key )
                
                for i in ( "name", "price", "veg", "egg_free", "dairy_free", "nut_free" ):
                    assert i in meal_details , "meal key '{0}': does not specify {1}".format( meal_key, i )
                for detail_key in meal_details:
                    assert type(detail_key) is str , "meal key '{0}': {1} is not str".format( meal_key, detail_key )
                
                assert type(meal_details["name"]) is str , "meal key '{0}', detail key '{1}': {2} is not str".format( meal_key, "name", meal_details["name"] )
                assert type(meal_details["price"]) is float , "meal key '{0}', detail key '{1}': {2} is not int".format( meal_key, "price", meal_details["price"] )
                assert meal_details["veg"] in ( 0, 1, 2, None ) , "meal key '{0}', detail key '{1}': {2} not in ( 0, 1, 2, None )".format( meal_key, "veg", meal_details["veg"] )
                assert meal_details["egg_free"] in ( True, False, None ) , "meal key '{0}', detail key '{1}': {2} is not bool or None".format( meal_key, "egg_free", meal_details["egg_free"] )
                assert meal_details["dairy_free"] in ( True, False, None ) , "meal key '{0}', detail key '{1}': {2} is not bool or None".format( meal_key, "dairy_free", meal_details["dairy_free"] )
                assert meal_details["nut_free"] in ( True, False, None ) , "meal key '{0}', detail key '{1}': {2} is not bool or None".format( meal_key, "nut_free", meal_details["nut_free"] )
            
        except AssertionError as e:
            print( "Error in {0}: {1}".format( sys._getframe().f_code.co_name, e.args ) )
            raise # Re-raise error for handling
        
        self.completed_transactions = {}
        self.in_progress_transactions = {}
        self.next_transaction_no = 0
        
        self.times = []
        self.timetable = {}
        for hour in range(self.opening_time[0], self.closing_time[0]):
            for minute in range(0, 61, self.timing_interval_mins):
                time = (hour * 100) + minute
                self.times.append( time )
                self.timetable[time] = None
    
    def add_party( self, meals:dict, booked:bool, name:str="anon", caravan_no:int=-1, telephone_no:int=-1, additional_notes:str="" ) -> None:
        try:
            assert type(meals) is dict , "meals is not dict"
            for key, value in meals.items():
                assert type(key) is str , "meals key '{0}' not str".format( key )
                assert type(value) is int , "meals key '{0}': value not int".format( key )
            
            assert type(booked) is bool , "booked not int"
            assert type(name) is str , "name not str"
            assert type(caravan_no) is int , "caravan_no not int"
            assert type(telephone_no) is int , "telephone_no not int"
            assert type(additional_notes) is str , "additional_notes not str"
        except AssertionError as e:
            print( "Error in {}".format(sys._getframe().f_code.co_name), e.args )
            raise # Re-raise error for handling
        else:
            self.in_progress_transactions[ str(self.next_transaction_no) ] = { "meals":meals, "name":name, "caravan_no":caravan_no, "telephone_no":telephone_no, "additional_notes":additional_notes }
            self.next_transaction_no += 1
            return 0 # Success
    
    def modify_meals( self, iden:str, meals_add:meals_data_typing ) -> None:
        """ modify amount of meals in a party/booking order
        iden -- the party that the prices should be added to
        meals_add -- dictionary where key is the meal (normally a number), and the value is the amount to be added (to remove, use negative value)
        """
        #print(meals_add)
        for meal, amount in meals_add.items():
            ordered_meals = self.in_progress_transactions[str(iden)]["meals"] # copy meals from order (iden) from in_progress_transactions into ordered_meals
            ordered_meals[meal] += amount if meal in ordered_meals else exec("ordered_meals[meal] = amount")
    
    def get_price(self) -> None:
    
    def finish_party(self, iden:int) -> None:
        try:
            self.completed_transactions[iden] = self.in_progress_transactions[iden]
        except KeyError:
            print( "Error in {}".format(sys._getframe().f_code.co_name) )
            raise # Re-raise error for handling
    
    def search_bookings( self, category, data ):
        pass
    
    def hcf( self ):
        pass

if __name__ == "__main__":
    import sys
    print(sys.version)
    
    # instantiate
    main = Path('../haggerston_main.cfg')
    meals = Path('../haggerston_meals.cfg')
    drinks = Path('../haggerston_drinks.cfg')
    takeaways = Path('../haggerston_takeaways.cfg')
    
    # add bookings
    test = Restaurant( main, meals, drinks, takeaways )
    test.add_party( meals={ "1":3, "2":1 }, booked=True, name="the first 3 guys and a kid" )
    test.add_party( meals={"1":1}, booked=True, name="a lonely guy" )
    
    #print(test.in_progress_transactions)
    
    import doctest
    doctest.testfile("bookings_restam.doctest")