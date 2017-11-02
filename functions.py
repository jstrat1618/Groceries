# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 15:12:50 2017

@author: JustinandAbigail
"""

import psycopg2 as pg2
import pandas as pd

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
    
    print("AVAILABLE CATEGORIES")
    all_cats = cat_dict.keys()
    for cat in all_cats:
        print(cat)
    
    while selected_cat not in all_cats:
        print("Sorry, pleases select from the available categories")
        print("AVAILABLE CATEGORIES")
        for cat in all_cats:
            print(cat)
        selected_cat = input('Please input a category from the available categories ')
        selected_cat = selected_cat.lower()
    
    
    cat_id = cat_dict[selected_cat]
    cur.execute("INSERT INTO recipes(category_id, recipe_name, serving_size, meal_time, instructions) VALUES(%s, %s, %s, %s, %s);", (cat_id, rname, serv_size, meal_time, instructions))
    con.commit()

def get_grocery_list(recp_file):
    
    # Query the recipe database and obtain a data frame, qrdf
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
    
    try:
        unit_checks=[]
        for index, row in df.iterrows():
            ing_amt, ing_name, ing_unit = row
            #Eliminate leading and trailing spaces
            ing_unit = ing_unit.rstrip()
            ing_unit = ing_unit.lstrip()
            unit_check = ing_unit in ['oz can', 'whole'] or ing_unit[-1] == 's'
            unit_checks.append(unit_check)
            assert unit_check
    except Exception as err2:
        print(ing_unit +' must be either "whole", "oz can" or end in "s"')
            
    if meal_check & col_check & all(unit_checks):
        
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
    
    else:
        print("Sorry, there was an exception")
#insert_recipe_via_csv(ing_file = 'C:/Users/JustinandAbigail/Desktop/Fun_Projects/Groceries/recipes/pb toast.csv', rname='pb toast', selected_cat = 'quick and easy', serv_size=1, meal_time='breakfast')        
file = 'C:/Users/JustinandAbigail/Google Drive/recipes/Buffalo Ranch Sliders.csv'
inst = "" 

insert_recipe_via_csv(file, 'Buffalo Ranch Sliders', 'barbeque', 4, 'dinner', inst)
