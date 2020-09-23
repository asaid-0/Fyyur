from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def db_init(app):
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    return db

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
          "venue_image_link": self.venue.image_link,
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

    @property
    def serialize(self):
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
        }