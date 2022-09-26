from flask import render_template, redirect, url_for
from flask_login import login_required
from app import db
from app.models import (Project, Task)
from app.task.forms import (ProjectForm, TaskForm)
from app.task import bp
from datetime import date


@bp.route('/view_projects')
@login_required
def view_projects():
    projects = Project.query.all()
    return render_template('view_projects.html', title='View Projects', projects=projects)


@bp.route('/view_project/<project_id>')
@login_required
def view_project(project_id):
    project = Project.query.get(int(project_id))
    return render_template('view_project.html', title='View Project', project=project)


@bp.route('/add_project', methods=['GET', 'POST'])
@login_required
def add_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(title=form.title.data, description=form.title.description,
                          due_date=form.due.data, create_date=date.today())
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('task.view_project', project_id=project.id))
    return render_template('add_project.html', title='Add Project', form=form)


@bp.route('/edit_project/<project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get(int(project_id))
    form = ProjectForm()
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        project.due_date = form.due.data
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('task.view_project', project_id=project.id))
    form.title.data = project.title
    form.description.data = project.description
    form.due.data = project.due_date
    return render_template('edit_project.html', title='Edit Project', form=form)


@bp.route('/delete_project/<project_id>')
@login_required
def delete_project(project_id):
    project = Project.query.get(int(project_id))
    for task in project.tasks:
        db.session.delete(task)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('task.view_projects'))


@bp.route('/add_project_task/<project_id>', methods=['GET', 'POST'])
@login_required
def add_project_task(project_id):
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(title=form.title.data, description=form.description.data,
                    due_date=form.due.data, create_date=date.today(),
                    completed=False, project_id=int(project_id))
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('task.view_project', project_id=project_id))
    return render_template('add_task.html', title='Add Task', form=form)


@bp.route('/view_tasks')
@login_required
def view_tasks():
    tasks = Task.query.all()
    return render_template('view_tasks.html', title='View Tasks', tasks=tasks)


@bp.route('/view_task/<task_id>')
@login_required
def view_task(task_id):
    task = Task.query.get(int(task_id))
    return render_template('view_task.html', title='View Task', task=task)


@bp.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(title=form.title.data, description=form.description.data,
                    due_date=form.due.data, create_date=date.today(), completed=False)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('task.view_task', task_id=task.id))
    return render_template('add_task.html', title='Add Task', form=form)


@bp.route('/edit_task/<task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get(int(task_id))
    form = TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due.data
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('task.view_task', task_id=task.id))
    form.title.data = task.title
    form.description.data = task.description
    form.due.data = task.due_date
    return render_template('edit_task.html', title='Edit Task', form=form)


@bp.route('/delete_task/<task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get(int(task_id))
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('task.view_tasks'))


@bp.route('/complete_task/<task_id>')
@login_required
def complete_task(task_id):
    task = Task.query.get(int(task_id))
    task.completed = True
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('task.view_task', task_id=task_id))
