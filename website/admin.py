from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from .models import AuditionConfig, Candidate, Vote, SFOAParticipant, Round, Result, User
from .forms import SettingsBegin, SettingsRound
from flask_paginate import Pagination, get_page_parameter
from sqlalchemy.sql import func


admin = Blueprint('admin', __name__)


@admin.route('/dashboard')
def dashboard():
    return render_template('admin/interface/index.html',
                           user=current_user)


@admin.route('/dashboard/layout-static')
def layout_static():
    return render_template('admin/interface/layout-static.html',
                           user=current_user)


@admin.route('/dashboard/layout-sidenav-light')
def layout_sidenav_light():
    return render_template('admin/interface/layout-sidenav-light.html',
                           user=current_user)

# audition settings
@admin.route('/settings', methods=['GET', 'POST'])
# @login_required
def settings():
    # begin section - load form
    settings_begin = SettingsBegin()
    rounds = Round.query.all()
    # check the correct button has been pressed
    if settings_begin.submit_settings_begin.data and settings_begin.validate():
        # reset the AuditionConfig database
        AuditionConfig.query.delete()
        # set the data from form
        new_settings = AuditionConfig(number_of_candidates=settings_begin.number_of_candidates.data,
                                      number_of_rounds=settings_begin.number_of_rounds.data,
                                      current_round=1)
        db.session.add(new_settings)
        db.session.commit()
        flash('Settings changed!', category='success')
        # empty candidate db
        Candidate.query.delete()
        # define the range of candidates to be created
        candidates_set = int(settings_begin.number_of_candidates.data) + 1
        # create records in candidate db
        for candidate_num in range(1, candidates_set):
            new_candidate = Candidate(candidate_number=candidate_num, round=1)
            db.session.add(new_candidate)
            db.session.commit()

        Round.query.delete()
        # define the range of rounds to be created
        round_set = int(settings_begin.number_of_rounds.data) + 1
        # create records in round db
        for round_num in range(1, round_set):
            new_round = Round(number=round_num)
            db.session.add(new_round)
            db.session.commit()

    return render_template('admin/interface/audition/settings.html',
                           user=current_user,
                           settings_begin=settings_begin,
                           count_of_rounds=AuditionConfig.query.first().number_of_rounds,
                           count_of_candidates=SFOAParticipant.query.filter_by(checked_in=True).count(),
                           rounds=rounds)


@admin.route('/settings/rounds', methods=['GET', 'POST'])
def round_settings():
    rounds = Round.query.all()
    settings_round = SettingsRound()
    return render_template('admin/interface/audition/round-settings.html',
                           user=current_user,
                           rounds=rounds,
                           settings_round=settings_round
                           )


@admin.route('/round-edit/<int:rn>', methods=['GET', 'POST'])
def round_edit(rn):
    round_selected = Round.query.filter_by(number=rn).first()
    settings_round = SettingsRound()
    if settings_round.validate_on_submit():
        round_selected.scheme = settings_round.scheme.data
        round_selected.pass_limit = settings_round.pass_limit.data
        round_selected.duration = settings_round.duration.data
        round_selected.optional_piece = settings_round.optional_piece.data
        db.session.commit()
    settings_round.scheme.data = round_selected.scheme
    settings_round.pass_limit.data = round_selected.pass_limit
    settings_round.duration.data = round_selected.duration
    settings_round.optional_piece.data = round_selected.optional_piece

    return render_template('admin/interface/audition/round-edit.html',
                           user=current_user,
                           settings_round=settings_round,
                           round=round_selected
                           )

#audition settings end

@admin.route('/reset-voting', methods=['GET', 'POST'])
@login_required
def reset_voting():
    Vote.query.delete()
    db.session.commit()
    flash('Votes reset success!', category='success')
    return redirect(url_for('admin.settings'))


@admin.route('/all-candidates', methods=['GET', 'POST'])
@login_required
def all_candidates():
    all_candidates = Candidate.query.all()
    return render_template('all_candidates.html',
                           user=current_user,
                           all_candidates=all_candidates)


@admin.route('/all-candidates/<int:cid>')
def candidate(cid):
    current_candidate = Candidate.query.get(cid)
    votes = Vote.query.filter_by(candidate_number=cid).all()
    rounds = Round.query.all()
    results = Result.query
    return render_template("candidate.html", user=current_user,
                           candidate=current_candidate,
                           votes=votes,
                           rounds=rounds,
                           results=results)


@admin.route('/is-voting-time')
def is_voting_time():
    round = AuditionConfig.query.first()
    print(round.round_1_open)
    if round.round_1_open:
        open_voting = True
        print("Opened")
    else:
        open_voting = False
        print("Not opened")
    return render_template("is-voting-time.html", user=current_user, open_voting=open_voting)


@admin.route('/draw', methods=['GET', 'POST'])
def draw():
    page = request.args.get(get_page_parameter(), default=1, type=int)
    all_candidates = Candidate.query
    pagination = all_candidates.paginate(page=page, per_page=1)
    all_names = SFOAParticipant.query.all()
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        assigned_number = request.form.get('number_selected')
        touch_candidate = Candidate.query.filter_by(candidate_number=assigned_number).first()
        touch_candidate.first_name = first_name
        touch_candidate.last_name = last_name
        touch_candidate.lot = True
        sfoa = SFOAParticipant.query.filter_by(first_name=first_name, last_name=last_name).first()
        sfoa.lot = True
        db.session.commit()
        flash(f'Draw number {assigned_number} set for {first_name} {last_name} !', category='success')  # Gets the text note from the HTML
    return render_template('/production/production.html',
                           user=current_user,
                           pagination=pagination,
                           all_names=all_names,
                           all_candidates=all_candidates
                           )


@admin.route('/draw/reset')
def reset_draw():
    sfoa_participants = SFOAParticipant.query.all()
    for participant in sfoa_participants:
        participant.lot = False
    candidates = Candidate.query.all()
    for candidate in candidates:
        candidate.lot = False
    db.session.commit()
    flash('Reset successful !', category='success')

    return redirect(url_for('production.draw'))


@admin.route('/candidate/result/round<int:rn>', methods=['GET', 'POST'])
def candidate_result(rn):
    check_if_not_empty = Result.query.filter_by(round=rn).first()
    if not check_if_not_empty:
        if rn == 1:
            Result.query.delete()
            db.session.commit
            round_settings = Round.query.filter_by(number=rn).first()
            all_candidates = Candidate.query.filter_by(round=rn)
            for candidate in all_candidates:
                print(candidate.candidate_number)
                score = Vote.query. \
                    with_entities(func.avg(Vote.score)). \
                    filter_by(round_number=rn, candidate_number=candidate.candidate_number). \
                    all()
                score_avg = round(score[0][0], 2)
                print(score_avg)
                if score_avg >= float(round_settings.pass_limit):
                    passed = True
                    rounds_check = Round.query.count()
                    if rn != rounds_check:
                        candidate.round = rn + 1
                else:
                    passed = False
                result = Result(candidate=candidate.candidate_number, round=rn, score=score_avg, passed=passed)
                db.session.add(result)
                db.session.commit()
            return redirect(url_for('admin.round_results', rn=rn))
        else:
            round_settings = Round.query.filter_by(number=rn).first()
            all_candidates = Candidate.query.filter_by(round=rn)
            for candidate in all_candidates:
                print(candidate.candidate_number)
                score = Vote.query.\
                    with_entities(func.avg(Vote.score)).\
                    filter_by(round_number=rn, candidate_number=candidate.candidate_number).\
                    all()
                score_avg = round(score[0][0], 2)
                print(score_avg)
                if score_avg >= float(round_settings.pass_limit):
                    passed = True
                    rounds = Round.query.count()
                    if rounds != rn:
                        candidate.round = rn + 1
                else:
                    passed = False
                result = Result(candidate=candidate.candidate_number, round=rn, score=score_avg, passed=passed)
                db.session.add(result)
                db.session.commit()
            return redirect(url_for('admin.round_results', rn=rn))
    else:
        return redirect(url_for('admin.round_results', rn=rn))


@admin.route('/round/results/<int:rn>', methods=['GET', 'POST'])
def round_results(rn):
    round = rn
    results = Result.query.filter_by(round=rn).order_by(Result.score.desc()).all()
    return render_template('admin/interface/audition/results.html',
                           user=current_user,
                           results=results,
                           round=rn,
                           length=len(results))


@admin.route('/audition/start-voting', methods=['GET', 'POST'])
def start_voting():
    rounds_started = Round.query.filter_by(ended=True).count() + 1
    rounds = Round.query.all()
    check_round = Vote.query

    return render_template('admin/interface/audition/start-voting.html',
                           user=current_user,
                           rounds=rounds,
                           rounds_started=rounds_started,
                           check_round=check_round)


@admin.route('/audition/start-voting/round<int:rn>', methods=['GET', 'POST'])
def start_round(rn):
    other_rounds = Round.query.filter(Round.number != rn).all()
    for round in other_rounds:
        round.active = False
        selected_round = Round.query.filter_by(number=rn).first()
        selected_round.active = True
        db.session.commit()
    return redirect(url_for('admin.start_voting'))


@admin.route('/audition/start-voting/stop/round<int:rn>', methods=['GET', 'POST'])
def stop_round(rn):
    active_round = Round.query.filter_by(number=rn).first()
    active_round.active = False
    active_round.ended = True
    db.session.commit()
    return redirect(url_for('admin.start_voting'))
