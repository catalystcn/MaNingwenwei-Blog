from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify, make_response
from flask_mysqldb import MySQL
import markdown
from datetime import datetime
from PyPDF2 import PdfMerger
from pathlib import Path
import os
import threading
from io import BytesIO

extensions = [
    'markdown.extensions.extra',
    'markdown.extensions.codehilite',
    'markdown.extensions.toc',
    'markdown.extensions.tables',
    'markdown.extensions.fenced_code',
]

app = Flask(__name__)
app.secret_key = 'hello world'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'a88103882'
app.config['MYSQL_DB'] = 'blog'
mysql = MySQL(app)

# Index Page
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title, content, DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') AS created_at FROM posts ORDER BY created_at DESC")
    posts = cur.fetchall()
    cur.close()
    return render_template('index.html', posts=posts)

# Render Markdown text
@app.template_filter('md')
def markdown_filter(text):
    return markdown.markdown(text,extensions=extensions)

# Blog Post Page
@app.route('/post/<int:post_id>')
def post(post_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
    post = cur.fetchone()
    if post:
        post_content = markdown.markdown(post[2],extensions=extensions)
        return render_template('post.html', post=post, post_content=post_content)
    else:
        return render_template('404.html'), 404

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    if request.method == 'POST':
        password = request.form['password']
        # Query the database for the administrator password
        cur = mysql.connection.cursor()
        cur.execute("SELECT password FROM admin")
        result = cur.fetchone()
        cur.close()

        if result:
            db_password = result[0]
            if password == db_password:
                # Password is correct, redirect to management panel
                session['logged_in'] = True
                return redirect(url_for('manage_panel'))
            else:
                flash('密码错误，请重试', 'error')
        else:
            flash('管理员密码不存在', 'error')

    return render_template('manage.html')


# ManagePanel
@app.route('/manage_panel')
def manage_panel():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title, content, DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') AS created_at FROM posts ORDER BY created_at DESC")
    posts = cur.fetchall()
    cur.close()
    return render_template('manage_panel.html', posts=posts)

# ManagePost
@app.route('/manage_post/<int:post_id>')
def manage_post(post_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
    post = cur.fetchone()
    if post:
        post_content = markdown.markdown(post[2],extensions=extensions)
        return render_template('manage_post.html', post=post, post_content=post_content)
    else:
        return render_template('404.html'), 404

# Add Post
@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        created_at = datetime.now()  # Get current datetime
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO posts (title, content, created_at) VALUES (%s, %s, %s)", (title, content, created_at))
        mysql.connection.commit()
        # flash('Post added successfully', 'success')
        return redirect(url_for('manage_panel'))
    return render_template('add_post.html')

# Delete Post
@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        mysql.connection.commit()
        # flash('Post deleted successfully', 'success')
        return redirect(url_for('manage_panel'))
    return 'Method Not Allowed', 405

#Tool Box
@app.route('/toolbox')
def toolbox():
    # Dummy data for tool cards (replace with actual data)
    return render_template('toolbox.html')

#Tool1
@app.route('/tool1')
def tool1():
    return render_template('tool1.html')


#merge PDF
@app.route('/merge_pdf', methods=['POST'])
def merge_pdf():
    if 'folder[]' not in request.files:
        return jsonify({'error': 'No files selected'}), 400

    output_filename = 'merged_pdf.pdf'
    output_path = os.path.join('static', output_filename)

    pdf_files = request.files.getlist('folder[]')
    merger = PdfMerger()
    for pdf_file in pdf_files:
        merger.append(pdf_file)

    with open(output_path, 'wb') as output_file:
        merger.write(output_file)

    return jsonify({'file_url': output_path})


@app.route('/merge_pdf', methods=['POST'])
def merge_pdf_route():
    folder_path = request.files.getlist('folder')[0].filename
    output_filename = 'merged_pdf.pdf'
    output_path = os.path.join('static', output_filename)

    thread = threading.Thread(target=merge_pdf, args=(folder_path, output_path))
    thread.start()

    return jsonify({'output_path': output_path})


@app.route('/download_merged_pdf')
def download_merged_pdf():
    merged_pdf_path = request.args.get('merged_pdf_path')
    with open(merged_pdf_path, 'rb') as file:
        merged_pdf_data = file.read()

    response = make_response(merged_pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=merged_pdf.pdf'

    return response

if __name__ == '__main__':
    app.run(debug=True)