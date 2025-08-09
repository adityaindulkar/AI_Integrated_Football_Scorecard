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
**User-Specific Data**: All operations (team setups, matches, statistics) are scoped to the logged-in user via session-based authentication (@login_required decorator).    
**Data Privacy**: Database queries include userid checks to ensure users can only access/modify their own teams, players, and match records.

### 2. Intuitive User Interface
Drag-and-drop functionality for live match updates (player substitutions, event logging).
CRUD (Create, Read, Update, Delete) operations for matches, teams, players, and events.    
Smooth Player substitutions and Own Goal UI/UX backed by strong backend

### 3. Advanced Database Management
Relational SQL database with optimized queries using joins, sums, conditional fetches and foreign keys.
Tables for users, teams, players, matches, events, and player_stats.
Complex queries for real-time statistics (goals, assists, cards, substitutions).

### 4. AI-Generated Match Summaries
Automated post-match reports using AI APIs (Gemini).
Summaries include match comments, goals scored, player names, venue, date, time of the event, cards in natural language.

### 5. Comprehensive Statistics & History
Player performance tracking (goals, assists, disciplinary records).
Match history with filtering by player and team.

### 6. Real-Time Match Event Handling
Live logging of goals, substitutions, yellow/red cards with timestamps.
Dynamic updates using JavaScript and Jinja templating.
Event validation to prevent duplicate or incorrect entries.

### 7. User Feedback & Alerts
Success/error notifications for all user actions (e.g., "Match deleted successfully", "Invalid username or password").


## Images:
## Signup Page:
<img width="1200" height="1200" alt="Image" src="https://github.com/user-attachments/assets/389df9b2-0876-4060-a43f-a886b5535868" />

## Login Page:
<img width="1200" height="1200" alt="page2" src="https://github.com/user-attachments/assets/fec55f8d-ac25-4aec-8e36-2cb602f54788" />

## Home:
<img width="1919" height="911" alt="page3" src="https://github.com/user-attachments/assets/2ef7b019-6e19-4f03-9d2c-58ba5f838ed9" />

## Create new team:
<img width="1919" height="911" alt="page4" src="https://github.com/user-attachments/assets/342c2ff5-256b-4c09-b73a-103d0f05287a" />

## View and Alter Teams:
<img width="1200" height="1200" alt="page5" src="https://github.com/user-attachments/assets/47771447-2868-42f6-9732-93b0c40024ac" />
<img width="1200" height="1200" alt="page6" src="https://github.com/user-attachments/assets/b912d01f-187f-4736-bfec-fd153c58ae86" />

## Start Live Match-->Select Teams:
<img width="1200" height="1200" alt="page7" src="https://github.com/user-attachments/assets/75fd65da-e525-48de-83ba-062cc01fadc5" />

## Scorecard:
<img width="1200" height="1200" alt="page8" src="https://github.com/user-attachments/assets/2d4cf34e-cc4e-42d0-870c-f3122ffc46bd" />
<img width="1900" height="911" alt="page9" src="https://github.com/user-attachments/assets/f3a4d042-3637-42d2-96eb-3a4fd819a106" />
<img width="1759" height="505" alt="page10" src="https://github.com/user-attachments/assets/c0d0d41b-e7a9-478a-a149-cc0147a98012" />

## Substitute Player Functionality:
<img width="1200" height="1200" alt="page11" src="https://github.com/user-attachments/assets/98fe7e95-cebf-4f61-a524-342f7ed7e3f2" />

## Match Comments Functionality:
<img width="1524" height="278" alt="page12" src="https://github.com/user-attachments/assets/67b72aa4-cb27-4494-bf59-5bbcad904e41" />

## Match History and Summary:
<img width="1915" height="443" alt="page13" src="https://github.com/user-attachments/assets/a7fe2744-186d-463a-8bf4-a7629faeef2c" />
<img width="1867" height="515" alt="page14" src="https://github.com/user-attachments/assets/536a4733-0780-4b74-8fdd-e74c300e8e9d" />

## Player Statistics page:
<img width="1273" height="909" alt="page15" src="https://github.com/user-attachments/assets/3c83bd57-ba35-4663-ae50-448e88b2a884" />
<img width="1218" height="909" alt="page16" src="https://github.com/user-attachments/assets/4c43409e-f11e-46f0-b227-d69eeb8ba284" />

## Player statistics search functionality:
<img width="1266" height="344" alt="Screenshot 2025-08-09 215626" src="https://github.com/user-attachments/assets/99b02655-1372-4858-abc9-540ef7276532" />



