# DBMS_miniproject_VGUMSapp_PES2UG23CS565_PES2UG23CS546
Video Game User Management System (VGUMS)

A Python Tkinter + MySQL database application for managing users, roles, games, and player progress.

⭐ Overview

The Video Game User Management System (VGUMS) is a full-stack database application that allows administrators and players to interact with a gaming platform.
It provides functionalities such as:

User registration & authentication

Automatic role assignment

Game creation and management

Tracking player scores, levels, and last-played timestamps

Leaderboards and admin reports

Stored procedures, triggers, functions, and views

A complete graphical interface using Tkinter

This project demonstrates a fully normalized, secure, modular, and GUI-integrated database system.

🧰 Tools & Technologies Used

• Python 3
• Tkinter & Tkinter.ttk – GUI framework for widgets, Treeviews, Comboboxes, tab layouts
• Tkinter.messagebox – Popup alerts, warnings, confirmations
• mysql-connector-python – Database connector for running SQL queries, procedures, and triggers
• Python Standard Library (datetime, os, string handling)
• MySQL Server – Database backend storing all application data
• MySQL Workbench / phpMyAdmin – Database management, SQL execution, schema design
• VS Code / PyCharm – Development environment

🏗️ Database Structure
Tables

Users

Roles

User_Roles

Games

Player_Progress

SQL Features Implemented

Stored Procedures

sp_RegisterUser

sp_AuthenticateUser

sp_AdminAddGame

sp_UpdatePlayerScore

sp_DeleteGame

Function

fn_GetUserEmail

Triggers

trg_AfterUserInsert

trg_UpdateLastPlayed

Views

v_Leaderboard_CosmicRift

v_Admin_UserReport

Constraints

Primary key, foreign key, unique, default, composite

Normalization

The database is fully in 3NF (Third Normal Form):

No partial dependencies

No transitive dependencies

All non-key attributes depend ONLY on the primary key

Composite tables contain no additional attributes

💻 Features of the Application (GUI)
🔹 User Operations

Register new user (with validation)

Login with credential checking

Auto-role assignment (via trigger)

Profile viewing

🔹 Admin Operations

Add games

Delete games

View user-role reports

Access leaderboard

Manage player progress

🔹 Player Progress

Update score & level

Auto-update last_played timestamp

Display history and statistics

🔹 Reporting

Leaderboard for "Cosmic Rift"

Count of users per game

Players scoring above average (nested query)

⚙️ Installation & Setup
1. Install Python dependencies
pip install mysql-connector-python

2. Install MySQL Server

Download from:

https://dev.mysql.com/downloads/

Create a database user with permissions.

3. Import SQL Schema

Run the provided .sql file in:

MySQL Workbench
or

phpMyAdmin

This will create:
✔ All tables
✔ Views
✔ Triggers
✔ Stored Procedures
✔ Sample data

▶️ Running the Application

Open the project folder

Run the Python file:

python main.py


Login as:

Admin:
username: admin
password: admin

Players:
PlayerOne, PlayerTwo, ProGamer23

Use the GUI to:

Add games

Update player scores

View leaderboards

Generate admin reports

🔍 Testing Procedures & Triggers
Test user registration
CALL sp_RegisterUser('DemoUser', 'demo@mail.com', 'pass');

Test auto-role trigger
SELECT * FROM User_Roles WHERE user_id =
(SELECT user_id FROM Users WHERE username='DemoUser');

Test last_played trigger
UPDATE Player_Progress
SET score = score + 1000
WHERE user_id = 2 AND game_id = 1;

📊 Queries Included

✔ Simple queries
✔ GROUP BY & aggregate
✔ Nested query
✔ Correlated query
✔ Update operation
✔ Delete operation

All organized neatly in the accompanying SQL file.

🧾 Project Strengths

Fully normalized 3NF database

Real stored procedures and triggers

Clean GUI integrated with MySQL

Secure login and role-based operations

Professional industry-like structure

Excellent for academic grading

📁 Project Structure
VGUMS/
│-- README.md
│-- main.py
│-- db_connection.py
│-- gui/
│   ├── login.py
│   ├── register.py
│   ├── admin_panel.py
│   ├── leaderboard.py
│   └── progress_update.py
│-- sql/
│   ├── vgums_schema.sql
│   ├── procedures.sql
│   ├── triggers.sql
│   └── sample_data.sql
