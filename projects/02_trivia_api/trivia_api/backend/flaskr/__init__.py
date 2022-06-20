import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  ###########################################################################
  '''
  CORS to Allow '*' for origins.
  '''
  CORS(app, resources={r"/api/*": {"origins": "*"}})

  ############################################################################
  '''
  After_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE')
    return response

  ############################################################################
  ''' 
  Endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = {category.id: category.type for category in Category.query.order_by(Category.id).all()}

    if len(categories) == 0:
      abort(404)

    return jsonify({
      "success": True,
      "categories": categories,
      "total_categories": len(categories)
    })

  ############################################################################
  '''
  Endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: When you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    selected_page = request.args.get('page', 1, type=int)
    current_index = selected_page - 1
    items_limit = QUESTIONS_PER_PAGE

    questions = [question.format() for question in Question.query.order_by(Question.id
              ).limit(items_limit).offset(current_index * items_limit).all()]

    categories = {category.id: category.type for category in Category.query.order_by(
        Category.id).all()}


    if len(questions) == 0 or len(categories) == 0:
      abort(404)

    return jsonify({
      "success": True,
      "questions": questions,
      "total_questions": len(questions),
      "categories": categories,
      "current_category": None
    })

  ############################################################################
  '''
  Endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.get(question_id)

    if question:
      question.delete()

      return jsonify({
        'success': True
      })
    else: 
      abort(404)

  ############################################################################
  '''
  Endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    question = request.json.get('question', '')
    answer = request.json.get('answer', '')
    category = request.json.get('category', '')
    difficulty = request.json.get('difficulty', '')

    if question == '' or answer == '' or category == '' or difficulty == '':
      abort(422)

    new_question = Question(
      question = question,
      answer = answer, 
      category = category,
      difficulty = difficulty
    )

    new_question.insert()

    return jsonify({
      'success': True
    })

  ############################################################################
  '''
  POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question.
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    search_term = request.json.get('searchTerm')

    questions = [question.format() for question in Question.query.filter(
      Question.question.ilike(f'%{search_term}%')).all()]

    if len(questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': questions,
      'total_questions': len(questions),
      'current_category': None
    })

  ############################################################################
  '''
  GET endpoint to get questions based on category. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):

    questions = [question.format() for question in Question.query.filter(
      Question.category == category_id).all()]

    if len(questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': questions,
      'total_questions': len(questions),
      'current_category': category_id
    })

  ############################################################################
  '''
  POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions.
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quiz_question():
    previous_questions = request.json.get('previous_questions', [])
    quiz_category = request.json.get('quiz_category', None)

    
    if ((quiz_category is None) or (previous_questions is None)):
            abort(400)

    if (quiz_category['id'] == 0):
        questions = Question.query.all()
    else:
        questions = Question.query.filter_by(category=quiz_category['id']).all()

    total = len(questions)

    def get_random_question():
        return questions[random.randrange(0, len(questions), 1)]

    def check_if_used(question):
        used = False
        for question in previous_questions:
            if (question == question.id):
                used = True

        return used

    question = get_random_question()

    while (check_if_used(question)):
        question = get_random_question()
        if (len(previous_questions) == total):
            return jsonify({
                'success': True
            })

    # return the question
    return jsonify({
        'success': True,
        'question': question.format()
    })

  ############################################################################
  '''
  error handlers for all expected errors 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "Bad Request"
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "Not found"
    }), 404

  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "Method Not Allowed"
    }), 405

  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "Method Not Allowed"
    }), 422

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "Internal Server Error"
    }), 500

  ############################################################################ 
  return app

    