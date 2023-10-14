from flask import Flask, redirect, render_template, request, flash, session
from forms import SignUpForm, SignInForm, TaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
basedir=os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY']='Khang Python-Flask Web App'
# app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'app.db')
app.config['SQLALCHEMY_DATABASE_URI']='postgres://ryjfmzscusuqan:7b60b5c3c25e730459f1a24dbb554c06d98f78f5727ad8962d824a84111a39f8@ec2-44-213-228-107.compute-1.amazonaws.com:5432/d36ouh0vnvkc79'

app.config['SQLITECHEMY_TRACK_MODIFICATIONS']=False
app.app_context().push() 

db=SQLAlchemy(app)
migrate=Migrate(app,db)

import models
@app.route('/')

def main():
    todolist=[
        {
            'name': 'Buy milk',
            'description': 'Buy 2 liters of milk in Coompart.'
        },
        {
            'name': 'Get money',
            'description': 'Get 500k from ATM'
        }
    ]
    return render_template('index.html', todolist=todolist)

@app.route('/signUp', methods=['GET', 'POST'])
def showSignUp():
    form=SignUpForm()

    if form.validate_on_submit():
    # if request.method=='POST':
        print("Validate on submit")
        _fname=form.inputFirstName.data
        _lname=form.inputLastName.data
        _email=form.inputEmail.data
        _password=form.inputPassword.data
        # _name=request.form['inputName']
        # _email=request.form['inputEmail']
        # _password=request.form['inputPassword']

        # user={'fname':_fname,'lname':_lname, 'email':_email,'password':_password}
        if(db.session.query(models.User).filter_by(email=_email).count()==0):
            user=models.User(first_name=_fname,last_name=_lname, email=_email)
            user.set_password(_password)
            db.session.add(user)
            db.session.commit()
            return render_template('signUpSuccess.html', user=user)
        else:
            flash('Email {} is already exsits!'.format(_email))
            return render_template('signup.html',form=form)
    # return render_template('index.html')
    # return render_template('signup.html')
    print("Not validate on submit")
    return render_template('signup.html', form = form)

@app.route('/signIn',methods=['GET','POST'])
def signIn():
    form=SignInForm()
    if form.validate_on_submit():
        _email=form.inputEmail.data
        _password=form.inputPassword.data

        user=db.session.query(models.User).filter_by(email=_email).first()
        if(user is None):
            flash('Wrong email address or password!')
        else:
            if(user.check_password(_password)):
                session['user']=user.user_id
                # return render_template('userhome.html')
                return redirect('/userHome')
            else:
                flash('Wrong email address or password')
    return render_template('signin.html', form=form)


@app.route('/userHome',methods=['GET','POST'])
def userHome():
    _user_id=session.get('user')
    if _user_id:
        user=db.session.query(models.User).filter_by(user_id=_user_id).first()
        return render_template('userhome.html',user=user)
    else:
        return redirect('/')

@app.route('/logOut',methods=['GET','POST'])
def logOut():
    session.pop('user', None)
    return redirect('/userHome')

@app.route('/newTask',methods=['GET','POST'])
def newTask():
    a_user_id=session.get('user')
    form=TaskForm()
    form.inputPriority.choices=[(p.priority_id,p.text) for p in db.session.query(models.Priority).all()]
    if a_user_id:
        user=db.session.query(models.User).filter_by(user_id=a_user_id).first()
        
        if form.validate_on_submit():
            _description=form.inputDescription.data
            _priority_id=form.inputPriority.data
            priority=db.session.query(models.Priority).filter_by(priority_id=_priority_id).first()

            _task_id=request.form['hiddenTaskId']
            if (_task_id=="0"):
                task=models.Task(description=_description, user=user, priority=priority)
                db.session.add(task)
            else:
                task = db.session.query(models.Task).filter_by(task_id=_task_id).first()
                task.description=_description
                task.priority=priority

            db.session.commit()
            return redirect('/userHome')
        return render_template('/newTask.html', form=form, user=user)
    return redirect('/')

@app.route('/deleteTask', methods=['GET','POST'])
def deleteTask():
    _user_id=session.get('user')
    if _user_id:
        _task_id=request.form['hiddenTaskId']
        if _task_id:
            task=db.session.query(models.Task).filter_by(task_id=_task_id).first()
            db.session.delete(task)
            db.session.commit()
        return redirect('/userHome')
    return redirect('/')

@app.route('/editTask', methods=['GET', 'POST'])
def editTask():
    _user_id=session.get('user')
    form=TaskForm()
    form.inputPriority.choices=[(p.priority_id, p.text) for p in db.session.query(models.Priority).all()]
    if _user_id:
        user=db.session.query(models.User).filter_by(user_id=_user_id).first()
        _task_id=request.form['hiddenTaskId']
        if _task_id:
            task=db.session.query(models.Task).filter_by(task_id=_task_id).first()
            form.inputDescription.default=task.description
            form.inputPriority.default=task.priority_id
            form.process()
            return render_template('/newtask.html', form=form, user=user, task=task)
    return redirect('/')

@app.route('/doneTask', methods=['GET', 'POST'])
def doneTask():
    _user_id=session.get('user')
    if _user_id:
        _task_id=request.form['hiddenTaskId']
        if _task_id:
            task=db.session.query(models.Task).filter_by(task_id=_task_id).first()
            task.isCompleted=True
            db.session.commit()
        return redirect('/userHome')
    return redirect('/')
if __name__=='__main__':
    app.run(host='127.0.0.1', port='8080', debug=True)

