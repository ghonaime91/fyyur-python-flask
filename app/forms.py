from datetime import datetime
from email import message
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, Regexp, ValidationError,Optional
from app.enums import *



#  function to validate Genre ,i took a look in this link
# https://wtforms.readthedocs.io/en/stable/validators/#custom-validators

def validate_genres(genres):
    def _validate(form, field):
        error = False

        for value in field.data:
            if value not in genres:
                error = True

        if error:
            raise ValidationError('Not valid option')

    return _validate





class ShowForm(FlaskForm):
    artist_id = StringField('artist_id',validators=[DataRequired(),
    Regexp(r'^\d+$',message='Invalid Id !')])

    venue_id = StringField('venue_id' ,validators=[DataRequired(),
    Regexp(r'^\d+$',message='Invalid Id !')])
    
    start_time = DateTimeField( 'start_time',
    validators=[DataRequired()], default= datetime.today() )




class VenueForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()] )

    city = StringField('city', validators=[DataRequired()] )
    
    state = SelectField('state', validators=[ DataRequired(),
    AnyOf([item.value for item in State])], choices=State.items() )

    address = StringField( 'address', validators=[DataRequired()] )

    phone = StringField('phone', validators= [ DataRequired(),Regexp(r'^[0-9\-\+]+$', 0, 
    message='The phone must be valid' )] )

    image_link = StringField('image_link', validators=[URL()] )

    genres = SelectMultipleField('genres', validators=[DataRequired(),
    validate_genres([item.value for item in Genre])], choices=Genre.items() )

    facebook_link = StringField('facebook_link', validators=[URL()] )

    website_link = StringField( 'website_link', validators=[URL()] )

    seeking_talent = BooleanField( 'seeking_talent' )

    seeking_description = StringField( 'seeking_description' )




class ArtistForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()] )

    city = StringField('city', validators=[DataRequired()] )

    state = SelectField('state', validators=[ DataRequired(),
    AnyOf([item.value for item in State]) ],choices=State.items() )

    phone = StringField('phone', validators=[DataRequired(), Regexp(
    r'^[0-9\-\+]+$', 0, message='The phone must be valid' )] )

    image_link = StringField('image_link', validators=[URL()])

    genres = SelectMultipleField('genres', validators=[DataRequired(),
    validate_genres([item.value for item in Genre])], choices=Genre.items() )

    facebook_link = StringField('facebook_link', validators=[Optional(),URL()] )

    website_link = StringField('website_link' , validators=[Optional(), URL()])

    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = StringField('seeking_description' )

