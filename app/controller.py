#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
from unicodedata import name
from app import app
import dateutil.parser
import babel
from flask import (
    render_template,
    request,
    flash,
    redirect,
    url_for,
    abort
)
from sqlalchemy import desc
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from app.forms import *
from app.models import *
import collections


collections.Callable = collections.abc.Callable

moment = Moment(app)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
#function to show form's error
def show_form_errors(field, err_msgs):
    return flash(
        f'Some errors on {field.replace("_", " ")}: ' +
        ' '.join([str(msg) for msg in err_msgs]),
        'danger'
    )


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
# Done
@app.route('/venues')
def venues():

    #venues grouped by city & state
    areas = Venue.query.with_entities(
        Venue.city, Venue.state
    ).distinct().all()
    #all venues data
    venues = db.session.query(Venue.id, Venue.name,
    Venue.city, Venue.state).order_by(Venue.id.desc()).all()
    #query for upcoming shows
    num_upcoming_shows = db.session.query(Venue.id, Venue.name,
     Show.start_time).join(Show)\
    .filter(Show.start_time > datetime.utcnow()).all()

    data = []
    #first loop for every venue by state and city
    for area in areas:
        rowArea = {'city': area.city, 'state': area.state, 'venues': []}
        #loop for all venues data
        for venue in venues:
            if area.city == venue.city and area.state == venue.state:
                rowVenue = {'id': venue.id, 'name': venue.name,
                            "num_upcoming_shows": 0}
                #loop for gettig future shows number
                for num in num_upcoming_shows:
                    if num.id == venue.id:
                        rowVenue["num_upcoming_shows"] += 1

                rowArea['venues'].append(rowVenue)

        data.append(rowArea)

    return render_template('pages/venues.html', areas=data)


# search venue
# Done
@app.route('/venues/search', methods=['POST'])
def search_venues():
    #getting search key then query based on it (case insensitive)
    search_term = request.form.get('search_term')
    results = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
    count = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).count()
    
    #Results list build
    response = {}
    response['count'] = count
    data = []
    for result in results:
        num_upcoming_shows = Show.query.filter(Show.venue_id == result.id)\
            .filter(Show.start_time > datetime.utcnow()).count()
        row = {
            'id': result.id,
            'name': result.name,
            "num_upcoming_shows": num_upcoming_shows
        }
        data.append(row)

    response['data'] = data

    return render_template('pages/search_venues.html',
    results=response, search_term=request.form.get('search_term', ''))


#Done
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    #getting venue by its id
    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    #convert genres to a list after removing the curly braces that came from DB
    genres = venue.genres.replace('{', '').replace('}', '').split(',')
    #getting past shows and its count with artist information
    past_shows_query = db.session.query(Show.venue_id,
        Show.artist_id, Show.start_time,
        Artist.name, Artist.image_link)\
        .filter(Show.venue_id==venue_id)\
        .filter(Show.start_time<datetime.utcnow()).join(Artist).all()
    #loop through past shows and build the list data for an artist
    past_show = []
    past_show_count = 0
    for show in past_shows_query:
        row = {
            'artist_id':show.artist_id,
            'artist_name':show.name,
            'artist_image_link':show.image_link,
            #convert date time to string
            'start_time':show.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
        past_show_count += 1
        past_show.append(row)
    
    #getting future shows and its count with artist information
    upcoming_shows_query = db.session.query(Show.venue_id,
        Show.artist_id, Show.start_time,
        Artist.name, Artist.image_link)\
        .filter(Show.venue_id==venue_id)\
        .filter(Show.start_time>datetime.utcnow()).join(Artist).all()
    
    #loop through future shows and build the list data for an artist
    upcoming_show = []
    upcoming_show_count = 0
    for show in upcoming_shows_query:
        row = {
            'artist_id':show.artist_id,
            'artist_name':show.name,
            'artist_image_link':show.image_link,
            #convert date time to string
            'start_time':show.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
        upcoming_show_count += 1
        upcoming_show.append(row)


    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_show,
        "upcoming_shows": upcoming_show,
        "past_shows_count": past_show_count,
        "upcoming_shows_count": upcoming_show_count,
    }
    
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


# Done
# --------------------------------------------------------------------------
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    form = VenueForm()
    # first work on form validation errors
    if not form.validate_on_submit():
        for field, error in form.errors.items():
            show_form_errors(field, error)
        return redirect(url_for('create_venue_form'))
    # if there is no validation error creste a venue object
    try:
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            genres=form.genres.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            facebook_link=form.facebook_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(venue)
        db.session.commit()
    except Exception:
        error = True
        db.session.rollback()
        #errors log
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        flash(f'Venue {form.name.data} was successfully listed!', 'success')
    else:
        abort(400)
        flash(
            f'An error occurred. Venue {form.name.data} could not be listed.', 'danger')
    return redirect(url_for('venues'))
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    # -----------------------------------------------------------------------------------

#Done
@app.route('/venues/<venue_id>', methods=['DELETE', 'POST'])
def delete_venue(venue_id):
    error=False
    try:
        venue = Venue.query.get_or_404(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except Exception:
        error=True
        db.session.rollback()
        print(sys.exc_info())
        return render_template('errors/500.html', error=str(Exception))
    finally:
        db.session.close()
    if error:
        abort(404)
        flash(' error The venue did not delete !','warning')
    else:
        flash('Venue deleted successfully','info')
    return render_template('pages/home.html')




#  Artists
#  ----------------------------------------------------------------
#Done
@app.route('/artists')
def artists():
    # Getting all artists order by id descending 
    artists = db.session.query(Artist.id, Artist.name).order_by(desc(Artist.id)).all()
    data = []
    for artist in artists:
        data.append({
            'id':artist.id,
            'name':artist.name
        })
   
    return render_template('pages/artists.html', artists=data)

#Done
@app.route('/artists/search', methods=['POST'])
def search_artists():
    #getting search key then query based on it (case insensitive)
    search_term = request.form.get('search_term')
    artists= Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
    #build a list for an artist info
    data=[]
    for artist in artists:
        num_upcoming_shows = Show.query.filter(Show.artist_id==artist.id).count()
        data.append({
            'id':artist.id,
            'name':artist.name,
            'num_upcoming_shows':num_upcoming_shows
        })
    #build search result for the artist
    response = {
        "count": len(artists),
        "data": data
    }
    return render_template('pages/search_artists.html',
    results=response, search_term=request.form.get('search_term', ''))

#Done
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    # getting the artist and shows and venues with the given artist_id
    artist = Artist.query.get_or_404(artist_id)

    past_shows = db.session.query(
        Show.artist_id,Show.start_time, Venue.id,
        Venue.name,Venue.image_link
        )\
        .filter(
            Show.artist_id == artist_id
            )\
        .filter(
            Show.start_time<datetime.utcnow()
            ).join(Venue).all()

    upcoming_shows = db.session.query(
        Show.artist_id,Show.start_time, Venue.id,
        Venue.name,Venue.image_link
        )\
        .filter(
            Show.artist_id == artist_id
            )\
        .filter(
            Show.start_time>datetime.utcnow()
            ).join(Venue).all()
    # formating genres and convert it to a list    
    genres = artist.genres.replace('{', '').replace('}', '').split(',')    
    
    past_shows_list=[]
    upcoming_shows_list=[]
    #loop through past shows and build the list data for a venue
    for show in past_shows:
        past_shows_list.append({
            "venue_id": show.id,
            "venue_name": show.name,
            "venue_image_link": show.image_link,
            #convert date time to string
            "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        })
    #loop through future shows and build the list data for a venue
    for show in upcoming_shows:
        upcoming_shows_list.append({
            "venue_id": show.id,
            "venue_name": show.name,
            "venue_image_link": show.image_link,
            #convert date time to string
            "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        })

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link":artist.facebook_link ,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows_list,
        "upcoming_shows": upcoming_shows_list,
        "past_shows_count": len(past_shows_list),
        "upcoming_shows_count": len(upcoming_shows_list),
    }
   

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
#Done
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

    form = ArtistForm()
    artist_query = Artist.query.get_or_404(artist_id)
    genres = artist_query.genres.replace('{', '').replace('}', '').split(',') 
    print(genres)
    artist = {
        "id": artist_query.id,
        "name": artist_query.name
       }

    # populate form with values from artist with ID <artist_id>
    form.name.data=artist_query.name
    form.genres.data= genres
    form.city.data= artist_query.city
    form.state.data= artist_query.state
    form.phone.data= artist_query.phone
    form.website_link.data= artist_query.website_link
    form.facebook_link.data= artist_query.facebook_link
    form.seeking_venue.data= artist_query.seeking_venue
    form.seeking_description.data= artist_query.seeking_description
    form.image_link.data= artist_query.image_link
    
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error = False
    form = ArtistForm()
    artist = Artist.query.get_or_404(artist_id)
    if not form.validate_on_submit():
        for field, error in form.errors.items():
            show_form_errors(field,error)
            return redirect(url_for('edit_venue',artist_id=artist_id))
    try:
        artist.name=form.name.data
        artist.city=form.city.data
        artist.state=form.state.data
        artist.phone=form.phone.data
        artist.genres=form.genres.data
        artist.image_link=form.image_link.data
        artist.facebook_link=form.facebook_link.data
        artist.website_link=form.website_link.data
        artist.seeking_description=form.seeking_description.data
        artist.seeking_venue=form.seeking_venue.data
        db.session.commit()
    except Exception:
        error=True
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        flash(f'Artist {form.name.data} was successfully updated', 'success')
    else:
        abort(400)
        flash(
            f'An error occurred. Artist {form.name.data} could not be updated.', 'danger')
    return redirect(url_for('show_artist', artist_id=artist_id))

#Done
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

    venue_query = Venue.query.get_or_404(venue_id)
    form = VenueForm()
    genres = venue_query.genres.replace('{', '').replace('}', '').split(',') 
    venue = {
        "id": venue_query.id,
        "name": venue_query.name
       }

    # populate form with values from venue with ID <venue_id>
    form.name.data=venue_query.name
    form.genres.data= genres
    form.address.data= venue_query.address
    form.city.data= venue_query.city
    form.state.data= venue_query.state
    form.phone.data= venue_query.phone
    form.website_link.data= venue_query.website_link
    form.facebook_link.data= venue_query.facebook_link
    form.seeking_talent.data= venue_query.seeking_talent
    form.seeking_description.data= venue_query.seeking_description
    form.image_link.data= venue_query.image_link

    return render_template('forms/edit_venue.html', form=form, venue=venue)

#Done
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False
    form = VenueForm()
    venue = Venue.query.get_or_404(venue_id)
    if not form.validate_on_submit():
        for field, error in form.errors.items():
            show_form_errors(field,error)
            return redirect(url_for('edit_venue',venue_id=venue_id))
    try:
        venue.name=form.name.data
        venue.city=form.city.data
        venue.state=form.state.data
        venue.address=form.address.data
        venue.phone=form.phone.data
        venue.genres=form.genres.data
        venue.image_link=form.image_link.data
        venue.facebook_link=form.facebook_link.data
        venue.website_link=form.website_link.data
        venue.seeking_description=form.seeking_description.data
        venue.seeking_talent=form.seeking_talent.data
        db.session.commit()
    except Exception:
        error=True
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()
    if not error:
        flash(f'Venue {form.name.data} was successfully updated', 'success')
    else:
        abort(400)
        flash(
            f'An error occurred. Venue {form.name.data} could not be updated.', 'danger')
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


# Done
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    error = False
    form = ArtistForm()
    if not form.validate_on_submit():
        for field, error in form.errors.items():
            show_form_errors(field, error)
            return redirect(url_for('create_artist_form'))
    try:
        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            facebook_link=form.facebook_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(artist)
        db.session.commit()
    except Exception:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        flash(f'Artist {form.name.data} was successfully listed!', 'success')
    else:
        abort(400)
        flash(
            f'An error occurred. Artist {form.name.data} could not be listed.', 'danger')

    return redirect(url_for('artists'))

#Done
@app.route('/artists/<int:artist_id>', methods=['DELETE', 'POST'])
def delete_artist(artist_id):
    error=False
    try:
        artist = Artist.query.get_or_404(artist_id)
        db.session.delete(artist)
        db.session.commit()
    except Exception:
        error=True
        db.session.rollback()
        print(sys.exc_info())
        return render_template('errors/500.html', error=str(Exception))
    finally:
        db.session.close()
    if error:
        abort(404)
        flash(' error The artist did not delete !','warning')
    else:
        flash('Artist deleted successfully','info')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    shows = db.session.query(
        Show.artist_id, Show.venue_id,
        Show.start_time,
        Venue.name,
        Artist.name,Artist.image_link,
        ).join(Venue).join(Artist).all()

    data = []
    for show in shows:
        data.append({
        "venue_id": show[1],
        "venue_name": show[3],
        "artist_id":show[0],
        "artist_name": show[4],
        "artist_image_link": show[5],
        "start_time": str(show[2])
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


# Done
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    form = ShowForm()
    if not form.validate_on_submit():
        for field, error in form.errors.items():
            show_form_errors(field, error)
            return redirect(url_for('create_shows'))
    # check if the id is exist
    venue = Venue.query.filter_by(id=form.venue_id.data).first()
    artist = Artist.query.filter_by(id=form.artist_id.data).first()
    if venue is not None and artist is not None:
        try:
            show = Show(
                venue_id=form.venue_id.data,
                artist_id=form.artist_id.data,
                start_time=form.start_time.data
            )
            db.session.add(show)
            db.session.commit()
        except Exception:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close

        if not error:
            flash('Show was successfully listed!', 'success')
        else:
            abort(400)
            flash('An error occurred. Show could not be listed.', 'danger')
    # # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    else:
        flash('one or more of the ids is not exist', 'danger')
        return redirect(url_for('create_shows'))

    return redirect(url_for('shows'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(405)
def not_found_error(error):
    return render_template('errors/405.html'), 405


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
