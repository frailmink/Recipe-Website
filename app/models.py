from app import db
from flask_login import UserMixin

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), nullable=False, index=True, unique=True)
    password = db.Column(db.String(120), nullable=False, index=True)

class Recipes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False, index=True)
    image = db.Column(db.String(40), nullable=False, index=True)
    text = db.Column(db.String(10000), nullable=False, index=True)

userRecipes = db.Table('userRecipes',
    db.Column('userId', db.Integer, db.ForeignKey('users.id')),
    db.Column('recipeId', db.Integer, db.ForeignKey('recipes.id'))
)

class FollowedRecipes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipeId = db.Column(db.Integer, db.ForeignKey('recipes.id'))
    