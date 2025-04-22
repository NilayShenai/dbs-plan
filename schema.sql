-- Users Table (Enhanced)
CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email TEXT UNIQUE,
    age INTEGER CHECK (age >= 1 AND age <= 120),
    gender TEXT,
    height REAL CHECK (height > 0),  -- in cm
    weight REAL CHECK (weight > 0),   -- in kg
    fitness_goal TEXT,
    activity_level TEXT CHECK (activity_level IN (
        'sedentary', 
        'lightly active', 
        'moderately active', 
        'very active', 
        'extra active'
    )),
    daily_calorie_goal INTEGER CHECK (daily_calorie_goal > 0),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Meals Table (Enhanced)
CREATE TABLE Meals (
    meal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    meal_name TEXT NOT NULL,
    description TEXT,
    calories INTEGER NOT NULL CHECK (calories >= 0),
    protein REAL CHECK (protein >= 0),      -- in grams
    carbs REAL CHECK (carbs >= 0),          -- in grams
    fats REAL CHECK (fats >= 0),            -- in grams
    fiber REAL CHECK (fiber >= 0),          -- in grams
    sugar REAL CHECK (sugar >= 0),          -- in grams
    sodium REAL CHECK (sodium >= 0),        -- in mg
    dietary_preference TEXT CHECK (dietary_preference IN (
        'None',
        'Vegetarian',
        'Vegan',
        'Gluten-Free',
        'Keto',
        'Paleo'
    )),
    meal_type TEXT CHECK (meal_type IN (
        'Breakfast',
        'Lunch',
        'Dinner',
        'Snack'
    )),
    created_by INTEGER REFERENCES Users(user_id) ON DELETE SET NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- UserMealPlans Table (Enhanced)
CREATE TABLE UserMealPlans (
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    meal_id INTEGER NOT NULL REFERENCES Meals(meal_id) ON DELETE CASCADE,
    date TEXT NOT NULL,
    portion_size REAL DEFAULT 1.0 CHECK (portion_size > 0),
    meal_type TEXT CHECK (meal_type IN (
        'Breakfast',
        'Lunch',
        'Dinner',
        'Snack'
    )),
    UNIQUE(user_id, meal_id, date, meal_type)  -- Prevent duplicate meal plans
);

-- Progress Tracking Table (Enhanced)
CREATE TABLE Progress (
    progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    date TEXT NOT NULL,
    weight REAL CHECK (weight > 0),           -- in kg
    total_calories INTEGER CHECK (total_calories >= 0),
    total_protein REAL CHECK (total_protein >= 0),    -- in grams
    total_carbs REAL CHECK (total_carbs >= 0),        -- in grams
    total_fats REAL CHECK (total_fats >= 0),          -- in grams
    notes TEXT,
    UNIQUE(user_id, date)  -- One entry per user per day
);

-- Exercises Table
CREATE TABLE Exercises (
    exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_name TEXT NOT NULL UNIQUE,
    calories_burned_per_hour INTEGER CHECK (calories_burned_per_hour >= 0),
    description TEXT,
    intensity TEXT CHECK (intensity IN (
        'Low',
        'Medium',
        'High'
    )),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- User Exercises Log Table
CREATE TABLE UserExercises (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    exercise_id INTEGER NOT NULL REFERENCES Exercises(exercise_id) ON DELETE CASCADE,
    date TEXT NOT NULL,
    duration_minutes REAL CHECK (duration_minutes > 0),
    calories_burned INTEGER CHECK (calories_burned >= 0),
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX idx_user_meal_plans ON UserMealPlans(user_id, date);
CREATE INDEX idx_progress ON Progress(user_id, date);
CREATE INDEX idx_user_exercises ON UserExercises(user_id, date);