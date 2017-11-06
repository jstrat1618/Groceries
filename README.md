# Purpose
I created this project in part to manage my groceries and to practice my python, SQL, and interfacing the two.

# Getting a Meal Plan and a Grocery List
There are two options:
1.) Input a grocery list in a two column csv file with headers "recipe" and "servings". See grocery_list.csv for practice.
2.) Generate a meal plan randomly by
recipes, glist = get_weekly_meal_plan()
recipes.to_csv('C:/Users/JustinandAbigail/Desktop/ThisWeekRecipes.csv')
glist.to_csv('C:/Users/JustinandAbigail/Desktop/ThisWeekGroceryList.csv')

The defaults are set by get_weekly_meal_plan to generate 2 lunches and 3 dinners. This set to give you lunches and dinner for the weekdays M-F; though one lunch should serve as a lunch and as a dinner. The only difference between lunches is that lunches should be relatively easier to pack.

# SQL
You can find the queries to create the tables in the SQL folder. You can also find queries to insert categories and two recipes (pb & j and a hummus veggie sandwich).

