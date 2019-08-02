#!/usr/bin/env python3
#

from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem

app = Flask(__name__)

engine = create_engine('sqlite:///categories.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/categories/')
def showCategories():
  categories = session.query(Category).all()
  latestItems = session.query(CategoryItem).order_by(text('id desc')).all()
  return render_template('showCategories.html', categories=categories, latest_items=latestItems)

@app.route('/category/new/', methods=['GET', 'POST'])
def addCategory():
  if request.method == 'POST':
    addCategory = Category(name=request.form['name'])
    session.add(addCategory)
    session.commit()
    return redirect(url_for('showCategories'))
  else:
    return render_template('addCategory.html')

@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
  editedCategory = session.query(Category).filter_by(id = category_id).one()
  if request.method == 'POST':
    if request.form['name']:
      editedCategory.name = request.form['name']
    session.add(editedCategory)
    session.commit()
    return redirect(url_for('showItems', category_id=category_id))
  else:
    return render_template('editCategory.html', category_id=category_id, category_name=editedCategory.name)

@app.route('/category/<int:category_id>/delete/')
def deleteCategory(category_id):
  itemToDelete = session.query(Category).filter_by(id = category_id).one()
  if request.method == 'POST':
    session.delete(itemToDelete)
    session.commit()
    return redirect(url_for('showItems', category_id=category_id))
  else:
    return render_template('deleteCategory.html', category_id=category_id, category_name=itemToDelete.name)

@app.route('/category/<int:category_id>/items/')
def showItems(category_id):
  categories = session.query(Category).all()
  category = session.query(Category).filter_by(id=category_id).one()
  categoryItems = session.query(CategoryItem).filter_by(category_id=category_id).all()
  return render_template('showItems.html',
    category=category,
    category_id=category_id,
    categories=categories,
    categoryItems=categoryItems
  )

@app.route('/category/<int:category_id>/item/<int:item_id>/')
def showItem(category_id, item_id):
  categoryItems = session.query(CategoryItem).filter_by(category_id=category_id).all()
  categoryItem = session.query(CategoryItem).filter_by(id=item_id).one()
  return render_template('showItem.html', category_id=category_id, item=categoryItem, categoryItems=categoryItems )

@app.route('/category/<int:category_id>/item/new/', methods=['GET', 'POST'])
def addItem(category_id):
  if request.method == 'POST':
    newCategoryItem = CategoryItem(name=request.form['name'], description=request.form['desc'], category_id=category_id)
    session.add(newCategoryItem)
    session.commit()
    return redirect(url_for('showItems', category_id=category_id))
  else:
    return render_template('addItem.html', category_id=category_id)

@app.route('/category/<int:category_id>/item/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(category_id, item_id):
  itemToEdit = session.query(CategoryItem).filter_by(id = item_id).one()
  if request.method == 'POST':
    if request.form['name']:
      itemToEdit.name = request.form['name']
    if request.form['desc']:
      itemToEdit.description = request.form['desc']
    session.add(itemToEdit)
    session.commit()
    return redirect(url_for('showItem', category_id=category_id, item_id=item_id))
  else:
    return render_template('editItem.html', category_id=category_id, item=itemToEdit)

@app.route('/category/<int:category_id>/item/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
  itemToDelete = session.query(CategoryItem).filter_by(id = item_id).one()
  if request.method == 'POST':
    session.delete(itemToDelete)
    session.commit()
    return redirect(url_for('showItem', category_id=category_id, item=itemToDelete))
  else:
    return render_template('deleteItem.html', category_id=category_id, item=itemToDelete)


if __name__ == '__main__':
  app.debug = True
  app.run(host='0.0.0.0', port=5000)

