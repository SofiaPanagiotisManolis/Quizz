import random
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from sqlalchemy.orm import relationship

app = Flask(__name__)

questions = {
       1: {
            'question': 'Ποιος ήταν ο πρώτος άνθρωπος που περπάτησε στη Σελήνη;',
            'options': ['Α) Neil Armstrong', 'Β) Yuri Gagarin', 'Γ) Buzz Aldrin', 'Δ) Michael Collins'],
            'correct_answer': 'Α'
        },
        2: {
            'question': 'Ποια πόλη είναι η πρωτεύουσα της Ιταλίας;',
            'options': ['Α) Βαρκελώνη', 'Β) Παρίσι', 'Γ) Ρώμη', 'Δ) Βιέννη'],
            'correct_answer': 'Γ'
        },
        3: {
            'question': 'Ποιος ζωγράφος δημιούργησε τον πίνακα "Η Μονάλιζ";',
            'options': ['Α) Vincent van Gogh', 'Β) Pablo Picasso', 'Γ) Leonardo da Vinci', 'Δ) Claude Monet'],
            'correct_answer': 'Γ'
        },
        4: {
            'question': 'Ποιος είναι ο μεγαλύτερος ποταμός στον κόσμο;',
            'options': ['Α) Νείλος', 'Β) Άμαζονας', 'Γ) Γάγγης', 'Δ) Μισισιπής'],
            'correct_answer': 'Β'
        },
        5: {
            'question': 'Ποιος συγγραφέας έγραψε το βιβλίο "Ο Άρχοντας των Δαχτυλιδιών";',
            'options': ['Α) J.K. Rowling', 'Β) George R.R. Martin', 'Γ) J.R.R. Tolkien', 'Δ) C.S. Lewis'],
            'correct_answer': 'Γ'
        }
    }


app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///questions.db'
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"

# Initialize The Database
db = SQLAlchemy(app)
app.app_context().push() 
# στο shell python from app import app    from app import db    db.create_all

#---------------------------------------------------------------
class QuestionForm(FlaskForm):
    
    question = StringField("Ερώτηση", validators=[DataRequired()])
    option_A = StringField("Α) επιλογή", validators=[DataRequired()])
    option_B = StringField("Β) επιλογή", validators=[DataRequired()])
    option_C = StringField("Γ) επιλογή", validators=[DataRequired()])
    option_D = StringField("Δ) επιλογή", validators=[DataRequired()])
    correct_answer = SelectField('Επίλεξε την σωστή απάντηση', validators=[DataRequired()], choices=[
        ('option_A', 'Α'),
        ('option_B', 'Β'),
        ('option_C', 'Γ'),
        ('option_D', 'Δ')
    ])
    category_id = SelectField('Κατηγορία', coerce=int, validators=[DataRequired()])

    submit = SubmitField("Submit")

class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

# Create Model
class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    question_text = db.Column(db.String(255), unique=True, nullable=False)
    option_A = db.Column(db.String(100), nullable=False)
    option_B = db.Column(db.String(100), nullable=False)
    option_C = db.Column(db.String(100), nullable=False)
    option_D = db.Column(db.String(100), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('questions', lazy=True))
    

#---------------------------------------------------------------
      
@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')


@app.route('/delete/<int:id>')
def delete(id):
	question_to_delete = Questions.query.get_or_404(id)
	form = QuestionForm()

	try:
		db.session.delete(question_to_delete)
		db.session.commit()
		flash("Η ερώτηση διαγράφηκε")

		our_questions = Questions.query.all()
		return render_template("add_question.html", 
		form=form,
		our_questions=our_questions)

	except:
		flash("Παρουσιάστηκε πρόβλημα με την διαγραφή, ξαναπροσπαθήστε")
		return render_template("add_question.html", 
		form=form,
		our_questions=our_questions)


@app.route('/add', methods=['GET', 'POST'])
def add_question():
    form = QuestionForm() 
    form.category_id.choices = [(category.id, category.name) for category in Category.query.all()]

    if form.validate_on_submit():
        quest = Questions( question_text=form.question.data, 
                     option_A=form.option_A.data,
                     option_B=form.option_B.data,
                     option_C=form.option_C.data,
                     option_D=form.option_D.data,
                     correct_answer = form.correct_answer.data,
                    category_id = form.category_id.data ) 
        db.session.add(quest)
        db.session.commit()
        form.question.data = ''
        form.option_A.data = ''
        form.option_B.data = ''
        form.option_C.data = ''
        form.option_D.data = ''
        form.correct_answer.data = ''
        form.category_id.data = ''
        flash("Η ερώτηση καταχωρίστηκε")
    our_questions = Questions.query.all()
   # our_questions = Questions.query.order_by(Questions.id)
    # our_categories = Category.query.all()
    return render_template("add_question.html", 
		form=form,
		our_questions=our_questions)



@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):

    form = QuestionForm() 
    form.category_id.choices = [(category.id, category.name) for category in Category.query.all()]

    if request.method == 'POST':
        question_to_update = Questions.query.get_or_404(id)
        question_to_update.question_text = request.form['question']
        question_to_update.option_A = request.form['option_A']
        question_to_update.option_B = request.form['option_B']
        question_to_update.option_C = request.form['option_C']
        question_to_update.option_D = request.form['option_D']
        question_to_update.correct_answer = request.form['correct_answer']
        question_to_update.category_id = request.form['category_id']

        try:
            db.session.commit()
            flash ("Η ερώτηση ενημερώθηκε")
            return render_template("update.html", 
						  form=form, question_to_update=question_to_update, id=id)
        except:
            flash ("Λάθος")
            return render_template("update.html", 
						  form=form, question_to_update=question_to_update,id=id)
    else:
        if id!=0 :
            question_to_update = Questions.query.get_or_404(id)
            return render_template("update.html", 
						  form=form, question_to_update=question_to_update,id=id)
        else:
            question_to_update = Questions.query.all()
            return render_template("choose.html")

# Εμφάνιση όλων των ερωτήσεων και επιλογή μίας για διόρθωση ή διαγραφή 
@app.route('/choose/')
def choose():

    form = QuestionForm() 
    q = Questions.query.all()
    categories = Category.query.all()
    categories_id_names = {}
    # Προσθέτουμε τα id και τα name κάθε αντικειμένου Category στο λεξικό
    for category in categories:
        categories_id_names[category.id] = category.name
    return render_template("chooseQuestion.html", questions=q, categories_id_names=categories_id_names)

# Εμφάνιση όλων των κατηγοριών και επιλογή μίας για διόρθωση ή διαγραφή 

@app.route('/cards')
def cards():
    form = CategoryForm()
    categories = Category.query.all()
    
    return render_template("cards.html", categories=categories) 

if __name__ == '__main__':
    app.run(debug=True)