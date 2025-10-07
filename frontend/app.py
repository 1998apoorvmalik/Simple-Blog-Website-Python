from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests

app = Flask(__name__)
app.secret_key = 'simplefrontend'
BACKEND_URL = "http://127.0.0.1:5000"


@app.route('/')
def home():
    response = requests.get(f"{BACKEND_URL}/blogs")
    blogs = response.json()
    print("Current user:", session.get('user'))
    return render_template('home.html', blogs=blogs, user=session.get('user'))


@app.route('/about')
def about():
    return render_template('about.html', user=session.get('user'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        response = requests.post(f"{BACKEND_URL}/register", json={'username': username, 'password': password})
        if response.status_code == 200:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash(response.json().get('error', 'Error registering user'), 'error')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        response = requests.post(f"{BACKEND_URL}/login", json={'username': username, 'password': password})
        if response.status_code == 200:
            user_data = response.json()
            session['user'] = {'id': user_data['user_id'], 'username': username}
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out.', 'info')
    return redirect(url_for('home'))


@app.route('/create', methods=['GET', 'POST'])
def create():
    if 'user' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = session['user']['id']
        response = requests.post(f"{BACKEND_URL}/blogs", json={'user_id': user_id, 'title': title, 'content': content})
        if response.status_code == 200:
            flash('Blog created!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Error creating blog', 'error')
    return render_template('create.html', user=session.get('user'))


@app.route('/delete/<int:blog_id>')
def delete(blog_id):
    if 'user' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))

    user_id = session['user']['id']
    response = requests.delete(f"{BACKEND_URL}/blogs/{blog_id}?user_id={user_id}")
    if response.status_code == 200:
        flash('Blog deleted.', 'info')
    else:
        flash('Unable to delete blog.', 'error')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(port=5001, debug=True)
