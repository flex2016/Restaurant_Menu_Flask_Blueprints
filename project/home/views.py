#################
#### imports ####
#################

from flask import flash, redirect, render_template, request, url_for, \
    Blueprint, jsonify
from project import db
from project.models import Restaurant, User, MenuItem
from project.user.views import login_session, getUserInfo
import json
import requests



################
#### config ####
################

home_blueprint = Blueprint('home', __name__, template_folder='templates')


################
#### routes ####
################


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
@home_blueprint.route('/restaurant')
def showRestaurants():
    # restaurants = Restaurant.query.all()
    restaurants = db.session.query(Restaurant).order_by(Restaurant.name.asc())
    if 'username' not in login_session:  # render diff templates based on if user is logged in or not
        return render_template('publicrestaurants.html', restaurants=restaurants)
    else:
        return render_template('restaurants.html', restaurants=restaurants)


# Create a new restaurant
@home_blueprint.route('/restaurant/new', methods=['GET', 'POST'])
def newRestaurant():
    if 'username' not in login_session:  # verify if user is logged in
        return redirect('/login')
    if request.method == 'POST':
        newRestaurant = Restaurant(
            name=request.form['name'], user_id=login_session['user_id'])  # add user id to know who created the restaurant
        newRestaurant.save()
        flash('New Restaurant %s Successfully Created' % newRestaurant.name)
        return redirect(url_for('home.showRestaurants'))
    else:
        return render_template('newRestaurant.html')

# Edit a restaurant


@home_blueprint.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedRestaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
    if editedRestaurant.user_id != login_session['user_id']:
        return "<script> function myFunction() {alert('You are not authorized to edit this restaurant. Please create your own restaurant in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedRestaurant.name = request.form['name']
            editedRestaurant.save()
            flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
            return redirect(url_for('home.showRestaurants'))
    else:
        return render_template('editRestaurant.html', restaurant=editedRestaurant)


# Delete a restaurant


@home_blueprint.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
    restaurantToDelete = db.session.query(
        Restaurant).filter_by(id=restaurant_id).one()
    # alert messages tro let user know hes not authorized since he didnt create it, used in create, edit, delete functions
    if restaurantToDelete.user_id != login_session['user_id']:
        return "<script> function myFunction() {alert('You are not authorized to delete this restaurant. Please create your own restaurant in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        restaurantToDelete.delete()
        flash('%s Successfully Deleted' % restaurantToDelete.name)
        return redirect(url_for('home.showRestaurants', restaurant_id=restaurant_id))
    else:
        return render_template('deleteRestaurant.html', restaurant=restaurantToDelete)

# Show a restaurant menu


@home_blueprint.route('/restaurant/<int:restaurant_id>')
@home_blueprint.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
    restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
    creator = getUserInfo(restaurant.user_id)  # who created the menu
    items = db.session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    # check who created the file and render template based on that
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicmenu.html', items=items, restaurant=restaurant, creator=creator)
    else:
        return render_template('menu.html', items=items, restaurant=restaurant, creator=creator)


# Create a new menu item
@home_blueprint.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
    restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
    if login_session['user_id'] != restaurant.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add menu items to this restaurant. Please create your own restaurant in order to add items.');}</script><body onload='myFunction()''>"
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
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = db.session.query(MenuItem).filter_by(id=menu_id).one()
    restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
    if login_session['user_id'] != restaurant.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit menu items to this restaurant. Please create your own restaurant in order to edit items.');}</script><body onload='myFunction()''>"

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
    if 'username' not in login_session:
        return redirect('/login')
    restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).one()
    itemToDelete = db.session.query(MenuItem).filter_by(id=menu_id).one()
    if login_session['user_id'] != restaurant.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete menu items to this restaurant. Please create your own restaurant in order to delete items.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        itemToDelete.delete()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('home.showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deleteMenuItem.html',  restaurant=restaurant, item=itemToDelete)



@home_blueprint.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/upload', methods=['GET', 'POST'])
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

@home_blueprint.errorhandler(404)
def not_found(error):
    return render_template('404.html')

# error example code


@home_blueprint.route('/slashboard')
def slashboard():
    restaurants = db.session.query(Restaurant).order_by(Restaurant.name.asc())
    try:
        return render_template('publicrestaurants.html', restaurants=restaurants)
    except Exception as error:
        return render_template('404.html', error=error)


@home_blueprint.route('/request-info')
def request_info():
    # Get location info using https://freegeoip.net/
    geoip_url = 'http://freegeoip.net/json/{}'.format(request.remote_addr)
    client_location = requests.get(geoip_url).json()
    return render_template('info.html',
                           client_location=client_location)
