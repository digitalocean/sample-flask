from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_parameter
from . import db
import json
from .models import Vote, Candidate, Note, Round

ROWS_PER_PAGE = 5
view = Blueprint('view', __name__)


@view.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')  # Gets the text note from the HTML

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            # adding the note to the library
            new_note = Note(data=note, user_id=current_user.id)  # providing the schema for the note
            db.session.add(new_note)  # adding the note to the database
            db.session.commit()
            flash('Note added!', category='success')
    return render_template("home.html", user=current_user)


@view.route('/select_project', methods=['GET', 'POST'])
@login_required
def select_project():
    return render_template("select_project.html", user=current_user)


@view.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data)  # this function expects a JSON from the INDEX.js file
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


@view.context_processor
def base():
    get = Round.query.filter_by(active=True).first()
    if get is None:
        get_current_round = 0
    else:
        get_current_round = get.number
    return dict(current_round=get_current_round)


@view.route('/voting-sheet', methods=['GET', 'POST'])
@login_required
def voting_sheet():
    voting_active = Round.query.filter_by(active=True).first()
    if not voting_active:
        return render_template('404_voting_not_started.html',
                               user=current_user)
    else:
        # get hold of current round
        get_current_round = Round.query.filter_by(active=True).first()
        current_round = get_current_round
        # pagination
        page = request.args.get(get_page_parameter(), default=1, type=int)
        all_candidates = Candidate.query.filter_by(round=current_round.number).order_by(Candidate.candidate_number)
        pagination = all_candidates.paginate(page=page, per_page=1)
        print(pagination.iter_pages())

        if request.method == 'POST':
            # form requests
            print(current_round)
            print(type(current_round))
            score = request.form.get('score')  # providing the schema for the note
            comment = request.form.get('comment')
            candidate_number = request.form.get('candidate_number')
            new_vote = Vote(candidate_number=candidate_number,
                            round_number=current_round.number,
                            score=score,
                            comment=comment,
                            user_id=current_user.id)
            # check if already voted
            lookup_vote = Vote.query.filter_by(round_number=current_round.number,
                                               candidate_number=candidate_number,
                                               user_id=current_user.id).first()
            if not lookup_vote:
                # adding the vote to the database
                db.session.add(new_vote)
                db.session.commit()
                flash(f'Vote for candidate {candidate_number} added!', category='success')  # Gets the text note from the HTML
            else:
                flash('Already voted, vote not saved!', category='error')  # Gets the text note from the HTML

            # checking if at the end of voting
            last_candidate_get = Candidate.query.\
                filter_by(round=current_round.number).\
                order_by(Candidate.candidate_number.desc()).\
                first()
            last_candidate = last_candidate_get.candidate_number
            if int(candidate_number) == last_candidate:
                return redirect(url_for('admin.dashboard'))
            else:
                return render_template('voting_sheet.html',
                                       user=current_user,
                                       pagination=pagination,
                                       current_round=current_round)
        else:
            return render_template('voting_sheet.html',
                                   user=current_user,
                                   pagination=pagination,
                                   current_round=current_round)


@view.route('/all-votes')
@login_required
def all_votes():
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    print(page)
    all_votes = Vote.query.all()
    pagination = Pagination(page=page,
                            total=len(all_votes),
                            per_page=3,
                            search=search,
                            record_name='All Votes')
    return render_template('all_votes.html', user=current_user, all_votes=all_votes, pagination=pagination)
