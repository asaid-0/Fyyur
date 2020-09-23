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
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = db_init(app)

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
  current_time = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
  # JOIN QUERY
  venue = Venue.query.join(Show, Venue.shows).filter(Show.venue_id == venue_id).first()
  data = venue.serialize
  data['upcoming_shows'] = [show.serialize for show in venue.shows if show.serialize['start_time'] > current_time]
  data['past_shows'] = [show.serialize for show in venue.shows if show.serialize['start_time'] <= current_time]
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
  current_time = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
  # JOIN QUERY
  artist = Artist.query.join(Show, Artist.shows).filter(Show.artist_id == artist_id).first()
  data = artist.serialize
  data['upcoming_shows'] = [show.serialize for show in artist.shows if show.serialize['start_time'] > current_time]
  data['past_shows'] = [show.serialize for show in artist.shows if show.serialize['start_time'] <= current_time]

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
