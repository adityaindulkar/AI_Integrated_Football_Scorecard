from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_mysqldb import MySQL
from datetime import date, timedelta
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import json
from collections import defaultdict
import google.generativeai as genai
from flask_wtf.csrf import CSRFProtect
genai.configure(api_key='*****')

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Session configuration
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=150)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'footballscorecard'

mysql = MySQL(app)
# csrf = CSRFProtect(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            session['next_url'] = request.url
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        un = request.form.get('username')
        pw = request.form.get('password')
        cpw = request.form.get('confpassword')

        cursor.execute("SELECT * FROM users WHERE username = %s", (un,))
        existing_user = cursor.fetchone()
        if existing_user:
            return "<script>alert('Username already exists!'); window.history.back();</script>"

        if pw != cpw:
            return "<script>alert('Passwords do not match!'); window.history.back();</script>"
        if not pw:
            return "<script>alert('Password cannot be empty!'); window.history.back();</script>"
        if len(pw) < 8:
            return "<script>alert('Password must be at least 8 characters long!'); window.history.back();</script>"

        hashed_pw = generate_password_hash(pw)
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (un, hashed_pw))
        mysql.connection.commit()

        return "<script>alert('Signup successful!'); window.location.href='/login';</script>"

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        usnm = request.form.get('loginusername')
        pswd = request.form.get('loginpassword')

        cursor.execute("SELECT userid, username, password FROM users WHERE username = %s", (usnm,))
        user = cursor.fetchone()

        if (user and check_password_hash(user[2], pswd)):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return "<script>alert('Login Successful!'); window.location.href='/home';</script>"
        else:
            return "<script>alert('Invalid Username or Password!'); window.history.back();</script>"

    return render_template('login.html')

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/teamsetup', methods=['GET', 'POST'])
@login_required
def team_setup():
    if request.method == 'POST':
        team_name = request.form['teamName']
        userid = session.get('user_id')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO teams (teamname, userid) VALUES (%s, %s)", (team_name, userid))
        team_id = cur.lastrowid

        for i in range(1, 16):
            player_key = f"APlayer{i}"
            player_name = request.form.get(player_key)
            if player_name:
                cur.execute(
                    "INSERT INTO players (playername, teamid, userid) VALUES (%s, %s, %s)",
                    (player_name, team_id, userid)
                )

        mysql.connection.commit()
        cur.close()
        return redirect(url_for('home'))
    return render_template('teamsetup.html')

@app.route('/add-player', methods=['POST'])
@login_required
def add_player():
    team_id = request.form['team_id']
    player_name = request.form['player_name']
    userid = session.get('user_id')

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO players (playername, teamid, userid) VALUES (%s, %s, %s)", (player_name, team_id, userid))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('view_alter_teams'), code=307)


@app.route('/delete-player', methods=['POST'])
@login_required
def delete_player():
    player_id = request.form['player_id']

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM players WHERE playerid = %s AND userid = %s", (player_id, session.get('user_id')))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('view_alter_teams'))

@app.route('/delete-team', methods=['POST'])
@login_required
def delete_team():
    team_id = request.form['team_id']
    userid = session.get('user_id')
    cursor = mysql.connection.cursor()
    
    cursor.execute("DELETE FROM players WHERE teamid = %s AND userid = %s", (team_id, userid))
    cursor.execute("DELETE FROM teams WHERE teamid = %s AND userid = %s", (team_id, userid))
    mysql.connection.commit()
    
    return redirect(url_for('view_alter_teams'))

@app.route('/change-team-name', methods=['POST'])
@login_required
def change_team_name():
    team_id = request.form['team_id']
    new_name = request.form['new_name']
    userid = session.get('user_id')

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE teams SET teamname = %s WHERE teamid = %s AND userid = %s", (new_name, team_id, userid))
    mysql.connection.commit()
    return redirect(url_for('view_alter_teams'))

@app.route('/view-alter-teams', methods=['GET', 'POST'])
@login_required
def view_alter_teams():
    search_query = request.form.get('search', "").strip() if request.method == 'POST' else ""
    userid = session.get('user_id')

    cur = mysql.connection.cursor()

    if search_query:
        cur.execute("""
            SELECT teamid, teamname FROM teams
            WHERE userid = %s AND (teamname LIKE %s OR teamid = %s)
        """, (userid, f"%{search_query}%", search_query if search_query.isdigit() else 0))
    else:
        cur.execute("SELECT teamid, teamname FROM teams WHERE userid = %s", (userid,))

    teams = cur.fetchall()

    teams_with_players = []
    for teamid, teamname in teams:
        cur.execute("SELECT playerid, playername FROM players WHERE teamid = %s AND userid = %s", (teamid, userid))
        players = cur.fetchall()
        teams_with_players.append({
            'teamid': teamid,
            'teamname': teamname,
            'players': players
        })

    cur.close()
    return render_template('view_alter_teams.html', teams=teams_with_players, search=search_query)

@app.route('/select-teams', methods=['GET', 'POST'])
@login_required
def select_teams():
    userid = session.get('user_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT teamid, teamname FROM teams WHERE userid = %s", (userid,))
    teams = cur.fetchall()
    cur.close()

    today = date.today().strftime("%Y-%m-%d")

    if request.method == 'POST':
        home_team = request.form['home_team']
        away_team = request.form['away_team']
        match_date = request.form['match_date']
        venue = request.form['venue']

        return redirect(url_for('select_lineups', 
                                home_team=home_team, 
                                away_team=away_team,
                                venue=venue,
                                match_date=match_date))

    return render_template('select_teams.html', teams=teams, today=today)

@app.route('/select-lineups', methods=['GET', 'POST'])
@login_required
def select_lineups():
    userid = session.get('user_id')
    home_team_id = request.args.get('home_team')
    away_team_id = request.args.get('away_team')
    venue = request.args.get('venue')
    match_date = request.args.get('match_date')

    cur = mysql.connection.cursor()

    cur.execute("INSERT INTO matches (home_team_id, away_team_id, venue, match_date, home_score, away_score, userid) VALUES (%s, %s, %s, %s, 0, 0, %s)", (home_team_id, away_team_id, venue, match_date, userid))
    match_id = cur.lastrowid
    session['current_match_id'] = match_id

    # Get team and player data for rendering and POST
    cur.execute("SELECT playerid, playername FROM players WHERE teamid = %s AND userid = %s", (home_team_id, userid))
    home_players = cur.fetchall()
    cur.execute("SELECT playerid, playername FROM players WHERE teamid = %s AND userid = %s", (away_team_id, userid))
    away_players = cur.fetchall()

    cur.execute("SELECT teamname FROM teams WHERE teamid = %s AND userid = %s", (home_team_id, userid))
    home_team_name = cur.fetchone()[0]
    cur.execute("SELECT teamname FROM teams WHERE teamid = %s AND userid = %s", (away_team_id, userid))
    away_team_name = cur.fetchone()[0]

    if request.method == 'POST':

        # Insert selected players
        home_starters = request.form.getlist("home_starting")
        away_starters = request.form.getlist("away_starting")

        for player in home_players:
            playerid = str(player[0])  # IDs from form are strings
            if playerid in home_starters:
                cur.execute("""
                    INSERT INTO player_appearances (user_id, team_id, player_id, started, substituted_in, match_id	)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (userid, home_team_id, playerid, 1, 0, match_id))

        for player in away_players:
            playerid = str(player[0])
            if playerid in away_starters:
                cur.execute("""
                    INSERT INTO player_appearances (user_id, team_id, player_id, started, substituted_in, match_id	)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (userid, away_team_id, playerid, 1, 0, match_id))


        mysql.connection.commit()
        cur.close()

        return redirect(url_for('scorecard',
                                home_team=home_team_id,
                                away_team=away_team_id,
                                venue=venue,
                                match_date=match_date,
                                match_id=match_id,
                                home_starters=home_starters,
                                away_starters=away_starters))

    cur.close()
    return render_template('select_lineups.html',
                           home_team_name=home_team_name,
                           away_team_name=away_team_name,
                           home_players=home_players,
                           away_players=away_players)



@app.route('/scorecard', methods=['GET'])
@login_required
def scorecard():
    home_team_id = request.args.get('home_team')
    away_team_id = request.args.get('away_team')
    match_id = request.args.get('match_id')
    venue = request.args.get('venue')
    match_date = request.args.get('match_date')
    home_starters = request.args.getlist('home_starters')
    away_starters = request.args.getlist('away_starters')
    userid = session.get('user_id')

    if not all([home_team_id, away_team_id, venue, match_date, match_id]):
        return "Missing one or more required parameters.", 400

    if home_team_id == away_team_id:
        return "Home and Away teams must be different.", 400

    cur = mysql.connection.cursor()

    cur.execute("SELECT teamname FROM teams WHERE teamid = %s AND userid = %s", (home_team_id, userid))
    home_team_row = cur.fetchone()
    if not home_team_row:
        return "Home team not found.", 404
    home_team_name = home_team_row[0]

    cur.execute("SELECT teamname FROM teams WHERE teamid = %s AND userid = %s", (away_team_id, userid))
    away_team_row = cur.fetchone()
    if not away_team_row:
        return "Away team not found.", 404
    away_team_name = away_team_row[0]

    # Fetch all players
    cur.execute("SELECT playerid, playername FROM players WHERE teamid = %s AND userid = %s", (home_team_id, userid))
    home_players = [{'player_id': row[0], 'player_name': row[1]} for row in cur.fetchall()]

    cur.execute("SELECT playerid, playername FROM players WHERE teamid = %s AND userid = %s", (away_team_id, userid))
    away_players = [{'player_id': row[0], 'player_name': row[1]} for row in cur.fetchall()]

    # Get only selected starter players
    home_starter_players = []
    for playerid in home_starters:
        cur.execute("SELECT playerid, playername FROM players WHERE playerid = %s AND userid = %s", (playerid, userid))
        row = cur.fetchone()
        if row:
            home_starter_players.append({'player_id': row[0], 'player_name': row[1]})
    
    cur.execute("""
    SELECT p.playerid, p.playername 
    FROM player_appearances pa
    JOIN players p ON pa.player_id = p.playerid
    WHERE pa.match_id = %s AND pa.user_id = %s AND pa.team_id = %s
    AND (pa.started = 1 OR pa.substituted_in = 1)
    """, (match_id, userid, home_team_id))
    home_active_players = [{'player_id': row[0], 'player_name': row[1]} for row in cur.fetchall()]

    away_starter_players = []
    for playerid in away_starters:
        cur.execute("SELECT playerid, playername FROM players WHERE playerid = %s AND userid = %s", (playerid, userid))
        row = cur.fetchone()
        if row:
            away_starter_players.append({'player_id': row[0], 'player_name': row[1]})

    cur.execute("""
    SELECT p.playerid, p.playername 
    FROM player_appearances pa
    JOIN players p ON pa.player_id = p.playerid
    WHERE pa.match_id = %s AND pa.user_id = %s AND pa.team_id = %s
      AND (pa.started = 1 OR pa.substituted_in = 1)
    """, (match_id, userid, away_team_id))
    away_active_players = [{'player_id': row[0], 'player_name': row[1]} for row in cur.fetchall()]


    home_starter_ids = [player['player_id'] for player in home_starter_players]
    home_bench_players = [player for player in home_players if player['player_id'] not in home_starter_ids]
    away_starter_ids = [player['player_id'] for player in away_starter_players]
    away_bench_players = [player for player in away_players if player['player_id'] not in away_starter_ids]

    cur.close()

    return render_template('scorecard.html',
                           home_team_id=home_team_id,
                           away_team_id=away_team_id,
                           home_team_name=home_team_name,
                           away_team_name=away_team_name,
                           home_starter_players=home_starter_players,
                           away_starter_players=away_starter_players,
                           home_bench_players=home_bench_players,
                           away_bench_players=away_bench_players,
                           home_active_players=home_active_players,
                           away_active_players=away_active_players,
                           match_id = match_id,
                           venue=venue,
                           match_date=match_date)

@app.route('/substitute', methods=['POST'])
def substitute():
    data = request.get_json()
    starter_id = data.get('starter_id')
    sub_id = data.get('sub_id')
    team_id = data.get('team_id')  # Changed from 'team' to match frontend
    match_id = data.get('match_id')
    minute = data.get('minute')
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'success': False, 'message': 'User not logged in'}), 403
    
    try:
        cur = mysql.connection.cursor()

        # Get player names first
        cur.execute("SELECT playername FROM players WHERE playerid = %s", (starter_id,))
        starter_name = cur.fetchone()[0]
        
        cur.execute("SELECT playername FROM players WHERE playerid = %s", (sub_id,))
        sub_name = cur.fetchone()[0]

        # Perform substitution
        cur.execute("""
            INSERT INTO player_appearances 
            (user_id, team_id, player_id, match_id, started, substituted_in, substitution_minute)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, team_id, sub_id, match_id, 0, 1, minute))

        cur.execute("""
            UPDATE player_appearances 
            SET substituted_out = 1, substitution_minute = %s
            WHERE match_id = %s AND user_id = %s AND player_id = %s
        """, (minute, match_id, user_id, starter_id))

        mysql.connection.commit()
        cur.close()
        
        return jsonify({ 
            'success': True,
            'starter_id': starter_id,
            'starter_name': starter_name,
            'sub_id': sub_id,
            'sub_name': sub_name,
            'minute': minute
        })

    except Exception as e:
        print("Substitution error:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/complete-match', methods=['POST'])
@login_required
def complete_match():
    try:
        home_score = int(request.form.get('home_score', 0))
        away_score = int(request.form.get('away_score', 0))
        comments = request.form.get('match_comments', '')
        userid = session.get('user_id')
        match_id = session.get('current_match_id')

        cur = mysql.connection.cursor()
        cur.execute("""
        UPDATE matches
        SET home_score = %s, away_score = %s, comments = %s
        WHERE match_id = %s AND userid = %s
    """, (home_score, away_score, comments, match_id, userid))

        event_data_json = request.form.get('event_data')
        if event_data_json:
            try:
                event_data = json.loads(event_data_json)
                for event in event_data:
                    cur.execute("""
                        INSERT INTO events (match_id, player_id, team_id, player_name, event_type, team_side, event_time, userid)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        match_id,
                        event.get('player_id'),
                        event.get('team_id'),
                        event.get('player_name'),
                        event.get('event_type'),
                        event.get('team_side'),
                        event.get('event_time'),
                        userid
                    ))
            except json.JSONDecodeError:
                return "Failed to parse event data", 400

        mysql.connection.commit()
        cur.close()
        return redirect(url_for('home'))

    except Exception as e:
        return f"Error completing match: {str(e)}", 500
    
@app.route('/view-matches')
@login_required
def view_matches():
    userid = session.get('user_id')
    cur = mysql.connection.cursor()

    # Fetch matches for this user
    cur.execute("""
        SELECT m.match_id, m.match_date, m.venue, m.home_score, m.away_score, m.comments,
               ht.teamname AS home_team, at.teamname AS away_team
        FROM matches m
        JOIN teams ht ON m.home_team_id = ht.teamid
        JOIN teams at ON m.away_team_id = at.teamid
        WHERE m.userid = %s
        ORDER BY m.match_date DESC
    """, (userid,))
    matches = cur.fetchall()

    match_list = []
    for match in matches:
        match_id, match_date, venue, home_score, away_score, comments, home_team, away_team = match

        # Get all events for this match
        cur.execute("""
            SELECT event_type, player_name, event_time, team_side
            FROM events
            WHERE match_id = %s AND userid = %s
            ORDER BY event_time
        """, (match_id, userid))
        events = cur.fetchall()

        goals = []
        cards = []

        for ev in events:
            event_type, player_name, event_time, team_side = ev
            if event_type in ['goal', 'own goal', '']:  # Include all possible goal types
                # Standardize empty string to 'own goal'
                if event_type == '':
                    event_type = 'own goal'
                    
                # For own goals, we keep the original team_side but mark them as own goals
                # The template will handle displaying them under the opposite team
                goals.append({
                    'player_name': player_name,
                    'time': event_time,
                    'team_side': team_side,  # Keep original team side
                    'event_type': event_type,
                    'is_own_goal': event_type == 'own goal'  # Add flag for own goals
                })
            elif event_type in ['yellow', 'red']:
                cards.append({
                    'player_name': player_name, 
                    'time': event_time, 
                    'team_side': team_side, 
                    'type': event_type
                })

        # Generate summary
        summary = generate_summary_gemini(home_team, away_team, home_score, away_score, 
                                        venue, match_date, goals, cards, comments)

        match_list.append({
            'match_id': match_id,
            'home_team': home_team,
            'away_team': away_team,
            'home_score': home_score,
            'away_score': away_score,
            'venue': venue,
            'match_date': match_date.strftime('%Y-%m-%d'),  # Format date as string
            'goals': goals,
            'cards': cards,
            'summary': summary
        })

    # Group matches by date
    grouped_matches = defaultdict(list)
    for match in match_list:
        grouped_matches[match['match_date']].append(match)

    cur.close()
    return render_template('view_matches.html', grouped_matches=dict(grouped_matches))  # Convert defaultdict to dict


@app.route('/player-stats')
@login_required
def player_stats():
    userid = session.get('user_id')
    search_query = request.args.get('search', '').strip()
    
    cur = mysql.connection.cursor()
    
    # Get all players with their team names and appearances
    query = """
        SELECT 
            p.playerid,
            p.playername,
            t.teamname,
            COUNT(DISTINCT pa.match_id) AS appearances,
            (SELECT COUNT(*) FROM events 
             WHERE player_id = p.playerid AND event_type = 'goal' AND userid = %s) AS goals,
            (SELECT COUNT(*) FROM events 
             WHERE player_id = p.playerid AND event_type = 'yellow' AND userid = %s) AS yellow_cards,
            (SELECT COUNT(*) FROM events 
             WHERE player_id = p.playerid AND event_type = 'red' AND userid = %s) AS red_cards,
            (SELECT COUNT(*) FROM events 
             WHERE player_id = p.playerid AND event_type = '' AND userid = %s) AS own_goals
        FROM 
            players p
        LEFT JOIN 
            teams t ON p.teamid = t.teamid AND t.userid = %s
        LEFT JOIN 
            player_appearances pa ON p.playerid = pa.player_id AND pa.user_id = %s
        WHERE 
            p.userid = %s
    """
    
    params = [userid, userid, userid, userid, userid, userid, userid]
    
    if search_query:
        query += " AND (p.playername LIKE %s OR t.teamname LIKE %s)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
    
    query += " GROUP BY p.playerid, p.playername, t.teamname ORDER BY t.teamname, p.playername"
    
    cur.execute(query, params)
    players_stats = cur.fetchall()
    cur.close()
    
    return render_template('player_stats.html', 
                         players_stats=players_stats, 
                         search_query=search_query)

@app.route('/delete_match/<int:match_id>', methods=['DELETE'])
@login_required
def delete_match(match_id):
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401

        cur = mysql.connection.cursor()
        
        # Verify match exists and belongs to user
        cur.execute("""
            SELECT m.userid 
            FROM matches m
            WHERE m.match_id = %s
        """, (match_id,))
        match = cur.fetchone()
        
        if not match:
            return jsonify({'error': 'Match not found'}), 404
        if match[0] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Delete related events first
        cur.execute("DELETE FROM events WHERE match_id = %s", (match_id,))
        
        # Delete the match
        cur.execute("DELETE FROM matches WHERE match_id = %s", (match_id,))
        
        mysql.connection.commit()
        return jsonify({'success': True}), 200
        
    except Exception as e:
        mysql.connection.rollback()
        print(f"Error deleting match: {str(e)}")  # Log the error
        return jsonify({'error': 'Database error'}), 500
    finally:
        if cur:
            cur.close()

def generate_summary_gemini(home, away, home_score, away_score, venue, date, goals, cards, comments):
    prompt = f"""
        Match Summary for: {home} vs {away}
        Final Score: {home} {home_score} - {away_score} {away}
        Venue: {venue}, Date: {date}

        Goals:
        {chr(10).join([f"{g['player_name']} ({g['team_side']}) at {g['time']} min" for g in goals])}

        Cards:
        {chr(10).join([f"{c['player_name']} - {c['type']} ({c['team_side']}) at {c['time']} min" for c in cards])}

        comments: {comments}

        Write a short football match summary based on this data.
        """

    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else "No summary available."
    except Exception as e:
        print(f"[Gemini Error] {e}")  # Logs the actual reason in your Flask console
        return "Summary could not be generated."


if __name__ == '__main__':
    app.run(debug=True)
