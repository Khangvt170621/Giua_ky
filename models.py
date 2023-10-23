from tpl import db
from sqlalchemy import ForeignKey, Sequence
from werkzeug.security import check_password_hash,generate_password_hash

class User(db.Model):
    user_id=db.Column(db.Integer, Sequence('user_id_seq'),primary_key=True)
    first_name=db.Column(db.String(64), index=True,nullable=False)
    last_name=db.Column(db.String(64), index=True,nullable=False)
    email=db.Column(db.String(120), index=True,unique=True,nullable=False)
    password_hash=db.Column(db.String(128),nullable=False)

    projects = db.relationship('Project', back_populates='user')

    def __repr__(self):
        return '<User full name:{} {},email:{}>'.format(self.first_name,self.last_name,self.email)

    def set_password(self,password):
        self.password_hash=generate_password_hash(password)
        return

    def check_password(self, password):
        return check_password_hash(self.password_hash,password)
    
class Project(db.Model):
    project_id=db.Column(db.Integer, Sequence('priority_id_seq'), primary_key=True)
    description=db.Column(db.String(255), nullable=False)
    name=db.Column(db.String(255), nullable=False)
    deadline=db.Column(db.DateTime, nullable=False)

    user_id=db.Column(db.Integer, ForeignKey('user.user_id'))
    user=db.relationship('User', back_populates='projects')
    
    status_id=db.Column(db.Integer, ForeignKey('status.status_id'))
    status=db.relationship('Status', back_populates='project')

    tasks=db.relationship('Task', back_populates='project')

    def __repr__(self):
        return '{}'.format(self.name)
    
    def getStatusClasss(self):
        if(self.status_id==1):
            return "table-danger"
        elif(self.status_id==2):
            return "table-warning"
        elif(self.status_id==3):
            return "table-info"
        else:
            return "table-primary"

class Task(db.Model):
    task_id=db.Column(db.Integer, Sequence('task_id_seq'), primary_key=True)
    description=db.Column(db.String(255), nullable=False)
    deadline=db.Column(db.DateTime, nullable=False)

    priority_id=db.Column(db.Integer, ForeignKey('priority.priority_id'))
    priority=db.relationship('Priority',back_populates="tasks")

    status_id=db.Column(db.Integer, ForeignKey('status.status_id'))
    status=db.relationship('Status',back_populates="tasks")

    project_id=db.Column(db.Integer, ForeignKey('project.project_id'))
    project=db.relationship('Project',back_populates="tasks")

    def __repr__(self):
        return '<Task: {} of user {}>'.format(self.description, self.user_id)
    
    def getPriorityClasss(self):
        if(self.priority_id==1):
            return "table-danger"
        elif(self.priority_id==2):
            return "table-warning"
        elif(self.priority_id==3):
            return "table-info"
        else:
            return "table-primary"

class Priority(db.Model):
    priority_id=db.Column(db.Integer, Sequence('priority_id_seq'), primary_key=True)
    text=db.Column(db.String(50), nullable=False)

    tasks=db.relationship('Task', back_populates='priority')

    def __repr__(self):
        return '<Priority: {} with {}>'.format(self.priority_id, self.text)
    
class Status(db.Model):
    status_id=db.Column(db.Integer, Sequence('priority_id_seq'), primary_key=True)
    description=db.Column(db.String(255), nullable=False)

    tasks=db.relationship('Task', back_populates='status')
    
    project=db.relationship('Project', back_populates='status')

    def __repr__(self):
        return '{}'.format(self.description)
    
    
    


