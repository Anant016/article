from flask import Flask, render_template,flash,redirect,session,logging,url_for,request
#from flask.ext.session import Session

SESSION_TYPE = 'memcache'

#from data import Articles

from wtforms import Form,StringField,PasswordField, TextAreaField,validators
from passlib.hash import sha256_crypt

from functools import wraps

import pymysql as MySQLdb

import pymysql as MySQLdb
import pymysql.cursors

app=Flask(__name__)


#config MySQL
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='Happy@1711',
                             db='py_articles',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


# Open database connection
#db = MySQLdb.connect("localhost","root","root","test" )

# prepare a cursor object using cursor() method
#cursor = db.cursor()

# execute SQL query using execute() method.
#cursor.execute("show tables")

# Fetch a single row using fetchone() method.
#data = cursor.fetchall()
#print (data)

# disconnect from server
#db.close()

#################################################



#Articles= Articles()

@app.route('/')
def index():
   #return 'INDEX3'
    return render_template('home.html');

@app.route('/about')
def about():
    return render_template('about.html');

@app.route('/articles')
def articles():
    with connection.cursor() as cursor:
        # Read a single record
        result = cursor.execute("SELECT * FROM articles")
        articles=cursor.fetchall()
        if(result>0):
            return render_template('articles.html',articles=articles)
        else:
            msg='No Articles Found';
            return render_template('articles.html',msg=msg)
        cursor.close();

@app.route('/article/<string:id>/')
def article(id):
    with connection.cursor() as cursor:
        # Read a single record
        result = cursor.execute("SELECT * FROM articles WHERE id=%s",[id])
        article=cursor.fetchone()
        return render_template('article.html',article=article)
        cursor.close();
    return render_template('article.html',id=id,article=Articles);

class RegisterForm(Form):
    name= StringField('Name',[validators.Length(min=1,max=50)]);
    username= StringField('Username',[validators.Length(min=4,max=25)]);
    email= StringField('Email',[validators.Length(min=6,max=50)]);
    password= PasswordField('password',[validators.DataRequired(),
     validators.EqualTo('confirm',message="password do not match")]);
    confirm=PasswordField('ConfirmPassword');

    ###################################################
@app.route('/register',methods=['GET','POST'])
def register():
    form=RegisterForm(request.form)
    if (request.method =='POST' and form.validate()):
        name=form.name.data
        email=form.email.data
        username=form.username.data
        password=sha256_crypt.encrypt(str(form.password.data))
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO users (name,email,username, password) VALUES (%s, %s,%s,%s)"
                cursor.execute(sql,(name,email,username,password))
                connection.commit()


        finally:
            cursor.close()
            flash('You are now registered.','success');
            return redirect(url_for('login'))
        #create Cursor
        return render_template('register.html', form=form);
    return render_template('register.html', form=form)

#################################################################

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        #get Form Fields
        username=request.form['username']
        password_c=request.form['password']

        with connection.cursor() as cursor:
            # Read a single record
            result = cursor.execute("SELECT * FROM users WHERE username = %s", [username])

            if(result>0):
                data = cursor.fetchone()
                password=data['password']

                if(sha256_crypt.verify(password_c,password)):
                    #passed
                    session['logged_in']=True
                    session['username']=username
                    flash ('you are now logged in','success')
                    return redirect(url_for('dashboard'))
                else:
                    error='Invalid Login';
                    return render_template('login.html',error=error)
                cursor.close();
            else:
                error="Username not found";
                return render_template('login.html',error=error)
    return render_template('login.html');

def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if('logged_in' in session):
             return f(*args,**kwargs)
        else:
            flash('Unauthorized.','danger')
            return redirect(url_for('login'));
    return wrap



@app.route('/dashboard')
@is_logged_in
def dashboard():
    with connection.cursor() as cursor:
        # Read a single record
        result = cursor.execute("SELECT * FROM articles")
        articles=cursor.fetchall()
        if(result>0):
            return render_template('dashboard.html',articles=articles)
        else:
            msg='No Articles Found';
            return render_template('dashboard.html',msg=msg)
        cursor.close();



@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are logged out.','success')
    return redirect(url_for('login'));

class ArticleForm(Form):
    title= StringField('Title',[validators.Length(min=1,max=200)]);
    body= TextAreaField('Body',[validators.Length(min=30)]);

@app.route('/add_article',methods=['GET','POST'])
@is_logged_in
def add_article():
    form=ArticleForm(request.form)
    if(request.method=='POST' and form.validate()):
        title=form.title.data
        body=form.body.data
        try:
            with connection.cursor() as cursor:
                sql="INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)"
                cursor.execute(sql,(title,body,session['username']))
                connection.commit()
        finally:
            cursor.close()
            flash('Article Created Successfully','success')
        return redirect(url_for('dashboard'));


    return render_template('add_article.html',form=form);


@app.route('/edit_article/<string:id>',methods=['GET','POST'])
@is_logged_in
def edit_article(id):
    with connection.cursor() as cursor:
        # Read a single record
        result = cursor.execute("SELECT * FROM articles WHERE id=%s",[id])
        article=cursor.fetchone()
        form=ArticleForm(request.form)
        form.title.data=article['title']
        form.body.data=article['body']

        if(request.method=='POST' and form.validate()):
            title=request.form['title']
            body=request.form['body']
            try:
                with connection.cursor() as cursor:
                    sql="UPDATE articles SET title=%s, body=%s WHERE id=%s"
                    cursor.execute(sql,(title,body,id))
                    connection.commit()
            finally:
                    cursor.close()
                    flash('Article Updated','success')
            return redirect(url_for('dashboard'));
        return render_template('edit_article.html',form=form);


@app.route('/delete_article/<string:id>',methods=['POST'])
@is_logged_in
def delete_article(id):
    with connection.cursor() as cursor:

        cursor.execute("DELETE FROM articles WHERE id=%s",[id]);
        connection.commit();
        cursor.close();

    flash("Article Deleted Successfuly.",'success');
    return redirect(url_for('dashboard'));


if(__name__)=='__main__':
    app.secret_key='anu-secret'
    app.config['SESSION_TYPE'] = 'filesystem'

    #sess.init_app(app)
    app.run(debug=True)






    #def login():
    #if request.method=='POST':
    #    #get Form Fields
    #    username=request.form['username']
    #   password_c=request.form['password']

    #    with connection.cursor() as cursor:
     #       # Read a single record
      #      result = cursor.execute("SELECT * FROM users WHERE username = %s", [username])
#
 #           if(result>0):
  ##             password=data['password']
#
 #               if(sha256_crypt.verify(password_c,password)):
  #                  #passed
   #                 session['logged_in']=True
    #                session['username']=username
     #               flash ('you are now logged in','success')
      #              return redirect(url_for('dashboard'))
        #        else:
       #             error='Invalid Login';
         #           return render_template('login.html',error=error)
           #     cursor.clode();
          #  else:
            #    error="Username not found";
             #   return render_template('login.html',error=error)
#    return render_template('login.html');
