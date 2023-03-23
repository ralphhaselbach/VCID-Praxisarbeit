from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from flask_babel import _, get_locale
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, \
    EmptyForm, TaskForm
from app.models import User, Task

# Übernommen
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())

# Übernommen, Anpassungen für Tasks
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    tasks = Task.query.order_by(Task.timestamp.desc()).paginate(
        page=page, per_page=5, error_out=False)
    next_url = url_for('index', page=tasks.next_num) \
        if tasks.has_next else None
    prev_url = url_for('index', page=tasks.prev_num) \
        if tasks.has_prev else None
    return render_template('index.html', title=_('Home'),
                           tasks=tasks.items, next_url=next_url,
                           prev_url=prev_url, datetime=datetime)


# Übernommen, wenige Anpassungen für Tasks
@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    tasks = Task.query.order_by(Task.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False)
    next_url = url_for('explore', page=tasks.next_num) \
        if tasks.has_next else None
    prev_url = url_for('explore', page=tasks.prev_num) \
        if tasks.has_prev else None
    return render_template('index.html', title=_('Explore'),
                           tasks=tasks.items, next_url=next_url,
                           prev_url=prev_url, datetime=datetime)

# Übernommen
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title=_('Sign In'), form=form)

# Übernommen
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Übernommen
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html', title=_('Register'), form=form)

# Übernommen & Eigenentwicklung um Tasks anzuzeigen
@app.route('/user/<username>')
@login_required
def user(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    tasks = Task.query.filter_by(creator=user).order_by(Task.timestamp.desc()).paginate(
        page=page, per_page=5, error_out=False)
    page = request.args.get('page', 1, type=int)
    next_url = url_for('user', username=user.username, page=tasks.next_num) \
        if tasks.has_next else None
    prev_url = url_for('user', username=user.username, page=tasks.prev_num) \
        if tasks.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, tasks=tasks.items,
                           next_url=next_url, prev_url=prev_url, form=form, datetime=datetime)

# Übernommen
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)

# Eigenentwicklung
@app.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(title=form.title.data, description = form.description.data, due_date = form.due_date.data, status=form.status.data, creator = current_user)
        db.session.add(task)
        db.session.commit()
        flash('Your task has been updated!', 'success')
        return redirect(url_for('index'))
    return render_template('index.html', title=_('Task Home'), form=form)

# Eigenentwicklung
# Diese Route zeigt einen einzelnen Task an
@app.route('/tasks/<int:task_id>', methods=['GET'])
@login_required
def view_task(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template('task.html', title=task.title, task=task, datetime=datetime)

# Eigenentwicklung
# Diese Route ermöglicht das Bearbeiten eines Tasks
@app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if current_user != task.creator:
        abort(403)
    form = TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.status = form.status.data
        db.session.commit()
        flash('Your task has been updated!', 'success')
        return redirect(url_for('view_task', task_id=task_id))
    elif request.method == 'GET':
        form.title.data = task.title
        form.description.data = task.description
        form.due_date.data = task.due_date
        form.status.data = task.status
    return render_template('index.html', title='Edit Task', form=form)

