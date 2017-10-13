INSERT INTO recipes(category_id, recipe_name, serving_size, meal_time, instructions)
VALUES(6,'pb & j', 1, 'snack', 'Spread peanut butter on one slice of bread and jelly on the other slice. Then stack the bread together so that the peanut butter and jelly meet.');

INSERT INTO ingredients(recipe_id, ingredient_name, amount, unit)
VALUES
(1, 'bread', 2, 'slices'),
(1, 'peanut butter', 2, 'tablespoons'),
(1, 'jelly', 1, 'tablespoons');

