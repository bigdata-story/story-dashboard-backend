import os

from cassandra.cluster import Cluster
from flask import Flask, request, abort, make_response
from flask_cors import CORS
from flask_restful import Resource, Api

cluster = Cluster([os.getenv('CASSANDRA_HOST', 'localhost')])
keyspace = os.getenv('CASSANDRA_KEYSPACE', 'story')
app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
api = Api(app)



class ActiveUser(Resource):
    def get(self):
        session = cluster.connect(keyspace)
        row = session.execute('SELECT sum(user_count) as "count" FROM active_users where tof = 1').one()
        return make_response({'count': row.count}, 200)


class EventCount(Resource):
    def get(self):
        event_type = request.args.get('event_type')
        if event_type is None:
            abort(400)
        session = cluster.connect(keyspace)
        stmt = session.prepare('SELECT sum(event_count) as "count" FROM event_types_count where event_type=?')
        row = session.execute(stmt, [event_type]).one()
        return make_response({'count': row.count}, 200)


class ActiveUserInCourse(Resource):
    def get(self):
        course_id = request.args.get('course_id')
        if course_id is None:
            abort(400)
        session = cluster.connect(keyspace)
        stmt = session.prepare('SELECT sum(user_count) as "count" FROM active_users_in_course where course_id = ?')
        row = session.execute(stmt, [course_id]).one()
        return make_response({'count': row.count}, 200)


class EventCountInCourse(Resource):
    def get(self):
        course_id = request.args.get('course_id')
        if course_id is None:
            abort(400)
        event_type = request.args.get('event_type')
        if event_type is None:
            abort(400)
        session = cluster.connect(keyspace)
        stmt = session.prepare(
            'SELECT sum(event_count) as "count" FROM event_types_count_in_course where event_type=? and course_id=?'
        )
        row = session.execute(stmt, [event_type, course_id]).one()
        return make_response({'count': row.count}, 200)


class CoursePlayedTime(Resource):
    def get(self):
        course_id = request.args.get('course_id')
        if course_id is None:
            abort(400)
        session = cluster.connect(keyspace)
        stmt = session.prepare('SELECT sum(play_time) as "count" FROM course_played_time where course_id = ?')
        row = session.execute(stmt, [course_id]).one()
        return make_response({'count': row.count}, 200)


api.add_resource(ActiveUser, '/active-users')
api.add_resource(EventCount, '/event-count')
api.add_resource(ActiveUserInCourse, '/active-users-in-course')
api.add_resource(EventCountInCourse, '/event-count-in-course')
api.add_resource(CoursePlayedTime, '/course-played-time')

if __name__ == '__main__':
    app.run()
