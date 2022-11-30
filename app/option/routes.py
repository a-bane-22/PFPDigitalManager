from flask import render_template, redirect, url_for
from flask_login import login_required
from app import db
from app.models import (Security, OptionQuote)
from app.option.forms import (AddOptionQuoteForm, UploadFileForm)
from app.option import bp
from app.route_helpers import (process_option_quote_csv_file)
from datetime import date


@bp.route('/view_option_quotes')
@login_required
def view_option_quotes():
    quotes = OptionQuote.query.all()
    return render_template('view_option_quotes.html',
                           title='View Option Quotes',
                           quotes=quotes)


@bp.route('/view_option_quote/<quote_id>')
@login_required
def view_option_quote(quote_id):
    quote = OptionQuote.query.get(int(quote_id))
    return render_template('view_option_quote.html',
                           title='View Option Quote',
                           quote=quote)


@bp.route('/add_option_quote/<security_id>', methods=['GET', 'POST'])
@login_required
def add_option_quote(security_id):
    form = AddOptionQuoteForm()
    if form.validate_on_submit():
        security = Security.query.get(int(security_id))
        quote = OptionQuote(symbol=security.symbol,
                            security_id=security.id,
                            quote_date=date.today(),
                            type=form.type.data,
                            expiration_date=form.expiration_date.data,
                            strike_price=form.strike_price.data,
                            bid=form.bid.data,
                            ask=form.ask.data,
                            last=form.last.data,
                            high=form.high.data,
                            low=form.low.data,
                            change=form.change.data,
                            volume=form.volume.data,
                            open_interest=form.open_interest.data)
        db.session.add(quote)
        db.session.commit()
        return redirect(url_for('option.view_option_quote',
                                quote_id=quote.id))
    return render_template('add_option_quote.html',
                           title='Add Option Quote',
                           form=form)


@bp.route('/upload_option_quotes', methods=['GET', 'POST'])
@login_required
def upload_option_quotes():
    form = UploadFileForm()
    if form.validate_on_submit():
        process_option_quote_csv_file(file_object=form.upload_file.data)
        return redirect(url_for('option.view_option_quotes'))
    return render_template('upload_option_quotes.html',
                           title='Upload Option Quotes',
                           form=form)
