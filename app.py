# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import datetime
import json
import sys

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import distinct

from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
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

    # implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
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

    # implement any missing fields, as a database migration using Flask-Migrate


'''
class Genre(db.Model):
    __tablename__ = "Genre"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=True)
    venue = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
'''


# Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = "show"

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.ForeignKey("venue.id"), nullable=False)
    artist_id = db.Column(db.ForeignKey("artist.id"), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)
    venue = db.relationship("Venue", backref="show", lazy=True, cascade="all")
    artist = db.relationship("Artist", backref="show", lazy=True, cascade="all")


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    locations = db.session.query(distinct(Venue.city), Venue.state).order_by("state").all()

    data = []
    for location in locations:
        dict = {
            "city": location[0],
            "state": location[1],
            "venues": []
        }
        venues = Venue.query.filter_by(city=dict["city"], state=dict["state"]).all()
        for v in venues:
            upcomingShows = Show.query.filter_by(venue_id=v.id).filter(Show.start_time > datetime.now()).count()
            dict["venues"].append({
                "id": v.id,
                "name": v.name,
                "num_upcoming_shows": upcomingShows
            })
        data.append(dict)
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    request_data = request.form["search_term"]
    query = db.session.query(Venue).filter(Venue.name.ilike('%' + request_data + '%')).all()
    response = {
        "count": len(query),
        "data": []
    }
    for q in query:
        upcomingShows = Show.query.filter_by(venue_id=q.id).filter(Show.start_time > datetime.now()).count()
        venueObject = {
            "id": q.id,
            "name": q.name,
            "num_upcoming_shows": upcomingShows
        }
        response["data"].append(venueObject)
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # replace with real venue data from the venues table, using venue_id
    error = False
    if db.session.query(Venue.id).first() is not None:
        venue = Venue.query.get(venue_id)
        data = {
            **venue.__dict__,
            "past_shows":[],
            "upcoming_shows": [],
            "past_shows_count": 0,
            "upcoming_shows_count": 0,
        }
        upcoming_shows = db.session.query(Show) \
            .join(Venue).filter(Show.venue_id == venue_id) \
            .filter(Show.start_time > datetime.now()) \
            .order_by(Show.start_time)\
            .all()
        past_shows = db.session.query(Show) \
            .join(Venue).filter(Show.venue_id == venue_id) \
            .filter(Show.start_time < datetime.now()) \
            .order_by(Show.start_time)\
            .all()
        past_shows_count = Show.query.filter_by(venue_id=venue_id).filter(Show.start_time < datetime.now()).count()
        upcoming_shows_count = Show.query.filter_by(venue_id=venue_id).filter(Show.start_time > datetime.now()).count()

        for s in upcoming_shows:
            listed = {
                "artist_id": s.artist.id,
                "artist_name": s.artist.name,
                "artist_image_link": s.artist.image_link,
                "start_time": str(s.start_time)
            }
            data["upcoming_shows"].append(listed)

        for s in past_shows:
            listed = {
                "artist_id": s.artist.id,
                "artist_name": s.artist.name,
                "artist_image_link": s.artist.image_link,
                "start_time": str(s.start_time)
            }
            data["past_shows"].append(listed)

        data["past_shows_count"] = past_shows_count
        data["upcoming_shows_count"] = upcoming_shows_count
    else:
        error = True

    if error:
        abort(404)
    else:
        return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # insert form data as a new Venue record in the db, instead
    # modify data to be the data object returned from db insertion

    # on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    error = False
    # get value from form
    form = VenueForm(request.form)
    try:
        venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, address=form.address.data,
                      phone=form.phone.data, facebook_link=form.facebook_link.data, image_link=form.image_link.data,
                      website=form.website_link.data, seeking_talent=form.seeking_talent.data,
                      seeking_description=form.seeking_description.data, genres=form.genres.data)

        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + venue.name + ' was successfully listed!')
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
    finally:
        db.session.close()
        return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # replace with real data returned from querying the database
    data = []
    artists = Artist.query.all()
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name,
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    request_data = request.form["search_term"]
    query = db.session.query(Artist).filter(Artist.name.ilike('%' + request_data + '%')).all()
    response = {
        "count": len(query),
        "data": []
    }
    for q in query:
        upcomingShows = Show.query.filter_by(artist_id=q.id).filter(Show.start_time > datetime.now()).count()
        artistObject = {
            "id": q.id,
            "name": q.name,
            "num_upcoming_shows": upcomingShows
        }
        response["data"].append(artistObject)
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # replace with real artist data from the artist table, using artist_id
    error = False
    if db.session.query(Artist.id).first() is not None:
        artist = Artist.query.get(artist_id)
        data = {
            **artist.__dict__,
            "past_shows":[],
            "upcoming_shows": [],
            "past_shows_count": 0,
            "upcoming_shows_count": 0,
        }
        upcoming_shows = db.session.query(Show) \
            .join(Venue).filter(Show.artist_id == artist_id) \
            .filter(Show.start_time > datetime.now()) \
            .order_by(Show.start_time)\
            .all()
        past_shows = db.session.query(Show) \
            .join(Venue).filter(Show.artist_id == artist_id) \
            .filter(Show.start_time < datetime.now()) \
            .order_by(Show.start_time)\
            .all()

        past_shows_count = Show.query.filter_by(artist_id=artist_id).filter(
            Show.start_time < datetime.now()
        ).count()
        upcoming_shows_count = Show.query.filter_by(artist_id=artist_id).filter(
            Show.start_time > datetime.now()
        ).count()

        for s in upcoming_shows:
            listed = {
                "venue_id": s.venue.id,
                "venue_name": s.venue.name,
                "venue_image_link": s.venue.image_link,
                "start_time": str(s.start_time)
            }
            data["upcoming_shows"].append(listed)

        for s in past_shows:
            listed = {
                "venue_id": s.venue.id,
                "venue_name": s.venue.name,
                "venue_image_link": s.venue.image_link,
                "start_time": str(s.start_time)
            }
            data["past_shows"].append(listed)

        data["past_shows_count"] = past_shows_count
        data["upcoming_shows_count"] = upcoming_shows_count
    else:
        error = True

    if error:
        abort(404)
    else:
        return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # populate form with fields from artist with ID <artist_id>
    artist = Artist.query.get(artist_id)
    form = ArtistForm(id=artist.id, name=artist.name, genres=artist.genres, city=artist.city,
                      state=artist.state, phone=artist.phone, website_link=artist.website,
                      facebook_link=artist.facebook_link,
                      seeking_venue=artist.looking_venues, seeking_description=artist.seeking_description,
                      image_link=artist.image_link)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    try:
        db.session.query(Artist).filter(Artist.id == artist_id).update({
            "name": form.name.data,
            "city": form.city.data,
            "state": form.state.data,
            "phone": form.phone.data,
            "facebook_link": form.facebook_link.data,
            "image_link": form.image_link.data,
            "website": form.website_link.data,
            "looking_venues": form.seeking_venue.data,
            "seeking_description": form.seeking_description.data,
            "genres": form.genres.data
        })
        db.session.commit()
        # on successful db update, flash success
        flash('Artist ' + form.name.data + ' was successfully edited!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist ' + form.name.data + ' could not be edited.')
    finally:
        db.session.close()
        return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # populate form with values from venue with ID <venue_id>
    venue = Venue.query.get(venue_id)
    form = VenueForm(id=venue.id, name=venue.name, genres=venue.genres, address=venue.address, city=venue.city,
                     state=venue.state, phone=venue.phone, website_link=venue.website,
                     facebook_link=venue.facebook_link,
                     seeking_talent=venue.seeking_talent, seeking_description=venue.seeking_description,
                     image_link=venue.image_link)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)
    print(form.website_link.data)
    try:
        db.session.query(Venue).filter(Venue.id == venue_id).update({
            "name": form.name.data,
            "city": form.city.data,
            "state": form.state.data,
            "address": form.address.data,
            "phone": form.phone.data,
            "facebook_link": form.facebook_link.data,
            "image_link": form.image_link.data,
            "website": form.website_link.data,
            "seeking_talent": form.seeking_talent.data,
            "seeking_description": form.seeking_description.data,
            "genres": form.genres.data
        })
        db.session.commit()
        # on successful db update, flash success
        flash('Venue ' + form.name.data + ' was successfully edited!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' + form.name.data + ' could not be edited.')
    finally:
        db.session.close()
        return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # insert form data as a new Venue record in the db, instead
    # modify data to be the data object returned from db insertion
    # get value from form
    form = ArtistForm(request.form)
    try:
        artist = Artist(name=form.name.data, city=form.city.data, state=form.state.data, phone=form.phone.data,
                        image_link=form.image_link.data, facebook_link=form.facebook_link.data,
                        website=form.website_link.data, looking_venues=form.seeking_venue.data,
                        seeking_description=form.seeking_description.data, genres=form.genres.data)
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        # on unsuccessful db insert, flash an error instead.
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    finally:
        db.session.close()
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # replace with real venues data.
    data = []
    shows = Show.query.order_by(Show.start_time).all()

    for s in shows:
        artist = Artist.query.get(s.artist_id)
        venue = Venue.query.get(s.venue_id)
        data.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(s.start_time)
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # insert form data as a new Show record in the db, instead
    form = ShowForm(request.form)
    try:
        show = Show(venue_id=form.venue_id.data, artist_id=form.artist_id.data, start_time=form.start_time.data)
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be listed.')
    finally:
        return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
