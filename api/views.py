import sys
# print(sys.path)
# print()
# sys.path.append("c:\\Users\\K Teja\\Documents\\3rd_year\\mini_project\\Flask_api\\youtube")
# print(sys.path)

from flask import Blueprint, jsonify, request
from extract import main_method
# from .models import Movie
# from . import db,create_app
# print(can_you())
from . import db 
from .models import Movie


main = Blueprint('main', __name__)

# def setDatabase():
#     db.creat_all(app=create_app())

# setDatabase()
 
@main.route('/',methods=['GET'])
def index():
    return "Welcome"


@main.route('/add_url', methods=['POST'])
def add_url():
    yt_link = request.get_json()
    # url=yt_link['url']
    link=yt_link['url']
    test=main_method(link)
    print("\n".join(test[8]))
    print("\n".join(test[9]))
    print("\n".join(test[10]))
    new_movie = Movie(url=yt_link['url'],video_title=test[4],pos_percentage=test[0],thumbnail=test[5],description=test[3],channel_name=test[6],published_date=test[7],neg_percentage=test[1],nutral_percentage=test[2])

    db.session.add(new_movie)
    db.session.commit()

    return 'Done', 201

@main.route('/analysis')
def analysis():
    movie_list = Movie.query.all()
    movies = []

    for movie in movie_list[::-1]:
        movies.append({'id':movie.id,'url' : movie.url,'video_title':movie.video_title ,'pos_percentage' : movie.pos_percentage,'thumbnail':movie.thumbnail,'description':movie.description,'channel_name':movie.channel_name,'neg_percentage':movie.neg_percentage,'nutral_percentage':movie.nutral_percentage,'pusblished_date':movie.published_date})

    return jsonify({'movies' : movies})