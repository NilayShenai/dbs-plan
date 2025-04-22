import streamlit as st
import sqlite3
from datetime import datetime
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

# Database connection with error handling
def create_connection(db_name):
    try:
        conn = sqlite3.connect(db_name)
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        return conn
    except sqlite3.Error as e:
        st.error(f"Database connection error: {e}")
        return None

# Password hashing for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize database with improved schema
def init_db(conn):
    try:
        cursor = conn.cursor()
        
        # Users table with more fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT UNIQUE,
                age INTEGER CHECK (age >= 1 AND age <= 120),
                gender TEXT,
                height REAL CHECK (height > 0),
                weight REAL CHECK (weight > 0),
                fitness_goal TEXT,
                activity_level TEXT,
                daily_calorie_goal INTEGER CHECK (daily_calorie_goal > 0),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Meals table with more nutritional info
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Meals (
                meal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                meal_name TEXT NOT NULL,
                description TEXT,
                calories INTEGER NOT NULL CHECK (calories >= 0),
                protein REAL CHECK (protein >= 0),
                carbs REAL CHECK (carbs >= 0),
                fats REAL CHECK (fats >= 0),
                fiber REAL CHECK (fiber >= 0),
                sugar REAL CHECK (sugar >= 0),
                sodium REAL CHECK (sodium >= 0),
                dietary_preference TEXT,
                meal_type TEXT CHECK (meal_type IN ('Breakfast', 'Lunch', 'Dinner', 'Snack')),
                created_by INTEGER REFERENCES Users(user_id),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Meal plans with portion size
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS UserMealPlans (
                plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
                meal_id INTEGER NOT NULL REFERENCES Meals(meal_id) ON DELETE CASCADE,
                date TEXT NOT NULL,
                portion_size REAL DEFAULT 1.0 CHECK (portion_size > 0),
                meal_type TEXT,
                UNIQUE(user_id, meal_id, date, meal_type)
            )
        ''')
        
        # Progress tracking with weight tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Progress (
                progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
                date TEXT NOT NULL,
                weight REAL CHECK (weight > 0),
                total_calories INTEGER CHECK (total_calories >= 0),
                total_protein REAL CHECK (total_protein >= 0),
                total_carbs REAL CHECK (total_carbs >= 0),
                total_fats REAL CHECK (total_fats >= 0),
                notes TEXT,
                UNIQUE(user_id, date)
            )
        ''')
        
        # Exercise tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Exercises (
                exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercise_name TEXT NOT NULL,
                calories_burned_per_hour INTEGER CHECK (calories_burned_per_hour >= 0),
                description TEXT,
                intensity TEXT CHECK (intensity IN ('Low', 'Medium', 'High'))
            )
        ''')
        
        # User exercises
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS UserExercises (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
                exercise_id INTEGER NOT NULL REFERENCES Exercises(exercise_id) ON DELETE CASCADE,
                date TEXT NOT NULL,
                duration_minutes REAL CHECK (duration_minutes > 0),
                calories_burned INTEGER CHECK (calories_burned >= 0)
            )
        ''')
        
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database initialization error: {e}")

# User management functions
def add_user(conn, username, password, email, age, gender, height, weight, fitness_goal, activity_level, daily_calorie_goal):
    try:
        cursor = conn.cursor()
        hashed_pw = hash_password(password)
        cursor.execute('''
            INSERT INTO Users (username, password, email, age, gender, height, weight, 
                             fitness_goal, activity_level, daily_calorie_goal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, hashed_pw, email, age, gender, height, weight, 
              fitness_goal, activity_level, daily_calorie_goal))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        st.error(f"Error adding user: {e}")
        return None

def get_user_info(conn, user_id):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE user_id = ?', (user_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        st.error(f"Error fetching user info: {e}")
        return None

# Meal management functions
def add_meal(conn, meal_data):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Meals (
                meal_name, description, calories, protein, carbs, fats, 
                fiber, sugar, sodium, dietary_preference, meal_type, created_by
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', meal_data)
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        st.error(f"Error adding meal: {e}")
        return None

def get_meal_by_id(conn, meal_id):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Meals WHERE meal_id = ?', (meal_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        st.error(f"Error fetching meal: {e}")
        return None

# Meal planning functions
def plan_meal(conn, user_id, meal_id, date, portion_size=1.0, meal_type=None):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO UserMealPlans (user_id, meal_id, date, portion_size, meal_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, meal_id, date, portion_size, meal_type))
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Error planning meal: {e}")
        return False

def get_user_meal_plan(conn, user_id, date):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.meal_id, m.meal_name, m.calories, m.protein, m.carbs, m.fats, 
                   up.portion_size, up.meal_type, m.dietary_preference
            FROM UserMealPlans up
            JOIN Meals m ON up.meal_id = m.meal_id
            WHERE up.user_id = ? AND up.date = ?
            ORDER BY up.meal_type
        ''', (user_id, date))
        return cursor.fetchall()
    except sqlite3.Error as e:
        st.error(f"Error fetching meal plan: {e}")
        return []

# Progress tracking functions
def track_progress(conn, user_id, date, weight=None, total_calories=None, 
                  total_protein=None, total_carbs=None, total_fats=None, notes=None):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO Progress (
                user_id, date, weight, total_calories, 
                total_protein, total_carbs, total_fats, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, date, weight, total_calories, 
              total_protein, total_carbs, total_fats, notes))
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Error tracking progress: {e}")
        return False

def get_user_progress(conn, user_id, start_date=None, end_date=None):
    try:
        cursor = conn.cursor()
        if start_date and end_date:
            cursor.execute('''
                SELECT date, weight, total_calories, total_protein, 
                       total_carbs, total_fats, notes
                FROM Progress
                WHERE user_id = ? AND date BETWEEN ? AND ?
                ORDER BY date
            ''', (user_id, start_date, end_date))
        else:
            cursor.execute('''
                SELECT date, weight, total_calories, total_protein, 
                       total_carbs, total_fats, notes
                FROM Progress
                WHERE user_id = ?
                ORDER BY date
            ''', (user_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        st.error(f"Error fetching progress: {e}")
        return []

# Exercise functions
def add_exercise(conn, exercise_name, calories_burned_per_hour, description, intensity):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Exercises (exercise_name, calories_burned_per_hour, description, intensity)
            VALUES (?, ?, ?, ?)
        ''', (exercise_name, calories_burned_per_hour, description, intensity))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        st.error(f"Error adding exercise: {e}")
        return None

def log_exercise(conn, user_id, exercise_id, date, duration_minutes, calories_burned):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO UserExercises (user_id, exercise_id, date, duration_minutes, calories_burned)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, exercise_id, date, duration_minutes, calories_burned))
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Error logging exercise: {e}")
        return False

# Authentication functions
def authenticate_user(conn, username, password):
    try:
        cursor = conn.cursor()
        hashed_pw = hash_password(password)
        cursor.execute('''
            SELECT user_id, username FROM Users WHERE username = ? AND password = ?
        ''', (username, hashed_pw))
        return cursor.fetchone()
    except sqlite3.Error as e:
        st.error(f"Authentication error: {e}")
        return None

# Helper functions
def calculate_bmi(height, weight):
    if height > 0 and weight > 0:
        return weight / ((height / 100) ** 2)
    return None

def calculate_daily_calorie_goal(age, gender, height, weight, activity_level, fitness_goal):
    # Basic Harris-Benedict equation for BMR
    if gender.lower() == 'male':
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    
    # Activity level multipliers
    activity_multipliers = {
        'sedentary': 1.2,
        'lightly active': 1.375,
        'moderately active': 1.55,
        'very active': 1.725,
        'extra active': 1.9
    }
    
    tdee = bmr * activity_multipliers.get(activity_level.lower(), 1.2)
    
    # Adjust based on fitness goal
    if fitness_goal.lower() == 'weight loss':
        return tdee * 0.8  # 20% deficit
    elif fitness_goal.lower() == 'muscle gain':
        return tdee * 1.1  # 10% surplus
    else:  # maintenance
        return tdee

# Streamlit UI Components
def login_form(conn):
    with st.form("Login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            user = authenticate_user(conn, username, password)
            if user:
                st.session_state.user_id = user[0]
                st.session_state.username = user[1]
                st.success(f"Welcome back, {user[1]}!")
                return True
            else:
                st.error("Invalid username or password")
    return False

def registration_form(conn):
    with st.form("Registration"):
        st.subheader("Create Your Account")
        username = st.text_input("Username (must be unique)")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=1, max_value=120, value=25)
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=70.0)
        
        fitness_goal = st.selectbox("Fitness Goal", ["Weight Loss", "Muscle Gain", "Maintenance"])
        activity_level = st.selectbox("Activity Level", [
            "Sedentary (little or no exercise)",
            "Lightly Active (light exercise 1-3 days/week)",
            "Moderately Active (moderate exercise 3-5 days/week)",
            "Very Active (hard exercise 6-7 days/week)",
            "Extra Active (very hard exercise & physical job)"
        ])
        
        # Calculate suggested calorie goal
        activity_level_key = activity_level.split(" ")[0].lower()
        suggested_calories = int(calculate_daily_calorie_goal(
            age, gender, height, weight, activity_level_key, fitness_goal
        ))
        
        daily_calorie_goal = st.number_input(
            "Daily Calorie Goal", 
            min_value=1000, 
            max_value=10000, 
            value=suggested_calories
        )
        
        if st.form_submit_button("Register"):
            if password != confirm_password:
                st.error("Passwords do not match!")
                return False
            
            if len(password) < 8:
                st.error("Password must be at least 8 characters long")
                return False
                
            user_id = add_user(
                conn, username, password, email, age, gender, height, weight,
                fitness_goal, activity_level_key, daily_calorie_goal
            )
            
            if user_id:
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.success("Account created successfully!")
                return True
            else:
                st.error("Username or email already exists!")
    return False

def dashboard(conn, user_id):
    user_info = get_user_info(conn, user_id)
    if not user_info:
        st.error("Could not load user information")
        return
    
    st.title(f"Welcome, {user_info[1]}!")
    
    # User stats overview
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Weight", f"{user_info[7]} kg")
    with col2:
        bmi = calculate_bmi(user_info[6], user_info[7])
        st.metric("BMI", f"{bmi:.1f}")
    with col3:
        st.metric("Daily Calorie Goal", user_info[10])
    
    # Navigation
    menu = [
        "Meal Planner", "Add Meal", "Track Progress", 
        "View Progress", "Exercise Log", "Profile Settings"
    ]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Meal Planner":
        meal_planner(conn, user_id)
    elif choice == "Add Meal":
        add_meal_form(conn, user_id)
    elif choice == "Track Progress":
        track_progress_form(conn, user_id)
    elif choice == "View Progress":
        view_progress(conn, user_id)
    elif choice == "Exercise Log":
        exercise_log(conn, user_id)
    elif choice == "Profile Settings":
        profile_settings(conn, user_id)

def meal_planner(conn, user_id):
    st.header("Meal Planner")
    
    date = st.date_input("Select Date", datetime.today())
    dietary_preference = st.selectbox("Dietary Preference", 
                                    ["None", "Vegetarian", "Vegan", "Gluten-Free", "Keto", "Paleo"])
    
    # Get meals filtered by preference
    cursor = conn.cursor()
    if dietary_preference == "None":
        cursor.execute('SELECT meal_id, meal_name, calories, meal_type FROM Meals ORDER BY meal_type')
    else:
        cursor.execute('''
            SELECT meal_id, meal_name, calories, meal_type 
            FROM Meals 
            WHERE dietary_preference = ? 
            ORDER BY meal_type
        ''', (dietary_preference,))
    meals = cursor.fetchall()
    
    # Group by meal type
    meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]
    planned_meals = {mt: [] for mt in meal_types}
    
    # Get already planned meals for the day
    planned = get_user_meal_plan(conn, user_id, date)
    for meal in planned:
        meal_type = meal[7] if meal[7] else "Uncategorized"
        if meal_type in planned_meals:
            planned_meals[meal_type].append(meal)
    
    # Display planner
    for meal_type in meal_types:
        st.subheader(meal_type)
        
        # Show planned meals
        if planned_meals[meal_type]:
            for meal in planned_meals[meal_type]:
                cols = st.columns([3, 1, 1, 1])
                with cols[0]:
                    st.write(f"**{meal[1]}** (Portion: {meal[6]}x)")
                with cols[1]:
                    st.write(f"{int(meal[2] * meal[6])} kcal")
                with cols[2]:
                    st.write(f"{meal[3]*meal[6]:.1f}g protein")
                with cols[3]:
                    if st.button("Remove", key=f"remove_{meal[0]}_{meal_type}"):
                        remove_planned_meal(conn, user_id, meal[0], date, meal_type)
                        st.rerun()
        
        # Add new meal
        with st.expander(f"Add {meal_type}"):
            filtered_meals = [m for m in meals if m[3] == meal_type]
            if filtered_meals:
                selected_meal = st.selectbox(
                    f"Select {meal_type} Meal", 
                    filtered_meals, 
                    format_func=lambda x: f"{x[1]} ({x[2]} kcal)",
                    key=f"select_{meal_type}"
                )
                portion_size = st.slider(
                    "Portion Size", 
                    min_value=0.5, 
                    max_value=3.0, 
                    value=1.0, 
                    step=0.1,
                    key=f"portion_{meal_type}"
                )
                if st.button(f"Add {meal_type}", key=f"add_{meal_type}"):
                    plan_meal(
                        conn, user_id, selected_meal[0], date, 
                        portion_size, meal_type
                    )
                    st.success(f"{selected_meal[1]} added to {meal_type}!")
                    st.rerun()
            else:
                st.warning(f"No {meal_type.lower()} meals available")
    
    # Daily summary
    st.subheader("Daily Summary")
    planned_meals = get_user_meal_plan(conn, user_id, date)
    if planned_meals:
        total_calories = sum(m[2] * m[6] for m in planned_meals)
        total_protein = sum(m[3] * m[6] for m in planned_meals)
        total_carbs = sum(m[4] * m[6] for m in planned_meals)
        total_fats = sum(m[5] * m[6] for m in planned_meals)
        
        cols = st.columns(4)
        cols[0].metric("Total Calories", f"{total_calories:.0f}")
        cols[1].metric("Protein", f"{total_protein:.1f}g")
        cols[2].metric("Carbs", f"{total_carbs:.1f}g")
        cols[3].metric("Fats", f"{total_fats:.1f}g")
        
        # Save to progress
        if st.button("Save Daily Plan"):
            track_progress(
                conn, user_id, date, 
                total_calories=total_calories,
                total_protein=total_protein,
                total_carbs=total_carbs,
                total_fats=total_fats
            )
            st.success("Daily plan saved to progress!")
    else:
        st.info("No meals planned for this day")

def remove_planned_meal(conn, user_id, meal_id, date, meal_type):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM UserMealPlans 
            WHERE user_id = ? AND meal_id = ? AND date = ? AND meal_type = ?
        ''', (user_id, meal_id, date, meal_type))
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Error removing meal: {e}")
        return False

def add_meal_form(conn, user_id):
    st.header("Add New Meal")
    
    with st.form("Add Meal"):
        meal_name = st.text_input("Meal Name")
        description = st.text_area("Description")
        
        col1, col2 = st.columns(2)
        with col1:
            calories = st.number_input("Calories", min_value=0, value=300)
            protein = st.number_input("Protein (g)", min_value=0.0, value=0.0, step=0.1)
            carbs = st.number_input("Carbs (g)", min_value=0.0, value=0.0, step=0.1)
        with col2:
            fats = st.number_input("Fats (g)", min_value=0.0, value=0.0, step=0.1)
            fiber = st.number_input("Fiber (g)", min_value=0.0, value=0.0, step=0.1)
            sugar = st.number_input("Sugar (g)", min_value=0.0, value=0.0, step=0.1)
        
        dietary_preference = st.selectbox("Dietary Preference", 
                                        ["None", "Vegetarian", "Vegan", "Gluten-Free", "Keto", "Paleo"])
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        
        if st.form_submit_button("Add Meal"):
            meal_data = (
                meal_name, description, calories, protein, carbs, fats,
                fiber, sugar, 0, dietary_preference, meal_type, user_id
            )
            if add_meal(conn, meal_data):
                st.success("Meal added successfully!")
            else:
                st.error("Failed to add meal")

def track_progress_form(conn, user_id):
    st.header("Track Daily Progress")
    date = st.date_input("Date", datetime.today())
    
    user_info = get_user_info(conn, user_id)
    current_weight = float(user_info[7])  # Ensure float type
    
    with st.form("Progress Tracking"):
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=current_weight, step=0.1)
        
        meal_plan = get_user_meal_plan(conn, user_id, date)
        if meal_plan:
            total_calories = float(sum(m[2] * m[6] for m in meal_plan))
            total_protein = float(sum(m[3] * m[6] for m in meal_plan))
            total_carbs = float(sum(m[4] * m[6] for m in meal_plan))
            total_fats = float(sum(m[5] * m[6] for m in meal_plan))
        else:
            total_calories, total_protein, total_carbs, total_fats = 0.0, 0.0, 0.0, 0.0
        
        col1, col2 = st.columns(2)
        with col1:
            calories = st.number_input("Calories Consumed", min_value=0, value=int(total_calories))
            protein = st.number_input("Protein (g)", min_value=0.0, value=total_protein, step=0.1)
        with col2:
            carbs = st.number_input("Carbs (g)", min_value=0.0, value=total_carbs, step=0.1)
            fats = st.number_input("Fats (g)", min_value=0.0, value=total_fats, step=0.1)
        
        notes = st.text_area("Notes")
        
        submitted = st.form_submit_button("Save Progress")
        if submitted:
            if track_progress(
                conn, user_id, date, weight, calories, protein, carbs, fats, notes
            ):
                st.success("Progress saved successfully!")
                st.rerun()
            else:
                st.error("Failed to save progress")


def view_progress(conn, user_id):
    st.header("Your Progress")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.today() - pd.Timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.today())
    
    progress_data = get_user_progress(conn, user_id, start_date, end_date)
    
    if not progress_data:
        st.warning("No progress data available for the selected period")
        return
    
    df = pd.DataFrame(progress_data, columns=[
        "date", "weight", "calories", "protein", "carbs", "fats", "notes"
    ])
    df['date'] = pd.to_datetime(df['date'])
    
    st.subheader("Progress Summary")
    latest = df.iloc[-1]
    oldest = df.iloc[0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        weight_diff = latest['weight'] - oldest['weight']
        st.metric("Current Weight", f"{latest['weight']} kg", 
                 f"{weight_diff:+.1f} kg")
    with col2:
        avg_calories = df['calories'].mean()
        st.metric("Avg Daily Calories", f"{avg_calories:.0f}")
    with col3:
        compliance = (df['calories'] > 0).mean() * 100
        st.metric("Tracking Compliance", f"{compliance:.0f}%")
    
    st.subheader("Progress Charts")
    
    tab1, tab2, tab3 = st.tabs(["Weight Trend", "Nutrition", "Calories"])
    
    with tab1:
        if len(df) > 1:
            fig, ax = plt.subplots()
            sns.lineplot(data=df, x='date', y='weight', marker='o', ax=ax)
            ax.set_title("Weight Trend")
            ax.set_xlabel("Date")
            ax.set_ylabel("Weight (kg)")
            st.pyplot(fig)
        else:
            st.warning("Need at least 2 data points to show trend")
    
    with tab2:
        if len(df) > 1:
            fig, ax = plt.subplots()
            df_melted = df.melt(id_vars=['date'], 
                               value_vars=['protein', 'carbs', 'fats'],
                               var_name='macro', value_name='grams')
            sns.lineplot(data=df_melted, x='date', y='grams', hue='macro', ax=ax)
            ax.set_title("Macronutrient Intake")
            ax.set_xlabel("Date")
            ax.set_ylabel("Grams")
            st.pyplot(fig)
        else:
            st.warning("Need at least 2 data points to show trend")
    
    with tab3:
        if len(df) > 1:
            fig, ax = plt.subplots()
            sns.barplot(data=df, x='date', y='calories', ax=ax)
            ax.set_title("Daily Calorie Intake")
            ax.set_xlabel("Date")
            ax.set_ylabel("Calories")
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.warning("Need at least 2 data points to show trend")
    
    st.subheader("Detailed Data")
    st.dataframe(df.sort_values('date', ascending=False))

def exercise_log(conn, user_id):
    st.header("Exercise Log")
    
    tab1, tab2 = st.tabs(["Log Exercise", "Exercise History"])
    
    with tab1:
        date = st.date_input("Exercise Date", datetime.today())
        
        cursor = conn.cursor()
        cursor.execute('SELECT exercise_id, exercise_name FROM Exercises ORDER BY exercise_name')
        exercises = cursor.fetchall()
        
        if exercises:
            selected_exercise = st.selectbox(
                "Select Exercise", 
                exercises, 
                format_func=lambda x: x[1]
            )
            
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=300, value=30)
            
            cursor.execute('''
                SELECT calories_burned_per_hour 
                FROM Exercises 
                WHERE exercise_id = ?
            ''', (selected_exercise[0],))
            calories_per_hour = cursor.fetchone()[0]
            calories_burned = int(calories_per_hour * (duration / 60))
            
            st.write(f"Estimated calories burned: {calories_burned}")
            
            if st.button("Log Exercise"):
                if log_exercise(
                    conn, user_id, selected_exercise[0], date, duration, calories_burned
                ):
                    st.success("Exercise logged successfully!")
                else:
                    st.error("Failed to log exercise")
        else:
            st.warning("No exercises available in database")
    
    with tab2:
        cursor.execute('''
            SELECT e.exercise_name, ue.date, ue.duration_minutes, ue.calories_burned
            FROM UserExercises ue
            JOIN Exercises e ON ue.exercise_id = e.exercise_id
            WHERE ue.user_id = ?
            ORDER BY ue.date DESC
        ''', (user_id,))
        history = cursor.fetchall()
        
        if history:
            df = pd.DataFrame(history, columns=["Exercise", "Date", "Duration (min)", "Calories Burned"])
            st.dataframe(df)
            
            st.subheader("Exercise Summary")
            total_calories = df["Calories Burned"].sum()
            total_minutes = df["Duration (min)"].sum()
            avg_calories = df["Calories Burned"].mean()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Exercises", len(df))
            col2.metric("Total Calories Burned", total_calories)
            col3.metric("Total Exercise Time", f"{total_minutes} minutes")
        else:
            st.info("No exercise history available")

def profile_settings(conn, user_id):
    st.header("Profile Settings")
    user_info = get_user_info(conn, user_id)
    if not user_info:
        st.error("Could not load user information")
        return
    
    with st.form("Update Profile"):
        st.subheader("Basic Information")
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Username", value=user_info[1])
            new_age = st.number_input("Age", min_value=1, max_value=120, value=int(user_info[4]))
            new_height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=float(user_info[6]), step=0.1)
        with col2:
            new_email = st.text_input("Email", value=user_info[3])
            new_gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                    index=["Male", "Female", "Other"].index(user_info[5]))
            new_weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=float(user_info[7]), step=0.1)
        
        st.subheader("Fitness Goals")
        new_fitness_goal = st.selectbox(
            "Fitness Goal", 
            ["Weight Loss", "Muscle Gain", "Maintenance"],
            index=["Weight Loss", "Muscle Gain", "Maintenance"].index(user_info[8])
        )
        new_activity_level = st.selectbox(
            "Activity Level", 
            ["sedentary", "lightly active", "moderately active", "very active", "extra active"],
            index=["sedentary", "lightly active", "moderately active", "very active", "extra active"].index(user_info[9])
        )
        
        suggested_calories = int(calculate_daily_calorie_goal(
            new_age, new_gender, new_height, new_weight, new_activity_level, new_fitness_goal
        ))
        new_calorie_goal = st.number_input(
            "Daily Calorie Goal", 
            min_value=1000, 
            max_value=10000, 
            value=suggested_calories
        )
        
        st.subheader("Change Password")
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submitted = st.form_submit_button("Update Profile")
        if submitted:
            if new_password:
                if not authenticate_user(conn, user_info[1], current_password):
                    st.error("Current password is incorrect")
                    return
                
                if new_password != confirm_password:
                    st.error("New passwords do not match")
                    return
                
                if len(new_password) < 8:
                    st.error("Password must be at least 8 characters")
                    return
            
            try:
                cursor = conn.cursor()
                if new_password:
                    hashed_pw = hash_password(new_password)
                    cursor.execute('''
                        UPDATE Users 
                        SET username = ?, email = ?, age = ?, gender = ?, 
                            height = ?, weight = ?, fitness_goal = ?, 
                            activity_level = ?, daily_calorie_goal = ?, password = ?
                        WHERE user_id = ?
                    ''', (new_username, new_email, new_age, new_gender, new_height,
                         new_weight, new_fitness_goal, new_activity_level, 
                         new_calorie_goal, hashed_pw, user_id))
                else:
                    cursor.execute('''
                        UPDATE Users 
                        SET username = ?, email = ?, age = ?, gender = ?, 
                            height = ?, weight = ?, fitness_goal = ?, 
                            activity_level = ?, daily_calorie_goal = ?
                        WHERE user_id = ?
                    ''', (new_username, new_email, new_age, new_gender, new_height,
                         new_weight, new_fitness_goal, new_activity_level, 
                         new_calorie_goal, user_id))
                
                conn.commit()
                st.session_state.username = new_username
                st.success("Profile updated successfully!")
                st.rerun()
            except sqlite3.Error as e:
                st.error(f"Error updating profile: {e}")
def main():
    
    st.set_page_config(
        page_title="Meal Planner & Fitness Tracker",
        page_icon="🍏",
        layout="wide"
    )
    st.markdown(
        """
        <style>
            .github-icon {
                position: absolute;
                top: 15px;
                right: 15px;
                z-index: 999;
                opacity: 0.7;
                transition: opacity 0.2s;
            }
            .github-icon:hover {
                opacity: 1;
            }
        </style>
        <div class="github-icon">
            <a href="https://github.com/NilayShenai/dbs-plan" target="_blank">
                <svg width="24" height="24" viewBox="0 0 16 16" fill="#6b7280">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    conn = create_connection("meal_planner.db")
    if not conn:
        st.error("Failed to connect to database")
        return
    
    init_db(conn)
    
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None
     
    st.title("Meal Planner & Fitness Tracker")
    
    if st.session_state.user_id:
        dashboard(conn, st.session_state.user_id)
    else:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            if login_form(conn):
                st.rerun()
        
        with tab2:
            if registration_form(conn):
                st.rerun()
    st.markdown(
        """
        <style>
            .footer {
                text-align: center;
                color: #6b7280;
                font-size: 0.8rem;
                padding: 10px;
                margin-top: 2rem;
            }
        </style>
        <div class="footer">Created by Nilay D. Shenai</div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()