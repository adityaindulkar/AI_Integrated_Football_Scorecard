# AI Integrated Football Scorecard

A secure web application featuring mandatory user authentication with session-based credential management, ensuring data protection at all access points. The system leverages AI-powered APIs to automatically generate insightful match summaries and performance analytics. At its core, advanced SQL database architecture safely stores all match data while enabling complex statistical computations and real-time player performance metrics. The platform offers intuitive drag-and-drop functionality for live score updates and team management. Designed for usability, the interface provides streamlined CRUD operations with a clean, responsive design that simplifies scorekeeping and data management for users at all technical levels. 

## Tech Stack:
### Backend
Framework: Flask (Python)    
Database:  MySQL    
Authentication: Session-based with server-side storage
AI Integration: Gemini API    
### Frontend
UI: HTML5, CSS3, JavaScript    
Templating: Jinja2 (Flask)   
Dynamic Updates: AJAX, Fetch API   

## Features:
### 1. Secure Authentication
Role-based user authentication required to access all pages.
Session-based login with 150-minute inactivity timeout.
Credentials securely hashed and validated server-side.

### 2. Intuitive User Interface
Drag-and-drop functionality for live match updates (player substitutions, event logging).
CRUD (Create, Read, Update, Delete) operations for matches, teams, players, and events.

### 3. Advanced Database Management
Relational SQL database with optimized queries using joins, sums, conditional fetches and foreign keys.
Tables for users, teams, players, matches, events, and player_stats.
Complex queries for real-time statistics (goals, assists, cards, substitutions).

### 4. AI-Generated Match Summaries
Automated post-match reports using AI APIs (Gemini).
Summaries include match comments, goals scored, player names, venue, date, time of the event, cards in natural language.

### 5. Comprehensive Statistics & History
Player performance tracking (goals, assists, disciplinary records).
Match history with filtering by date, team, or competition.

### 6. Real-Time Match Event Handling
Live logging of goals, substitutions, yellow/red cards with timestamps.
Dynamic updates using JavaScript and Jinja templating.
Event validation to prevent duplicate or incorrect entries.

### 7. User Feedback & Alerts
Success/error notifications for all user actions (e.g., "Match deleted successfully", "Invalid username or password").


