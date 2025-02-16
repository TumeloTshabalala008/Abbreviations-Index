from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///abbreviations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class Abbreviation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.String(50), nullable=False, unique=True)
    full_form = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Abbreviation {self.abbreviation}>'

# WTForms Form
class AbbreviationForm(FlaskForm):
    abbreviation = StringField('Abbreviation', validators=[DataRequired()])
    full_form = StringField('Full Form', validators=[DataRequired()])
    description = TextAreaField('Description')

# Routes
@app.route('/')
def index():
    # Optional: Implement searching if needed
    search_query = request.args.get('search')
    if search_query:
        abbreviations = Abbreviation.query.filter(
            Abbreviation.abbreviation.contains(search_query) |
            Abbreviation.full_form.contains(search_query) |
            Abbreviation.description.contains(search_query)
        ).all()
    else:
        abbreviations = Abbreviation.query.all()
    return render_template('index.html', abbreviations=abbreviations)

@app.route('/create', methods=['GET', 'POST'])
def create():
    form = AbbreviationForm()
    if form.validate_on_submit():
        new_abbrev = Abbreviation(
            abbreviation=form.abbreviation.data,
            full_form=form.full_form.data,
            description=form.description.data
        )
        db.session.add(new_abbrev)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create.html', form=form)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    abbreviation = Abbreviation.query.get_or_404(id)
    form = AbbreviationForm(obj=abbreviation)
    if form.validate_on_submit():
        abbreviation.abbreviation = form.abbreviation.data
        abbreviation.full_form = form.full_form.data
        abbreviation.description = form.description.data
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update.html', form=form, abbreviation=abbreviation)

@app.route('/delete/<int:id>')
def delete(id):
    abbreviation = Abbreviation.query.get_or_404(id)
    db.session.delete(abbreviation)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
