# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 12:40:58 2017

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


'''
Input: Can take a csv file with columns recipe and servings
Or can take a pandas data frame with columns recipe and servings, such
as the data frame outputed by get_lunches, get_dinners or get_weekly_meal_plan

Outputs a grocery list in a pandas data frame 
'''
    
def get_grocery_list(df, recp_file=None):
    
    if recp_file:
        rdf = pd.read_csv(recp_file)
    else:
        rdf = df
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
    
    try:
        assert set(rdf.recipe) <= set(qdf.recipe)    
        servs_for_qdf = []
        for rep in range(len(qdf)):
            lab = qdf['recipe'].values[rep]
            servs_for_qdf.append(rdict[lab])
        
        qdf['servings_requested'] = servs_for_qdf
        
        qdf = qdf.assign(new_amt = qdf.amount * qdf.servings_requested / qdf.serving_size)
        
        out_df = qdf.groupby(['ingredient_name', 'unit']).agg({'new_amt':'sum'})
        out_df = out_df.rename(columns={"new_amt":"amount"})
        
        return(out_df)
    except Exception as err:
        print("Sorry, There was an exception")
        diff = set(rdf.recipe) - set(qdf.recipe)
        print("The following recipes were not found in the database:")
        print(diff)


def get_lunches(num_lunch = 3):
    cur.execute("SELECT recipe_id, recipe_name FROM recipes WHERE meal_time = 'lunch' ")
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
    cur.execute("SELECT recipe_id, recipe_name FROM recipes WHERE meal_time = 'dinner' ")
    all_lunches = cur.fetchall()
    dinner_list = sample(all_lunches, num_dinner)
    
    rnames = []
    servings = [4] * num_dinner
    for dinner in dinner_list:
        dinner_id, rname = dinner
        rnames.append(rname)
    
    df = pd.DataFrame({'recipe':rnames, 'servings':servings})
    return(df)

'''
If grocery_list is True returns a tuple where the first element is the full meal plan
and the second element is the grocery list
Otherwise: returns the full meal plan in a pd DataFrame that can be
modified and written to.
'''
def get_weekly_meal_plan(num_lunch=3 , num_dinner=2, grocery_list= True):
    lunches = get_lunches(num_lunch)
    dinners = get_dinners(num_dinner)
    full_plan = lunches.append(dinners)
    if grocery_list:
        glist = get_grocery_list(full_plan)
        return( (full_plan,  glist) )
    else:
        return(full_plan)
        
'''
Examples
rfile = 'C:/Users/JustinandAbigail/Google Drive/recipes/simple_grocery_list.csv'
glist = get_grocery_list(rfile)
glist.to_csv('C:/Users/JustinandAbigail/Desktop/GroceryListNov4th.csv')

recipes, glist = get_weekly_meal_plan()
recipes.to_csv('C:/Users/JustinandAbigail/Desktop/ThisWeekRecipes.csv')
glist.to_csv('C:/Users/JustinandAbigail/Desktop/ThisWeekGroceryList.csv')
'''
