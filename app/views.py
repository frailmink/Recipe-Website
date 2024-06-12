from flask import render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from app import app
from .forms import LoginForm, SignUpForm, RecipeForm, RecipeOpenForm, FollowRecipeForm, SearchForm
from app import db, models
from flask_bcrypt import Bcrypt
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from datetime import datetime
import os
import json

# define folder location
UPLOAD_FOLDER = 'app/static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
bcrypt = Bcrypt(app)

# setup login manager system
loginManager = LoginManager()
loginManager.init_app(app)
loginManager.login_view = "login"

@loginManager.user_loader
def LoadUser(userId):
    with app.app_context():
        return models.Users.query.get(int(userId))

# search through to see if any recipes match the search result
def search(search, recipes):
    tempList = []
    for recipe in recipes:
            if search.upper() in recipe.name.upper():
                tempList.append(recipe)
    
    return tempList

@app.route('/', methods=['GET', 'POST'])
def index():
    form = RecipeOpenForm()
    searchForm = SearchForm()

    with app.app_context():
        # get all the recipes
        tempRecipes = models.Recipes.query.all()
        followedRecipesTemp = []
        followedRecipes = []

        # checks if the user is signed in
        if current_user.is_authenticated:
            followedRecipesTemp = models.FollowedRecipes.query.filter_by(userId=current_user.id).all()

        # removes all the followed recipes in recipes
        for relation in followedRecipesTemp:
            followedRecipes.append(models.Recipes.query.filter_by(id=relation.recipeId).first())
        recipes = [element for element in tempRecipes if element not in followedRecipes]

    # redirects the user to the correct recipe
    if form.validate_on_submit() and form.submit7.data:
        return redirect(url_for('recipe', id=form.id.data))
    
    # searches for what the user searched for
    if searchForm.validate_on_submit() and searchForm.submit5.data:
        recipes = search(searchForm.searchbar.data, recipes)
        followedRecipes = search(searchForm.searchbar.data, followedRecipes)
    
    return render_template('index.html',
                           title='Main Page',
                           recipes=recipes,
                           form=form,
                           searchForm=searchForm,
                           followedRecipes=followedRecipes)

@app.route('/recipe', methods=['GET', 'POST'])
def recipe():
    form = FollowRecipeForm()
    followed = False
    with app.app_context():
        # gets the recipe that was passed when being redirected
        recipe = models.Recipes.query.get(request.args.get('id', 'Guest'))

        # checks if the user is signed in and if they are it checks if they follow the recipe
        if current_user.is_authenticated:
            relationship = models.FollowedRecipes.query.filter_by(userId=current_user.id, recipeId=recipe.id).first()
            if relationship:
                followed = True
    return render_template('recipe.html',
                           title='Main Page',
                           recipe=recipe,
                           form=form,
                           followed=followed)

@app.route('/followRecipe', methods=['POST'])
def FollowRecipe():
    data = json.loads(request.data)
    # adds the follow relation or removes it corresponding to whether the user already follows it or not
    with app.app_context():
        relationship = models.FollowedRecipes.query.filter_by(userId=int(data.get('userId')), recipeId=int(data.get('recipeId'))).first()
        if relationship:
            db.session.delete(relationship)
        else:
            tempVar = models.FollowedRecipes(userId=int(data.get('userId')), recipeId=int(data.get('recipeId')))
            db.session.add(tempVar)
        db.session.commit()

    return json.dumps({'status': 'OK'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with app.app_context():
            # checks to see if there exists a user with the username inputted
            user = models.Users.query.filter_by(username=form.username.data).first()
            if user:
                # checks if the hashed password is correct
                if bcrypt.check_password_hash(user.password, form.password.data):
                    login_user(user)
                    return redirect(url_for('index'))

    return render_template('login.html',
                           title='Login Page',
                           form=form)

@app.route('/signUp', methods=['GET', 'POST'])
def SignUp():
    form = SignUpForm()
    if form.validate_on_submit():
        # creates a new hashed password
        hashedPassword = bcrypt.generate_password_hash(form.password1.data)
        with app.app_context():
            tempVar = models.Users(username=form.username.data, password=hashedPassword)
            db.session.add(tempVar)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('signUp.html',
                           title='Signup Page',
                           form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    # logs out the user and redicets them to the login page
    logout_user()
    return redirect(url_for('login'))

@app.route('/createRecipe', methods=['GET', 'POST'])
def CreateRecipe():
    form = RecipeForm()
    if form.validate_on_submit():
        # secure the filename
        filename = secure_filename(form.image.data.filename)

        # add a timestamp to make each file unique
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        uniqueFilename = f"{timestamp}_{filename}"

        # save file to the file UPLOAD_FOLDER
        form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], uniqueFilename))

        # saves the data into the database
        with app.app_context():
            p = models.Recipes(name=form.title.data, image=uniqueFilename, text=form.text.data.replace('\r\n', '<br>').replace('\n', '<br>'))
            db.session.add(p)
            db.session.commit()

        # redirects the user to the main page
        return redirect(url_for('index'))

    return render_template('recipeCreation.html',
                           title='Recipe Creation Page',
                           form=form)