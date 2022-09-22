from flask import render_template, flash, redirect, url_for
from flask_login import current_user, logout_user, login_required
from app import db
from app.models import User
from app.user.forms import (AddUserForm, EditUserForm, ChangePasswordForm, DeleteUserForm)
from app.user import bp


@bp.route('/view_users')
@login_required
def view_users():
    users = User.query.all()
    return render_template('view_users.html', title='Users', users=users)


@bp.route('/view_user/<user_id>')
@login_required
def view_user(user_id):
    user = User.query.get(int(user_id))
    return render_template('view_user.html', title='User Dashboard', user=user)


@bp.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name=form.last_name.data,
                    username=form.username.data, email=form.email.data, phone=form.phone.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user.view_user', user_id=user.id))
    return render_template('add_user.html', title='Add User', form=form)


@bp.route('/edit_user/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get(int(user_id))
    form = EditUserForm()
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.phone = form.phone.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user.view_user', user_id=user.id))
    form.first_name.data = user.first_name
    form.last_name.data = user.last_name
    form.email.data = user.email
    form.phone.data = user.phone
    return render_template('edit_user.html', title='Edit User', form=form)


@bp.route('/change_password/<user_id>', methods=['GET', 'POST'])
@login_required
def change_password(user_id):
    user = User.query.get(int(user_id))
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if user.check_password(form.old_password.data):
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('user.view_user', user_id=user.id))
        else:
            flash('The password provided was not correct')
            return redirect(url_for('main.change_password', user_id=user.id))
    return render_template('change_password.html', title='Change Password', form=form)


@bp.route('/delete_user/<user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    user = User.query.get(int(user_id))
    form = DeleteUserForm()
    if form.validate_on_submit():
        if form.confirm.data:
            if current_user.id == user.id:
                logout_user()
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for('main.index'))
        else:
            return redirect(url_for('main.index'))
    return render_template('delete_user.html', title='Delete User', form=form, user=user)
