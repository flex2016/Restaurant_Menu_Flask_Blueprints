#################
#### imports ####
#################

from flask import flash, redirect, render_template, request, session, url_for, Blueprint, jsonify, make_response
from project import db
from project.models import Restaurant, User, MenuItem

from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets  # stores client id , secrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenCredentials
import httplib2
import json
import requests
import os


################
#### config ####
################

home_blueprint = Blueprint('home', __name__, template_folder='templates')


################
#### routes ####
################


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    db.session.add(newUser)
    db.session.commit()
    user = db.session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = db.session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = db.session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Create anti-forgery state token to protect the security of your user


@home_blueprint.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@home_blueprint.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = os.environ['FACEBOOK_APP_ID']
    app_secret = os.environ['FACEBOOK_APP_SECRET']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.9/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.9/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@home_blueprint.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"



# Disconnect based on provider
@home_blueprint.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('home.showRestaurants'))
    else:
        flash("You were not logged in")
        return redirect(url_for('home.showRestaurants'))



# JSON APIs to view Restaurant Information
@home_blueprint.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = db.session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@home_blueprint.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    Menu_Item = db.session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(Menu_Item=Menu_Item.serialize)


@home_blueprint.route('/restaurant/JSON')
def restaurantsJSON():
    restaurants = db.session.query(Restaurant).all()
    return jsonify(restaurants=[r.serialize for r in restaurants])


# Show all restaurants
@home_blueprint.route('/')
@home_blueprint.route('/restaurant/')
def showRestaurants():
    # restaurants = Restaurant.query.all()
    restaurants = db.session.query(Restaurant).order_by(Restaurant.name.asc())
    return render_template('restaurants.html', restaurants=restaurants)


# Create a new restaurant


@home_blueprint.route('/restaurant/new/', methods=['GET', 'POST'])
def newRestaurant():
    if request.method == 'POST':
        newRestaurant = Restaurant(
            name=request.form['name'], user_id=1)
        newRestaurant.save()
        flash('New Restaurant %s Successfully Created' % newRestaurant.name)
        return redirect(url_for('home.showRestaurants'))
    else:
        return render_template('newRestaurant.html')

# Edit a restaurant


@home_blueprint.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):

    editedRestaurant = db.session.query(
        Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedRestaurant.name = request.form['name']
            editedRestaurant.save()
            flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
            return redirect(url_for('home.showRestaurants'))
    else:
        return render_template('editRestaurant.html', restaurant=editedRestaurant)


# Delete a restaurant


@home_blueprint.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):

    restaurantToDelete = db.session.query(
        Restaurant).filter_by(id=restaurant_id).one()
    # alert messages tro let user know hes not authorized since he didnt create it, used in create, edit, delete functions

    if request.method == 'POST':
        restaurantToDelete.delete()
        flash('%s Successfully Deleted' % restaurantToDelete.name)
        return redirect(url_for('home.showRestaurants', restaurant_id=restaurant_id))
    else:
        return render_template('deleteRestaurant.html', restaurant=restaurantToDelete)

# Show a restaurant menu


@home_blueprint.route('/restaurant/<int:restaurant_id>/')
@home_blueprint.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()

    items = db.session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    # check who created the file and render template based on that
    return render_template('menu.html', items=items, restaurant=restaurant)


# Create a new menu item
@home_blueprint.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'], description=request.form['description'], price=request.form[
                           'price'], course=request.form['course'], restaurant_id=restaurant_id, user_id=restaurant.user_id)
        newItem.save()
        flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('home.showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant=restaurant)

# Edit a menu item


@home_blueprint.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    editedItem = db.session.query(MenuItem).filter_by(id=menu_id).one()
    restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        editedItem.save()
        flash('Menu Item Successfully Edited')
        return redirect(url_for('home.showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html',  item=editedItem, restaurant=restaurant)


# Delete a menu item
@home_blueprint.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
    itemToDelete = db.session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        itemToDelete.delete()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('home.showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deleteMenuItem.html',  restaurant=restaurant, item=itemToDelete)



@home_blueprint.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/upload/', methods=['GET', 'POST'])
def upload(restaurant_id, menu_id):
    restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = db.session.query(MenuItem).filter_by(id=menu_id).one()  # find item to edit
    if request.method == 'POST':
        flash("Photo Uploaded!")
        return redirect(url_for('home.showMenu', restaurant_id=restaurant_id))
    else:
        # USE THE RENDER_TEMPLATE FUNCTION BELOW TO SEE THE VARIABLES YOU
        # SHOULD USE IN YOUR EDITMENUITEM TEMPLATE
        return render_template(
            'upload.html',  restaurant=restaurant, item=item)  # item represents the item we want to edit
