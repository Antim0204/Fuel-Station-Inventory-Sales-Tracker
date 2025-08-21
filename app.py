# from flask import Flask,jsonify,request
# from flask_sqlalchemy import SQLAlchemy


# app=Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1609@localhost:5433/mydb'


# db=SQLAlchemy(app)

# class Task(db.Model):
#     # defining table name
#     __tablename__='tasks'
#     id=db.Column(db.Integer, primary_key=True, autoincrement=True)
#     title=db.Column(db.String(200), nullable=False)
#     done=db.Column(db.Boolean, default=False)

# with app.app_context():
#     db.create_all()


# @app.route('/')
# def hello_world():
#     return 'Hello World!'

# @app.route('/products')
# def products():
#     return 'List of products'



# @app.route('/tasks')
# def get_tasks():
#     tasks=Task.query.all()
#     task_list=[{'id':task.id,'title':task.title,'done':task.done}for task in tasks] 
#     return jsonify({"tasks":task_list})


# @app.route('/tasks',methods=['POST'])
# def create_task():
#     data=request.get_json()
#     new_task=Task(title=data['title'], done=data.get('done', False))
#     db.session.add(new_task)
#     db.session.commit()
#     return jsonify({"message": "Task created successfully", "task": {"id": new_task.id, "title": new_task.title, "done": new_task.done}}), 201  
# if __name__ == '__main__':
#     app.run(debug=True)


 
import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from config import Config
from db import db, migrate
from models import *  # ensure models are imported for migrations
from routes.fuel_types import bp as fuel_types_bp
from routes.inventory import bp as inventory_bp
from routes.sales import bp as sales_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Blueprints (REST APIs)
    app.register_blueprint(fuel_types_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(sales_bp)

    @app.get("/")
    def health():
        return jsonify({"status": "ok"}), 200

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
