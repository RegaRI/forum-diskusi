from flask import Flask, render_template, request, redirect, url_for, session, flash
import MySQLdb
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret'

# Konfigurasi direktori unggahan media
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db_config = {
    "host": "localhost",
    "user": "root",
    "passwd": "kalitengah",
    "db": "bobi_db"
}

def get_db_connection():
    return MySQLdb.connect(**db_config)

# Fungsi validasi file yang diunggah
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Membuat tabel
def create_tables():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Tabel users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(200) NOT NULL
            );
        """)

        # Tabel posts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                content TEXT NOT NULL,
                media_path VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """)

        # Tabel comments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                post_id INT NOT NULL,
                user_id INT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """)

        # Tabel likes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                post_id INT NOT NULL,
                user_id INT NOT NULL,
                is_like BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """)
        conn.commit()
    except Exception as e:
        print(f"Error creating tables: {e}")
    finally:
        cursor.close()
        conn.close()

create_tables()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    if not name or not email or not password:
        flash('Semua kolom harus diisi!')
        return redirect(url_for('home'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash('Email sudah terdaftar!')
            return redirect(url_for('home'))

        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        conn.commit()
        flash('Registrasi berhasil!')
    except Exception as e:
        flash(f'Error: {e}')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            flash(f'Selamat datang, {user[1]}!')
            return redirect(url_for('user_home'))
        else:
            flash('Email atau password salah!')
    except Exception as e:
        flash(f'Error: {e}')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('home'))

@app.route('/home', methods=['GET', 'POST'])
def user_home():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('home'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            if 'content' in request.form:
                content = request.form.get('content')
                file = request.files.get('media')
                media_path = None

                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    media_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(media_path)

                if content or media_path:
                    cursor.execute("INSERT INTO posts (user_id, content, media_path) VALUES (%s, %s, %s)",
                                   (user_id, content, media_path))
                    conn.commit()
                    flash('Posting berhasil ditambahkan!')

        cursor.execute("""
            SELECT posts.id, posts.content, posts.created_at, users.name, posts.media_path
            FROM posts
            JOIN users ON posts.user_id = users.id
            ORDER BY posts.created_at DESC
        """)
        posts = cursor.fetchall()

        likes_data = {}
        for post in posts:
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN is_like = TRUE THEN 1 ELSE 0 END) AS likes,
                    SUM(CASE WHEN is_like = FALSE THEN 1 ELSE 0 END) AS dislikes
                FROM likes
                WHERE post_id = %s
            """, (post[0],))
            likes_data[post[0]] = cursor.fetchone()

        return render_template('home.html', user=session['user_name'], posts=posts, likes_data=likes_data)
    except Exception as e:
        flash(f'Error: {e}')
        return redirect(url_for('home'))
    finally:
        cursor.close()
        conn.close()

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('home'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Ambil detail posting berdasarkan ID
        cursor.execute("""
            SELECT posts.id, posts.content, posts.created_at, users.name, posts.media_path
            FROM posts
            JOIN users ON posts.user_id = users.id
            WHERE posts.id = %s
        """, (post_id,))
        post = cursor.fetchone()

        # Ambil komentar untuk posting ini
        cursor.execute("""
            SELECT comments.content, comments.created_at, users.name
            FROM comments
            JOIN users ON comments.user_id = users.id
            WHERE comments.post_id = %s
            ORDER BY comments.created_at ASC
        """, (post_id,))
        comments = cursor.fetchall()

        # Ambil jumlah like dan dislike untuk posting ini
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN is_like = TRUE THEN 1 ELSE 0 END) AS likes,
                SUM(CASE WHEN is_like = FALSE THEN 1 ELSE 0 END) AS dislikes
            FROM likes
            WHERE post_id = %s
        """, (post_id,))
        likes_data = cursor.fetchone()

        if request.method == 'POST':
            # Tambahkan komentar baru
            comment = request.form.get('comment')
            if comment:
                cursor.execute("INSERT INTO comments (post_id, user_id, content) VALUES (%s, %s, %s)", 
                               (post_id, user_id, comment))
                conn.commit()
                flash('Komentar berhasil ditambahkan!')
                return redirect(url_for('post_detail', post_id=post_id))

        return render_template(
            'post_detail.html', 
            post=post, 
            comments=comments, 
            likes=likes_data,
            user_id=user_id
        )
    except Exception as e:
        flash(f'Error: {e}')
        return redirect(url_for('home'))
    finally:
        cursor.close()
        conn.close()


@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('home'))

    is_like = request.form.get('is_like') == 'true'

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM likes
            WHERE post_id = %s AND user_id = %s
        """, (post_id, user_id))

        cursor.execute("""
            INSERT INTO likes (post_id, user_id, is_like)
            VALUES (%s, %s, %s)
        """, (post_id, user_id, is_like))
        conn.commit()
    except Exception as e:
        flash(f'Error: {e}')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('user_home'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Berhasil logout!')
    return redirect(url_for('home'))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
