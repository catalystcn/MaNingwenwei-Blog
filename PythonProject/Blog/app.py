import json
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
import pymysql
import markdown
import datetime
# from datetime import datetime
from PyPDF2 import PdfMerger
import os
from bs4 import BeautifulSoup

extensions = [
    'markdown.extensions.extra',
    'markdown.extensions.codehilite',
    'markdown.extensions.toc',
    'markdown.extensions.tables',
    'markdown.extensions.fenced_code',
]

app = Flask(__name__)
app.secret_key = 'hello world'

# 设置上传文件目录
app.config['UPLOAD_FOLDER'] = 'Temp/PDFfile'

# # MySQL Configuration
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'a88103882'
# app.config['MYSQL_DB'] = 'blog'
# mysql = MySQL(app)

conn = pymysql.connect(
    port=3306,  # 端口号，默认为3306
    user='root',  # 用户名
    database='blog',
    password='a88103882',  # 密码
    charset='utf8mb4'  # 设置字符编码
)
# Index Page
@app.route('/')
def index():
    conn.ping(reconnect=True)
    cur = conn.cursor()
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
    conn.ping(reconnect=True)
    cur = conn.cursor()
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
        conn.ping(reconnect=True)
        cur = conn.cursor()
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
    conn.ping(reconnect=True)
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:%s') AS created_at FROM posts ORDER BY created_at DESC")
    posts = cur.fetchall()
    cur.close()
    return render_template('manage_panel.html', posts=posts)

# ManagePost
@app.route('/manage_post/<int:post_id>')
def manage_post(post_id):
    conn.ping(reconnect=True)
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
    post = cur.fetchone()
    if post:
        post_content = markdown.markdown(post[2],extensions=extensions)
        return render_template('manage_post.html', post=post, post_content=post_content)
    else:
        return render_template('404.html'), 404

# Update Post
@app.route('/update_post/<int:post_id>', methods=['POST'])
def update_post(post_id):
    # Get the updated title and content from the form
    title = request.form['title']
    content = request.form['content']

    conn.ping(reconnect=True)
    cur = conn.cursor()

    # Update the post in the database
    cur.execute("UPDATE posts SET title = %s, content = %s WHERE id = %s", (title, content, post_id))
    conn.commit()
    cur.close()

    # Redirect back to the manage post page with updated content
    # flash('Post updated successfully', 'success')
    return redirect(url_for('manage_post', post_id=post_id))

# Add Post
@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        created_at = datetime.datetime.now()  # Get current datetime
        conn.ping(reconnect=True)
        cur = conn.cursor()
        cur.execute("INSERT INTO posts (title, content, created_at) VALUES (%s, %s, %s)", (title, content, created_at))
        conn.commit()
        # flash('Post added successfully', 'success')
        return redirect(url_for('manage_panel'))
    return render_template('add_post.html')

# Delete Post
@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if request.method == 'POST':
        conn.ping(reconnect=True)
        cur = conn.cursor()
        cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        conn.commit()
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

#清除Temp文件
def clear_temp_directory():
    temp_directory = app.config['UPLOAD_FOLDER']
    for filename in os.listdir(temp_directory):
        file_path = os.path.join(temp_directory, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

#Merge PDF
@app.route('/merge_pdf', methods=['POST'])
def merge_pdf():
    if 'folder[]' not in request.files:
        return jsonify({'error': 'No files selected'}), 400

    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 每次上传前清空临时目录
    clear_temp_directory()

    output_filename = 'merged_pdf.pdf'
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

    pdf_files = request.files.getlist('folder[]')
    merger = PdfMerger()
    for pdf_file in pdf_files:
        pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename))
        merger.append(os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename))

    with open(output_path, 'wb') as output_file:
        merger.write(output_file)

    return jsonify({'file_url': output_path})


@app.route('/download_merged_pdf')
def download_merged_pdf():
    merged_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'merged_pdf.pdf')
    with open(merged_pdf_path, 'rb') as file:
        merged_pdf_data = file.read()

    response = make_response(merged_pdf_data)
    print(response)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=merged_pdf.pdf'
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Pragma'] = 'no-cache'

    return response


# 设置微博热搜接口和请求头
url = 'https://weibo.com/ajax/side/hotSearch'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}
Interval_time = 10  # 更新时间间隔，单位：秒

# 获取实时微博热搜内容和更新时间
def get_hot_search_data():
    now_time = datetime.datetime.now().strftime('%F %T')
    response = requests.get(url=url, headers=headers)
    response_text = json.loads(response.text)
    data = response_text['data']['realtime']
    hotnews = []
    for each in data:
        hotnews.append("NO.{:<5}\t{}".format(int(each["rank"]) + 1, each["note"]))  # 使用format()函数对齐
    hot_search_content = "\n\n".join(hotnews)
    return hot_search_content, now_time

# Add a new route to fetch hot search content
@app.route('/get_hot_search_content')
def get_hot_search_content():
    hot_search_content, update_time = get_hot_search_data()
    return jsonify({'hot_search_content': hot_search_content, 'update_time': update_time})

# 渲染Tool2.html模板，并传递实时微博热搜内容
@app.route('/tool2')
def tool2():
    hot_search_content, update_time = get_hot_search_data()
    return render_template('tool2.html', hot_search_content=hot_search_content, update_time=update_time)

@app.route('/translate', methods=['POST'])
def translate():
    result=""
    if request.method == 'POST':
        url = 'https://m.youdao.com/translate'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
        }
        text = request.form['inputText']
        data = {"inputtext": text, "type": "AUTO"}
        res = requests.post(url=url, headers=headers, data=data)
        soup = BeautifulSoup(res.text, 'html.parser')
        result = soup.find(id='translateResult').get_text()
    return result

@app.route('/tool3')
def tool3():
    result=translate()
    return render_template('tool3.html', outputText=result)

# 获取指定歌手的歌曲信息
# 获取指定歌手的歌曲信息
def get_artist_songs(artist_id):
    url = 'https://music.163.com/api/v1/artist/songs'  # 歌手歌曲信息api的url
    params = {
        'id': artist_id,  # 歌手id
        'offset': 0,  # 偏移量
        'total': True,  # 是否获取全部歌曲信息
        'limit': 1000  # 获取歌曲数量
    }
    response = requests.get(url, headers=headers, params=params)  # 使用requests模块发送get请求
    if response.status_code == 200:  # 如果请求成功
        result = json.loads(response.text)  # 将response的文本内容转为json格式
        songs = result['songs']  # 获取歌曲列表
        return songs
    else:
        print('请求出错：', response.status_code)  # 如果请求失败
        return None

# 获取歌曲名称和播放链接
def get_song_info(song,search_type,input):
    song_name = song['name']  # 歌曲名称
    song_id = song['id']  # 歌曲id
    if search_type=='singer':
        song_cover = song['album']['blurPicUrl']
        song_people = input
    elif search_type=='song':
        song_cover = "https://p2.music.126.net/6y-UleORITEDbvrOLV0Q8A==/5639395138885805.jpg"
        song_people = song['artists'][0]['name'] or "未知歌手"
    song_url = 'https://music.163.com/song/media/outer/url?id={}.mp3'.format(song_id)  # 歌曲播放链接
    return song_name, song_url, song_cover ,song_people

# 根据音乐名搜索歌曲ID
def search_song(search_content):
    search_url = f'https://music.163.com/api/search/get/web?csrf_token=&hlpretag=&hlposttag=&s={search_content}&type=1&offset=0&total=true&limit=5'
    response = requests.get(url=search_url, headers=headers)
    if response.status_code == 200:
        result = response.json()
        song_list = result['result']['songs']
        return song_list
    else:
        print('请求出错：', response.status_code)
        return None

# 搜索歌手或歌名路由
@app.route('/search')
def search():
    search_input = request.args.get('input')
    search_type = request.args.get('type')

    if search_type == 'singer':
        # Fetch artist_id from database
        conn.ping(reconnect=True)
        cur = conn.cursor()
        cur.execute("SELECT id FROM singer_id WHERE singer=%s", (search_input,))
        artist_id = cur.fetchone()
        cur.close()

        if artist_id:
            songs = get_artist_songs(artist_id[0])  # 获取歌手的歌曲信息
            if songs:
                song_list = []
                for song in songs:
                    song_name, song_url, song_cover,song_people= get_song_info(song,search_type,search_input)  # 获取歌曲名称和播放链接
                    song_list.append({'song_name': song_name, 'song_url': song_url, 'song_cover': song_cover, 'artist_names': song_people})
                return jsonify(song_list)
            else:
                return jsonify({'error': '获取歌曲信息失败！'}), 500
        else:
            return jsonify({'error': '歌手未找到！'}), 404
    elif search_type == 'song':
        songs = search_song(search_input)  # 根据歌名搜索歌曲
        if songs:
            song_list = []
            for song in songs:
                song_name, song_url, song_cover,song_people= get_song_info(song,search_type,search_input)  # 获取歌曲名称和播放链接
                song_list.append({'song_name': song_name, 'song_url': song_url, 'song_cover': song_cover,'artist_names': song_people})
            return jsonify(song_list)
        else:
            return jsonify({'error': '获取歌曲信息失败！'}), 500
    else:
        return jsonify({'error': '无效的搜索类型！'}), 400

@app.route('/tool4')
def tool4():
    return render_template('tool4.html')

@app.route('/tool5')
def tool5():
    return render_template('tool5.html')

if __name__ == '__main__':
    # server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
    # server.serve_forever()
    app.run(host='0.0.0.0',port=5000,debug=True)