INSERT INTO recipes(category_id, recipe_name, serving_size, meal_time, instructions)
VALUES(6,'hummus veggie sandwich', 1, 'lunch or dinner', 'Spread the hummus on both sides of the bread. Slice the cucumber and tomatoe. Throw on cucumbers, tomatoes, shredded carrot and spinach.');

INSERT INTO ingredients(recipe_id, ingredient_name, amount, unit)
VALUES
(2, 'bread', 2, 'slices'),
(2, 'cucumber', 0.25, 'whole'),
(2, 'tomatoe', 1, 'whole'),
(2, 'shredded carrot', 0.25, 'cups'),
(2, 'spinach', 0.5, 'cups');