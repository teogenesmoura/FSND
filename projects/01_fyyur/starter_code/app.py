#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import datetime
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate 
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys 
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
  start_time = db.Column(db.DateTime, default=datetime.utcnow)
  artist = db.relationship('Artist', backref="venue")
  venue = db.relationship('Venue', backref="artist")

class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, unique=True, nullable=False)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(500))
  image_link = db.Column(db.String(120))
  artists = db.relationship('Show', backref="Venue")

class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, unique=True, nullable=False)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(500))
  venues = db.relationship('Show', backref="Artist")

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venues = Venue.query.all()
  return render_template('pages/venues.html', areas=venues);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  response['data'] = []
  search_term = request.form.get('search_term').lower()
  venues = Venue.query.filter(func.lower(Venue.name).contains(search_term))
  count = 0
  for venue in venues:
    count += 1 
    data = {}
    data['id'] = venue.id 
    data['name'] = venue.name
    response['data'].append(data)
  response['count'] = count  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  error = False 
  try: 
    venue = Venue.query.get(venue_id)
  except:
    error = True 
    print(sys.exc_info())
  if error:
    flash('An error occurred. Venue with id ' + venue_id + ' could not be shown.')
  else: 
    body = {}
    body['id'] = venue.id
    body['name'] = venue.name
    body['city'] = venue.city
    body['phone'] = venue.phone
    body['genres'] = venue.genres if venue.genres else []
    body['image_link'] = venue.image_link 
    body['facebook_link'] = venue.facebook_link 
    body['website'] = venue.website 
    body['seeking_talent'] = venue.seeking_talent
    body['seeking_description'] = venue.seeking_description
    body['upcoming_shows'] = get_shows_by_page_and_date_status("venue",venue.id,"upcoming")
    body['upcoming_shows_count'] = len(body['upcoming_shows'])
    body['past_shows'] = get_shows_by_page_and_date_status("venue", venue.id,"past")
    body['past_shows_count'] = len(body['past_shows'])
  return render_template('pages/show_venue.html', venue=body)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False 
  try: 
    new_venue = Venue(name=request.form['name'], 
                      city=request.form['city'],
                      state=request.form['state'],
                      phone=request.form['phone'],
                      genres=request.form['genres'],
                      facebook_link=request.form['facebook_link'])
    db.session.add(new_venue)
    db.session.commit()
  except:
    error = True 
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + 'was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  error = False
  venue = Venue.query.get(venue_id)
  venue_name = venue.name
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error = True 
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + venue_name + ' could not be deleted!')
  else:
    flash('Venue ' + venue_name + ' was successfully deleted! ')
  return render_template('pages/home.html')
  
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = []
  for artist in artists:
  	data.append({"id": artist.id, "name": artist.name})
  return render_template('pages/artists.html', artists=data)

def get_shows_by_page_and_date_status(page,entity_id,status):
    #Returns an array of Show objects filtered by whether we want 
    #information for artists or venues and classified by upcoming or 
    #past shows.

    #Parameters:
    # page (str):Valid values are "artist" and "venue"
    # entity_id (integer): artist_id or venue_id 
    # status (str): Valid values are "upcoming" and "past"

    #Returns:
    #    result (Array): Array of objects containing artist_name, 
    # artist_id, venue_name, venue_id and the show's start_time   
  page, status = page.lower(), status.lower()
  result = []
  if page == "artist":
    shows = Show.query.filter_by(artist_id=entity_id)
  if page == "venue":
    shows = Show.query.filter_by(venue_id=entity_id)
  for show in shows:
    curr = {}
    curr['artist_name'] = Artist.query.get(show.artist_id).name
    curr['venue_name'] = Venue.query.get(show.venue_id).name
    curr['artist_id'] = show.artist_id 
    curr['venue_id'] = show.venue_id 
    curr['start_time'] = str(show.start_time)    
    if status == 'upcoming' and show.start_time > datetime.today():
      result.append(curr)
    if status == 'past' and show.start_time < datetime.today():
      result.append(curr)   
  return result 

@app.route('/artists/search', methods=['POST'])
def search_artists():
  response = {}
  response['data'] = []
  search_term = request.form.get('search_term').lower()
  artists = Artist.query.filter(func.lower(Artist.name).contains(search_term)) 
  count = 0
  for artist in artists:
    count += 1 
    data = {}
    data['id'] = artist.id 
    data['name'] = artist.name 
    response['data'].append(data)
  response['count'] = count
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id  error = False
  error = False 
  try: 
    artist = Artist.query.get(artist_id)
  except:
    error = True 
    print(sys.exc_info())
  if error:
    flash('An error occurred. Artist with id ' + artist_id + ' could not be shown.')
  else: 
    body = {}
    body['id'] = artist.id
    body['name'] = artist.name
    body['city'] = artist.city
    body['phone'] = artist.phone
    body['genres'] = artist.genres if artist.genres else []
    body['image_link'] = artist.image_link 
    body['facebook_link'] = artist.facebook_link 
    body['website'] = artist.website 
    body['seeking_venue'] = artist.seeking_venue
    body['seeking_description'] = artist.seeking_description
    body['upcoming_shows'] = get_shows_by_page_and_date_status("artist",artist.id,"upcoming")
    body['upcoming_shows_count'] = len(body['upcoming_shows'])
    body['past_shows'] = get_shows_by_page_and_date_status("artist", artist.id,"past")
    body['past_shows_count'] = len(body['past_shows'])
  return render_template('pages/show_artist.html', artist=body)
  
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # artist record with ID <artist_id> using the new attributes
  error = False 
  try: 
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form['genres']
    artist.facebook_link = request.form['facebook_link']
    db.session.commit()
  except:
    error = True 
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  else:
    flash('Artist ' + request.form['name'] + 'was successfully updated!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.genres = request.form['genres']
    venue.facebook_link = request.form['facebook_link']
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + 'was not updated')
  else:
    flash('Venue ' + request.form['name'] + 'was updated successfully')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False 
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    new_artist = Artist(name=name, city=city, state=state, phone=phone)
    db.session.add(new_artist)
    db.session.commit()
  except:
    error = True 
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close() 
  if error:
    abort(400)
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows:
    curr = {}
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)
    curr["venue_name"] = venue.name 
    curr["artist_name"] = artist.name 
    curr["venue_id"] = show.venue_id 
    curr["artist_id"] = show.artist_id 
    curr["artist_image_link"] = artist.image_link
    curr["start_time"] = str(show.start_time)
    data.append(curr)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create', methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    error = True 
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close() 
  if error:
    flash('Show by artist' + request.form['artist_id'] + 'at ' + request.form['venue_id'] + 'could not be created :(')
  else:
    flash('Successfully created show by ' + request.form['artist_id'] + ' :)')
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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
