#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
from datetime import datetime
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
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
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    venue = db.relationship('Venue', backref=db.backref('shows', cascade="all,delete"))
    artist = db.relationship('Artist', backref=db.backref('shows', cascade="all,delete"))

    @property
    def serialize(self):
        return {
          "venue_id": self.venue_id,
          "venue_name": self.venue.name,
          "artist_id": self.artist_id,
          "artist_name": self.artist.name,
          "artist_image_link": self.artist.image_link,
          "start_time": self.start_time.strftime("%Y-%m-%d, %H:%M:%S")
        }


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    # artists = db.relationship('Show', back_populates="venues")

    def getShowsList(self, shows):
      shows_list = []
      for show in shows:
        showObj = {
          'artist_id': show.artist.id,
          'artist_name': show.artist.name,
          'artist_image_link': show.artist.image_link,
          'start_time': show.start_time.strftime("%Y-%m-%d, %H:%M:%S")
        }
        shows_list.append(showObj)
      return shows_list

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'image_link': self.image_link,
            'website_link': self.website_link,
            'facebook_link': self.facebook_link,
            'genres': self.genres,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description
        }
    @property
    def populateShows(self):
        current_time = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        upcoming_shows = Show.query.filter(Show.venue_id == self.id, Show.start_time > current_time).all()
        past_shows = Show.query.filter(Show.venue_id == self.id, Show.start_time < current_time).all()
        
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'image_link': self.image_link,
            'website_link': self.website_link,
            'facebook_link': self.facebook_link,
            'genres': self.genres,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'upcoming_shows': self.getShowsList(upcoming_shows),
            'past_shows': self.getShowsList(past_shows),
            'upcoming_shows_count': len(upcoming_shows),
            'past_shows_count': len(past_shows),
        }
class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)

    def getShowsList(self, shows):
      shows_list = []
      for show in shows:
        showObj = {
          'venue_id': show.venue.id,
          'venue_name': show.venue.name,
          'venue_image_link': show.venue.image_link,
          'start_time': show.start_time.strftime("%Y-%m-%d, %H:%M:%S")
        }
        shows_list.append(showObj)
      return shows_list

    @property
    def populateShows(self):
        current_time = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        upcoming_shows = Show.query.filter(Show.artist_id == self.id, Show.start_time > current_time).all()
        past_shows = Show.query.filter(Show.artist_id == self.id, Show.start_time < current_time).all()
        
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'image_link': self.image_link,
            'website_link': self.website_link,
            'facebook_link': self.facebook_link,
            'seeking_description': self.seeking_description,
            'seeking_venue': self.seeking_venue,
            'genres': self.genres,
            'upcoming_shows': self.getShowsList(upcoming_shows),
            'past_shows': self.getShowsList(past_shows),
            'upcoming_shows_count': len(upcoming_shows),
            'past_shows_count': len(past_shows)
        }

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
  recent_artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
  recent_venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
  
  return render_template('pages/home.html', venues=recent_venues, artists=recent_artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = Venue.query.distinct(Venue.city, Venue.state).all()
  for venue in data:
    venue.venues = [ i.serialize for i in Venue.query.filter_by(city=venue.city, state=venue.state).all() ]
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  response = {}
  search = Venue.query.filter(Venue.name.ilike(f"%{request.form.get('search_term', '')}%")).all()
  response['count'] = len(search)
  response['data'] = search
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = Venue.query.filter_by(id=venue_id).first().populateShows
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  if not form.validate():
    return render_template('forms/new_venue.html', form=form)
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    seeking_description = request.form.get('seeking_description')
    seeking_talent = form.seeking_talent.data
    facebook_link = request.form.get('facebook_link')
    website_link = request.form.get('website_link')
    image_link = request.form.get('image_link')
    venue = Venue(
      name=name,
      city=city,
      state=state,
      address=address,
      phone=phone,
      genres=genres,
      seeking_description=seeking_description,
      seeking_talent=seeking_talent,
      facebook_link=facebook_link,
      website_link=website_link,
      image_link=image_link
    )
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Error adding venue: ' + request.form['name'])
  finally:
    db.session.close()

  # return render_template('pages/home.html')
  return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.filter_by(id=int(venue_id)).first()
    if venue:
      db.session.delete(venue)
      db.session.commit()
      flash('Venue deleted successfuly!')
    else:
      raise Exception("Couldn't find venue matching this id") 
    return json.dumps({ 'success': True })
  except:
    db.session.rollback()
    flash('Error deleting venue!')
    return json.dumps({ 'success': False })
  finally:
    db.session.close()

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:
    artist = Artist.query.filter_by(id=int(artist_id)).first()
    if artist:
      db.session.delete(artist)
      db.session.commit()
      flash('Artist deleted successfuly!')
    else:
      raise Exception("Couldn't find artist matching this id") 
    return json.dumps({ 'success': True })
  except:
    db.session.rollback()
    flash('Error deleting artist!')
    return json.dumps({ 'success': False })
  finally:
    db.session.close()

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  response = {}
  search = Artist.query.filter(Artist.name.ilike(f"%{request.form.get('search_term', '')}%")).all()
  response['count'] = len(search)
  response['data'] = search
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = Artist.query.filter_by(id=artist_id).first().populateShows
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).first()
  if not artist:
    return redirect(url_for('index'))
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()
  form = ArtistForm(request.form)

  try:
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.getlist('genres')
    artist.seeking_description = request.form.get('seeking_description')
    artist.seeking_venue = form.seeking_venue.data
    artist.facebook_link = request.form.get('facebook_link')
    artist.website_link = request.form.get('website_link')
    artist.image_link = request.form.get('image_link')
    if not form.validate():
      return render_template('forms/edit_artist.html', form=form, artist=artist)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Error updating artist: ' + request.form['name'])
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()
  if not venue:
    return redirect(url_for('index'))
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()
  form = VenueForm(request.form)
  try:
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.genres = request.form.getlist('genres')
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = request.form.get('seeking_description')
    venue.facebook_link = request.form.get('facebook_link')
    venue.website_link = request.form.get('website_link')
    venue.image_link = request.form.get('image_link')
    if not form.validate():
      return render_template('forms/edit_venue.html', form=form, venue=venue)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Error updating venue: ' + request.form['name'])
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
  form = ArtistForm(request.form)
  if not form.validate():
    return render_template('forms/new_artist.html', form=form)
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    seeking_description = request.form.get('seeking_description')
    seeking_venue = form.seeking_venue.data
    facebook_link = request.form.get('facebook_link')
    website_link = request.form.get('website_link')
    image_link = request.form.get('image_link')

    artist = Artist(
      name=name,
      city=city,
      state=state,
      phone=phone,
      genres=genres,
      seeking_description=seeking_description,
      seeking_venue=seeking_venue,
      facebook_link=facebook_link,
      website_link=website_link,
      image_link=image_link
    )
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Error adding artist: ' + request.form['name'])
  finally:
    db.session.close()

  return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = [show.serialize for show in Show.query.order_by(Show.start_time.desc()).all()]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  if not form.validate():
    return render_template('forms/new_show.html', form=form)
  try:
    show = Show(artist_id=request.form.get('artist_id'), venue_id=request.form.get('venue_id'), start_time=request.form.get('start_time'))
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Error creating show!')
  finally:
    db.session.close()

  
  return redirect(url_for('index'))

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
