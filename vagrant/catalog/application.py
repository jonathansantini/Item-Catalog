#!/usr/bin/env python3
#

from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem

app = Flask(__name__)

engine = create_engine('sqlite:///categories.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/categories/')
def getCategories():
  categories = session.query(Category).all()
  return render_template('categories.html', categories=categories)

@app.route('/category/new/', methods=['GET', 'POST'])
def addCategory():
  if request.method == 'POST':
    addCategory = Category(name=request.form['name'])
    session.add(addCategory)
    session.commit()
    return redirect(url_for('getCategories'))
  else:
    return render_template('addCategory.html')

@app.route('/category/<int:category_id>/edit/')
def editCategory(category_id):
  return 'edit category %s!' % category_id

@app.route('/category/<int:category_id>/delete/')
def deleteCategory(category_id):
  return 'delete category %s!' % category_id

@app.route('/category/<int:category_id>/items/')
def showCategoryItems(category_id):
  categories = session.query(Category).all()
  category = session.query(Category).filter_by(id=category_id).one()
  categoryItems = session.query(CategoryItem).filter_by(category_id=category_id).all()
  return render_template('showCategoryItems.html',
    category=category,
    category_id=category_id,
    categories=categories,
    categoryItems=categoryItems
  )

@app.route('/category/<int:category_id>/item/<int:item_id>/')
def showCategoryItem(category_id, item_id):
  return 'show category %s item %s!' % (category_id, item_id)

@app.route('/category/<int:category_id>/item/new/', methods=['GET', 'POST'])
def addCategoryItem(category_id):
  if request.method == 'POST':
    newCategoryItem = CategoryItem(name=request.form['name'], description=request.form['desc'], category_id=category_id)
    session.add(newCategoryItem)
    session.commit()
    return redirect(url_for('showCategoryItems', category_id=category_id))
  else:
    return render_template('addCategoryItem.html', category_id=category_id)

@app.route('/category/<int:category_id>/item/<int:item_id>/edit/')
def editCategoryItem(category_id, item_id):
  return 'edit category %s item %s!' % (category_id, item_id)

@app.route('/category/<int:category_id>/item/<int:item_id>/delete/')
def deleteCategoryItem(category_id, item_id):
  return 'delete category %s item %s!' % (category_id, item_id)


if __name__ == '__main__':
  app.debug = True
  app.run(host='0.0.0.0', port=5000)

