import streamlit as st
import sqlite3
from datetime import datetime

# Database connection
def create_connection(db_name):
    conn = sqlite3.connect(db_name)
    return conn

# Initialize database
def init_db(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            fitness_goal TEXT,
            daily_calorie_goal INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Meals (
            meal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_name TEXT NOT NULL,
            calories INTEGER NOT NULL,
            protein REAL,
            carbs REAL,
            fats REAL,
            dietary_preference TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserMealPlans (
            plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            meal_id INTEGER,
            date TEXT,
            FOREIGN KEY (user_id) REFERENCES Users(user_id),
            FOREIGN KEY (meal_id) REFERENCES Meals(meal_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Progress (
            progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            total_calories INTEGER,
            total_protein REAL,
            total_carbs REAL,
            total_fats REAL,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    ''')
    conn.commit()

# Add a new user
def add_user(conn, username, password, age, gender, fitness_goal, daily_calorie_goal):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Users (username, password, age, gender, fitness_goal, daily_calorie_goal)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, password, age, gender, fitness_goal, daily_calorie_goal))
    conn.commit()

# Add a new meal
def add_meal(conn, meal_name, calories, protein, carbs, fats, dietary_preference):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Meals (meal_name, calories, protein, carbs, fats, dietary_preference)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (meal_name, calories, protein, carbs, fats, dietary_preference))
    conn.commit()

# Plan a meal for a user
def plan_meal(conn, user_id, meal_id, date):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO UserMealPlans (user_id, meal_id, date)
        VALUES (?, ?, ?)
    ''', (user_id, meal_id, date))
    conn.commit()

# Fetch meals based on dietary preference
def fetch_meals(conn, dietary_preference):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM Meals WHERE dietary_preference = ?
    ''', (dietary_preference,))
    return cursor.fetchall()

# Fetch user's meal plan
def fetch_user_meal_plan(conn, user_id, date):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT Meals.meal_name, Meals.calories, Meals.protein, Meals.carbs, Meals.fats
        FROM UserMealPlans
        JOIN Meals ON UserMealPlans.meal_id = Meals.meal_id
        WHERE UserMealPlans.user_id = ? AND UserMealPlans.date = ?
    ''', (user_id, date))
    return cursor.fetchall()

# Track user progress
def track_progress(conn, user_id, date, total_calories, total_protein, total_carbs, total_fats):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Progress (user_id, date, total_calories, total_protein, total_carbs, total_fats)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, date, total_calories, total_protein, total_carbs, total_fats))
    conn.commit()

# Fetch user progress
def fetch_progress(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT date, total_calories, total_protein, total_carbs, total_fats
        FROM Progress
        WHERE user_id = ?
        ORDER BY date
    ''', (user_id,))
    return cursor.fetchall()

# Authenticate user
def authenticate_user(conn, username, password):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_id FROM Users WHERE username = ? AND password = ?
    ''', (username, password))
    return cursor.fetchone()

# Streamlit App
def main():
    st.title("MEAL PLANNER")
    conn = create_connection("meal_planner.db")
    init_db(conn)

    # Session state for user authentication
    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    menu = ["Home", "Sign Up", "Login", "Add Meal", "Plan Meals", "View Meal Plan", "Track Progress"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("MEAL PLANNING TEST")
        st.write("STILL TESTING")

    elif choice == "Sign Up":
        st.subheader("Create an Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        age = st.number_input("Age", min_value=1, max_value=100)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        fitness_goal = st.selectbox("Fitness Goal", ["Weight Loss", "Muscle Gain", "Maintenance"])
        daily_calorie_goal = st.number_input("Daily Calorie Goal", min_value=0)
        if st.button("Sign Up"):
            add_user(conn, username, password, age, gender, fitness_goal, daily_calorie_goal)
            st.success("Account created successfully!")

    elif choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = authenticate_user(conn, username, password)
            if user:
                st.session_state.user_id = user[0]
                st.success(f"Logged in as {username}")
            else:
                st.error("Invalid username or password")

    elif choice == "Add Meal":
        if st.session_state.user_id:
            st.subheader("Add a New Meal")
            meal_name = st.text_input("Meal Name")
            calories = st.number_input("Calories", min_value=0)
            protein = st.number_input("Protein (g)", min_value=0.0)
            carbs = st.number_input("Carbs (g)", min_value=0.0)
            fats = st.number_input("Fats (g)", min_value=0.0)
            dietary_preference = st.selectbox("Dietary Preference", ["Vegetarian", "Gluten-Free", "Keto", "None"])
            if st.button("Add Meal"):
                add_meal(conn, meal_name, calories, protein, carbs, fats, dietary_preference)
                st.success("Meal added successfully!")
        else:
            st.warning("Please login to add meals.")

    elif choice == "Plan Meals":
        if st.session_state.user_id:
            st.subheader("Plan Your Meals")
            date = st.date_input("Date")
            dietary_preference = st.selectbox("Dietary Preference", ["Vegetarian", "Gluten-Free", "Keto", "None"])
            meals = fetch_meals(conn, dietary_preference)
            meal_options = {meal[1]: meal[0] for meal in meals}  # {meal_name: meal_id}
            selected_meal = st.selectbox("Select a Meal", list(meal_options.keys()))
            if st.button("Plan Meal"):
                meal_id = meal_options[selected_meal]
                plan_meal(conn, st.session_state.user_id, meal_id, date)
                st.success("Meal planned successfully!")
        else:
            st.warning("Please login to plan meals.")

    elif choice == "View Meal Plan":
        if st.session_state.user_id:
            st.subheader("View Your Meal Plan")
            date = st.date_input("Date")
            if st.button("View Plan"):
                meal_plan = fetch_user_meal_plan(conn, st.session_state.user_id, date)
                if meal_plan:
                    st.write("Your Meal Plan:")
                    total_calories = 0
                    total_protein = 0
                    total_carbs = 0
                    total_fats = 0
                    for meal in meal_plan:
                        st.write(f"Meal: {meal[0]}, Calories: {meal[1]}, Protein: {meal[2]}g, Carbs: {meal[3]}g, Fats: {meal[4]}g")
                        total_calories += meal[1]
                        total_protein += meal[2]
                        total_carbs += meal[3]
                        total_fats += meal[4]
                    st.write(f"Total Calories: {total_calories}, Total Protein: {total_protein}g, Total Carbs: {total_carbs}g, Total Fats: {total_fats}g")
                    track_progress(conn, st.session_state.user_id, date, total_calories, total_protein, total_carbs, total_fats)
                else:
                    st.warning("No meals planned for this date.")
        else:
            st.warning("Please login to view your meal plan.")

    elif choice == "Track Progress":
        if st.session_state.user_id:
            st.subheader("Track Your Progress")
            progress = fetch_progress(conn, st.session_state.user_id)
            if progress:
                st.write("Your Progress Over Time:")
                for entry in progress:
                    st.write(f"Date: {entry[0]}, Calories: {entry[1]}, Protein: {entry[2]}g, Carbs: {entry[3]}g, Fats: {entry[4]}g")
            else:
                st.warning("No progress data available.")
        else:
            st.warning("Please login to track your progress.")

if __name__ == "__main__":
    main()