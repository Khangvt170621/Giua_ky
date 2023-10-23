from flask import Flask, redirect, render_template, request, flash, session
from forms import SignUpForm, SignInForm, TaskForm, ProjectForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
basedir=os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY']='Khang Python-Flask Web App'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'app.db')

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
    form.inputProject.choices=[(p.project_id, p.name) for p in db.session.query(models.Project).all()]
    form.inputPriority.choices=[(p.priority_id,p.text) for p in db.session.query(models.Priority).all()]
    form.inputStatus.choices=[(p.status_id, p.description) for p in db.session.query(models.Status).all()]
    if a_user_id:
        user=db.session.query(models.User).filter_by(user_id=a_user_id).first()
        if form.validate_on_submit():
            _description=form.inputDescription.data
            _priority_id=form.inputPriority.data
            _project_id=form.inputProject.data
            _deadline=form.inputDeadline.data
            _status_id=form.inputStatus.data
            priority=db.session.query(models.Priority).filter_by(priority_id=_priority_id).first()
            project=db.session.query(models.Project).filter_by(project_id=_project_id).first()
            status=db.session.query(models.Status).filter_by(status_id=_status_id).first()
            
            _task_id=request.form['hiddenTaskId']

            if project and _deadline > project.deadline:
                flash("Deadline of the task cannot be later than the project's deadline.", "error")
                return render_template('/newTask.html', form=form, user=user)

            if (_task_id=="0"):
                task=models.Task(description=_description, priority=priority, deadline=_deadline, project=project, status=status)
                db.session.add(task)
            else:
                task = db.session.query(models.Task).filter_by(task_id=_task_id).first()
                task.description=_description
                task.priority=priority
                task.deadline=_deadline
                task.project=project
                task.status=status

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
    forms=ProjectForm()
    form.inputProject.choices=[(p.project_id, p.name) for p in db.session.query(models.Project).all()]
    form.inputPriority.choices=[(p.priority_id, p.text) for p in db.session.query(models.Priority).all()]
    form.inputStatus.choices=[(p.status_id, p.description) for p in db.session.query(models.Status).all()]
    if _user_id:
        _task_id=request.form['hiddenTaskId']
        task=db.session.query(models.Task).filter_by(task_id=_task_id).first()
        
        if _task_id:
            form.inputDescription.default=task.description
            form.inputDeadline.default=task.deadline
            form.inputPriority.default=task.priority_id
            form.inputStatus.default=task.status_id
            form.inputProject.default=task.project_id
            forms.inputStatus.default=task.status_id
            form.process()
            forms.process()
        _project_id=task.project_id
        update_project_status_if_all_tasks_completed(_project_id)
        return render_template('/newtask.html', form=form, task=task, user=_user_id)
    return redirect('/')


def update_project_status_if_all_tasks_completed(project_id):
    project = db.session.query(models.Project).filter_by(project_id=project_id).first()
    tasks = db.session.query(models.Task).filter_by(project_id=project_id).all()
    
    # Kiểm tra xem tất cả tasks trong project đã hoàn thành hay chưa
    all_tasks_completed = all(task.status.description == 'Hoàn thành' for task in tasks)
    
    if all_tasks_completed:
        project.status_id = 4  # Cập nhật trạng thái project thành "Hoàn thành"
        db.session.commit()
    else:
        project.status_id = 2  # Cập nhật trạng thái project thành "Hoàn thành"
        db.session.commit()

@app.route('/newProject',methods=['GET','POST'])
def newProject():
    a_user_id=session.get('user')
    form=ProjectForm()
    form.inputStatus.choices=[(s.status_id,s.description) for s in db.session.query(models.Status).all()]
    if a_user_id:
        user=db.session.query(models.User).filter_by(user_id=a_user_id).first()
        
        if form.validate_on_submit():
            _name=form.inputName.data
            _description=form.inputDescription.data
            _deadline=form.inputDeadline.data
            _status_id=form.inputStatus.data
            status=db.session.query(models.Status).filter_by(status_id=_status_id).first()

            _project_id=request.form['hiddenProjectId']
            if (_project_id=="0"):
                project=models.Project(name=_name, description=_description,deadline=_deadline, user=user, status=status)
                db.session.add(project)
            else:
                project = db.session.query(models.Project).filter_by(project_id=_project_id).first()
                project.name=_name
                project.description=_description
                project.deadline=_deadline
                project.status=status

            db.session.commit()
            return redirect('/userHome')
        return render_template('/newProject.html', form=form, user=user)
    return redirect('/')

@app.route('/deleteProject', methods=['GET','POST'])
def deleteProject():
    _user_id=session.get('user')
    if _user_id:
        _project_id=request.form['hiddenProjectId']
        if _project_id:
            project=db.session.query(models.Project).filter_by(project_id=_project_id).first()
            db.session.delete(project)
            db.session.commit()
        return redirect('/userHome')
    return redirect('/')

@app.route('/editProject', methods=['GET', 'POST'])
def editProject():
    _user_id=session.get('user')
    form=ProjectForm()
    form.inputStatus.choices=[(p.status_id, p.description) for p in db.session.query(models.Status).all()]
    if _user_id:
        _project_id=request.form['hiddenProjectId']
        if _project_id:
            project=db.session.query(models.Project).filter_by(project_id=_project_id).first()
            form.inputName.default=project.name
            form.inputDescription.default=project.description
            form.inputDeadline.default=project.deadline
            form.inputStatus.default=project.status_id
            form.process()
            return render_template('/newProject.html', form=form, project=project, user=_user_id)
    return redirect('/')

@app.route('/search', methods=['GET', 'POST'])
def search():
    _user_id=session.get('user')
    search_query = request.args.get('search_query')  # Lấy giá trị tìm kiếm từ tham số GET
    status = request.args.get('status')  # Lấy giá trị trạng thái từ tham số GET

    if search_query:
        # Tìm kiếm theo tên và trạng thái được chọn
        if status:
            if status == '1':
                projects = db.session.query(models.Project).filter(
                    (models.Project.name.ilike(f"%{search_query}%")) & (models.Project.status_id == 1)
                ).all()
                tasks = db.session.query(models.Task).filter(
                    (models.Task.description.ilike(f"%{search_query}%")) & (models.Task.status_id == 1)
                ).all()
            elif status == '2':
                projects = db.session.query(models.Project).filter(
                    (models.Project.name.ilike(f"%{search_query}%")) & (models.Project.status_id == 2)
                ).all()
                tasks = db.session.query(models.Task).filter(
                    (models.Task.description.ilike(f"%{search_query}%")) & (models.Task.status_id == 2)
                ).all()
            elif status == '3':
                projects = db.session.query(models.Project).filter(
                    (models.Project.name.ilike(f"%{search_query}%")) & (models.Project.status_id == 3)
                ).all()
                tasks = db.session.query(models.Task).filter(
                    (models.Task.description.ilike(f"%{search_query}%")) & (models.Task.status_id == 3)
                ).all()
            elif status == '4':
                projects = db.session.query(models.Project).filter(
                    (models.Project.name.ilike(f"%{search_query}%")) & (models.Project.status_id == 4)
                ).all()
                tasks = db.session.query(models.Task).filter(
                    (models.Task.description.ilike(f"%{search_query}%")) & (models.Task.status_id == 4)
                ).all()
        else:
            # Nếu không chọn trạng thái cụ thể, chỉ tìm kiếm theo tên
            projects = db.session.query(models.Project).filter(models.Project.name.ilike(f"%{search_query}%")).all()
            tasks = db.session.query(models.Task).filter(models.Task.description.ilike(f"%{search_query}%")).all()
    else:
        # Nếu không có tìm kiếm tên, thực hiện tìm kiếm dựa trên trạng thái
        if status:
            if status == '1':
                projects = db.session.query(models.Project).filter_by(status_id=1).all()
                tasks = db.session.query(models.Task).filter_by(status_id=1).all()
            elif status == '2':
                projects = db.session.query(models.Project).filter_by(status_id=2).all()
                tasks = db.session.query(models.Task).filter_by(status_id=2).all()
            elif status == '3':
                projects = db.session.query(models.Project).filter_by(status_id=3).all()
                tasks = db.session.query(models.Task).filter_by(status_id=3).all()
            elif status == '4':
                projects = db.session.query(models.Project).filter_by(status_id=4).all()
                tasks = db.session.query(models.Task).filter_by(status_id=4).all()
        else:
            # Nếu không chọn tìm kiếm tên và trạng thái cụ thể, hiển thị tất cả các dự án và công việc
            projects = db.session.query(models.Project).all()
            tasks = db.session.query(models.Task).all()

    return render_template('search_results.html', projects=projects, tasks=tasks, user=_user_id)


if __name__=='__main__':
    app.run(host='127.0.0.1', port='8080', debug=True)

