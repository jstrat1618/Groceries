# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 12:56:59 2017

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

def insert_recipe(rname):
    cat_dict = get_recipe_categories()
    
    print("AVAILABLE CATEGORIES")
    all_cats = cat_dict.keys()
    for cat in all_cats:
        print(cat)
    
    selected_cat = input('Please input a category from the available categories ')
    selected_cat = selected_cat.lower() 
    
    while selected_cat not in all_cats:
        print("Sorry, pleases select from the available categories")
        print("AVAILABLE CATEGORIES")
        for cat in all_cats:
            print(cat)
        selected_cat = input('Please input a category from the available categories ')
        selected_cat = selected_cat.lower()
    
    
    cat_id = cat_dict[selected_cat]
    

    
    serv_size = input('What is the serving size? [Enter an integer] ')
    serv_size = int(serv_size)
    instructions = input('Please input instructions ')
             
    cur.execute("INSERT INTO recipes(category_id, recipe_name, serving_size, instructions) VALUES(%s, %s, %s, %s);", (cat_id,rname, serv_size, instructions))
    con.commit()


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




def insert_ingredients(rname):
    
    rname = rname.lower()
    
    my_reps = get_recipes()

    rep_id = my_reps[rname] 
    
    
    cont = 'y'
    
    while cont.lower() in ['y', 'yes', 'yeah']:
        ing_name = input("Enter the name of the ingredient ")
        ing_unit = input("Enter the units of the ingredient. Please input whole for a whole unit, for example 1 avacado or input a unit ending in 's' for example tablespoons")
        ing_amt = input("Enter the amount of the ingredient ")    
        cur.execute("INSERT INTO ingredients(recipe_id, ingredient_name, unit, amount) VALUES(%s, %s, %s, %s);", (rep_id,ing_name, ing_unit, ing_amt))
        con.commit()

        cont = input('Would you like to insert another ingredient? Enter y/n ')
    

def get_grocery_list():
    recp_file = input('Please input the file path to the grocery list. Make sure it is formatted as described in the README ')
    
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

    
print('These are the current options:')
print('Option 1: Insert recipe, serving size and instructions')
print('Option 2: Insert ingredients for an existing recipe')
print('Option 3: Insert recipe, serving size, instructions and ingredients')

opt =  input('Please input the appropriate option 1,2, or 3? ')
opt = opt.replace(' ', '')
while opt not in ['1', '2', '3']:
    print("Sorry invalid option")
    print("Make sure you input 1, 2 or 3 ")
    opt =  input('Please input the appropriate option 1,2, or 3? ')

opt = int(opt)

rname = input("What is the name of the recipe? ")
rname = rname.lower()
    
if opt == 1:
    insert_recipe(rname)
elif opt == 2:
    insert_ingredients(rname)
else:
    insert_recipe(rname)
    insert_ingredients(rname)


print('Done!')    