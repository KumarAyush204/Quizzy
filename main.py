from flask import Flask,render_template,url_for,request,redirect,flash
from flask_sqlalchemy import SQLAlchemy
import os

current_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.secret_key = 'ayush'


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "quiz.sqlite3")
db = SQLAlchemy(app)
app.app_context().push()

class Quiz(db.Model):
    __tablename__ = 'quiz'
    quiz_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    title = db.Column(db.String,nullable=False)
    description = db.Column(db.String)
    date_created = db.Column(db.DateTime,default=db.func.current_timestamp())

class Questions(db.Model):
    __tablename__='questions'
    quiestion_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    question_text = db.Column(db.String,nullable=False)
    id = db.Column(db.Integer,db.ForeignKey("quiz.quiz_id"),nullable=False)

class Choices(db.Model):
    __tablename__ = 'choices'
    choice_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    choice1 = db.Column(db.String,nullable=False)
    choice2 = db.Column(db.String, nullable=False)
    choice3 = db.Column(db.String, nullable=False)
    choice4 = db.Column(db.String, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.quiestion_id"),nullable=False)

class CorrectOptions(db.Model):
    __tablename__='correctoptions'
    co_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.quiz_id"),nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.quiestion_id"),nullable=False)
    correct_option = db.Column(db.String,nullable=False)

user_admin = False

@app.route('/')
def indexpage():
    return  render_template('index.html')

@app.route('/quizes')
def quizes():
    query=Quiz.query.all()
    print(query)
    return  render_template('quizes.html',quizes=query)

@app.route('/quizes/<int:q_id>',methods=['GET','POST'])
def quiz_questions(q_id):
    if request.method=='GET':
        query = Questions.query.filter_by(id=q_id).all()
        question_ids = []
        for question in query:
            question_ids.append(question.quiestion_id)
        print(question_ids)
        choice_ids=[]
        for choice in question_ids:
            choices_query = Choices.query.filter_by(question_id=choice).first()
            choice_ids.append(choices_query)
        print(choice_ids)
        query3=Quiz.query.filter_by(quiz_id=q_id).first()
        return render_template('quiz_questions.html',questions=query,choices=choice_ids,quiz_id=q_id,q_name=query3,total_question=len(query))

@app.route('/quizes/<int:q_id>/answercheck',methods=['GET','POST'])
def AnswerCheck(q_id):
    query = Questions.query.filter_by(id=q_id).all()
    choices = []
    for q in query:
       query_c = Choices.query.filter_by(question_id=q.quiestion_id).first()
       choices.append(query_c)

    #Finding choices of particular question and quiz
    correct_choices=[]
    query_o = CorrectOptions.query.filter_by(quiz_id=q_id).all()

    # print(query_o)

    for i in query_o:
        correct_o = i.correct_option
        correct_choices.append(correct_o)
    print(correct_choices)
    marked_choices=[]

    #Submit choices are stored
    for c in choices:
        c_o=c.choice_id
        c_o=str(c_o)
        print(type(c_o))
        j=request.form.get(c_o)
        marked_choices.append(j)
    print(marked_choices)

    l=len(correct_choices)
    score=0
    for j in range(l):
        if correct_choices[j]==marked_choices[j]:
            score+=1

    return render_template('score.html',score=score)

@app.route('/admin')
def Admin():
    query = Quiz.query.all()
    print(query)
    return render_template('admin.html',quiz=query)
@app.route('/admin/newquiz',methods=['GET','POST'])
def AddNewQuiz():
    flag=False
    if request.method=='GET':
        return render_template('newquiz.html',flag=flag,submit=False)
    elif request.method=='POST':

        title = request.form['title']
        description = request.form['description']
        print(title,description)

        if title=='' or description=='':
            return render_template('newquiz.html', flag=flag,submt=True)
        new_quiz = Quiz(title=title,description=description)
        db.session.add(new_quiz)
        db.session.commit()
        flag=True
        # return render_template('newquiz.html',flag=flag)
        return redirect(url_for('Admin'))
@app.route('/admin/editquiz/<int:quiz_id>',methods=['GET','POST'])
def EditQuiz(quiz_id):
    if request.method=='GET':
        query = Questions.query.filter_by(id=quiz_id).all()
        print("Questions",query)
        choices=[]
        for i in query:

            query2 = Choices.query.filter_by(question_id=i.quiestion_id).first()
            # print("edit quiz")
            choices.append(query2)
        print(choices)
        len_query = len(query)
        print(len_query)
        if len_query==0:
            return render_template('editquiz.html', questions=query, choices=choices, len_choices=False,quiz_id=quiz_id)
        return render_template('editquiz.html',questions=query,choices=choices,len_choices=True,quiz_id=quiz_id)
    elif request.method=='POST':
        pass



@app.route('/admin/editquiz/<int:quiz_id>/addquestion',methods=['GET','POST'])
def AddQuestion(quiz_id):
    if request.method=='GET':
        return render_template('addquestion.html',quiz_id=quiz_id,flag=False)
    elif request.method=='POST':
        question = request.form['question']
        choice1 = request.form['c1']
        choice2 = request.form['c2']
        choice3 = request.form['c3']
        choice4 = request.form['c4']
        correct_option = request.form['correctoption']
        new_question = Questions(question_text=question,id=quiz_id)
        db.session.add(new_question)
        db.session.commit()

        query = Questions.query.filter_by(id=quiz_id).all()
        len_query = len(query)
        question_id=query[-1].quiestion_id

        new_choice = Choices(choice1=choice1,choice2=choice2,choice3=choice3,choice4=choice4,question_id=question_id)
        db.session.add(new_choice)
        db.session.commit()

        correctoption = CorrectOptions(quiz_id=quiz_id,question_id=question_id,correct_option=correct_option)
        db.session.add(correctoption)
        db.session.commit()


        # return render_template('addquestion.html',flag=True)
        return redirect(url_for('EditQuiz',quiz_id=quiz_id))
@app.route('/admin/<int:quiz_id>/deletequiz',methods=['GET','POST'])
def DeleteQuiz(quiz_id):
    if request.method=='GET':
        return render_template('deleteconfirm.html',quiz_id=quiz_id)
    elif request.method=='POST':
        if request.form.get('yes')=='c1':
            print("Data is going to be deleted")
            query_questions = Questions.query.filter_by(id=quiz_id).all()
            print(query_questions)
            choices=[]
            for i in query_questions:
                query_choices = Choices.query.filter_by(question_id=i.quiestion_id).first()
                choices.append(query_choices)
            print(choices)
            query_correct_choice=CorrectOptions.query.filter_by(quiz_id=quiz_id).all()
            #to delete correct choice
            print("to delete correct choice")
            for l in query_correct_choice:
                db.session.delete(l)
                db.session.commit()
                print(l)
            print('to delete choice')
            for k in choices:
                db.session.delete(k)
                db.session.commit()
                print(k)
            print('to delete questions')
            print(query_questions)
            for m in query_questions:
                db.session.delete(m)
                db.session.commit()
                print(m)

            delete_quiz=Quiz.query.filter_by(quiz_id=quiz_id).first()
            if delete_quiz:
                db.session.delete(delete_quiz)
                db.session.commit()
                print(delete_quiz)

            print("Came on delete")
            return redirect(url_for('Admin'))
        else:
            return redirect(url_for('Admin'))

@app.route('/admin/editquiz/<int:question_id>/deletequestion')
def DeleteQuestion(question_id):
    query = Choices.query.filter_by(question_id=question_id).first()
    if query:
        db.session.delete(query)
        db.session.commit()
    query2 = CorrectOptions.query.filter_by(question_id=question_id).first()
    quiz = query2.quiz_id
    if query2:
        db.session.delete(query2)
        db.session.commit()
    query3 = Questions.query.filter_by(quiestion_id=question_id).first()
    if query3:
        db.session.delete(query3)
        db.session.commit()
    # print(query)

    print("Delete Question")
    return redirect(url_for('EditQuiz',quiz_id=quiz))


if __name__=='__main__':
    #with app.app_context():
    #     db.create_all()

    #new quiz
    # new_quiz = Quiz(title="Fruit Quiz", description="Take this fruit quiz at Quizzy to test your knowledge of fruits.")
    # db.session.add(new_quiz)
    # db.session.commit()

    #new question
    # new_question = Questions(question_text="Growing up to 59 feet (18 meters) long, which is the world’s largest living fish?",id=1)
    # db.session.add(new_question)
    # db.session.commit()

    #new choice
    # new_choice = Choices(choice1='Jenny', choice2='Stacy', choice3='Isabella', choice4='Linda', question_id=7)
    # db.session.add(new_choice)
    # db.session.commit()
    # new_choice = Choices(choice1='Spinach',choice2='Bueberries',choice3='Cherries',choice4='Parsnips',question_id=8)
    # db.session.add(new_choice)
    # db.session.commit()

    #correctoption
    # correctoption = CorrectOptions(co_id=7,quiz_id=3,question_id=7,correct_option='c2')
    # db.session.add(correctoption)
    # db.session.commit()
    # correctoption = CorrectOptions(co_id=8, quiz_id=3, question_id=8, correct_option='c4')
    # db.session.add(correctoption)
    # db.session.commit()
    app.run()
