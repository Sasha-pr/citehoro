from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flasgger import Swagger
import json
import os

app = Flask("NoteAPI")

CORS(app)
swagger = Swagger(app)

DATA_FILE = 'notes.json'

def load_notes():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return []

def save_notes(notes):
    with open(DATA_FILE, 'w') as file:
        json.dump(notes, file)

notes = load_notes()
note_id_counter = max((note['id'] for note in notes), default=0) + 1

@app.route('/cite',methods=['GET'])
def cite():
    return render_template("cite.html"), 200

@app.route('/notes', methods=['GET'])
def get_notes():
    """Получить все заметки
    ---
    responses:
      200:
        description: Список заметок
        schema:
          type: array
          items:
            properties:
              id:
                type: integer
              content:
                type: string
              status:
                type: string
    """
    return jsonify(notes), 200

@app.route('/notes', methods=['POST'])
def create_note():
    """Создать новую заметку
    ---
    parameters:
      - name: note
        in: body
        required: true
        schema:
          type: object
          properties:
            content:
              type: string
            status:
              type: string
    responses:
      201:
        description: Созданная заметка
        schema:
          type: object
          properties:
            id:
              type: integer
            content:
              type: string
            status:
              type: string
    """
    global note_id_counter
    new_note = request.get_json()
    new_note['id'] = note_id_counter
    note_id_counter += 1
    notes.append(new_note)
    save_notes(notes)
    return jsonify(new_note), 201

@app.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Получить заметку по ID
    ---
    parameters:
      - name: note_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Заметка
        schema:
          type: object
          properties:
            id:
              type: integer
            content:
              type: string
            status:
              type: string
      404:
        description: Заметка не найдена
    """
    note = next((note for note in notes if note['id'] == note_id), None)
    if note:
        return jsonify(note), 200
    return jsonify({'error': 'Note not found'}), 404

@app.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Обновить заметку по ID
    ---
    parameters:
      - name: note_id
        in: path
        required: true
        type: integer
      - name: note
        in: body
        required: true
        schema:
          type: object
          properties:
            content:
              type: string
            status:
              type: string
    responses:
      200:
        description: Обновленная заметка
        schema:
          type: object
          properties:
            id:
              type: integer
            content:
              type: string
            status:
              type: string
      404:
        description: Заметка не найдена
    """
    note = next((note for note in notes if note['id'] == note_id), None)
    if note:
        updated_data = request.get_json()
        note.update(updated_data)
        save_notes(notes)
        return jsonify(note), 200
    return jsonify({'error': 'Note not found'}), 404

@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Удалить заметку по ID
    ---
    parameters:
      - name: note_id
        in: path
        required: true
        type: integer
    responses:
      204:
        description: Заметка удалена
      404:
        description: Заметка не найдена
    """
    global notes
    note = next((note for note in notes if note['id'] == note_id), None)
    if note:
        notes = [note for note in notes if note['id'] != note_id]
        save_notes(notes)
        return jsonify({'message': 'Note deleted'}), 204
    return jsonify({'error': 'Note not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)