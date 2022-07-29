import sqlite3
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

db_connection_count = 0
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global db_connection_count
    db_connection_count += 1
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

def get_all_post():
   connection = get_db_connection()
   posts = connection.execute('SELECT * FROM posts').fetchall()
   connection.close()
   return posts

def get_post_count():
  connection = get_db_connection()
  post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
  connection.close()
  return post_count

# Define the main route of the web application 
@app.route('/')
def index():
    posts = get_all_post()
    return render_template('index.html', posts=posts)

# Define Healthcheck endpoint
@app.route('/healthz')
def healthcheck():
  response = app.response_class(
          response=json.dumps({"result":"OK - healthy"}),
          status=200,
          mimetype='application/json'
  )
  ## log line
  app.logger.info('Healthcheck request successfully')
  return response

# Define Metrics endpoint
@app.route('/metrics')
def metrics():
  post_count = get_post_count()
  print(post_count)
  response = app.response_class(
          response=json.dumps({"status":"success","code":0,"data":{"db_connection_count":db_connection_count,"post_count":post_count}}),
          status=200,
          mimetype='application/json'
  )
  ## log line
  app.logger.info('Metrics request successfully')
  return response

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      ## log line
      app.logger.info('Article not found, redirected to 404 page')
      return render_template('404.html'), 404
    else:
       ## log line
      app.logger.info('Article "%s" retrieved!', post['title'])
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    ## log line
    app.logger.info('Access "About Us" page successfully')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('A new article named "%s" is created', title)
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   # Stream logs to a file, and set the default log level to DEBUG
   logging.basicConfig(filename='app.log',level=logging.DEBUG)
   app.run(host='0.0.0.0', port='3111')
