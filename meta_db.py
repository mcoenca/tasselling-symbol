from peewee import *

db = SqliteDatabase('meta.db')

class BaseModel(Model):
    class Meta:
        database = db

class Movie(BaseModel):
    id = PrimaryKeyField()
    avguserscore = IntegerField(null=True)
    genre = CharField(max_length=255)
    score = IntegerField(null=True)
    rating = CharField()
    cast = CharField(max_length=255)
    runtime = CharField(max_length=255)
    url = CharField(max_length=255)
    name = CharField(max_length=255, unique=True)
    rlsdate = CharField(max_length=255)
    userreviews = IntegerField(null=True)
    criticreviews = IntegerField(null=True)

class UserReview(BaseModel):
    id = PrimaryKeyField()
    date = CharField(max_length=255, null=True)
    total_thumbs = IntegerField()
    review = TextField()
    name = CharField(max_length=255, null=True)
    total_ups = IntegerField()
    score = IntegerField()
    movie = ForeignKeyField(Movie, related_name='user_reviews')

class CriticReview(BaseModel):
    id = PrimaryKeyField()
    link = CharField(max_length=255, null=True)
    critic = CharField(max_length=255, null=True)
    excerpt = TextField()
    score = IntegerField()
    movie = ForeignKeyField(Movie, related_name='critic_reviews')


db.connect()
db.create_tables([Movie, UserReview, CriticReview], safe=True)