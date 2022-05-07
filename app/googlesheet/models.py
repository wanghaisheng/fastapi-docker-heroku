from datetime import datetime, timedelta
import jwt
from flask import current_app

db      = SQLAlchemy()


class Player(db.Model):
    __tablename__ = 'player'

    def __repr__(self):
      return '<Player {} {} {}>'.format(self.id, self.first_name, self.last_name)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), nullable=True)
    captain = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)
    subscribed = db.Column(db.Boolean, default=True)

    # Relationships
    player_games = db.relationship('PlayerGame', back_populates='player', foreign_keys='PlayerGame.player_id')
    team = db.relationship('Team', back_populates='players', foreign_keys=[team_id])

    def encode_auth_token(self, player_id, expiration=None):
        try:
            payload = {
                'iat': datetime.utcnow(),
                'sub': player_id
            }
            
            if expiration:
                payload['exp'] = datetime.utcnow() + timedelta(days=0, seconds=expiration)

            return jwt.encode(
                payload,
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(
              auth_token, 
              current_app.config['SECRET_KEY'], 
              algorithms=["HS256"]
            )

            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please login again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please login again.'


class Game(db.Model):
    __tablename__ = 'game'

    def __repr__(self):
      return f'<Game {self.id}>'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    date = db.Column(db.DateTime)

    team_winner_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    team_loser_id  = db.Column(db.Integer, db.ForeignKey('team.id'))

    score_winner = db.Column(db.Integer, default=0)
    score_loser  = db.Column(db.Integer, default=0)
    total_innings = db.Column(db.Integer, default=3)

    # Relationships
    player_games = db.relationship('PlayerGame', back_populates='game', foreign_keys='PlayerGame.game_id')
    team_winner = db.relationship('Team', foreign_keys=[team_winner_id])
    team_loser = db.relationship('Team', foreign_keys=[team_loser_id])


class PlayerGame(db.Model):
    __tablename__ = 'player_game'

    def __repr__(self):
      return f'<PlayerGame {self.id}>'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    singles = db.Column(db.Integer, default=0)
    doubles = db.Column(db.Integer, default=0)
    triples = db.Column(db.Integer, default=0)
    home_runs = db.Column(db.Integer, default=0)
    strikeouts = db.Column(db.Integer, default=0)
    outs = db.Column(db.Integer, default=0)
    base_on_balls = db.Column(db.Integer, default=0)
    hit_by_pitch = db.Column(db.Integer, default=0)
    runs_batted_in = db.Column(db.Integer, default=0)
    error = db.Column(db.Integer, default=0)
    stolen_bases = db.Column(db.Integer, default=0)
    caught_stealing = db.Column(db.Integer, default=0)

    innings_pitched = db.Column(db.Integer, default=0)
    earned_runs = db.Column(db.Integer, default=0)
    runs = db.Column(db.Integer, default=0)
    pitching_strikeouts = db.Column(db.Integer, default=0)
    pitching_base_on_balls = db.Column(db.Integer, default=0)
    saves = db.Column(db.Integer, default=0)
    blown_saves = db.Column(db.Integer, default=0)
    win = db.Column(db.Integer, default=0)
    loss = db.Column(db.Integer, default=0)

    # Relationships
    player = db.relationship('Player', back_populates='player_games', foreign_keys=[player_id])
    game = db.relationship('Game', back_populates='player_games', foreign_keys=[game_id])


class Team(db.Model):
    __tablename__ = 'team'

    def __repr__(self):
      return f'<Team {self.id} {self.name}>'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    abbreviation = db.Column(db.String(45))
    name = db.Column(db.String(45))
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
   
    # Relationships
    players = db.relationship('Player', back_populates='team', foreign_keys='Player.team_id')