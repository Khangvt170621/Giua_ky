from flask import Flask

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
    return '''
    <html>
        <head>
            <title>To do list app</title>
        </head>
        <body>
            <div>
                <h1>To do list app</h1>
                <p>
                    <a href="#">Sign up now</a> 
                </p>
            </div>
            <div>
                <h4>''' + todolist[0]['name'] +'''</h4>
                <h4>''' + todolist[0]['description'] +'''</h4>
                <h4>''' + todolist[1]['name'] +'''</h4>
                <h4>''' + todolist[1]['description'] +'''</h4>
            </div>
        </body>
    </html>
    '''
if __name__=='__main__':
    app.run(host='127.0.0.1', port='8080', debug=True)