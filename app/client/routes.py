from flask import render_template, redirect, url_for
from flask_login import login_required
from app import db
from app.models import Client, Group
from app.client.forms import (ClientInformationForm, GroupForm, AssignClientsForm, AssignClientForm, UploadFileForm)
from app.client import bp
from app.route_helpers import upload_file
from datetime import date


@bp.route('/view_clients')
@login_required
def view_clients():
    clients = Client.query.all()
    return render_template('view_clients.html', title='Clients', clients=clients)


@bp.route('/view_client/<client_id>')
@login_required
def view_client(client_id):
    client = Client.query.get(int(client_id))
    accounts = client.accounts
    return render_template('view_client.html', title='Client Dashboard', client=client, accounts=accounts)


@bp.route('/add_client', methods=['GET', 'POST'])
@login_required
def add_client():
    form = ClientInformationForm()
    if form.validate_on_submit():
        client = Client(first_name=form.first_name.data, last_name=form.last_name.data,
                        middle_name=form.middle_name.data, dob=form.dob.data, email=form.email.data,
                        cell_phone=form.cell_phone.data, work_phone=form.work_phone.data,
                        home_phone=form.home_phone.data, assigned=False)
        db.session.add(client)
        db.session.commit()
        return redirect(url_for('client.view_client', client_id=client.id))
    return render_template('add_client.html', title='Add Client', form=form)


@bp.route('/upload_clients', methods=['GET', 'POST'])
@login_required
def upload_clients():
    form = UploadFileForm()
    if form.validate_on_submit():
        f = form.upload_file.data
        lines = upload_file(file_object=f)
        for line in lines:
            data = line.split(',')
            first = data[0].strip()
            middle = data[1].strip()
            last = data[2].strip()
            dob = date.fromisoformat(data[3].strip())
            email = data[4].strip()
            cell = data[5].strip()
            work = data[6].strip()
            home = data[7].strip()
            group_name = data[8].strip()
            group_id = None
            assigned = False
            if group_name is not None:
                assigned = True
                group = Group.query.filter_by(name=group_name).first()
                if group is None:
                    group = Group(name=group_name)
                    db.session.add(group)
                    db.session.commit()
                group_id = group.id
            client = Client(first_name=first, middle_name=middle, last_name=last, dob=dob, email=email,
                            cell_phone=cell, work_phone=work, home_phone=home, group_id=group_id, assigned=assigned)
            db.session.add(client)
        db.session.commit()
        return redirect(url_for('client.view_clients'))
    return render_template('upload_client_file.html', title='Upload Clients', form=form)


@bp.route('/edit_client/<client_id>', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    client = Client.query.get(int(client_id))
    form = ClientInformationForm()
    if form.validate_on_submit():
        client.first_name = form.first_name.data
        client.middle_name = form.middle_name.data
        client.last_name = form.last_name.data
        client.dob = form.dob.data
        client.email = form.email.data
        client.cell_phone = form.cell_phone.data
        client.work_phone = form.work_phone.data
        client.home_phone = form.home_phone.data
        db.session.add(client)
        db.session.commit()
        return redirect(url_for('client.view_client', client_id=client_id))
    form.first_name.data = client.first_name
    form.last_name.data = client.last_name
    if client.middle_name is not None:
        form.middle_name.data = client.middle_name
    form.dob.data = client.dob
    form.email.data = client.email
    form.cell_phone.data = client.cell_phone
    form.work_phone.data = client.work_phone
    form.home_phone.data = client.home_phone
    return render_template('edit_client.html', title='Edit Client', form=form)


@bp.route('/delete_client/<client_id>')
@login_required
def delete_client(client_id):
    client = Client.query.get(int(client_id))
    db.session.delete(client)
    db.session.commit()
    return redirect(url_for('client.view_clients'))


@bp.route('/delete_all_clients')
@login_required
def delete_all_clients():
    clients = Client.query.all()
    for client in clients:
        db.session.delete(client)
    db.session.commit()
    return redirect(url_for('main.index'))


@bp.route('/view_groups')
@login_required
def view_groups():
    groups = Group.query.all()
    return render_template('view_groups.html', title='Groups', groups=groups)


@bp.route('/view_group/<group_id>')
@login_required
def view_group(group_id):
    group = Group.query.get(int(group_id))
    clients = group.clients
    return render_template('view_group.html', title='Group Dashboard', group=group, clients=clients)


@bp.route('/add_group/', methods=['GET', 'POST'])
@login_required
def add_group():
    form = GroupForm()
    if form.validate_on_submit():
        group = Group(name=form.name.data)
        db.session.add(group)
        db.session.commit()
        return redirect(url_for('client.view_group', group_id=group.id))
    return render_template('add_group.html', title='Add Group', form=form)


@bp.route('/edit_group/<group_id>', methods=['GET', 'POST'])
@login_required
def edit_group(group_id):
    group = Group.query.get(int(group_id))
    form = GroupForm()
    if form.validate_on_submit():
        group.name = form.name.data
        db.session.add(group)
        db.session.commit()
        return redirect(url_for('client.view_group', group_id=group.id))
    form.name.data = group.name
    return render_template('edit_group.html', title='Edit Group', form=form)


@bp.route('/assign_clients/<group_id>', methods=['GET', 'POST'])
@login_required
def assign_clients(group_id):
    group = Group.query.get(int(group_id))
    form = AssignClientsForm()
    unassigned_clients = Client.query.filter_by(group_id=None).all()
    choices = []
    for client in unassigned_clients:
        choices.append((client.id, client.get_name()))
    form.selections.choices = choices
    form.selections.size = len(choices)
    if form.validate_on_submit():
        assigned_client_ids = form.selections.data
        for client_id in assigned_client_ids:
            client = Client.query.get(client_id)
            client.group_id = group.id
            client.assigned = True
            db.session.add(client)
            for account in client.accounts:
                for snapshot in account.snapshots:
                    snapshot.group_id = group.id
                    db.session.add(snapshot)
        db.session.commit()
        return redirect(url_for('client.view_group', group_id=group_id))
    return render_template('assign_clients.html', title='Assign Clients', group=group, form=form)


@bp.route('/assign_client/<client_id>', methods=['GET', 'POST'])
@login_required
def assign_client(client_id):
    client = Client.query.get(int(client_id))
    groups = Group.query.all()
    choices = []
    for group in groups:
        choices.append((group.id, group.name))
    form = AssignClientForm()
    form.selection.choices = choices
    if form.validate_on_submit():
        client.group_id = form.selection.data
        client.assigned = True
        db.session.add(client)
        for account in client.accounts:
            for snapshot in account.snapshots:
                snapshot.group_id = client.group_id
                db.session.add(snapshot)
        db.session.commit()
        return redirect(url_for('client.view_client', client_id=client_id))
    return render_template('assign_client.html', title='Assign Client', client=client, form=form)
