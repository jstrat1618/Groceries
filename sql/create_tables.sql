DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS recipes;
DROP TABLE IF EXISTS categories;

CREATE TABLE categories(
category_id SERIAL PRIMARY KEY,
category_name VARCHAR(50) UNIQUE
    CHECK(category_name = LOWER(category_name))
);

CREATE TABLE recipes(
recipe_id SERIAL PRIMARY KEY,
category_id INTEGER REFERENCES categories (category_id),
recipe_name VARCHAR(50) UNIQUE NOT NULL 
    CHECK(recipe_name = LOWER(recipe_name)),
serving_size INTEGER,
meal_time VARCHAR(15)
    CHECK(meal_time IN ('breakfast', 'lunch', 'dinner', 'any', 'snack')),    
instructions VARCHAR(15000)
);


CREATE TABLE ingredients(
ingredient_id SERIAL PRIMARY KEY,
recipe_id INTEGER REFERENCES recipes (recipe_id),
ingredient_name VARCHAR(300) NOT NULL
    CHECK(ingredient_name = LOWER(ingredient_name)),
amount REAL,
unit VARCHAR(30)
    CHECK( (unit LIKE '%s' OR unit LIKE '%oz can' OR unit ='whole') AND unit = LOWER(unit)),
is_optional BOOL DEFAULT FALSE,    
note VARCHAR(50)
);
