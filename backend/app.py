from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from models import db, Task
from datetime import datetime
from sqlalchemy import or_, and_
import os

app = Flask(__name__, static_folder='../frontend/angular-app/dist/angular-app/browser')

CORS(app)

app.config.from_object(Config)

db.init_app(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
        print('path', path)
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

@app.route('/create-task', methods=['POST'])
def create_task():
    try:
        data = request.json
        print(data)

        if(data['id']):
            return update_task(data['id'], data)

        date_str = data['date']
        time_str = data['time']
        
        time_obj = datetime.strptime(time_str, "%H:%M")

        time_epoch = time_obj.hour * 3600 + time_obj.minute * 60

        date_epoch = int(datetime.strptime(date_str, "%Y-%m-%d").timestamp())
        print('epoch DATA', date_epoch)

        task = Task(
            entity_name=data['entityName'],
            date_created=date_epoch,
            task_time=time_epoch,
            task_type=data['taskType'],
            phone_number=data['phoneNumber'],
            contact_person=data['contactPerson'],
            note=data['notes']
        )

        db.session.add(task)
        db.session.commit()
        return jsonify({'message': 'Task created successfully'}), 201
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

def update_task(task_id, data):
    print('update_task')
    try:
        task = Task.query.get(task_id)

        date_str = data['date']
        time_str = data['time']
        
        time_obj = datetime.strptime(time_str, "%H:%M")

        time_epoch = time_obj.hour * 3600 + time_obj.minute * 60

        date_epoch = int(datetime.strptime(date_str, "%Y-%m-%d").timestamp())
        
        if task:
            task.entity_name = data['entityName']
            task.task_type = data['taskType']
            task.phone_number = data['phoneNumber']
            task.contact_person = data['contactPerson']
            task.note = data['notes']
            task.date_created = date_epoch
            task.task_time = time_epoch

            db.session.commit()
            return jsonify({'message': 'Task updated successfully'}), 200
        else:
            return jsonify({'error': 'Task not found'}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to update task'}), 500
    
@app.route('/close-task', methods=['POST'])
def close_task():
    print('close_task')
    try:
        data = request.json
        task_id = data['id']
        task = Task.query.get(task_id)

        if task:
            task.status = 'Closed'
            db.session.commit()
            return jsonify({'message': 'Task closed successfully'}), 200
        else:
            return jsonify({'error': 'Task not found'}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to close task'}), 500
    
#save notes
@app.route('/save-notes', methods=['POST'])
def save_notes():
    print('save_notes')
    try:
        data = request.json
        task_id = data['id']
        task = Task.query.get(task_id)

        if task:
            task.note = data['notes']
            db.session.commit()
            return jsonify({'message': 'Notes saved successfully'}), 200
        else:
            return jsonify({'error': 'Task not found'}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to save notes'}), 500
    
@app.route('/tasks', methods=['GET'])
def get_tasks():
    print('get_tasks')
    try:
        tasks = Task.query.all()
        task_list = []
        for task in tasks:

            date_created_str = datetime.utcfromtimestamp(task.date_created).strftime('%d-%m-%Y')
            task_time_str = datetime.utcfromtimestamp(task.task_time).strftime('%H:%M')

            task_data = {
                'id': task.id,
                'entityName': task.entity_name,
                'date': date_created_str,
                'time': task_time_str,
                'taskType': task.task_type,
                'phoneNumber': task.phone_number,
                'contactPerson': task.contact_person,
                'notes': task.note,
                'status': task.status
            }
            task_list.append(task_data)
        print(task_list)
        print('tasks', tasks)

        return jsonify({'tasks': task_list}), 200
    except Exception as e:
        print('error')
        print(e)
        return jsonify({'error': 'Failed to retrieve tasks'}), 500
    

# Route to apply multiple filters
@app.route('/tasks/applyFilters', methods=['POST'])
def apply_filters():
    print('apply_filters')
    try:
        data = request.json

        query_filters = []

        if data.get('taskType'):
            task_type_filters = []
            if data['taskType'].get('call'):
                task_type_filters.append(Task.task_type == 'call')
            if data['taskType'].get('meeting'):
                task_type_filters.append(Task.task_type == 'Meeting')
            if data['taskType'].get('videoCall'):
                task_type_filters.append(Task.task_type == 'Video Call')
            query_filters.append(or_(*task_type_filters))

        if data.get('entityName'):
            query_filters.append(Task.entity_name.like(f'%{data["entityName"]}%'))

        if data.get('contactPerson'):
            query_filters.append(Task.contact_person.like(f'%{data["contactPerson"]}%'))

        if data.get('status'):
            query_filters.append(Task.status == data['status'])

        if data.get('notes'):
            query_filters.append(Task.note.like(f'%{data["notes"]}%'))

        if data.get('fromDate') or data.get('toDate'):
            date_from = data.get('fromDate')
            date_to = data.get('toDate')
            date_filters = []

            if date_from:
                date_from = datetime.strptime(date_from, "%Y-%m-%d").timestamp()

            if date_to:
                date_to = datetime.strptime(date_to, "%Y-%m-%d").timestamp()
                date_to = date_to + 86400 # Add 1 day to make it end of the day
   
            if date_from and date_to:
                date_filters.append(Task.date_created >= date_from)
                date_filters.append(Task.date_created <= date_to)

            elif date_from:
                date_filters.append(Task.date_created >= date_from)
            elif date_to:
                date_filters.append(Task.date_created <= date_to)

            query_filters.append(and_(*date_filters))

        if data.get('fromTime') or data.get('toTime'):
            time_from = data.get('fromTime')
            time_to = data.get('toTime')
            time_filters = []

            if (time_from):
                time_obj = datetime.strptime(time_from, "%H:%M")
                time_from = time_obj.hour * 3600 + time_obj.minute * 60

            if (time_to):
                time_obj = datetime.strptime(time_to, "%H:%M")
                time_to = time_obj.hour * 3600 + time_obj.minute * 60

            if time_from and time_to:
                time_filters.append(Task.task_time >= time_from)
                time_filters.append(Task.task_time <= time_to)
            elif time_from:
                time_filters.append(Task.task_time >= time_from)
            elif time_to:
                    time_filters.append(Task.task_time <= time_to)
            query_filters.append(and_(*time_filters))

        tasks = Task.query.filter(and_(*query_filters)).all()

        task_list = []
        for task in tasks:
            date_created_str = datetime.utcfromtimestamp(task.date_created).strftime('%d-%m-%Y')
            task_time_str = datetime.utcfromtimestamp(task.task_time).strftime('%H:%M')

            task_data = {
                'id': task.id,
                'entityName': task.entity_name,
                'date': date_created_str,
                'time': task_time_str,
                'taskType': task.task_type,
                'phoneNumber': task.phone_number,
                'contactPerson': task.contact_person,
                'notes': task.note,
                'status': task.status
            }
            task_list.append(task_data)


        return jsonify({'tasks': task_list}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to retrieve tasks with filters'}), 500


def create_tables():
    with app.app_context():
        try:
            db.create_all()
            print("Tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
