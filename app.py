from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import sqlite3
import flask
from flask import Flask, render_template, request, url_for, flash, redirect, abort

# ...

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
def get_ingridient(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM Ingridient WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post
def get_recipe(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM recipe WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post
def get_recipe_name(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT name FROM recipe WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

@app.route('/', methods=('GET', 'POST'))
def index():
    conn = get_db_connection()
    hist = conn.execute("SELECT * FROM History ").fetchall()
    conn.close()
    if request.method=='GET':
        return render_template('index.html', hist=hist)
    if request.method == 'POST':
        return render_template('index.html', hist=hist)
@app.route('/all_recipe', methods=('GET', 'POST'))
def all_recipe():
    conn = get_db_connection()
    all_recipe = conn.execute("SELECT * FROM recipe ").fetchall()

    conn.close()
    if request.method == 'GET':
        return render_template('all_recipe.html', all_recipe=all_recipe)

    if request.method == 'POST':
        return render_template('all_recipe.html', all_recipe=all_recipe)

@app.route('/all_ingridient', methods=('GET', 'POST'))
def all_ingridient():
    conn = get_db_connection()
    all_ingridient = conn.execute("SELECT * FROM Ingridient  ").fetchall()

    conn.close()
    if request.method=='GET':
        return render_template('all_ingridient.html', all_ingridient=all_ingridient)

    if request.method == 'POST':

        return render_template('index.html',all_ingridient=all_ingridient)
@app.route('/create_ingridient/', methods=('GET', 'POST'))
def create_ingridient():
    if request.method=='GET':
        return render_template('create.html')
    if request.method == 'POST':
        name = request.form['name']
        cost = request.form['cost']
        weight=request.form['weight']
        koef=request.form['koef']
        if not name:
            flash('Name is required!')
        elif not cost:
            flash('Cost is required!')
        elif not weight:
            flash('Weight is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO Ingridient (name, cost,weight,koef) VALUES (?, ?,?,?)',
                         (name, cost,weight,koef))
            conn.commit()
            conn.close()
            return redirect(url_for('all_ingridient'))
@app.route('/create_recipe/', methods=('GET', 'POST'))
def create_recipe():
    if request.method=='GET':
        conn = get_db_connection()
        all_ingridient = conn.execute("SELECT * FROM Ingridient  ").fetchall()
        conn.close()
        return render_template('create_recipe.html', all_ingridient=all_ingridient)
    if request.method == 'POST':
        name = request.form['name_recipe']
        ingridients_words= request.form['ingridients']
        ingridients= ingridients_words.split(',')
        ingridients_len=len(ingridients_words)
        if not name:
            flash('Name is required!')
        elif not ingridients:
            flash('ingridients is required!')

        else:
            conn = get_db_connection()

            conn.execute('INSERT INTO recipe (name,ingridients) VALUES (?, ?)',
                         (name,ingridients_words))
            conn.execute(f'DROP TABLE IF EXISTS {name}')
            conn.execute(f'  CREATE TABLE {name}(id INTEGER PRIMARY KEY AUTOINCREMENT,ingridient TEXT NOT NULL,FOREIGN KEY (ingridient) REFERENCES Ingridient(name) ON DELETE RESTRICT)')
            for ingridient  in ingridients :
                conn.execute(f'INSERT INTO {name} (ingridient) VALUES(?)',(ingridient,))
            conn.commit()
            conn.close()
            return redirect(url_for('all_recipe'))

@app.route('/<int:id>/edit_recipe/', methods=('GET', 'POST'))
def edit_recipe(id):
    recipe = get_recipe(id)

    if request.method == 'POST':
        name = request.form['name_recipe']
        ingridients_words= request.form['ingridients']
        ingridients= ingridients_words.split(',')
        ingridients_len=len(ingridients_words)
        if not name:
            flash('Name is required!')
        elif not ingridients:
            flash('ingridients is required!')

        else:
            conn = get_db_connection()
            conn.execute('UPDATE recipe  SET name=?, ingridients=?'
                         ' WHERE id = ?',
                         (name, ingridients_words, id))

            #conn.execute(f'DROP TABLE IF EXISTS {name}')
            #conn.execute(f'  CREATE TABLE {name}(id INTEGER PRIMARY KEY AUTOINCREMENT,ingridient TEXT NOT NULL,FOREIGN KEY (ingridient) REFERENCES Ingridient(name) ON DELETE RESTRICT)')
            conn.execute(f'DROP TABLE IF EXISTS {name}')
            conn.execute(f'  CREATE TABLE {name}(id INTEGER PRIMARY KEY AUTOINCREMENT,ingridient TEXT NOT NULL,FOREIGN KEY (ingridient) REFERENCES Ingridient(name) ON DELETE RESTRICT)')
            for ingridient  in ingridients :
                conn.execute(f'INSERT INTO {name} (ingridient) VALUES(?)',(ingridient,))
            conn.commit()
            conn.close()
            return redirect(url_for('all_recipe'))
    return render_template('edit_recipe.html',recipe=recipe)
@app.route('/<int:id>/delete_recipe/', methods=('POST',))
def delete_recipe(id):
    recipe = get_recipe(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM recipe WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(recipe['name']))
    return redirect(url_for('all_recipe'))

@app.route('/<int:id>/edit_ingridient/', methods=('GET', 'POST'))
def edit_ingridient(id):
    ingridient = get_ingridient(id)


    if request.method == 'POST':
        name = request.form['name']
        cost = request.form['cost']
        weight=request.form['weight']
        koef=request.form['koef']
        if not name:
            flash('Name is required!')
        elif not cost:
            flash('Cost is required!')
        elif not weight:
            flash('Weight is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE Ingridient  SET name=?, cost=?,weight=?,koef=?'
                         ' WHERE id = ?',
                         (name,cost,weight,koef, id))
            conn.commit()
            conn.close()
            return redirect(url_for('all_ingridient'))
    return render_template('edit_ingridient.html',ingridient=ingridient )

@app.route('/<int:id>/delete_ingridient/', methods=('POST', ))
def delete_ingridient(id):
    ingridient = get_ingridient(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM Ingridient WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(ingridient['name']))
    return redirect(url_for('all_ingridient'))

@app.route('/<int:id>/calculation/', methods=('POST','GET'))
def calculation(id):
    #name=get_recipe_name(id)
    conn = get_db_connection()
    for row in conn.execute('SELECT name FROM recipe WHERE id=?',(id,)).fetchall():
        name=row[0]
    #recipe = conn.execute(f"SELECT * FROM {name} ").fetchall()
    recipe=conn.execute(f"SELECT {name}.ingridient, Ingridient.cost,Ingridient.weight,Ingridient.koef FROM {name} JOIN Ingridient ON Ingridient.name={name}.ingridient ").fetchall()
    koef=conn.execute(f"SELECT Ingridient.koef FROM Ingridient JOIN {name} on Ingridient.name={name}.ingridient ").fetchall()
    conn.close()

    if request.method == 'POST':
        results_list=request.form.getlist('res')
        conn = get_db_connection()
        koefs= conn.execute(f"SELECT Ingridient.koef FROM Ingridient JOIN {name} on Ingridient.name={name}.ingridient").fetchall()
        koef_list=[koef[0] for koef in koefs]
        koef=[float(item) for item in koef_list]
        result=[float(item) for item in results_list]
        res=[]

        for dt1,dt2 in zip (koef,result):
            res.append(dt1*dt2)

        general_res=sum(res)
        conn.execute('INSERT INTO History (recipe, result ) VALUES (?,?)',
                     (name,general_res))
        conn.commit()
        conn.close()

        return render_template('calculate.html',result=results_list  ,recipe=recipe, name=name,koef=koef_list,res=res, general_res=general_res)

    return render_template('calculate.html', recipe=recipe, name=name)

if __name__ == '__main__':
    app.run(debug=True)

 #for row in conn.execute("SElECT koef FROM Ingridient pages WHERE name=='butter'").fetchall():
 #       koef_butter = row[0]