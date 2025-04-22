# Meal Planner & Fitness Tracker

A comprehensive web app built with Streamlit and SQLite for personalized meal planning, nutrition tracking, and fitness management. Users can set goals, plan meals, log workouts, and visualize health progress from a streamlined dashboard.

## Features

<<<<<<< HEAD
### User Authentication & Profile Management

- Secure registration and login with SHA-256 password hashing
- Unique usernames and email enforcement
- Update profile details and change password

### User Profile & Personalization

- Store personal info: age, gender, height, weight, goals, activity level
- Automatically calculate BMI and daily calorie goals (Harris-Benedict equation + TDEE)

### Meal Planning

- Plan meals by type: Breakfast, Lunch, Dinner, Snacks
- Filter by dietary preferences: Vegetarian, Vegan, Keto, etc.
- Adjust portion sizes and view nutritional breakdown (Calories, Protein, Carbs, Fats, Fiber, Sugar, Sodium)
- Add custom meals with nutritional details

### Progress Tracking

- Log daily nutrition and weight
- Visualize trends with charts (weight, macro intake, calorie goals)
- View summary statistics and compliance

### Exercise Logging

- Log workouts with duration and intensity
- Track calories burned, total time, and history

### Admin & Settings

- Update user info, goals, and password
- Real-time updates across the dashboard

## Screenshots

Add images of the dashboard, meal planner, charts, and workout logs.

## Tech Stack

- Frontend/UI: Streamlit
- Database: SQLite
- Data Visualization: Matplotlib, Seaborn
- Data Handling: Pandas
- Image Support: PIL (future feature)

## Setup & Installation

### Clone the Repository

```bash
git clone https://github.com/NilayShenai/dbs-plan.git
cd meal-planner
```

### Install Dependencies

```bash
pip install streamlit pandas matplotlib seaborn pillow cryptography
```

### Run the App

```bash
streamlit run app.py
```

App will be available at: [http://localhost:8501](http://localhost:8501)

## Usage Guide

### Registration & Login

- Sign up with a unique username and email
- Enter personal details and fitness goals
- Get a daily calorie goal suggestion

### Meal Planner

- Select a date and meal type
- Browse or add meals with nutrition info
- Adjust portion sizes and track intake

### Track Progress

- Record daily weight and nutrition
- View trends through charts

### Exercise Log

- Log exercises with time and intensity
- Review calories burned and history

### Profile Settings

- Update personal info and password

## Database Schema

- Users: Profile and authentication
- Meals: Meal data and nutrition
- UserMealPlans: Planned meals by user/date/type
- Progress: Daily logs of weight and intake
- Exercises: Exercise master list
- UserExercises: User-specific workout logs

## Security

- Passwords hashed with SHA-256
- Data stored locally in meal\_planner.db
- Input validation and foreign key constraints

## Customization

- Add dietary preferences or meal types
- Extend with new nutrition or fitness features
- Integrate with cloud services or APIs
=======
## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/NilayShenai/dbs-plan.git
   cd meal-planner
   ```
2. Install dependencies:
   ```sh
   pip install streamlit cryptography
   ```
3. Run the application:
   ```sh
   streamlit run app.py
   ```
>>>>>>> 8b8fa53aabe700c60613f6e4ad593554c3f92ea1

