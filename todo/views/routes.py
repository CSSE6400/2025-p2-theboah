from flask import Blueprint, jsonify, request 
from todo.models import db 
from todo.models.todo import Todo 
from datetime import datetime, timedelta
 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"}), 200


@api.route('/todos', methods=['GET']) 
def get_todos():
    hasWindow = request.args.get('window', False)
    if hasWindow:
        try:
            window_days = int(request.args.get('window'))
            end_date = datetime.now() + timedelta(days=window_days)
            todos = Todo.query.filter(Todo.deadline_at <= end_date).all()
        except ValueError:
            return jsonify({'error': 'Invalid window parameter'}), 400
    elif request.args.get('completed') == 'true':
        todos = Todo.query.filter_by(completed=True).all()
    elif request.args.get('completed') == 'false':
        todos = Todo.query.filter_by(completed=False).all()
    else:
        todos = Todo.query.all()
    
    result = [todo.to_dict() for todo in todos]

    return jsonify(result), 200

@api.route('/todos/<int:todo_id>', methods=['GET']) 
def get_todo(todo_id): 
   todo = Todo.query.get(todo_id) 
   if todo is None: 
      return jsonify({'error': 'Todo not found'}), 404 
   return jsonify(todo.to_dict()), 200

@api.route('/todos', methods=['POST']) 
def create_todo():

    #Filter for invalid query parameters
    argsList = ['title', 'description', 'completed', 'deadline_at']
    for key in request.json:
        if key not in argsList:
            return jsonify({'error': 'Invalid query parameter'}), 400

    #check that title is not empty
    hasTitle = request.json.get('title', False)
    if not hasTitle:
           return jsonify({'error': 'Title cannot be empty'}), 400       

    todo = Todo( 
      title=request.json.get('title'), 
      description=request.json.get('description',""), 
      completed=request.json.get('completed', False),
    ) 
    if 'deadline_at' in request.json: 
      todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))
      
 
   # Adds a new record to the database or will update an existing record. 
    db.session.add(todo) 
   # Commits the changes to the database. 
   # This must be called for the changes to be saved. 
    db.session.commit()
   
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT']) 
def update_todo(todo_id): 
   todo = Todo.query.get(todo_id) 
   if todo is None: 
      return jsonify({'error': 'Todo not found'}), 404 
   
   argsList = ['title', 'description', 'completed', 'deadline_at']
   #Filter for invalid query parameters
   for key in request.json:
        if key not in argsList:
            return jsonify({'error': 'Invalid query parameter'}), 400
        
   todo.title = request.json.get('title', todo.title) 
   todo.description = request.json.get('description', todo.description) 
   todo.completed = request.json.get('completed', todo.completed) 
   todo.deadline_at = request.json.get('deadline_at', todo.deadline_at) 
   db.session.commit() 
 
   return jsonify(todo.to_dict()), 200

@api.route('/todos/<int:todo_id>', methods=['DELETE']) 
def delete_todo(todo_id): 
   todo = Todo.query.get(todo_id) 
   if todo is None: 
      return jsonify({}), 200 
 
   db.session.delete(todo) 
   db.session.commit() 
   return jsonify(todo.to_dict()), 200
 
