-- schema.sql
CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    fitness_goal TEXT,
    daily_calorie_goal INTEGER
);

CREATE TABLE Meals (
    meal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    meal_name TEXT NOT NULL,
    calories INTEGER NOT NULL,
    protein REAL,
    carbs REAL,
    fats REAL,
    dietary_preference TEXT
);

CREATE TABLE UserMealPlans (
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    meal_id INTEGER,
    date TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (meal_id) REFERENCES Meals(meal_id)
);

CREATE TABLE Progress (
    progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    total_calories INTEGER,
    total_protein REAL,
    total_carbs REAL,
    total_fats REAL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);