from flask import Flask, render_template

app = Flask(__name__)
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
if __name__=='__main__':
    app.run(host='127.0.0.1', port='8080', debug=True)