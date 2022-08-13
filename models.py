from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def initialization(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    return db


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    """
    Venue table
    """
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(500), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.TEXT(), nullable=True)
    genres = db.Column(db.ARRAY(db.String))


class Artist(db.Model):
    """
    Artist table
    """
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(500), nullable=True)
    looking_venues = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.TEXT(), nullable=True)


class Show(db.Model):
    """
    show table
    """
    __tablename__ = "show"

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.ForeignKey("venue.id"), nullable=False)
    artist_id = db.Column(db.ForeignKey("artist.id"), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)
    venue = db.relationship("Venue", backref="show", lazy=True, cascade="all")
    artist = db.relationship("Artist", backref="show", lazy=True, cascade="all")
