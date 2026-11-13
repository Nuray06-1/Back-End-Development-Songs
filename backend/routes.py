"""Songs REST service, completed with OpenAI Codex assistance (2026-11-13)."""
from . import app
import os
import json
from pathlib import Path
from urllib.parse import quote_plus
from flask import jsonify, request
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson import json_util

host = os.environ.get('MONGODB_SERVICE', 'localhost')
port = int(os.environ.get('MONGODB_PORT', '27017'))
user = os.environ.get('MONGODB_USERNAME')
password = os.environ.get('MONGODB_PASSWORD')
auth = f'{quote_plus(user)}:{quote_plus(password)}@' if user and password else ''
client = MongoClient(f'mongodb://{auth}{host}:{port}', serverSelectionTimeoutMS=5000)
db = client.songs
db.songs.create_index('id', unique=True)
with (Path(__file__).parent / 'data' / 'songs.json').open() as source:
    for song in json.load(source):
        db.songs.update_one({'id': song['id']}, {'$setOnInsert': song}, upsert=True)

def parse_json(data):
    return json.loads(json_util.dumps(data))

@app.get('/health')
def health():
    return jsonify(status='OK'), 200

@app.get('/count')
def count():
    return jsonify(count=db.songs.count_documents({})), 200

@app.get('/song')
def songs():
    return jsonify(songs=parse_json(list(db.songs.find({})))), 200

@app.get('/song/<int:id>')
def get_song_by_id(id):
    song = db.songs.find_one({'id': id})
    if song is None:
        return {'message': 'song with id not found'}, 404
    return jsonify(parse_json(song)), 200

@app.post('/song')
def create_song():
    song = request.get_json()
    if not isinstance(song, dict) or type(song.get('id')) is not int:
        return {'message': 'song must have an integer id'}, 400
    if not all(isinstance(song.get(k), str) and song[k].strip() for k in ('title','lyrics')):
        return {'message': 'title and lyrics are required'}, 400
    clean = {k: song[k] for k in ('id','title','lyrics')}
    try:
        result = db.songs.insert_one(clean)
    except DuplicateKeyError:
        return {'Message': f"song with id {song['id']} already present"}, 302
    return jsonify(parse_json({'inserted id': result.inserted_id})), 201

@app.put('/song/<int:id>')
def update_song(id):
    incoming = request.get_json()
    if not isinstance(incoming, dict) or incoming.get('id',id) != id:
        return {'message': 'song id must match URL'}, 400
    changes = {k: incoming[k] for k in ('title','lyrics') if k in incoming}
    if not changes or not all(isinstance(v,str) and v.strip() for v in changes.values()):
        return {'message': 'non-empty title or lyrics required'}, 400
    result = db.songs.update_one({'id':id},{'$set':changes})
    if not result.matched_count:
        return {'message':'song not found'}, 404
    return jsonify(parse_json(db.songs.find_one({'id':id}))), 201

@app.delete('/song/<int:id>')
def delete_song(id):
    if not db.songs.delete_one({'id':id}).deleted_count:
        return {'message':'song not found'}, 404
    return '', 204
