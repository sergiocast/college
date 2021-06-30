import mysql.connector
from flask import Flask, render_template, request
import json



app = Flask(__name__)

@app.route("/")
def index():
    return render_template(“home.html")


config = {

     'user': 'root',
     'password': 'sergiocas',
     'host': 'localhost',
     'database': 'college'

}

db = mysql.connector.connect(**config)
cursor = db.cursor()


#homepage login button
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST': 
        username= request.form['username']
        


        #finds privelege of username. admin, teacher, student
        cursor.execute("SELECT privelege FROM users WHERE username ='%s'" % (username))
        privelege = cursor.fetchone()
        #gets all users
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        ###users = json.dumps(users1)
        #gets all students
        cursor.execute("SELECT * FROM users WHERE privelege = 'student'")
        students = cursor.fetchall()
        #get all from students table to get everyones attendance status from every date
        cursor.execute("SELECT * FROM students")
        attendance = cursor.fetchall()
        #get all attendance record of student based on username
        cursor.execute("SELECT * FROM students WHERE username ='%s'" % (username))
        record = cursor.fetchall()
        #checks which privelege it is. admin,teacher, student and returns that page
        if privelege != None:
            if privelege[0] == "admin":
                return render_template('admin.html', users=users, length= len(users))
            elif privelege[0] == "teacher":
                return render_template('teacher.html', students=students, length= len(students), attendance =attendance, length2=len(attendance))
            elif privelege[0] == "student":
                return render_template('student.html', record=record, length= len(record))
            else:
                return render_template('home.html', found="false")
        else:
            return render_template('home.html', found ="false")
      
             

#adduser function inserts to database
def add_user(firstname,lastname, username, password, privelege):
    sql = ("INSERT INTO users(first_name, last_name, username, password, privelege) VALUES (%s, %s, %s, %s, %s)")
    cursor.execute(sql, (firstname,lastname, username, password, privelege,))
    db.commit()



#adduser button
@app.route('/add', methods=['POST'])
def adduser():
    #gets all user info
    if request.method == 'POST':
        firstname= request.form['first']
        lastname= request.form['last']
        username= request.form['username']
        password= request.form['password']
        privelege= request.form['privelege']
    #if EVERYTHING is filled out, calls the function to add user to database   
    if firstname !="" and lastname !="" and username !="" and password !="" and privelege !="":  
        add_user(firstname,lastname, username, password, privelege)
    #gets all users again
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    #if EVERYTHING is filled out, then a success message will be printed
    if firstname !="" and lastname !="" and username !="" and password !="" and privelege !="":
        return render_template('admin.html', users=users, length= len(users), enter ="success")
    #if not, a fail message will be printed
    else:
        return render_template('admin.html', users=users, length= len(users), enter ="fail")

       

@app.route('/save', methods=['POST'])
def attendance():

    cursor.execute("SELECT * FROM users WHERE privelege = 'student'")
    students = cursor.fetchall()

    #while loop is used to check if ALL STATUS field attributes are filled by the user with present or absent
    x=0
    while x <len(students):
        status= request.form['status'+ str(x)]
        if status == "present" or status =="absent" or status == "Present" or status =="Absent":
        #if status == "present" or "absent":
            filled = "true"
        else:
            filled ="false"
            break
        x +=1

    
    #while loop to insert the values in mysql because it only recognized the first row name attributes
    #so had to add str(i) to each attribute which will go from 0 to the amount of students
    #and each attribute here is congruent with each attribute in the script tag
    
    if filled == "true":
        i=0
        while i <len(students):
       #str converts i to string to concatenate it  
            if request.method == 'POST':
                firstname= request.form['first'+str(i)]
                lastname= request.form['last'+ str(i)]
                date= request.form['date'+ str(i)]
                status= request.form['status'+ str(i)]
                username = request.form['username'+ str(i)]
               
        
            sql = ("INSERT INTO students(firstname, lastname, date, status, username) VALUES (%s, %s, %s, %s, %s)")
            cursor.execute(sql, (firstname,lastname, date, status, username,))
            db.commit()
        
            i +=1

    #now EACH row in the table will get added to the database
    
    #this will delete duplicate entries so the user cant mark a student attendance twice for the same day
    cursor.execute("DELETE t1 FROM students t1 INNER JOIN students t2 WHERE t1.id < t2.id AND t1.firstname = t2.firstname AND t1.date = t2.date;")
    db.commit()
    
    #get all from students table to use attendance for rendering the page and not get error when save button clicked
    cursor.execute("SELECT * FROM students")
    attendance = cursor.fetchall()

    #if all STATUS attributes were filled then the variable filled will be true
    if filled == "true":
        return render_template('teacher.html', students=students, length= len(students), filled = "true", attendance =attendance, length2=len(attendance))
    else:
        return render_template('teacher.html', students=students, length= len(students), filled = "false", attendance =attendance, length2=len(attendance))

    







   
@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        return render_template('home.html')





         
               




if(__name__) == '__main__':
    app.debug = True
    app.run()
