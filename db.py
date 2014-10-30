#!/usr/bin/env python

from peewee import *

db = SqliteDatabase('rotten.db')

class BaseModel(Model):
    class Meta:
        database = db

class Movie(BaseModel):
    id = PrimaryKeyField()
    title = CharField(max_length=255, unique=True)
    
    imdb_id = BigIntegerField(unique=True, null=True)
    rotten_id = BigIntegerField(unique=True)
    
    year = IntegerField()
    mpaa_rating = CharField()
    runtime = IntegerField()
    
    critics_score = IntegerField()
    audience_score = IntegerField()
    
    synopsis = TextField()

class Actor(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=255, unique=True)
    rotten_id = BigIntegerField(unique=True)

class Role(BaseModel):
    id = PrimaryKeyField()
    character = CharField(max_length=255)
    actor = ForeignKeyField(Actor, related_name='roles')
    movie = ForeignKeyField(Movie, related_name='roles')

class Critic(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=255, unique=True)

class Publication(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=255, unique=True)

class Review(BaseModel):
    id = PrimaryKeyField()
    critic = ForeignKeyField(Critic, related_name='reviews')
    movie = ForeignKeyField(Movie, related_name='reviews')
    publication = ForeignKeyField(Publication, related_name='reviews')
    is_top = BooleanField()
    is_fresh = BooleanField()
    original_score = CharField(max_length=20, null=True)
    score = IntegerField()
    quote = TextField()
    date = DateField()


db.connect()
db.create_tables([Movie, Actor, Role, Critic, Publication, Review], safe=True)