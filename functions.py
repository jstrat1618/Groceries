# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 15:12:50 2017

@author: JustinandAbigail
"""

import psycopg2 as pg2
import pandas as pd
from random import sample

pwd_file = open('C:/Users/JustinandAbigail/Desktop/Temp/dum_file.txt')
my_pwd = pwd_file.readlines()
pwd_file.close()

#Open database
con = pg2.connect(database = 'recipes', user = 'postgres', 
                      password = my_pwd[0])
cur = con.cursor()


def get_recipe_categories():
    #Returns a dictionary with the names as the key and id_nums as values

    #Query categories table
    cur.execute('SELECT * FROM categories;')
    cat_query = cur.fetchall()
    
    cat_dict = {}
    for cat in cat_query:
        id_num , lab = cat
        cat_dict[lab] = id_num
    return(cat_dict)


def insert_recipe(rname, selected_cat, serv_size, meal_time, instructions = ''):
    cat_dict = get_recipe_categories()
    
    all_cats = cat_dict.keys()
    
    try:
        assert selected_cat in all_cats
        cat_id = cat_dict[selected_cat]
        cur.execute("INSERT INTO recipes(category_id, recipe_name, serving_size, meal_time, instructions) VALUES(%s, %s, %s, %s, %s);", (cat_id, rname, serv_size, meal_time, instructions))
        con.commit()
    
    except Exception as err:
        print(err)
     

def clean_string(mystring):
    mystring = mystring.lower()
    mystring = mystring.rstrip()
    mystring = mystring.lstrip()
    return(mystring)
    
    
    
def get_grocery_list(recp_file):
    
    rdf = pd.read_csv(recp_file)
    recps_list = rdf['recipe'].values
    serv_list = rdf['servings'].values
    
    rdict = {}
    for i in range(len(recps_list)):
        rdict[recps_list[i]] =serv_list[i]
    
    recps_tup = tuple(recps_list)
    
    #Query the ingredients database
    sql = "SELECT recipe_name, serving_size, ingredient_name, unit, amount FROM ingredients JOIN recipes ON recipes.recipe_id = ingredients.recipe_id WHERE recipe_name IN %(recps_tup)s;"
    cur.execute(sql, {'recps_tup': recps_tup,})
    query = cur.fetchall()
    
    qdf = pd.DataFrame(query, columns = ["recipe", "serving_size", "ingredient_name", "unit", "amount"] )
    

    servs_for_qdf = []
    for rep in range(len(qdf)):
        lab = qdf['recipe'].values[rep]
        servs_for_qdf.append(rdict[lab])
    
    qdf['servings_requested'] = servs_for_qdf
    
    qdf = qdf.assign(new_amt = qdf.amount * qdf.servings_requested / qdf.serving_size)
    
    out_df = qdf.groupby(['ingredient_name', 'unit']).agg({'new_amt':'sum'})
    return(out_df)

def get_recipes():
    #Returns a dictionary with the names as the key and id_nums as values

    #Query categories table
    cur.execute('SELECT recipe_id, recipe_name FROM recipes;')
    rep_query = cur.fetchall()
    
    rep_dict = {}
    for rep in rep_query:
        id_num , lab = rep
        rep_dict[lab] = id_num
    return(rep_dict)

'''
Input: Takes a pandas column
Return a tuple based on the two conditions below
1.) If all the elements in unit will pass the checks for the database
    returns a tuple with the first element being True, and the 2nd element
    being the cleaned numpy array. The cleaned numpy array will
2.) If one or more of the elements of the numpy array do not pass will return 
    a tuple with False as the first element and the elementw that were
    improperly formated
'''
def clean_unit(unit):
    unit = unit.str.lower()
    unit = unit.apply(clean_string)
    
    unit = unit.replace(['tsp', 'tsps', 'teaspoon'], 'teaspoons')
    unit = unit.replace(['tbsp', 'tbsps', 'tablespoon'], 'tablespoons')
    unit = unit.replace('cup', 'cups')
    unit = unit.replace(['ounce', 'oz', 'ozs'], 'ounces')
    unit = unit.replace('pint', 'pints')
    unit = unit.replace('pinch', 'pinches')
    unit = unit.replace(['pound','lbs'], 'pounds')
    unit = unit.replace('gram', 'grams')
    unit = unit.replace('quart', 'quarts')
    
    pass_check = []
    for _ in unit:
        p_or_f = _ =='whole' or _[-1] =='s' or _.endswith('oz can')
        pass_check.append(p_or_f)
    
    pass_all = all(pass_check)
    
    if pass_all:
        return( (pass_all, unit) )
    else:
        bad = unit[[not p for p in pass_check]]
        return( (pass_all, bad) )

'''
Should return True if the recipe was successfully uploaded to the database
Otherwise return False.
'''    

def insert_recipe_via_csv(ing_file, rname, selected_cat, serv_size, meal_time, instructions=''):
    
    rname = rname.lower()
    selected_cat = selected_cat.lower()
    meal_time = meal_time.lower()
    
    try:
        meal_check = meal_time in ['breakfast', 'lunch', 'dinner', 'lunch or dinner', 'any', 'snack']
        assert meal_check
    except Exception as err1:
        print("meal time should be  'breakfast', 'lunch', 'dinner', 'lunch or dinner', 'any', or 'snack'")
        
    df = pd.read_csv(ing_file) 
    #Check that we have at least the columns amount, name and unit
    #We don't want someone to have an ingredient
    try:
        col_heads = list(df.columns[0:3])
        col_check = ['amount', 'name', 'unit'] == col_heads
        assert col_check
    except Exception as err2:
        print('Sorry, the first 3 columns should be named amount, name and unit' )
    
    pass_unit,unit = clean_unit(df.unit)
    
    if meal_check & col_check & pass_unit:
        
        df.unit = unit
        
        insert_recipe(rname, selected_cat, serv_size, meal_time, instructions)
        
        my_reps = get_recipes()
        rep_id = my_reps[rname]
        for index, row in df.iterrows():
            ing_amt, ing_name, ing_unit = row
            #Eliminate leading and trailing spaces
            ing_name = ing_name.rstrip()
            ing_name = ing_name.lstrip()
            ing_name = ing_name.lower()
            ing_unit = ing_unit.rstrip()
            ing_unit = ing_unit.lstrip()
            ing_unit = ing_unit.lower()
            cur.execute("INSERT INTO ingredients(recipe_id, ingredient_name, unit, amount) VALUES(%s, %s, %s, %s);", (rep_id,ing_name, ing_unit, ing_amt))
            con.commit()
         
        return(True)
            
    
    else:
        print("Sorry, there was an exception")
        print("The following caused problems")
        print(unit)
        return(False)

def get_lunches(num_lunch = 3):
    cur.execute("SELECT recipe_id, recipe_name FROM recipes WHERE meal_time LIKE '%lunch%' ")
    all_lunches = cur.fetchall()
    lunch_list = sample(all_lunches, num_lunch)
    
    rnames = []
    servings = [4] * num_lunch
    for lunch in lunch_list:
        lunch_id, rname = lunch
        rnames.append(rname)
    
    df = pd.DataFrame({'recipe':rnames, 'servings':servings})
    return(df)
    
   
def get_dinners(num_dinner = 2):
    cur.execute("SELECT recipe_id, recipe_name FROM recipes WHERE meal_time LIKE '%lunch%' ")
    all_lunches = cur.fetchall()
    dinner_list = sample(all_lunches, num_dinner)
    
    rnames = []
    servings = [4] * num_dinner
    for dinner in dinner_list:
        dinner_id, rname = dinner
        rnames.append(rname)
    
    df = pd.DataFrame({'recipe':rnames, 'servings':servings})
    return(df)


def add_multiple_recipes(file_of_recipes):
    df = pd.read_csv(file_of_recipes)
    essential_args = ["ing_file", "rname", "selected_cat", "serv_size", "meal_time"]
    
    not_uploaded = []

    try: 
        assert set(essential_args) <= set(list(df.columns))
        for index, row in df.iterrows():
            ing_file, rname, selected_cat, serv_size, meal_time = row
            upload = insert_recipe_via_csv(ing_file, rname, selected_cat, serv_size, meal_time)
            if not upload:
                not_uploaded.append(rname)
                  
    except Exception as err:
        print("Sorry, There was an exception")
        print("Check that the variables are named correctly")
        print("The current names are: ")
        for arg in list(df.columns):
            print(arg)
    
    if len(not_uploaded)>0:
        print("The following were not uploaded: ")
        for rep in not_uploaded:
            print(rep)
   
    
 
file="C:/Users/JustinandAbigail/Desktop/Fun_Projects/Groceries/recipes/Black_Eyed_Pea_Tacos.csv"
inst = "" 

insert_recipe_via_csv(file, "Black Eyed Pea Tacos", 'southwestern', 1, 'dinner', inst)

rfile = 'C:/Users/JustinandAbigail/Google Drive/recipes/simple_grocery_list.csv'
glist = get_grocery_list(rfile)
glist.to_csv('C:/Users/JustinandAbigail/Desktop/GroceryListNov4th.csv')


add_multiple_recipes('C:/Users/JustinandAbigail/Desktop/Fun_Projects/Groceries/recipes_2_upload.csv')
'''