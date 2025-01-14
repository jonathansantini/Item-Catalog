#!/usr/bin/env python3
#

from flask import (
    Flask,
    flash,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    session as login_session,
    make_response
)
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import random
import string

app = Flask(__name__)
app.config.from_pyfile('instance/application.cfg')

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

engine = create_engine('sqlite:///categories.db', connect_args={
  'check_same_thread': False}
  )
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads((h.request(url, 'GET')[1]).decode())
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
          json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

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
    output += ' " style = "width: 300px; height: 300px;"'
    output += ' "border-radius: 150px;-webkit-border-radius: "'
    output += '150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s'), access_token
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token='
    url += '%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("Failed to revoke token for given user.")
        return redirect(url_for('showCategories'))


# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/')
@app.route('/categories/')
def showCategories():
    categories = session.query(Category).all()
    latestItems = session.query(CategoryItem).order_by(text('id desc')).all()
    return render_template(
      'category/show.html',
      categories=categories,
      latest_items=latestItems
    )


@app.route('/category/new/', methods=['GET', 'POST'])
def addCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name']:
            addCategory = Category(
                name=request.form['name'],
                user_id=login_session['user_id']
            )
            session.add(addCategory)
            session.commit()
            flash('New Category %s Successfully Created' % addCategory.name)
            return redirect(url_for('showCategories'))
        else:
            flash('Please add a category name')
            return render_template('category/add.html')
    else:
        return render_template('category/add.html')


@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    editedCategory = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedCategory.user_id != login_session['user_id']:
        output = "<script>function myFunction() {"
        output += "alert('You are not authorized to edit this category. "
        output += "Please create your own category in order to edit.');}"
        output += "</script><body onload='myFunction()'>"
        return output
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            session.add(editedCategory)
            flash('Category Successfully Edited %s' % editedCategory.name)
            session.commit()
            return redirect(url_for('showItems', category_id=category_id))
        else:
            flash('Please add a category name')
            return render_template(
                'category/edit.html',
                category_id=category_id
            )
    else:
        return render_template(
            'category/edit.html',
            category_id=category_id,
            category_name=editedCategory.name
        )


@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    itemToDelete = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if itemToDelete.user_id != login_session['user_id']:
        output = "<script>function myFunction() {"
        output += "alert('You are not authorized to delete this category. "
        output += "Please create your own category in order to delete.');}"
        output += "</script>body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        flash('Category Successfully Deleted %s' % itemToDelete.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template(
            'category/delete.html',
            category_id=category_id,
            category_name=itemToDelete.name
        )


@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/items/')
def showItems(category_id):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()
    categoryItems = session.query(CategoryItem).filter_by(
        category_id=category_id
    ).all()
    isCreator = True if category.user_id == login_session['user_id'] else False
    return render_template(
      'item/showAll.html',
      category=category,
      category_id=category_id,
      categories=categories,
      categoryItems=categoryItems,
      isCreator=isCreator
    )


@app.route('/category/<int:category_id>/item/<int:item_id>/')
def showItem(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    categoryItems = session.query(CategoryItem).filter_by(
        category_id=category_id
    ).all()
    categoryItem = session.query(CategoryItem).filter_by(id=item_id).one()
    isCreator = True if category.user_id == login_session['user_id'] else False
    return render_template(
        'item/show.html',
        category_id=category_id,
        item=categoryItem,
        categoryItems=categoryItems,
        isCreator=isCreator
    )


@app.route('/category/<int:category_id>/item/new/', methods=['GET', 'POST'])
def addItem(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if login_session['user_id'] != category.user_id:
        output = "<script>function myFunction() {alert('You are not"
        output += "authorized to add items to this category. Please"
        output += "create your own category in order to add items.');}"
        output += "</script><body onload='myFunction()'>"
        return output
    if request.method == 'POST':
        if request.form['name']:
            newCategoryItem = CategoryItem(
                name=request.form['name'],
                description=request.form['desc'],
                category_id=category_id,
                user_id=category.user_id
            )
            session.add(newCategoryItem)
            session.commit()
            flash(
                'New Category Item Successfully Created %s'
                % newCategoryItem.name
            )
            return redirect(url_for('showItems', category_id=category_id))
        else:
            flash('Category Item Name is required.')
            return render_template('item/add.html', category_id=category_id)
    else:
        return render_template('item/add.html', category_id=category_id)


@app.route(
    '/category/<int:category_id>/item/<int:item_id>/edit/',
    methods=['GET', 'POST']
)
def editItem(category_id, item_id):
    itemToEdit = session.query(CategoryItem).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    print(login_session['user_id'])
    print(category.user_id)
    if login_session['user_id'] != category.user_id:
        output = "<script>function myFunction() {alert('You are not"
        output += "authorized to edit this item. Please create your"
        output += "own category item in order to edit.');}"
        output += "</script><body onload='myFunction()'>"
        return output
    if request.method == 'POST':
        if request.form['name']:
            itemToEdit.name = request.form['name']
            if request.form['desc']:
                itemToEdit.description = request.form['desc']
            session.add(itemToEdit)
            session.commit()
            flash(
                'Category Item Successfully Edited %s'
                % itemToEdit.name
            )
            return redirect(
                url_for(
                    'showItem',
                    category_id=category_id,
                    item_id=item_id
                )
            )
        else:
            flash('Item Name is required.')
            return render_template(
                'item/edit.html',
                category_id=category_id,
                item=itemToEdit
            )
    else:
        return render_template(
            'item/edit.html',
            category_id=category_id,
            item=itemToEdit
        )


@app.route(
    '/category/<int:category_id>/item/<int:item_id>/delete/',
    methods=['GET', 'POST']
)
def deleteItem(category_id, item_id):
    itemToDelete = session.query(CategoryItem).filter_by(id=item_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if itemToDelete.user_id != login_session['user_id']:
        output = "<script>function myFunction() {alert('You are not"
        output += "authorized to delete this item. Please create your own"
        output += "category item in order to delete.');}</script>"
        output += "<body onload='myFunction()'>"
        return output
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Category Item Successfully Deleted %s' % itemToDelete.name)
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template(
            'item/delete.html',
            category_id=category_id,
            item_id=item_id,
            item=itemToDelete
        )


# JSON endpoints
@app.route('/category/<int:category_id>/items/json')
def categoryItemsJSON(category_id):
    items = session.query(CategoryItem).filter_by(
        category_id=category_id).all()
    return jsonify(CategoryItems=[i.serialize for i in items])


@app.route('/category/<int:category_id>/item/<int:item_id>/json')
def itemJSON(category_id, item_id):
    Item = session.query(CategoryItem).filter_by(id=item_id).one()
    return jsonify(Item=Item.serialize)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
