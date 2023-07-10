from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from .models import AuditionConfig, Candidate, Vote, SFOAParticipant, Round, ProductionConfig
from .forms import SettingsBegin, SettingsRound, ParticipantForm, SearchForm
from flask_paginate import Pagination, get_page_parameter
from werkzeug.utils import secure_filename
import os
import uuid as uuid

from sqlalchemy import update

production = Blueprint('production', __name__)


@production.route('/participants', methods=['GET', 'POST'])
def participants():
    all_participants = SFOAParticipant.query.order_by(SFOAParticipant.last_name)
    return render_template('admin/interface/production/participants.html',
                           user=current_user,
                           all_participants=all_participants)


@production.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@production.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        searched = form.searched.data
        results = SFOAParticipant.query.filter(SFOAParticipant.first_name.like(searched) | SFOAParticipant.last_name.like(f'%{searched}%')).all()
        return render_template("admin/interface/production/search.html",
                               user=current_user,
                               form=form,
                               searched=searched,
                               results=results)


@production.route('/participants/participant-add', methods=['GET', 'POST'])
def participants_add():
    form = ParticipantForm()
    if request.method == 'POST':
        first_name = form.first_name.data
        last_name = form.last_name.data
        birth_date = form.birth_date.data
        email = form.email.data
        phone = form.phone.data
        street_number = form.street_number.data
        country = form.country.data
        zip = form.zip.data
        bio = form.bio.data

        # check for profile pic
        if form.photo.data:
            # grab image name
            pic_filename = secure_filename(form.photo.data.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            photo = pic_name
            # save image
            form.photo.data.save(os.path.join("website/static/images/profile_pictures/" + pic_name))

            new_participant = SFOAParticipant(first_name=first_name,
                                              last_name=last_name,
                                              birth_date=birth_date,
                                              email=email,
                                              phone=phone,
                                              street_number=street_number,
                                              country=country,
                                              zip=zip,
                                              bio=bio,
                                              photo=photo)  # providing the schema for the note
        else:
            new_participant = SFOAParticipant(first_name=first_name,
                                              last_name=last_name,
                                              birth_date=birth_date,
                                              email=email,
                                              phone=phone,
                                              street_number=street_number,
                                              country=country,
                                              zip=zip,
                                              bio=bio)  # providing the schema for the note
        db.session.add(new_participant)  # adding the note to the database
        db.session.commit()
        flash('Participant added!', category='success')  # Gets the text note from the HTML
        return redirect(url_for('production.participants'))
    # adding the note to the library
    print("Success")
    return render_template("admin/interface/production/participant-add.html", user=current_user, form=form)


@production.route('/participants/participant-edit/<int:cid>', methods=['GET', 'POST'])
def participant_edit(cid):
    participant = SFOAParticipant.query.get(cid)
    form = ParticipantForm()

    if request.method == "POST":
        participant.first_name = form.first_name.data
        participant.last_name = form.last_name.data
        participant.birth_date = form.birth_date.data
        participant.email = form.email.data
        participant.phone = form.phone.data
        participant.street_number = form.street_number.data
        participant.city = form.city.data
        participant.country = form.country.data
        participant.zip = form.zip.data
        participant.bio = form.bio.data

        # check for profile pic
        if form.photo.data:
            # grab image name
            pic_filename = secure_filename(form.photo.data.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            participant.photo = pic_name
            # save image
            form.photo.data.save(os.path.join("website/static/images/profile_pictures/" + pic_name))

        # send to db
        db.session.commit()
        flash("User Updated Successfully!")
    # upload file

    # prefill the form
    form.first_name.data = participant.first_name
    form.last_name.data = participant.last_name
    form.birth_date.data = participant.birth_date
    form.email.data = participant.email
    form.phone.data = participant.phone
    form.street_number.data = participant.street_number
    form.city.data = participant.city
    form.country.data = participant.country
    form.zip.data = participant.zip
    form.bio.data = participant.bio

    return render_template("admin/interface/production/participant-edit.html",
                           user=current_user,
                           participant=participant,
                           form=form)


@production.route('/participants/participant-view/<int:cid>', methods=['GET', 'POST'])
def participant_view(cid):
    participant = SFOAParticipant.query.get(cid)
    form = ParticipantForm()

    # prefill the form
    form.first_name.data = participant.first_name
    form.last_name.data = participant.last_name
    form.birth_date.data = participant.birth_date
    form.email.data = participant.email
    form.phone.data = participant.phone
    form.street_number.data = participant.street_number
    form.city.data = participant.city
    form.country.data = participant.country
    form.zip.data = participant.zip
    form.bio.data = participant.bio

    return render_template("admin/interface/production/participant-view.html",
                           user=current_user,
                           participant=participant,
                           form=form)


@production.route('/draw', methods=['GET', 'POST'])
def draw():
    page = request.args.get(get_page_parameter(), default=1, type=int)
    all_candidates = Candidate.query
    pagination = all_candidates.paginate(page=page, per_page=1)
    all_names = SFOAParticipant.query.order_by(SFOAParticipant.last_name)
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        assigned_number = request.form.get('number_selected')
        touch_candidate = Candidate.query.filter_by(candidate_number=assigned_number).first()
        touch_candidate.first_name = first_name
        touch_candidate.last_name = last_name
        touch_candidate.lot = True
        db.session.commit()
        sfoa = SFOAParticipant.query.filter_by(first_name=first_name, last_name=last_name).first()
        sfoa.lot = True
        db.session.commit()
        flash(f'Draw number {assigned_number} set for {first_name} {last_name} !', category='success')  # Gets the text note from the HTML
    return render_template('admin/interface/production/draw.html',
                           user=current_user,
                           pagination=pagination,
                           all_names=all_names,
                           all_candidates=all_candidates
                           )


@production.route('/participants/check-in', methods=['GET', 'POST'])
def participants_check_in():
    production_config = ProductionConfig.query.first()
    print(production_config.check_in)
    all_participants = SFOAParticipant.query.order_by(SFOAParticipant.last_name)
    if request.method == 'POST':
        participant_id = request.form['participant_id']
        get_participant = SFOAParticipant.query.get(participant_id)
        get_participant.checked_in = True
        db.session.commit()
    return render_template('admin/interface/production/participants-check-in.html',
                           user=current_user,
                           all_participants=all_participants,
                           production_config=production_config)


@production.route('/participants/check-in/reset', methods=['GET'])
def reset_check_in():
    all_participants = SFOAParticipant.query.all()
    for participant in all_participants:
        participant.checked_in = False
        db.session.commit()
    return redirect(url_for('production.participants_check_in'))


@production.route('/participants/check-in/start', methods=['GET', 'POST'])
def start_check_in():
    production_config = ProductionConfig.query.first()
    production_config.check_in = True
    db.session.commit()
    return redirect(url_for('production.participants_check_in'))


@production.route('/participants/check-in/stop', methods=['GET'])
def stop_check_in():
    count_participants = SFOAParticipant.query.filter_by(checked_in=True).count()
    # empty candidate db
    Candidate.query.delete()
    # define the range of candidates to be created
    candidates_set = count_participants + 1
    # create records in candidate db
    for candidate_num in range(1, candidates_set):
        new_candidate = Candidate(candidate_number=candidate_num)
        db.session.add(new_candidate)
        db.session.commit()
    production_config = ProductionConfig.query.first()
    print(production_config.check_in)
    production_config.check_in = False
    db.session.commit()
    return redirect(url_for('production.participants_check_in'))


@production.route('/create-candidates', methods=['GET'])
def create_candidates():
    count_participants = SFOAParticipant.query.filter_by(checked_in=True).count()
    # empty candidate db
    Candidate.query.delete()
    # define the range of candidates to be created
    candidates_set = count_participants + 1
    # create records in candidate db
    for candidate_num in range(1, candidates_set):
        new_candidate = Candidate(candidate_number=candidate_num)
        db.session.add(new_candidate)
        db.session.commit()

    return redirect(url_for('production.participants_check_in'))