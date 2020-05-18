from flask import Flask, render_template, url_for, request, session, redirect
import cx_Oracle
import datetime

conn = cx_Oracle.connect('stu002/Password@144.214.177.102/xe')

cur = conn.cursor()

app = Flask(__name__)
app.secret_key = 'abc'


@app.route("/index")
@app.route("/")
def index():
    if 'id' in session:
        return redirect(url_for('account'))
    if 'teacher' in session:
        return redirect(url_for('timetable'))
    error = None
    return render_template('home.html', error=error)


# ________________Home Page(Not Log In yet)__________________________________________
@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')


@app.route('/instrument')
def instrument():
    return render_template('instrument.html')


@app.route('/success', methods=['POST', 'GET'])
def success():
    error = None
    if request.method == 'POST':
        name = request.form["UserName"]
        email = request.form["email"]
        address = request.form["address"]
        gender = request.form["gender"]
        phone = int(request.form["phone"])
        pwd = request.form['pwd']

        cur.execute("INSERT INTO STUDENT (STUDENTID, STUDENTNAME, GENDER, PHONE, EMAIL, ADDRESS, PASSWORD) VALUES ("
                    "user_sequence.nextval, '%s','%s', '%d', '%s', '%s', '%s') " % (
                        name, gender, phone, email, address, pwd))

        cur.execute('commit')

        cur.execute("SELECT STUDENTID, STUDENTNAME FROM Student WHERE email= '%s'" % email)
        result = cur.fetchone()
        cur.execute('commit')
        ID = result[0]

        return render_template('success.html', accountid=ID, Name=name, Gender=gender,
                               Email=email, Phone=phone, Address=address, error=error)


# __________________Student log in page___________________________________________________________
@app.route('/account', methods=['POST', 'GET'])
def account():
    if request.method == 'POST':
        session.pop = ('id', None)
        UserID = request.form["UserID"]
        pwd = request.form['pwd']

        cur.execute("SELECT STUDENTID, STUDENTNAME, PASSWORD FROM Student WHERE StudentID= %s" % UserID)

        result = cur.fetchone()
        cur.execute('commit')
        if result is None:
            error = "Do not have this user"
            return render_template('home.html', error=error)
        password = result[2]

        if pwd == password:
            session['id'] = UserID

            cur.execute("SELECT a.course_name, a.courseid FROM Course a, CourseStudent b WHERE "
                        "a.courseid=b.courseid and b.StudentID= %s" % (session['id']))

            course_list = cur.fetchall()
            cur.execute('commit')
            No = len(course_list)

            cur.execute('commit')
            cur.execute("select a.levelid, a.coursetime,a.arrivaltime, b.course_name, c.levelname, a.leaveid, a.classid"
                        " from studentattent a,"
                        "course b, course_level c where a.courseid=b.courseid and a.levelid=c.levelid and "
                        "a.studentid='%s' and a.coursetime>TRUNC(SYSDATE-28) and a.coursetime<TRUNC(SYSDATE+28)"
                        " ORDER BY a.coursetime" % (session['id']))
            attend = cur.fetchall()
            cur.execute('commit')
            attend_no = len(attend)
            course_time = []
            course_date = []
            for i in range(attend_no):
                time = attend[i][1].strftime("%H:%M")
                date = attend[i][1].strftime("%Y-%m-%d")
                course_time.append(time)
                course_date.append(date)

            record_attend = '2020-01-31 00:00:00'
            record_attend = datetime.datetime.strptime(record_attend, '%Y-%m-%d %H:%M:%S')

            return render_template('account.html', result=result, course_list=course_list, No=No,
                                   attend=attend, attend_no=attend_no, course_time=course_time,
                                   course_date=course_date, record_attend=record_attend)
        error = "Invalid user id or password"
        return render_template('home.html', error=error)

    elif 'id' in session:
        cur.execute("SELECT STUDENTID, STUDENTNAME, GENDER, PHONE, EMAIL, ADDRESS, PASSWORD FROM Student WHERE "
                    "StudentID= %s" % (session['id']))
        result = cur.fetchone()
        cur.execute('commit')

        cur.execute("SELECT a.course_name, a.courseid FROM Course a, CourseStudent b WHERE "
                    "a.courseid=b.courseid and b.StudentID= %s" % (session['id']))

        course_list = cur.fetchall()
        cur.execute('commit')
        No = len(course_list)

        cur.execute("select a.levelid, a.coursetime,a.arrivaltime, b.course_name, c.levelname, a.leaveid, a.classid"
                    " from studentattent a,"
                    "course b, course_level c where a.courseid=b.courseid and a.levelid=c.levelid and "
                    "a.studentid='%s' and a.coursetime>TRUNC(SYSDATE-28) and a.coursetime<TRUNC(SYSDATE+28)"
                    " ORDER BY a.coursetime" % (session['id']))
        attend = cur.fetchall()
        cur.execute('commit')
        attend_no = len(attend)
        course_time = []
        course_date = []
        for i in range(attend_no):
            time = attend[i][1].strftime("%H:%M")
            date = attend[i][1].strftime("%Y-%m-%d")
            course_time.append(time)
            course_date.append(date)

        record_attend = '2020-01-31 00:00:00'
        record_attend = datetime.datetime.strptime(record_attend, '%Y-%m-%d %H:%M:%S')

        return render_template('account.html', result=result, course_list=course_list, No=No,
                               attend=attend, attend_no=attend_no, course_time=course_time,
                               course_date=course_date, record_attend=record_attend)
    else:
        return render_template('home.html')


@app.route('/my_lesson', methods=['POST', 'GET'])
def my_lesson():
    if 'id' in session:
        course_id = int(request.form["course_id"])
        cur.execute("SELECT a.course_name, a.courseid, b.timestart, b.timefinish, b.Weekday, c.gender, c.staffname, "
                    "b.levelid FROM Course a, CourseStudent b, staff c WHERE a.courseid=b.courseid and "
                    "b.teacherid=c.staffid and b.StudentID= '%s' and a.courseid='%s'" % (session['id'], course_id))
        course_list = cur.fetchone()
        cur.execute('commit')

        start = course_list[2].strftime("%H:%M")
        end = course_list[3].strftime("%H:%M")
        cur.execute("SELECT levelname from course_level where levelid='%s'" % course_list[7])
        level = cur.fetchone()
        cur.execute('commit')
        return render_template('my_lesson.html', course_list=course_list, start=start, end=end,
                               level=level)
    else:
        return render_template('home.html')


@app.route('/changed', methods=['POST', 'GET'])
def changed():
    if 'id' in session:
        name = request.form["UserName"]
        email = request.form["email"]
        address = request.form["address"]
        phone = int(request.form["phone"])
        pwd = request.form['pwd']

        cur.execute("Update STUDENT Set STUDENTNAME ='%s' , PHONE='%d',"
                    " EMAIL='%s', ADDRESS='%s', PASSWORD='%s'"
                    "Where StudentID= %s" % (
                        name, phone, email, address, pwd, session['id']))
        cur.execute('commit')

        return redirect(url_for('member'))


# ___________________Student account information__________________________________________________
@app.route('/member')
def member():
    if 'id' in session:
        cur.execute("SELECT STUDENTID, STUDENTNAME, GENDER, PHONE, EMAIL, ADDRESS, PASSWORD FROM Student WHERE "
                    "StudentID= %s" % (session['id']))

        result = cur.fetchone()
        cur.execute('commit')

        return render_template('member.html', result=result)
    return render_template('home.html')


@app.route('/logout')
def logout():
    session.pop('id', None)
    return redirect(url_for('index'))


@app.route('/changeaccount')
def changeaccount():
    if 'id' in session:
        cur.execute("SELECT STUDENTID, STUDENTNAME, GENDER, PHONE, EMAIL, ADDRESS, PASSWORD FROM Student WHERE "
                    "StudentID= %s" % (session['id']))

        result = cur.fetchone()
        cur.execute('commit')
        return render_template('changeaccount.html', result=result)
    return render_template('home.html')


# ________________________Student record________________________________
@app.route('/record')
def record():
    return render_template('record.html')


# Student attendant record
@app.route('/attendant_record')
def attendant_record():
    cur.execute("select a.levelid, a.coursetime,a.arrivaltime, b.course_name, c.levelname, a.leaveid, a.classid"
                " from studentattent a,"
                "course b, course_level c where a.courseid=b.courseid and a.levelid=c.levelid and "
                "a.studentid='%s' ORDER BY a.coursetime" % (session['id']))
    attend = cur.fetchall()
    cur.execute('commit')
    attend_no = len(attend)
    course_time = []
    course_date = []
    for i in range(attend_no):
        time = attend[i][1].strftime("%H:%M")
        date = attend[i][1].strftime("%Y-%m-%d")
        course_time.append(time)
        course_date.append(date)

    cur.execute("select a.classid, b.timestart"
                " from studentattent a, makeupclass b "
                "where a.classid=b.classid and "
                "a.studentid='%s' ORDER BY a.coursetime" % (session['id']))
    class_id = cur.fetchall()
    class_no = len(class_id)
    class_date = []
    for i in range(class_no):
        class_time = class_id[i][1].strftime("%Y-%m-%d %H:%M")
        class_date.append(class_time)

    record_attend = '2020-01-31 00:00:00'
    record_attend = datetime.datetime.strptime(record_attend, '%Y-%m-%d %H:%M:%S')
    return render_template('attendant_record.html', course_date=course_date, attend=attend, attend_no=attend_no,
                           course_time=course_time, record_attend=record_attend, class_date=class_date,
                           class_id=class_id, class_no=class_no)


# All Invoice Record
@app.route('/invoice_record')
def invoice_record():
    cur.execute("select a.invoiceid, a.lesson_month, a.totalprice, a.paymethod, a.paytime "
                "from invoice a, student_invoice b where b.invoiceid = a.invoiceid and "
                "b.studentid='%s' ORDER BY a.paytime" % (session['id']))
    invoice_list = cur.fetchall()
    cur.execute('commit')
    invoice_no = len(invoice_list)

    cur.execute("select c.levelname, d.course_name, b.qty, b.totalprice, a.invoiceid "
                "from invoice a, invoiceitem b, course_level c, course d, student_invoice e "
                "where a.invoiceid=b.invoiceid and b.levelid=c.levelid and b.courseid=d.courseid "
                "and a.invoiceid=e.invoiceid and e.studentid='%s'" % (session['id']))
    invoice_item = cur.fetchall()
    cur.execute('commit')
    item_no = len(invoice_item)

    course_month = []
    for i in range(invoice_no):
        month = invoice_list[i][1].strftime("%Y-%m-%d")
        course_month.append(month)

    return render_template('invoice_record.html', course_month=course_month, invoice_list=invoice_list,
                           invoice_no=invoice_no, invoice_item=invoice_item, item_no=item_no)


# Personal Leave Application
@app.route('/leave')
def leave():
    cur.execute("select a.levelid, a.coursetime, b.course_name, c.levelname, a.attentid from studentattent a,"
                "course b, course_level c where a.courseid=b.courseid and a.levelid=c.levelid and "
                "a.studentid='%s' and a.coursetime>TRUNC(SYSDATE) and a.coursetime<TRUNC(SYSDATE+28)"
                " And a.leaveid is Null and a.arrivaltime is null ORDER BY a.coursetime" % (session['id']))
    attend = cur.fetchall()
    cur.execute('commit')
    attend_no = len(attend)
    course_time = []
    course_date = []
    for i in range(attend_no):
        time = attend[i][1].strftime("%H:%M")
        date = attend[i][1].strftime("%d-%m-%Y")
        course_time.append(time)
        course_date.append(date)

    cur.execute("SELECT a.course_name, a.courseid FROM Course a, CourseStudent b WHERE "
                "a.courseid=b.courseid and b.StudentID= %s" % (session['id']))
    course_list = cur.fetchall()
    cur.execute('commit')
    No = len(course_list)

    return render_template('leave.html', course_list=course_list, No=No, attend=attend,
                           attend_no=attend_no, course_time=course_time, course_date=course_date)


# All Leave Record
@app.route('/leave_record')
def leave_record():
    cur.execute("SELECT a.leavetime, a.reason, a.needclass, a.approval, b.course_name, c.levelname"
                " FROM studentleave a, Course b, course_level c , studentleaving d WHERE "
                "a.leaveid= d.leaveid and a.courseid=b.courseid and a.courseid=b.courseid "
                "and a.levelid=c.levelid "
                "and d.StudentID= '%s' order by a.leavetime DESC" % (session['id']))
    course_list = cur.fetchall()
    cur.execute('commit')
    num = len(course_list)
    return render_template('leave_record.html', course_list=course_list, num=num)


# Add personal leave record (Student)
@app.route('/student_leave', methods=['POST', 'GET'])
def student_leave():
    attend_id = request.form["attend_id"]
    reason = request.form["reason"]
    need_class = request.form["makeup"]
    cur.execute("Select levelid, coursetime, courseid from studentattent Where attentid='%s'" %
                attend_id)
    result_1 = cur.fetchone()
    cur.execute('commit')

    level_id = result_1[0]
    coursetime = result_1[1]
    courseid = result_1[2]
    studentid = session["id"]

    cur.execute("insert into studentleave(leaveid, levelid, leavetime, reason, needclass, courseid) "
                "values(leaveid_SEQUENCE.nextval, '%s', TimeStamp'%s', '%s', '%s','%s')" %
                (level_id, coursetime, reason, need_class, courseid))
    cur.execute("commit")

    cur.execute("insert into studentleaving(leaveid, studentid) "
                "values(leaveid_SEQUENCE.currval, '%s')" % studentid)
    cur.execute("commit")

    cur.execute("Update studentattent set leaveid = leaveid_SEQUENCE.currval Where attentid='%s'" %
                attend_id)
    cur.execute('commit')

    return redirect(url_for('leave_record'))


# _________________________Add Course function_____________________________________


# Choose add course method
@app.route('/add_method')
def add_method():
    return render_template('add_method.html')


# Show All Teachers Available
@app.route('/by_teacher')
def by_teacher():
    cur.execute("select staffid, staffname, gender from staff where worktype = 'Teacher'")
    teacher_list = cur.fetchall()
    cur.execute('commit')
    teach_no = len(teacher_list)

    cur.execute("select a.teacherid, b.course_name, a.courseid "
                "from teacher_course a, course b where a.courseid=b.courseid")
    course_list = cur.fetchall()
    cur.execute('commit')
    course_no = len(course_list)

    cur.execute("select teacherid, weekday from teachertime")
    teacher_time = cur.fetchall()
    cur.execute('commit')
    time_no = len(teacher_time)

    cur.execute("SELECT courseid FROM CourseStudent WHERE "
                "StudentID= %s" % (session['id']))
    course_id = cur.fetchall()
    cur.execute('commit')
    cou_no = len(course_id)
    return render_template('by_teacher.html', teacher_list=teacher_list, teach_no=teach_no,
                           teacher_time=teacher_time, time_no=time_no, course_list=course_list,
                           course_no=course_no, cou_no=cou_no, course_id=course_id)


# Show all time available for 1 teacher
@app.route('/teacher_time', methods=['POST', 'GET'])
def teacher_time():
    course_id = request.form['course_id']
    teacher_id = request.form['staff_id']

    cur.execute("select staffname, gender from staff where staffid='%s'" % teacher_id)
    staff = cur.fetchone()

    cur.execute("select a.starttime, a.endtime, b.staffname, b.gender, a.teacherid, a.weekday, a.lunchtime, "
                "c.course_name, d.courseid from teachertime a, staff b , course c, teacher_course d where "
                "a.teacherid=b.staffid and d.courseid=c.courseid and d.teacherid=b.staffid "
                "and c.courseid= '%s' and b.staffid='%s' "
                "order by decode(a.weekday, 'Sun', 1, 'Mon', 2, 'Tue', 3, 'Wed', 4, 'Thur',5 , 'Fri', 6, 'Sat', 7, 8)" %
                (course_id, teacher_id))
    result2 = cur.fetchall()

    cur.execute("select timestart, timefinish, teacherid, courseid, weekday from coursestudent where courseid='%s' "
                % course_id)

    result = cur.fetchall()

    No = len(result2)
    AllTime = []
    Number = []
    LunchList = []
    LunchList2 = []
    Student_num = len(result)
    for i in range(No):
        now = result2[i][0]
        time = now.strftime("%H:%M")
        lunch = result2[i][6]
        Ltime = lunch.strftime("%H:%M")
        lunch2 = lunch + datetime.timedelta(minutes=30)
        Ltime2 = lunch2.strftime("%H:%M")
        ending = result2[i][1]
        time2 = ending.strftime("%H:%M")
        Tlist = []

        while time != time2:
            Tlist.append(time)
            now += datetime.timedelta(minutes=30)
            time = now.strftime("%H:%M")
        Num = len(Tlist)
        Number.append(Num)
        LunchList.append(Ltime)
        LunchList2.append(Ltime2)
        AllTime.append(Tlist)

    student_start_time = []
    if Student_num != '0':
        for i in range(Student_num):
            time_start = result[i][0]
            start_time = time_start.strftime("%H:%M")
            student_start_time.append(start_time)
    return render_template('teacher_time.html', result2=result2, No=No, AllTime=AllTime, Number=Number,
                           LunchList=LunchList, LunchList2=LunchList2, student_start_time=student_start_time,
                           staff=staff, Student_num=Student_num, result=result)


# Choose instrument
@app.route('/add')
def add():
    cur.execute("SELECT a.course_name FROM Course a, CourseStudent b WHERE "
                "a.courseid=b.courseid and b.StudentID= %s" % (session['id']))
    course_list = cur.fetchone()
    cur.execute('commit')
    return render_template('add.html', course_list=course_list)


# Show all teachers and time available (according to instruments and weekday)
@app.route('/course', methods=['POST', 'GET'])
def course():
    course_type = request.form['instrument']
    weekday = request.form['weekday']

    weekday_list = ['Sun', 'Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat']
    list_no = len(weekday_list)

    cur.execute("select a.starttime, a.endtime, b.staffname, b.gender, a.teacherid, a.weekday, a.lunchtime, "
                "c.course_name, d.courseid from teachertime a, staff b , course c, teacher_course d where "
                "a.teacherid=b.staffid "
                "and d.courseid=c.courseid and d.teacherid=b.staffid and c.course_name= '%s' and a.weekday='%s'" %
                (course_type, weekday))

    result2 = cur.fetchall()
    cur.execute("Select courseid from course where course_name = '%s'" % course_type)
    course_infor = cur.fetchone()
    courseid = course_infor[0]

    cur.execute("select timestart, timefinish, teacherid, courseid, weekday from coursestudent where courseid='%s' "
                "and weekday='%s'" %
                (courseid, weekday))

    result = cur.fetchall()

    cur.execute("select course_name from course")
    course_name = cur.fetchall()
    course_no = len(course_name)

    No = len(result2)
    AllTime = []
    Number = []
    LunchList = []
    LunchList2 = []
    Student_num = len(result)
    for i in range(No):
        now = result2[i][0]
        time = now.strftime("%H:%M")
        lunch = result2[i][6]
        Ltime = lunch.strftime("%H:%M")
        lunch2 = lunch + datetime.timedelta(minutes=30)
        Ltime2 = lunch2.strftime("%H:%M")
        ending = result2[i][1]
        time2 = ending.strftime("%H:%M")
        Tlist = []

        while time != time2:
            Tlist.append(time)
            now += datetime.timedelta(minutes=30)
            time = now.strftime("%H:%M")
        Num = len(Tlist)
        Number.append(Num)
        LunchList.append(Ltime)
        LunchList2.append(Ltime2)
        AllTime.append(Tlist)

    student_start_time = []
    if Student_num != '0':
        for i in range(Student_num):
            time_start = result[i][0]
            start_time = time_start.strftime("%H:%M")
            student_start_time.append(start_time)

    return render_template('course.html', result2=result2, No=No, AllTime=AllTime, Number=Number, LunchList=LunchList,
                           LunchList2=LunchList2, course_type=course_type, course=course_name, course_no=course_no,
                           weekday=weekday, weekday_list=weekday_list, list_no=list_no,
                           student_start_time=student_start_time, Student_num=Student_num, result=result)


# Show course information
@app.route('/courseinformation', methods=['POST', 'GET'])
def courseinformation():
    TeacherID = request.form["teacherid"]
    time = request.form['time']
    course_type = request.form['course']
    weekday = request.form['weekday']

    cur.execute("SELECT StaffNAME, Gender, StaffID FROM Staff WHERE StaffID= %s" % TeacherID)

    result = cur.fetchone()
    cur.execute('commit')

    cur.execute("SELECT levelid, price FROM course_level WHERE levelname = '%s'" % (course_type + 'interest'))

    result2 = cur.fetchone()
    cur.execute('commit')

    cur.execute("SELECT levelid, price FROM course_level WHERE levelname like '%30' ")

    level = cur.fetchall()
    cur.execute('commit')

    return render_template('courseinformation.html', result=result, time=time, course=course_type, weekday=weekday,
                           result2=result2, level=level)


# Provide payment method
@app.route('/payment', methods=['POST', 'GET'])
def payment():
    TeacherID = request.form["teacherid"]
    time = request.form['starttime']
    course_type = request.form['course']
    weekday = request.form['weekday']
    level = request.form['level']
    duration = int(request.form['duration'])

    cur.execute("SELECT StaffNAME, Gender, StaffID FROM Staff WHERE StaffID= %s" % TeacherID)

    result = cur.fetchone()
    cur.execute('commit')

    cur.execute("SELECT courseid FROM course WHERE course_name= '%s'" % course_type)

    course_result = cur.fetchone()
    cur.execute('commit')

    cur.execute("SELECT levelname, price, levelid FROM course_level WHERE levelid = '%s'" % level)

    result2 = cur.fetchone()
    cur.execute('commit')

    d = datetime.date.today()

    while d.strftime('%a') != weekday:
        d += datetime.timedelta(1)

    return render_template('payment.html', result=result, time=time, course=course_type, weekday=weekday,
                           result2=result2, duration=duration, date=d, course_result=course_result)


# Make invoice
@app.route('/invoice', methods=['POST', 'GET'])
def invoice():
    TeacherID = request.form["teacherid"]
    time = request.form['starttime']
    course_id = request.form['course']
    weekday = request.form['weekday']
    level = request.form['levelid']
    duration = int(request.form['duration'])
    price = float(request.form['price'])
    method = request.form['pay']
    qty = int(request.form['qty'])

    d = datetime.date.today()

    while d.strftime('%a') != weekday:
        d += datetime.timedelta(1)
    d = str(d) + ' 00:00:00.00'

    # _____________________________insert invoice details__________________________________
    cur.execute("INSERT INTO invoice (invoiceid, totalprice, paymethod, paytime, lesson_month) VALUES ("
                "invoiceid_seq.nextval,'%s', '%s', Current_Timestamp,TimeStamp'%s') " % (
                    price, method, d))
    cur.execute('commit')

    cur.execute("INSERT INTO invoiceitem (invoiceitemid, invoiceid, courseid, qty, totalprice, levelid) VALUES ("
                "invoiceitemid_seq.nextval, invoiceid_seq.currval, '%s', '%s', '%s', '%s') " % (
                    course_id, qty, price, level))
    cur.execute('commit')

    cur.execute("INSERT INTO student_invoice(studentid, invoiceid) VALUES ("
                "'%s', invoiceid_seq.currval)" % (session['id']))
    cur.execute('commit')

    # __________Insert attendance details (Base on the number of courses they have)_______________
    d = datetime.date.today()

    while d.strftime('%a') != weekday:
        d += datetime.timedelta(1)

    for a in range(qty):
        cur.execute("INSERT INTO studentattent (attentid, studentid, teacherid, levelid, coursetime, courseid) VALUES ("
                    "attentid_seq.nextval,'%s', '%s' , '%s', TimeStamp'%s %s:00.00', '%s') " % (
                        session['id'], TeacherID, level, d, time, course_id))
        cur.execute('commit')
        d += datetime.timedelta(7)

    # ______________Insert course details for student___________________________________________
    time = '2020-01-31 ' + str(time) + ':00'
    end_time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(minutes=duration)
    cur.execute("INSERT INTO coursestudent (studentid, teacherid, levelid, timestart, timefinish, weekday, courseid)"
                " VALUES ('%s','%s', '%s', TimeStamp'%s', TimeStamp'%s', '%s', '%s')" % (
                    session['id'], TeacherID, level, time, end_time, weekday, course_id))
    cur.execute('commit')

    # ______________________Show the invoice details____________________________________________
    cur.execute("SELECT a.invoiceid, a.paytime, a.lesson_month, a.paymethod FROM invoice a, student_invoice b, "
                "invoiceitem c WHERE a.invoiceid=b.invoiceid and a.invoiceid=c.invoiceid and b.studentid = '%s' and "
                "c.courseid= '%s'" % (session['id'], course_id))
    result3 = cur.fetchone()
    cur.execute('commit')

    month = result3[2].strftime("%b / %Y")

    cur.execute("SELECT StaffNAME, Gender, StaffID FROM Staff WHERE StaffID= %s" % TeacherID)

    result = cur.fetchone()
    cur.execute('commit')

    cur.execute("SELECT levelname, price, levelid FROM course_level WHERE levelid = '%s'" % level)

    result2 = cur.fetchone()
    cur.execute('commit')

    cur.execute("SELECT course_name FROM course WHERE courseid= '%s'" % course_id)

    course_result = cur.fetchone()
    cur.execute('commit')

    d = datetime.date.today()

    while d.strftime('%a') != weekday:
        d += datetime.timedelta(1)

    time = request.form['starttime']

    return render_template('invoice.html', result=result, time=time, course=course, weekday=weekday,
                           result2=result2, result3=result3, duration=duration, date=d, month=month,
                           qty=qty, course_result=course_result)


# Contact teacher page
@app.route('/contact')
def contact():
    cur.execute("select a.message, a.messagetime, b.staffname from "
                "StudentMessage a, staff b, studmes_staff c, StudentMesID d "
                "where a.Messageid=c.Messageid and c.staffid=b.staffid and a.Messageid=d.Messageid and "
                "d.studentid='%s'" % session['id'])
    received = cur.fetchall()
    received_no = len(received)

    cur.execute("select a.message, a.messagetime, b.staffname from "
                "TeacherMessage a, staff b, TeacherMesid c, STDTEACHMES d "
                "where a.Messageid=c.Messageid and c.staffid=b.staffid and a.Messageid=d.Messageid and "
                "d.studentid='%s'" % session['id'])
    message = cur.fetchall()
    message_no = len(message)

    cur.execute("select a.teacherid, b.staffname from coursestudent a, staff b "
                "where a.teacherid=b.staffid and a.studentid='%s'" % session['id'])
    teacher = cur.fetchall()
    teacher_no = len(teacher)
    return render_template('contact.html', teacher=teacher, teacher_no=teacher_no, message=message,
                           message_no=message_no, received_no=received_no, received=received)


# Add teacher message
@app.route('/write_message', methods=['POST', 'GET'])
def write_message():
    TeacherID = request.form["teacher_id"]
    message = request.form['message']

    cur.execute("INSERT INTO TeacherMessage (Messageid, Message, MessageTime) VALUES ("
                "TeacherMessageid_SEQUENCE.nextval,'%s', Current_Timestamp) " % message)
    cur.execute('commit')

    cur.execute("INSERT INTO TeacherMesid (Messageid, Staffid) VALUES ("
                "TeacherMessageid_SEQUENCE.currval,'%s') " % TeacherID)
    cur.execute('commit')

    cur.execute("INSERT INTO STDTEACHMES (Messageid, Studentid) VALUES ("
                "TeacherMessageid_SEQUENCE.currval,'%s') " % session['id'])
    cur.execute('commit')

    return redirect(url_for('contact'))


@app.route('/feedback')
def feedback():
    return render_template('contact.html')


# ________________Teacher Log In Page____________________________________________________
@app.route('/staff')
def staff():
    error = None
    return render_template('staff.html', error=error)


@app.route('/logoutteacher')
def logoutteacher():
    session.pop('teacher', None)
    return redirect(url_for('index'))


# __________________Show work schedule___________________________________________________________
@app.route('/timetable', methods=['POST', 'GET'])
def timetable():
    if 'teacher' in session:
        cur.execute("SELECT StaffID, StaffNAME, PASSWORD, Gender FROM Staff WHERE StaffID= %s" % (session['teacher']))

        result = cur.fetchone()
        cur.execute('commit')

        cur.execute("SELECT TeacherID, Weekday, starttime, endtime FROM TEACHERTIME WHERE TEACHERID= %s "
                    "order by decode(weekday, 'Sun', 1, 'Mon', 2, 'Tue', 3, 'Wed', 4, 'Thur',5 , 'Fri', 6, 'Sat', 7, 8)"
                    % (session['teacher']))

        result2 = cur.fetchall()
        No = len(result2)

        cur.execute("select a.studentname, b.levelname, c.timestart, c.timefinish, "
                    "d.course_name, c.weekday, a.studentid, d.courseid "
                    "from student a, course_level b, coursestudent c, course d "
                    "WHERE a.studentid=c.studentid and b.levelid=c.levelid and c.courseid=d.courseid and "
                    "c.TEACHERID= %s order by c.timestart" % (session['teacher']))

        student = cur.fetchall()
        student_no = len(student)

        cur.execute("select a.leavetime, b.studentid from studentleave a, coursestudent b, studentleaving c "
                    "where a.leaveid=c.leaveid and b.studentid=c.studentid and "
                    "b.teacherid='%s' and a.approval = 'Approved' and "
                    "a.leavetime>TRUNC(SYSDATE-14) and a.leavetime<TRUNC(SYSDATE+28)" % (session['teacher']))

        leave_list = cur.fetchall()
        leave_no = len(leave_list)

        Start_Time = []
        End_Time = []
        Work_start = []
        Work_end = []
        leave_date = []
        for i in range(student_no):
            now = student[i][2]
            start = now.strftime("%H:%M")
            finish = student[i][3]
            end = finish.strftime("%H:%M")

            Start_Time.append(start)
            End_Time.append(end)

        for i in range(No):
            start_work = result2[i][2]
            start_work = start_work.strftime("%H:%M")
            end_work = result2[i][3]
            end_work = end_work.strftime("%H:%M")
            Work_start.append(start_work)
            Work_end.append(end_work)

        for i in range(leave_no):
            date = leave_list[i][0]
            date = date.strftime("%d/ %m/ %Y")
            leave_date.append(date)

        cur.execute("select a.leaveid, e.studentname, b.timestart from "
                    "studentleave a, makeupclass b, teachernewclass c, studentleaving d, student e, "
                    "course f, course_level g where "
                    "a.leaveid=b.leaveid and a.leaveid=c.leaveid and b.classid=c.classid and "
                    "a.leaveid=d.leaveid and d.studentid=e.studentid and a.courseid=f.courseid "
                    "and a.levelid=g.levelid and c.teacherid = '%s' "
                    "order by b.timestart" % (session['teacher']))

        class_list = cur.fetchall()
        class_no = len(class_list)

        class_date = []
        class_start = []
        for i in range(class_no):
            date = class_list[i][2]
            date = date.strftime("%d/ %m/ %Y")
            class_date.append(date)

            date = class_list[i][2]
            start = date.strftime("%H:%M")
            class_start.append(start)

        return render_template('timetable.html', result=result, result2=result2, No=No, student=student,
                               student_no=student_no, Start_Time=Start_Time, End_Time=End_Time, Work_start=Work_start,
                               Work_end=Work_end, leave_date=leave_date, leave_list=leave_list, leave_no=leave_no,
                               class_no=class_no, class_list=class_list, class_date=class_date, class_start=class_start)

    elif request.method == 'POST':
        session.pop = ('teacher', None)
        UserID = request.form["UserID"]
        pwd = request.form['password']

        cur.execute("SELECT StaffID, StaffNAME, PASSWORD, Gender FROM Staff WHERE StaffID= %s" % UserID)

        result = cur.fetchone()
        cur.execute('commit')
        if result is None:
            error = "Do not have this user"
            return render_template('staff.html', error=error)
        password = result[2]

        if pwd == password:
            session['teacher'] = UserID
            cur.execute(
                "SELECT StaffID, StaffNAME, PASSWORD, Gender FROM Staff WHERE StaffID= %s" % (session['teacher']))

            result = cur.fetchone()
            cur.execute('commit')

            cur.execute("SELECT TeacherID, Weekday, starttime, endtime FROM TEACHERTIME WHERE TEACHERID= %s "
                        "order by decode(weekday, 'Sun', 1, 'Mon', 2, 'Tue', 3, 'Wed', 4, 'Thur',5 , "
                        "'Fri', 6, 'Sat', 7, 8)"
                        % (session['teacher']))

            result2 = cur.fetchall()
            No = len(result2)

            cur.execute("select a.studentname, b.levelname, c.timestart, c.timefinish, "
                        "d.course_name, c.weekday, a.studentid, d.courseid "
                        "from student a, course_level b, coursestudent c, course d "
                        "WHERE a.studentid=c.studentid and b.levelid=c.levelid and c.courseid=d.courseid and "
                        "c.TEACHERID= %s order by c.timestart" % (session['teacher']))

            student = cur.fetchall()
            student_no = len(student)

            cur.execute("select a.leavetime, b.studentid from studentleave a, coursestudent b, studentleaving c "
                        "where a.leaveid=c.leaveid and b.studentid=c.studentid and "
                        "b.teacherid='%s' and a.approval = 'Approved' and "
                        "a.leavetime>TRUNC(SYSDATE-14) and a.leavetime<TRUNC(SYSDATE+28)" % (session['teacher']))

            leave_list = cur.fetchall()
            leave_no = len(leave_list)

            Start_Time = []
            End_Time = []
            Work_start = []
            Work_end = []
            leave_date = []
            for i in range(student_no):
                now = student[i][2]
                start = now.strftime("%H:%M")
                finish = student[i][3]
                end = finish.strftime("%H:%M")

                Start_Time.append(start)
                End_Time.append(end)

            for i in range(No):
                start_work = result2[i][2]
                start_work = start_work.strftime("%H:%M")
                end_work = result2[i][3]
                end_work = end_work.strftime("%H:%M")
                Work_start.append(start_work)
                Work_end.append(end_work)

            for i in range(leave_no):
                date = leave_list[i][0]
                date = date.strftime("%d/ %m/ %Y")
                leave_date.append(date)

            cur.execute("select a.leaveid, e.studentname, b.timestart from "
                        "studentleave a, makeupclass b, teachernewclass c, studentleaving d, student e, "
                        "course f, course_level g where "
                        "a.leaveid=b.leaveid and a.leaveid=c.leaveid and b.classid=c.classid and "
                        "a.leaveid=d.leaveid and d.studentid=e.studentid and a.courseid=f.courseid "
                        "and a.levelid=g.levelid and c.teacherid = '%s' "
                        "order by b.timestart" % (session['teacher']))

            class_list = cur.fetchall()
            class_no = len(class_list)

            class_date = []
            class_start = []
            for i in range(class_no):
                date = class_list[i][2]
                date = date.strftime("%d/ %m/ %Y")
                class_date.append(date)

                date = class_list[i][2]
                start = date.strftime("%H:%M")
                class_start.append(start)

            return render_template('timetable.html', result=result, result2=result2, No=No, student=student,
                                   student_no=student_no, Start_Time=Start_Time, End_Time=End_Time,
                                   Work_start=Work_start,
                                   Work_end=Work_end, leave_date=leave_date, leave_list=leave_list, leave_no=leave_no,
                                   class_no=class_no, class_list=class_list, class_date=class_date,
                                   class_start=class_start)

        error = "Invalid user id or password"
        return render_template('staff.html', error=error)

    return render_template('timetable.html')


# _______________Teacher Account Management_______________________________________________________
@app.route('/teacherinfor')
def teacherinfor():
    if 'teacher' in session:
        cur.execute("SELECT StaffID, STAFFNAME, GENDER, PHONE, EMAIL, ADDRESS, PASSWORD, WorkType FROM Staff WHERE "
                    "StaffID= %s" % (session['teacher']))

        result = cur.fetchone()
        cur.execute('commit')
        return render_template('teacherinfor.html', result=result)
    return render_template('home.html')


@app.route('/changeteacherinfor')
def changeteacherinfor():
    if 'teacher' in session:
        cur.execute("SELECT StaffID, STAFFNAME, GENDER, PHONE, EMAIL, ADDRESS, PASSWORD, WorkType FROM Staff WHERE "
                    "StaffID= %s" % (session['teacher']))

        result = cur.fetchone()
        cur.execute('commit')
        return render_template('changeteacherinfor.html', result=result)
    return render_template('home.html')


@app.route('/changedteacher', methods=['POST', 'GET'])
def changedteacher():
    if 'teacher' in session:
        name = request.form["UserName"]
        email = request.form["email"]
        address = request.form["address"]
        phone = int(request.form["phone"])
        pwd = request.form['pwd']

        cur.execute("Update STAFF Set STAFFNAME ='%s' , PHONE='%d',"
                    " EMAIL='%s', ADDRESS='%s', PASSWORD='%s'"
                    "Where StaffID= %s" % (
                        name, phone, email, address, pwd, session['teacher']))
        cur.execute('commit')

        return redirect(url_for('teacherinfor'))


# _______________Student Leave Approval________________________________________
@app.route('/leave_approval')
def leave_approval():
    cur.execute("select a.studentname, b.leaveid, b.leavetime, b.reason, b.needclass, "
                "d.course_name, e.levelname, f.weekday, a.studentid "
                "from student a, studentleave b, studentleaving c, course d, course_level e, coursestudent f "
                "where a.studentid=c.studentid and b.leaveid=c.leaveid and b.courseid=d.courseid "
                "and b.levelid=e.levelid and a.studentid=f.studentid and d.courseid=f.courseid and "
                "f.teacherid='%s' and b.approval='Processing'" % (session['teacher']))

    result = cur.fetchall()
    num = len(result)
    CourseTime = []
    CourseDate = []
    for i in range(num):
        course_start = result[i][2]
        time = course_start.strftime("%H:%M")
        CourseTime.append(time)
        date = course_start.strftime("%d/%m/%Y")
        CourseDate.append(date)

    cur.execute('commit')
    Name = None

    return render_template('leave_approval.html', result=result, num=num, CourseTime=CourseTime,
                           CourseDate=CourseDate, Name=Name)


@app.route('/approve_leave', methods=['POST', 'GET'])
def approve_leave():
    leave_id = request.form["leave_id"]
    Name = request.form["Name"]
    Date = request.form["Date"]

    cur.execute("Update studentleave set approval='Approved' Where leaveid='%s'" %
                leave_id)
    cur.execute('commit')

    cur.execute("select a.studentname, b.leaveid, b.leavetime, b.reason, b.needclass, "
                "d.course_name, e.levelname, f.weekday, a.studentid "
                "from student a, studentleave b, studentleaving c, course d, course_level e, coursestudent f "
                "where a.studentid=c.studentid and b.leaveid=c.leaveid and b.courseid=d.courseid "
                "and b.leaveid=e.levelid and a.studentid=f.studentid and d.courseid=f.courseid and "
                "f.teacherid='%s' and b.approval='Processing'" % (session['teacher']))

    result = cur.fetchall()
    num = len(result)
    CourseTime = []
    CourseDate = []
    for i in range(num):
        course_start = result[i][2]
        time = course_start.strftime("%H:%M")
        CourseTime.append(time)
        date = course_start.strftime("%d/%m/%Y")
        CourseDate.append(date)

    cur.execute('commit')

    Not = ''

    return render_template('leave_approval.html', result=result, num=num, CourseTime=CourseTime,
                           CourseDate=CourseDate, Name=Name, Date=Date, Not=Not)


@app.route('/not_approve', methods=['POST', 'GET'])
def not_approve():
    leave_id = request.form["leave_id"]
    Name = request.form["Name"]
    Date = request.form["Date"]

    cur.execute("Update studentleave set approval='Not Approved' Where leaveid='%s'" %
                leave_id)
    cur.execute('commit')

    cur.execute("Update studentattent set arrivaltime = TimeStamp'2020-01-31 00:00:00.00' Where leaveid='%s'" %
                leave_id)
    cur.execute('commit')

    cur.execute("select a.studentname, b.leaveid, b.leavetime, b.reason, b.needclass, "
                "d.course_name, e.levelname, f.weekday, a.studentid "
                "from student a, studentleave b, studentleaving c, course d, course_level e, coursestudent f "
                "where a.studentid=c.studentid and b.leaveid=c.leaveid and b.courseid=d.courseid "
                "and b.leaveid=e.levelid and a.studentid=f.studentid and d.courseid=f.courseid and "
                "f.teacherid='%s' and b.approval='Processing'" % (session['teacher']))

    result = cur.fetchall()
    num = len(result)
    CourseTime = []
    CourseDate = []
    for i in range(num):
        course_start = result[i][2]
        time = course_start.strftime("%H:%M")
        CourseTime.append(time)
        date = course_start.strftime("%d/%m/%Y")
        CourseDate.append(date)

    cur.execute('commit')

    Not = 'not'

    return render_template('leave_approval.html', result=result, num=num, CourseTime=CourseTime,
                           CourseDate=CourseDate, Name=Name, Date=Date, Not=Not)


# ___________Manage Work Day________________________________
@app.route('/work')
def work():
    return render_template('work.html')


# Add Work schedule
@app.route('/edited', methods=['POST', 'GET'])
def edited():
    if 'teacher' in session:
        weekday = request.form["weekday"]
        lunch = request.form["lunch"]
        start = request.form["start"]
        ending = request.form["ending"]

        if lunch == '':
            lunch = '00:00'
        cur.execute("INSERT INTO TEACHERTIME (TeacherID, Weekday, LunchTime ,StartTime, EndTime) VALUES ("
                    "'%s','%s', TimeStamp'2020-01-31 %s:00.00',TimeStamp'2020-01-31 %s:00.00',"
                    "TimeStamp'2020-01-31 %s:00.00') " % (
                        session['teacher'], weekday, lunch, start, ending))

        cur.execute('commit')

    return redirect(url_for('timetable'))


# Personal Leave Application
@app.route('/leave_teacher')
def leave_teacher():
    return render_template('leave_teacher.html')


# Teacher Leave SQL
@app.route('/teacher_leave', methods=['POST', 'GET'])
def teacher_leave():
    day_leave = request.form["day_leave"]
    reason = request.form["reason"]

    cur.execute("Insert into staffleave(leaveid, leavetime, reason) values "
                "(staff_leaveid_SEQUENCE.nextval, TimeStamp'%s 00:00:00', '%s')" % (day_leave, reason))
    cur.execute('commit')

    cur.execute("Insert into staff_staffleave(leaveid, staffid) values "
                "(staff_leaveid_SEQUENCE.currval, '%s')" % session['teacher'])
    cur.execute('commit')

    return redirect(url_for('teacher_leave_record'))


# Teacher Leave Record
@app.route('/teacher_leave_record')
def teacher_leave_record():
    cur.execute("select a.leaveid, a.leavetime, a.reason, a.approval "
                "from staffleave a, staff_staffleave b where a.leaveid=b.leaveid and "
                "b.staffid='%s'" % session['teacher'])
    leave_list = cur.fetchall()
    num = len(leave_list)

    leave_date = []
    for i in range(num):
        date = leave_list[i][1]
        date = date.strftime("%d/ %m/ %Y")
        leave_date.append(date)
    return render_template('teacher_leave_record.html', leave_list=leave_list, num=num, leave_date=leave_date)


# ___________Check For Student Information (Teacher)________________________________
@app.route('/studentrecord', methods=['POST', 'GET'])
def studentrecord():
    student_id = request.form["student_id"]
    course_id = request.form["course_id"]

    cur.execute("select a.studentname, b.levelname, c.timestart, c.timefinish, "
                "d.course_name, c.weekday, a.studentid, d.courseid "
                "from student a, course_level b, coursestudent c, course d "
                "WHERE a.studentid=c.studentid and b.levelid=c.levelid and c.courseid=d.courseid and "
                "c.TEACHERID= '%s' and a.studentid='%s' and d.courseid='%s'" %
                (session['teacher'], student_id, course_id))

    student = cur.fetchone()

    cur.execute("select a.leavetime, b.studentid from studentleave a, coursestudent b, studentleaving c "
                "where a.leaveid=c.leaveid and b.studentid=c.studentid and "
                "b.teacherid='%s' and a.approval = 'Approved' "
                "and a.leavetime>TRUNC(SYSDATE-14) and a.leavetime<TRUNC(SYSDATE+28) "
                "and b.studentid= '%s'" % (session['teacher'], student_id))

    leave_list = cur.fetchall()
    leave_no = len(leave_list)

    Start_Time = []
    End_Time = []
    now = student[2]
    start = now.strftime("%H:%M")
    finish = student[3]
    end = finish.strftime("%H:%M")

    Start_Time.append(start)
    End_Time.append(end)

    leave_date = []
    for i in range(leave_no):
        date = leave_list[i][0]
        date = date.strftime("%d/ %m/ %Y")
        leave_date.append(date)

    cur.execute("select a.leaveid, b.timestart, b.timefinish from "
                "studentleave a, makeupclass b, teachernewclass c, studentleaving d, student e, "
                "course f, course_level g where "
                "a.leaveid=b.leaveid and a.leaveid=c.leaveid and b.classid=c.classid and "
                "a.leaveid=d.leaveid and d.studentid=e.studentid and a.courseid=f.courseid "
                "and a.levelid=g.levelid and c.teacherid = '%s' and d.studentid = '%s' and "
                "b.timestart>TRUNC(SYSDATE) and b.timestart<TRUNC(SYSDATE+28) "
                "order by b.timestart" % (session['teacher'], student_id))

    class_list = cur.fetchall()
    class_no = len(class_list)

    class_date = []
    class_start = []
    class_end = []
    for i in range(class_no):
        date = class_list[i][1]
        date = date.strftime("%d/ %m/ %Y")
        class_date.append(date)

        date = class_list[i][1]
        start = date.strftime("%H:%M")
        class_start.append(start)

        date = class_list[i][2]
        end = date.strftime("%H:%M")
        class_end.append(end)

    return render_template('studentrecord.html', student=student, Start_Time=Start_Time, End_Time=End_Time,
                           leave_date=leave_date, leave_list=leave_list, leave_no=leave_no, class_start=class_start,
                           class_date=class_date, class_list=class_list, class_no=class_no, class_end=class_end)


@app.route('/level_up', methods=['POST', 'GET'])
def level_up():
    student_id = request.form["student_id"]
    course_id = request.form["course_id"]

    cur.execute("select a.studentname, b.levelname, c.timestart, c.timefinish, "
                "d.course_name, c.weekday, a.studentid, d.courseid "
                "from student a, course_level b, coursestudent c, course d "
                "WHERE a.studentid=c.studentid and b.levelid=c.levelid and c.courseid=d.courseid and "
                "c.TEACHERID= '%s' and a.studentid='%s' and d.courseid='%s'" %
                (session['teacher'], student_id, course_id))

    student = cur.fetchone()

    Start_Time = []
    End_Time = []
    now = student[2]
    start = now.strftime("%H:%M")
    finish = student[3]
    end = finish.strftime("%H:%M")

    Start_Time.append(start)
    End_Time.append(end)

    time = (finish - now)
    seconds = time.total_seconds()
    minutes = int(seconds / 60)

    cur.execute("select levelid, levelname from course_level where levelname not like '%interest'"
                " and levelname like '%30'")

    level_list = cur.fetchall()
    level_no = len(level_list)

    return render_template('level_up.html', student=student, level_list=level_list, level_no=level_no,
                           Start_Time=Start_Time, End_Time=End_Time, minutes=minutes)


# Change student level function
@app.route('/change_level', methods=['POST', 'GET'])
def change_level():
    level_id = request.form["level_id"]
    student_id = request.form["student_id"]
    course_id = request.form["course_id"]

    cur.execute("Update coursestudent set levelid = '%s' "
                "WHERE TEACHERID= '%s' and studentid='%s' and courseid='%s'" %
                (level_id, session['teacher'], student_id, course_id))

    cur.execute('commit')

    cur.execute("select a.studentname, b.levelname, c.timestart, c.timefinish, "
                "d.course_name, c.weekday, a.studentid, d.courseid "
                "from student a, course_level b, coursestudent c, course d "
                "WHERE a.studentid=c.studentid and b.levelid=c.levelid and c.courseid=d.courseid and "
                "c.TEACHERID= '%s' and a.studentid='%s' and d.courseid='%s'" %
                (session['teacher'], student_id, course_id))

    student = cur.fetchone()

    cur.execute("select a.leavetime, b.studentid from studentleave a, coursestudent b, studentleaving c "
                "where a.leaveid=c.leaveid and b.studentid=c.studentid and "
                "b.teacherid='%s' and a.approval = 'Approved' "
                "and a.leavetime>TRUNC(SYSDATE-14) and a.leavetime<TRUNC(SYSDATE+28) "
                "and b.studentid= '%s'" % (session['teacher'], student_id))

    leave_list = cur.fetchall()
    leave_no = len(leave_list)

    Start_Time = []
    End_Time = []
    now = student[2]
    start = now.strftime("%H:%M")
    finish = student[3]
    end = finish.strftime("%H:%M")

    Start_Time.append(start)
    End_Time.append(end)

    leave_date = []
    for i in range(leave_no):
        date = leave_list[i][0]
        date = date.strftime("%d/ %m/ %Y")
        leave_date.append(date)

    cur.execute("select a.leaveid, b.timestart, b.timefinish from "
                "studentleave a, makeupclass b, teachernewclass c, studentleaving d, student e, "
                "course f, course_level g where "
                "a.leaveid=b.leaveid and a.leaveid=c.leaveid and b.classid=c.classid and "
                "a.leaveid=d.leaveid and d.studentid=e.studentid and a.courseid=f.courseid "
                "and a.levelid=g.levelid and c.teacherid = '%s' and d.studentid = '%s' and "
                "b.timestart>TRUNC(SYSDATE) and b.timestart<TRUNC(SYSDATE+28) "
                "order by b.timestart" % (session['teacher'], student_id))

    class_list = cur.fetchall()
    class_no = len(class_list)

    class_date = []
    class_start = []
    class_end = []
    for i in range(class_no):
        date = class_list[i][1]
        date = date.strftime("%d/ %m/ %Y")
        class_date.append(date)

        date = class_list[i][1]
        start = date.strftime("%H:%M")
        class_start.append(start)

        date = class_list[i][2]
        end = date.strftime("%H:%M")
        class_end.append(end)

    return render_template('studentrecord.html', student=student, Start_Time=Start_Time, End_Time=End_Time,
                           leave_date=leave_date, leave_list=leave_list, leave_no=leave_no, class_start=class_start,
                           class_date=class_date, class_list=class_list, class_no=class_no, class_end=class_end)


# Application for make-up class
@app.route('/add_class', methods=['POST', 'GET'])
def add_class():
    student_id = request.form["student_id"]
    course_id = request.form["course_id"]

    cur.execute("select a.leavetime, b.studentid from studentleave a, coursestudent b, studentleaving c "
                "where a.leaveid=c.leaveid and b.studentid=c.studentid and "
                "b.teacherid='%s' and a.approval = 'Approved' "
                "and a.leavetime>TRUNC(SYSDATE) and a.leavetime<TRUNC(SYSDATE+28) "
                "and b.studentid= '%s' and a.courseid = '%s' "
                "order by a.leavetime" % (session['teacher'], student_id, course_id))

    leave_list = cur.fetchall()
    leave_no = len(leave_list)

    cur.execute("select c.studentname, b.leavetime, b.leaveid, a.attentid, a.levelid, d.levelname, "
                "e.course_name "
                "from studentattent a, studentleave b, student c, course_level d, course e "
                "where a.leaveid=b.leaveid and c.studentid = a.studentid and a.levelid=d.levelid "
                "and a.courseid=e.courseid and a.classid is null and a.arrivaltime is null and "
                "a.leaveid is not null and b.needclass = 'Yes' and b.approval = 'Approved' "
                "and a.teacherid = '%s'" % session['teacher'])

    class_list = cur.fetchall()
    class_no = len(class_list)

    leave_date = []
    leave_time = []
    for i in range(leave_no):
        date = leave_list[i][0]
        date = date.strftime("%d/ %m/ %Y")
        leave_date.append(date)
        date = leave_list[i][0]
        start = date.strftime("%H:%M")
        leave_time.append(start)

    class_date = []
    for i in range(class_no):
        date = class_list[i][1]
        date = date.strftime("%d/ %m/ %Y")
        class_date.append(date)

    return render_template('add_class.html', leave_date=leave_date, leave_list=leave_list, leave_no=leave_no,
                           class_date=class_date, class_list=class_list, class_no=class_no, leave_time=leave_time)


# Adding make-up class SQL
@app.route('/adding_class', methods=['POST', 'GET'])
def adding_class():
    class_time = request.form["class_time"]
    leave_id = request.form["leave_id"]

    class_time = datetime.datetime.strptime(class_time, '%Y-%m-%d %H:%M:%S')

    class_end = class_time + datetime.timedelta(minutes=30)

    cur.execute("Insert into makeupclass(Classid, timestart, timefinish, leaveid) "
                "Values (classid_SEQUENCE.nextval, Timestamp'%s', Timestamp'%s', '%s')" %
                (class_time, class_end, leave_id))
    cur.execute("commit")

    cur.execute("Insert into teachernewclass(Classid, leaveid, teacherid) "
                "Values (classid_SEQUENCE.currval, '%s','%s')" % (leave_id, session['teacher']))
    cur.execute("commit")

    cur.execute("Update studentattent set "
                "Classid = classid_SEQUENCE.currval, teacherid = '%s' where"
                " leaveid = '%s'" % (session['teacher'], leave_id))
    cur.execute("commit")

    return redirect(url_for('class_record'))


# Make-up class record
@app.route('/class_record')
def class_record():
    cur.execute("select a.leaveid, b.classid, e.studentname, a.leavetime, b.timestart, b.timefinish,"
                " f.course_name, g.levelname from "
                "studentleave a, makeupclass b, teachernewclass c, studentleaving d, student e, "
                "course f, course_level g where "
                "a.leaveid=b.leaveid and a.leaveid=c.leaveid and b.classid=c.classid and "
                "a.leaveid=d.leaveid and d.studentid=e.studentid and a.courseid=f.courseid "
                "and a.levelid=g.levelid and c.teacherid = '%s' "
                "order by b.timestart" % (session['teacher']))

    class_list = cur.fetchall()
    class_no = len(class_list)

    leave_date = []

    class_date = []
    class_start = []
    class_end = []
    for i in range(class_no):
        date = class_list[i][3]
        date = date.strftime("%d/ %m/ %Y")
        leave_date.append(date)

        date = class_list[i][4]
        date = date.strftime("%d/ %m/ %Y")
        class_date.append(date)

        date = class_list[i][4]
        start = date.strftime("%H:%M")
        class_start.append(start)

        date = class_list[i][5]
        end = date.strftime("%H:%M")
        class_end.append(end)

    return render_template('class_record.html', leave_date=leave_date, class_list=class_list, class_no=class_no,
                           class_date=class_date, class_start=class_start, class_end=class_end)


# Check Salary
@app.route('/salary')
def salary():
    cur.execute("SELECT c.studentname, b.course_name, d.levelname, d.price, COUNT(*) "
                "FROM studentattent a,course b,student c,course_level d Where "
                # Find normal lesson
                "(a.courseid=b.courseid and a.studentid=c.studentid and a.levelid=d.levelid and"
                " a.leaveid is null and a.classid is null and "
                "to_char( sysdate, 'yyyy-mm' ) =  to_char( a.arrivaltime, 'yyyy-mm' ) and "
                "a.teacherid = '%s') "
                # Find make-up class
                "Or (a.courseid=b.courseid and a.studentid=c.studentid and a.levelid=d.levelid and "
                "a.classid is not null and "
                "to_char( sysdate, 'yyyy-mm' ) =  to_char( a.arrivaltime, 'yyyy-mm' ) and a.teacherid = '%s') "
                # Find lesson that teacher not approve to leave
                "Or (a.courseid=b.courseid and a.studentid=c.studentid and a.levelid=d.levelid and "
                "to_char( sysdate, 'yyyy-mm' ) =  to_char( a.coursetime, 'yyyy-mm' ) and "
                "a.arrivaltime = '31-JAN-20 12.00.00.000000000 AM' and a.teacherid = '%s') "

                "GROUP BY c.studentname, b.course_name, d.levelname, d.price" %
                (session['teacher'], session['teacher'], session['teacher']))

    salary_list = cur.fetchall()
    salary_no = len(salary_list)

    total_list = []

    for i in range(salary_no):
        course_price = salary_list[i][3]
        no = salary_list[i][4]
        if salary_list[i][2] == 'violin' \
                                'interest' or salary_list[i][2] == 'guitar' \
                                                                   'interest' or salary_list[i][2] == 'flute' \
                                                                                                      'interest':
            total = (course_price / 8 * no) / 2
        else:
            total = (course_price / 4 * no) / 2
        total_list.append(total)

    total_salary = sum(total_list)
    return render_template('salary.html', total_salary=total_salary, salary_list=salary_list, salary_no=salary_no,
                           total_list=total_list)


# Contact student page
@app.route('/contact_student')
def contact_student():
    cur.execute("select a.message, a.messagetime, b.studentname from "
                "StudentMessage a, student b, studmes_staff c, StudentMesID d "
                "where a.Messageid=c.Messageid and d.studentid=b.studentid and a.Messageid=d.Messageid and "
                "c.staffid='%s'" % session['teacher'])
    received = cur.fetchall()
    received_no = len(received)

    cur.execute("select a.message, a.messagetime, b.studentname from "
                "TeacherMessage a, student b, TeacherMesid c, STDTEACHMES d "
                "where a.Messageid=c.Messageid and d.studentid=b.studentid and a.Messageid=d.Messageid and "
                "c.staffid='%s'" % session['teacher'])
    message = cur.fetchall()
    message_no = len(message)

    cur.execute("select a.studentid, b.studentname from coursestudent a, student b "
                "where a.studentid=b.studentid and a.teacherid='%s'" % session['teacher'])
    student = cur.fetchall()
    student_no = len(student)
    return render_template('contact_student.html', student=student, student_no=student_no, message=message,
                           message_no=message_no, received=received, received_no=received_no)


# Add student message
@app.route('/write_student_message', methods=['POST', 'GET'])
def write_student_message():
    StudentID = request.form["student_id"]
    message = request.form['message']

    cur.execute("INSERT INTO StudentMessage (Messageid, Message, MessageTime) VALUES ("
                "StudentMessageid_SEQUENCE.nextval,'%s', Current_Timestamp) " % message)
    cur.execute('commit')

    cur.execute("INSERT INTO studmes_staff (Messageid, Staffid) VALUES ("
                "StudentMessageid_SEQUENCE.currval,'%s') " % session['teacher'])
    cur.execute('commit')

    cur.execute("INSERT INTO StudentMesID (Messageid, Studentid) VALUES ("
                "StudentMessageid_SEQUENCE.currval,'%s') " % StudentID)
    cur.execute('commit')

    return redirect(url_for('contact_student'))
# ________________Staff Login_________________________________________________
@app.route('/staff_login')
def staff_login():
    if 'staff' in session:
        return redirect(url_for('main_menu'))
    error = None
    return render_template('staff_login.html', error=error)


@app.route('/logoutstaff')
def logoutstaff():
    session.pop('staff', None)
    return redirect(url_for('index'))


@app.route('/main_menu', methods=['POST', 'GET'])
def main_menu():
    if 'staff' in session:
        UserID = session['staff']
        cur.execute("SELECT StaffID, StaffNAME, PASSWORD, Gender, worktype FROM Staff WHERE StaffID= %s" % UserID)

        result = cur.fetchone()
        cur.execute('commit')
        return render_template('main_menu.html', result=result)

    elif request.method == 'POST':
        session.pop = ('staff', None)
        UserID = request.form["UserID"]
        pwd = request.form['password']

        cur.execute("SELECT StaffID, StaffNAME, PASSWORD, Gender, worktype FROM Staff WHERE StaffID= %s" % UserID)

        result = cur.fetchone()
        cur.execute('commit')
        if result is None:
            error = "Do not have this user"
            return render_template('staff_login.html', error=error)

        if result[4] != "Manager":
            error = "Do not have right to use the system"
            return render_template('staff_login.html', error=error)
        password = result[2]

        if pwd == password:
            session['staff'] = UserID
            print(result)
            return render_template('main_menu.html', result=result)
        error = "Invalid user id or password"
        return render_template('staff_login.html', error=error)
    else:
        error = None
        return render_template('staff_login.html', error=error)


# __________________________ Add New Teacher____________________________________________
@app.route('/add_teacher')
def add_teacher():
    name = None
    return render_template('add_teacher.html', name=name)


# SQL add teacher
@app.route('/adding_teacher', methods=['POST', 'GET'])
def adding_teacher():
    if request.method == 'POST':
        name = request.form["UserName"]
        email = request.form["email"]
        address = request.form["address"]
        gender = request.form["gender"]
        phone = int(request.form["phone"])
        pwd = request.form['pwd']
        course_name = request.form['course']

        cur.execute("INSERT INTO STAFF (STAFFID, STAFFNAME, GENDER, PHONE, EMAIL, ADDRESS, PASSWORD,WORKTYPE) VALUES ("
                    "STAFF_SEQUENCE.nextval, '%s','%s', '%d', '%s', '%s', '%s','Teacher') " % (
                        name, gender, phone, email, address, pwd))

        cur.execute('commit')

        cur.execute("SELECT courseid FROM course WHERE course_name= '%s'" % course_name)
        result = cur.fetchone()
        cur.execute('commit')
        CourseID = result[0]

        cur.execute("INSERT INTO TEACHER_COURSE (TEACHERID, COURSEID) VALUES ("
                    "STAFF_SEQUENCE.CURRVAL, '%s') " % CourseID)

        cur.execute('commit')
        cur.execute("Select Max(StaffID) from staff ")
        staff_id = cur.fetchone()
        teacher_id = staff_id[0]

        cur.execute('commit')

        return render_template('add_teacher.html', name=name, teacher_id=teacher_id)


# ______________________Staff Account Management____________________
# show staff information
@app.route('/staff_account')
def staff_account():
    if 'staff' in session:
        cur.execute("SELECT STAFFID, STAFFNAME, GENDER, PHONE, EMAIL, ADDRESS, PASSWORD FROM Staff WHERE "
                    "StaffID= %s" % (session['staff']))

        result = cur.fetchone()
        cur.execute('commit')

        return render_template('staff_account.html', result=result)
    return render_template('home.html')


# Change account information
@app.route('/change_staff')
def change_staff():
    if 'staff' in session:
        cur.execute("SELECT STAFFID, STAFFNAME, GENDER, PHONE, EMAIL, ADDRESS, PASSWORD FROM Staff WHERE "
                    "StaffID= %s" % (session['staff']))

        result = cur.fetchone()
        cur.execute('commit')
        return render_template('change_staff.html', result=result)
    return render_template('home.html')


@app.route('/changed_staff', methods=['POST', 'GET'])
def changed_staff():
    if 'staff' in session:
        name = request.form["UserName"]
        email = request.form["email"]
        address = request.form["address"]
        phone = int(request.form["phone"])
        pwd = request.form['pwd']

        cur.execute("Update STAFF Set STAFFNAME ='%s' , PHONE='%d',"
                    " EMAIL='%s', ADDRESS='%s', PASSWORD='%s'"
                    "Where StaffID= %s" % (
                        name, phone, email, address, pwd, session['staff']))
        cur.execute('commit')

        return redirect(url_for('staff_account'))


# _________________________Student Attendance Management___________________________
@app.route('/take_attendance')
def take_attendance():
    return render_template('take_attendance.html')


@app.route('/show_attendant', methods=['POST', 'GET'])
def show_attendant():
    student_id = request.form["student_id"]
    cur.execute("select c.studentname, d.staffname, a.attentid, a.coursetime, b.weekday, "
                "e.course_name, a.classid from studentattent a, coursestudent b, student c, staff d, course e "
                "where a.studentid=c.studentid and a.studentid=b.studentid and a.teacherid=d.staffid and "
                "a.courseid=e.courseid and b.teacherid=d.staffid and a.coursetime>=TRUNC(SYSDATE) "
                "and a.coursetime<TRUNC(SYSDATE+14) and a.studentid='%s' and a.arrivaltime is null "
                "and a.leaveid is null "
                "order by coursetime" % student_id)

    result = cur.fetchall()

    cur.execute("select a.leaveid, c.timestart, b.coursetime, c.timefinish,d.studentname, e.staffname, "
                "b.attentid, e.levelname, f.course_name "
                "from studentleave a, studentattent b, makeupclass c, student d, staff e, "
                "course f, course_level e WHERE a.leaveid=b.leaveid and b.classid=c.classid "
                "and b.studentid=d.studentid and b.teacherid=e.staffid and b.courseid=f.courseid "
                "and b.levelid=e.levelid and b.arrivaltime is null and c.timestart>=TRUNC(SYSDATE) "
                "and c.timestart<TRUNC(SYSDATE+28) and b.studentid='%s'"
                "order by c.timestart" % student_id)

    class_list = cur.fetchall()

    CourseTime = []
    CourseDate = []
    Course_num = len(result)
    for i in range(Course_num):
        course_start = result[i][3]
        time = course_start.strftime("%H:%M")
        CourseTime.append(time)
        date = course_start.strftime("%d/%m/%Y")
        CourseDate.append(date)

    class_no = len(class_list)
    leave_date = []

    class_date = []
    class_start = []
    class_end = []
    for i in range(class_no):
        date = class_list[i][2]
        date = date.strftime("%d/ %m/ %Y")
        leave_date.append(date)

        date = class_list[i][1]
        date = date.strftime("%d/ %m/ %Y")
        class_date.append(date)

        date = class_list[i][1]
        start = date.strftime("%H:%M")
        class_start.append(start)

        date = class_list[i][3]
        end = date.strftime("%H:%M")
        class_end.append(end)

    Name = None
    Date = None

    return render_template('show_attendant.html', result=result, CourseDate=CourseDate, CourseTime=CourseTime,
                           Course_num=Course_num, Name=Name, Date=Date, leave_date=leave_date, class_list=class_list,
                           class_no=class_no, class_date=class_date, class_start=class_start, class_end=class_end)


@app.route('/taking_attend', methods=['POST', 'GET'])
def taking_attend():
    attend_id = request.form["attend_id"]
    cur.execute("Update studentattent set arrivaltime = Current_Timestamp Where attentid='%s'" %
                attend_id)
    cur.execute('commit')

    cur.execute("Select studentid from studentattent where attentid='%s'" % attend_id)
    student = cur.fetchone()
    cur.execute('commit')

    student_id = student[0]
    cur.execute("select c.studentname, d.staffname, a.attentid, a.coursetime, b.weekday, "
                "e.course_name, a.classid from studentattent a, coursestudent b, student c, staff d, course e "
                "where a.studentid=c.studentid and a.studentid=b.studentid and a.teacherid=d.staffid and "
                "a.courseid=e.courseid and b.teacherid=d.staffid and a.coursetime>=TRUNC(SYSDATE) "
                "and a.coursetime<TRUNC(SYSDATE+14) and a.studentid='%s' and a.arrivaltime is null "
                "and a.leaveid is null "
                "order by coursetime" % student_id)

    result = cur.fetchall()

    cur.execute("select a.leaveid, c.timestart, b.coursetime, c.timefinish,d.studentname, e.staffname, "
                "b.attentid, e.levelname, f.course_name "
                "from studentleave a, studentattent b, makeupclass c, student d, staff e, "
                "course f, course_level e WHERE a.leaveid=b.leaveid and b.classid=c.classid "
                "and b.studentid=d.studentid and b.teacherid=e.staffid and b.courseid=f.courseid "
                "and b.levelid=e.levelid and b.arrivaltime is null and c.timestart>=TRUNC(SYSDATE) "
                "and c.timestart<TRUNC(SYSDATE+28) and b.studentid='%s'"
                "order by c.timestart" % student_id)

    class_list = cur.fetchall()

    CourseTime = []
    CourseDate = []
    Course_num = len(result)
    for i in range(Course_num):
        course_start = result[i][3]
        time = course_start.strftime("%H:%M")
        CourseTime.append(time)
        date = course_start.strftime("%d/%m/%Y")
        CourseDate.append(date)

    class_no = len(class_list)
    leave_date = []

    class_date = []
    class_start = []
    class_end = []
    for i in range(class_no):
        date = class_list[i][2]
        date = date.strftime("%d/ %m/ %Y")
        leave_date.append(date)

        date = class_list[i][1]
        date = date.strftime("%d/ %m/ %Y")
        class_date.append(date)

        date = class_list[i][1]
        start = date.strftime("%H:%M")
        class_start.append(start)

        date = class_list[i][3]
        end = date.strftime("%H:%M")
        class_end.append(end)

    Name = request.form["Name"]
    Date = request.form["Date"]

    return render_template('show_attendant.html', result=result, CourseDate=CourseDate, CourseTime=CourseTime,
                           Course_num=Course_num, Name=Name, Date=Date, leave_date=leave_date, class_list=class_list,
                           class_no=class_no, class_date=class_date, class_start=class_start, class_end=class_end)


@app.route('/late_attend')
def late_attend():
    cur.execute("select c.studentname, d.staffname, a.attentid, a.coursetime, b.weekday, e.course_name, a.classid from "
                "studentattent a, coursestudent b, student c, staff d, course e where a.studentid=c.studentid and "
                "a.studentid=b.studentid and a.studentid=c.studentid and a.teacherid=d.staffid  and "
                "a.courseid=e.courseid and b.studentid=c.studentid and b.teacherid=d.staffid and a.coursetime<TRUNC("
                "SYSDATE) and a.arrivaltime is null and a.leaveid is null "
                "order by coursetime")

    result = cur.fetchall()
    cur.execute('commit')
    CourseTime = []
    CourseDate = []
    Course_num = len(result)
    for i in range(Course_num):
        course_start = result[i][3]
        time = course_start.strftime("%H:%M")
        CourseTime.append(time)
        date = course_start.strftime("%d/%m/%Y")
        CourseDate.append(date)

    cur.execute("select a.leaveid, c.timestart, b.coursetime, c.timefinish,d.studentname, e.staffname, "
                "b.attentid, e.levelname, f.course_name "
                "from studentleave a, studentattent b, makeupclass c, student d, staff e, "
                "course f, course_level e WHERE a.leaveid=b.leaveid and b.classid=c.classid "
                "and b.studentid=d.studentid and b.teacherid=e.staffid and b.courseid=f.courseid "
                "and b.levelid=e.levelid and b.arrivaltime is null and c.timestart<TRUNC(SYSDATE) "
                "order by c.timestart")

    class_list = cur.fetchall()

    CourseTime = []
    CourseDate = []
    Course_num = len(result)
    for i in range(Course_num):
        course_start = result[i][3]
        time = course_start.strftime("%H:%M")
        CourseTime.append(time)
        date = course_start.strftime("%d/%m/%Y")
        CourseDate.append(date)

    class_no = len(class_list)
    leave_date = []

    class_date = []
    class_start = []
    class_end = []
    for i in range(class_no):
        date = class_list[i][2]
        date = date.strftime("%d/ %m/ %Y")
        leave_date.append(date)

        date = class_list[i][1]
        date = date.strftime("%d/ %m/ %Y")
        class_date.append(date)

        date = class_list[i][1]
        start = date.strftime("%H:%M")
        class_start.append(start)

        date = class_list[i][3]
        end = date.strftime("%H:%M")
        class_end.append(end)

    Name = None
    Date = None
    marked = None
    return render_template('late_attend.html', result=result, CourseDate=CourseDate, CourseTime=CourseTime,
                           Course_num=Course_num, Name=Name, Date=Date, leave_date=leave_date, class_list=class_list,
                           class_no=class_no, class_date=class_date, class_start=class_start, class_end=class_end,
                           marked=marked)


@app.route('/mark_attend', methods=['POST', 'GET'])
def mark_attend():
    attend_id = request.form["attend_id"]
    Name = request.form["Name"]
    Date = request.form["Date"]
    cur.execute("Update studentattent set arrivaltime = TimeStamp'2020-01-31 00:00:00.00' Where attentid='%s'" %
                attend_id)
    cur.execute('commit')

    cur.execute("select c.studentname, d.staffname, a.attentid, a.coursetime, b.weekday, e.course_name, a.classid from "
                "studentattent a, coursestudent b, student c, staff d, course e where a.studentid=c.studentid and "
                "a.studentid=b.studentid and a.studentid=c.studentid and a.teacherid=d.staffid  and "
                "a.courseid=e.courseid and b.studentid=c.studentid and b.teacherid=d.staffid and a.coursetime<TRUNC("
                "SYSDATE) and a.arrivaltime is null and a.leaveid is null "
                "order by coursetime")

    result = cur.fetchall()
    cur.execute('commit')
    CourseTime = []
    CourseDate = []
    Course_num = len(result)
    for i in range(Course_num):
        course_start = result[i][3]
        time = course_start.strftime("%H:%M")
        CourseTime.append(time)
        date = course_start.strftime("%d/%m/%Y")
        CourseDate.append(date)

    cur.execute("select a.leaveid, c.timestart, b.coursetime, c.timefinish,d.studentname, e.staffname, "
                "b.attentid, e.levelname, f.course_name "
                "from studentleave a, studentattent b, makeupclass c, student d, staff e, "
                "course f, course_level e WHERE a.leaveid=b.leaveid and b.classid=c.classid "
                "and b.studentid=d.studentid and b.teacherid=e.staffid and b.courseid=f.courseid "
                "and b.levelid=e.levelid and b.arrivaltime is null and c.timestart<TRUNC(SYSDATE) "
                "order by c.timestart")

    class_list = cur.fetchall()

    CourseTime = []
    CourseDate = []
    Course_num = len(result)
    for i in range(Course_num):
        course_start = result[i][3]
        time = course_start.strftime("%H:%M")
        CourseTime.append(time)
        date = course_start.strftime("%d/%m/%Y")
        CourseDate.append(date)

    class_no = len(class_list)
    leave_date = []

    class_date = []
    class_start = []
    class_end = []
    for i in range(class_no):
        date = class_list[i][2]
        date = date.strftime("%d/ %m/ %Y")
        leave_date.append(date)

        date = class_list[i][1]
        date = date.strftime("%d/ %m/ %Y")
        class_date.append(date)

        date = class_list[i][1]
        start = date.strftime("%H:%M")
        class_start.append(start)

        date = class_list[i][3]
        end = date.strftime("%H:%M")
        class_end.append(end)

    marked = None
    return render_template('late_attend.html', result=result, CourseDate=CourseDate, CourseTime=CourseTime,
                           Course_num=Course_num, Name=Name, Date=Date, leave_date=leave_date, class_list=class_list,
                           class_no=class_no, class_date=class_date, class_start=class_start, class_end=class_end,
                           marked=marked)


@app.route('/mark_leave', methods=['POST', 'GET'])
def mark_leave():
    attend_id = request.form["attend_id"]
    name = request.form["Name"]
    date = request.form["Date"]
    cur.execute("Select levelid, coursetime, courseid, studentid from studentattent Where attentid='%s'" %
                attend_id)
    result_1 = cur.fetchone()
    cur.execute('commit')

    level_id = result_1[0]
    coursetime = result_1[1]
    courseid = result_1[2]
    studentid = result_1[3]

    cur.execute("insert into studentleave(leaveid, levelid, leavetime, reason, needclass, approval, courseid) "
                "values(leaveid_SEQUENCE.nextval, '%s', TimeStamp'%s', 'Illness/ Holiday', 'Yes','Approved','%s')" %
                (level_id, coursetime, courseid))
    cur.execute("commit")

    cur.execute("insert into studentleaving(leaveid, studentid) "
                "values(leaveid_SEQUENCE.currval, '%s')" % studentid)
    cur.execute("commit")

    cur.execute("Update studentattent set leaveid = leaveid_SEQUENCE.currval Where attentid='%s'" %
                attend_id)
    cur.execute('commit')

    cur.execute("select c.studentname, d.staffname, a.attentid, a.coursetime, b.weekday, e.course_name, a.classid from "
                "studentattent a, coursestudent b, student c, staff d, course e where a.studentid=c.studentid and "
                "a.studentid=b.studentid and a.studentid=c.studentid and a.teacherid=d.staffid  and "
                "a.courseid=e.courseid and b.studentid=c.studentid and b.teacherid=d.staffid and a.coursetime<TRUNC("
                "SYSDATE) and a.arrivaltime is null and a.leaveid is null "
                "order by coursetime")

    result = cur.fetchall()
    cur.execute('commit')
    CourseTime = []
    CourseDate = []
    Course_num = len(result)
    for i in range(Course_num):
        course_start = result[i][3]
        time = course_start.strftime("%H:%M")
        CourseTime.append(time)
        date = course_start.strftime("%d/%m/%Y")
        CourseDate.append(date)

    cur.execute("select a.leaveid, c.timestart, b.coursetime, c.timefinish,d.studentname, e.staffname, "
                "b.attentid, e.levelname, f.course_name "
                "from studentleave a, studentattent b, makeupclass c, student d, staff e, "
                "course f, course_level e WHERE a.leaveid=b.leaveid and b.classid=c.classid "
                "and b.studentid=d.studentid and b.teacherid=e.staffid and b.courseid=f.courseid "
                "and b.levelid=e.levelid and b.arrivaltime is null and c.timestart<TRUNC(SYSDATE) "
                "order by c.timestart")

    class_list = cur.fetchall()

    CourseTime = []
    CourseDate = []
    Course_num = len(result)
    for i in range(Course_num):
        course_start = result[i][3]
        time = course_start.strftime("%H:%M")
        CourseTime.append(time)
        date = course_start.strftime("%d/%m/%Y")
        CourseDate.append(date)

    class_no = len(class_list)
    leave_date = []

    class_date = []
    class_start = []
    class_end = []
    for i in range(class_no):
        date = class_list[i][2]
        date = date.strftime("%d/ %m/ %Y")
        leave_date.append(date)

        date = class_list[i][1]
        date = date.strftime("%d/ %m/ %Y")
        class_date.append(date)

        date = class_list[i][1]
        start = date.strftime("%H:%M")
        class_start.append(start)

        date = class_list[i][3]
        end = date.strftime("%H:%M")
        class_end.append(end)

    Name = None
    Date = None
    marked = ''
    return render_template('late_attend.html', result=result, CourseDate=CourseDate, CourseTime=CourseTime,
                           Course_num=Course_num, Name=Name, Date=Date, leave_date=leave_date, class_list=class_list,
                           class_no=class_no, class_date=class_date, class_start=class_start, class_end=class_end,
                           marked=marked, name=name, date=date)


# __________________Teacher Leave Approval__________________________________
@app.route('/teacher_leave_approval')
def teacher_leave_approval():
    cur.execute("select a.leaveid, a.leavetime, a.reason, a.approval, c.staffname "
                "from staffleave a, staff_staffleave b, staff c where a.leaveid=b.leaveid and "
                "b.staffid=c.staffid and a.approval='Processing'")
    leave_list = cur.fetchall()
    num = len(leave_list)

    leave_date = []
    for i in range(num):
        date = leave_list[i][1]
        date = date.strftime("%d/ %m/ %Y")
        leave_date.append(date)

    cur.execute('commit')
    Name = None

    return render_template('teacher_leave_approval.html', leave_date=leave_date, num=num,
                           leave_list=leave_list, Name=Name)


@app.route('/approve_leave_teacher', methods=['POST', 'GET'])
def approve_leave_teacher():
    leave_id = request.form["leave_id"]
    Name = request.form["Name"]
    Date = request.form["Date"]

    cur.execute("Update staffleave set approval='Approved' Where leaveid='%s'" %
                leave_id)
    cur.execute('commit')
    Not = ''

    cur.execute("select a.leaveid, a.leavetime, a.reason, a.approval, c.staffname "
                "from staffleave a, staff_staffleave b, staff c where a.leaveid=b.leaveid and "
                "b.staffid=c.staffid and a.approval='Processing'")
    leave_list = cur.fetchall()
    num = len(leave_list)

    leave_date = []
    for i in range(num):
        date = leave_list[i][1]
        date = date.strftime("%d/ %m/ %Y")
        leave_date.append(date)

    cur.execute('commit')

    return render_template('teacher_leave_approval.html', leave_date=leave_date, num=num,
                           leave_list=leave_list, Name=Name, Not=Not, Date=Date)


@app.route('/not_approve_teacher', methods=['POST', 'GET'])
def not_approve_teacher():
    leave_id = request.form["leave_id"]
    Name = request.form["Name"]
    Date = request.form["Date"]

    cur.execute("Update staffleave set approval='Not Approved' Where leaveid='%s'" %
                leave_id)
    cur.execute('commit')
    Not = 'not'

    cur.execute("select a.leaveid, a.leavetime, a.reason, a.approval, c.staffname "
                "from staffleave a, staff_staffleave b, staff c where a.leaveid=b.leaveid and "
                "b.staffid=c.staffid and a.approval='Processing'")
    leave_list = cur.fetchall()
    num = len(leave_list)

    leave_date = []
    for i in range(num):
        date = leave_list[i][1]
        date = date.strftime("%d/ %m/ %Y")
        leave_date.append(date)

    cur.execute('commit')

    return render_template('teacher_leave_approval.html', leave_date=leave_date, num=num,
                           leave_list=leave_list, Name=Name, Not=Not, Date=Date)


# ______________________Give Notice_________________________________________________
@app.route('/notice')
def notice():
    cur.execute("select a.Noticeid, a.noticetime, a.topic, a.message, b.staffname from "
                "Notice a, staff b, notice_staff c where "
                "a.noticeid=c.noticeid and b.staffid=c.staffid")

    result = cur.fetchall()
    cur.execute('commit')

    num = len(result)

    Topic = None

    return render_template('notice.html', result=result, num=num, Topic=Topic)


@app.route('/new_message', methods=['POST', 'GET'])
def new_message():
    Topic = request.form["topic"]
    message = request.form["message"]

    cur.execute("insert into notice(Noticeid, noticetime, topic, message) "
                "values(noticeid_SEQUENCE.nextval, Current_Timestamp, '%s','%s')" %
                (Topic, message))
    cur.execute("commit")

    cur.execute("insert into notice_staff(noticeid, staffid) "
                "values(noticeid_SEQUENCE.currval, '%s')" % session['staff'])
    cur.execute("commit")

    cur.execute("select a.Noticeid, a.noticetime, a.topic, a.message, b.staffname from "
                "Notice a, staff b, notice_staff c where "
                "a.noticeid=c.noticeid and b.staffid=c.staffid")

    result = cur.fetchall()
    cur.execute('commit')

    num = len(result)

    return render_template('notice.html', result=result, num=num, Topic=Topic)


@app.route('/staff_notice')
def staff_notice():
    cur.execute("select a.Noticeid, a.noticetime, a.topic, a.message, b.staffname from "
                "Notice a, staff b, notice_staff c where "
                "a.noticeid=c.noticeid and b.staffid=c.staffid "
                "order by a.noticetime desc")

    result = cur.fetchall()
    cur.execute('commit')

    num = len(result)

    return render_template('staff_notice.html', result=result, num=num)


# ___________________Student Contact Information_____________________________________
@app.route('/contact_teacher_id')
def contact_teacher_id():
    return render_template('contact_teacher_id.html')


@app.route('/show_student', methods=['POST', 'GET'])
def show_student():
    teacher_id = request.form["teacher_id"]
    cur.execute("select b.studentname, c.course_name, a.weekday, a.timestart, a.timefinish, b.phone "
                "from coursestudent a, student b, course c "
                "where a.studentid=b.studentid and a.courseid=c.courseid and a.teacherid = '%s' "
                "order by decode(a.weekday, 'Sun', 1, 'Mon', 2, 'Tue', 3, 'Wed', 4, 'Thur',5 , 'Fri', 6, 'Sat', 7, 8), "
                "a.timestart" % teacher_id)

    result = cur.fetchall()

    CourseTime = []
    Course_end = []
    Course_num = len(result)
    for i in range(Course_num):
        course_start = result[i][3]
        time = course_start.strftime("%H:%M")
        CourseTime.append(time)
        course_start = result[i][4]
        time = course_start.strftime("%H:%M")
        Course_end.append(time)

    return render_template('show_student.html', result=result, Course_end=Course_end, CourseTime=CourseTime,
                           Course_num=Course_num)


# Check Salary
@app.route('/income')
def income():
    cur.execute("SELECT b.course_name, d.levelname, d.price, COUNT(*) "
                "FROM studentattent a,course b,course_level d Where "
                # Find normal lesson
                "(a.courseid=b.courseid and a.levelid=d.levelid and"
                " a.leaveid is null and a.classid is null and "
                "to_char( sysdate, 'yyyy-mm' ) =  to_char( a.arrivaltime, 'yyyy-mm' )) "
                # Find make-up class
                "Or (a.courseid=b.courseid and a.levelid=d.levelid and "
                "a.classid is not null and "
                "to_char( sysdate, 'yyyy-mm' ) =  to_char( a.arrivaltime, 'yyyy-mm' )) "
                # Find lesson that teacher not approve to leave
                "Or (a.courseid=b.courseid and a.levelid=d.levelid and "
                "to_char( sysdate, 'yyyy-mm' ) =  to_char( a.coursetime, 'yyyy-mm' ) and "
                "a.arrivaltime = '31-JAN-20 12.00.00.000000000 AM' ) "

                "GROUP BY b.course_name, d.levelname, d.price")

    salary_list = cur.fetchall()
    salary_no = len(salary_list)

    total_list = []

    for i in range(salary_no):
        course_price = salary_list[i][2]
        no = salary_list[i][3]
        if salary_list[i][1] == 'violin' \
                                'interest' or salary_list[i][2] == 'guitar' \
                                                                   'interest' or salary_list[i][2] == 'flute' \
                                                                                                      'interest':
            total = (course_price / 8 * no) / 2
        else:
            total = (course_price / 4 * no) / 2
        total_list.append(total)

    total_salary = sum(total_list)
    return render_template('income.html', total_salary=total_salary, salary_list=salary_list, salary_no=salary_no,
                           total_list=total_list)


# ________________________invoice_____________________________________
@app.route('/make_invoice')
def make_invoice():
    return render_template('make_invoice.html')


@app.route('/lesson_fee', methods=['POST', 'GET'])
def lesson_fee():
    student_id = request.form["student_id"]
    cur.execute("select b.studentname, c.course_name, d.levelname,d.price,max(a.coursetime+7), "
                "e.courseid, e.studentid, e.levelid, e.teacherid "
                "from studentattent a, student b, course c, course_level d, coursestudent e "
                "where b.studentid = a.studentid and e.courseid=c.courseid and e.levelid=d.levelid "
                "and a.studentid=e.studentid and a.studentid= '%s' "
                "GROUP by e.courseid,b.studentname, e.studentid, c.course_name, "
                "d.levelname,d.price, e.levelid,e.teacherid"
                % student_id)

    result = cur.fetchall()
    num = len(result)

    lesson_date = []
    for i in range(num):
        date = result[i][4]
        date = date.strftime("%d/ %m/ %Y")
        lesson_date.append(date)

    cur.execute("select  b.studentname, c.course_name, d.levelname, d.price, COUNT(f.needclass), "
                "a.courseid, e.studentid, a.levelid, e.teacherid,(COUNT(f.needclass)*d.price/ 4) "
                "from studentattent a, student b, course c, course_level d, coursestudent e, studentleave f "
                "where b.studentid = a.studentid and a.courseid=c.courseid and a.levelid=d.levelid and "
                "a.studentid=e.studentid and a.leaveid=f.leaveid and f.needclass='No' and "
                "to_char( sysdate, 'yyyy-mm' ) =  to_char( f.leavetime, 'yyyy-mm' )"
                "and a.studentid= '%s' "
                "GROUP by a.courseid,b.studentname, e.studentid, c.course_name, "
                "d.levelname,d.price, a.levelid,e.teacherid"
                % student_id)

    result2 = cur.fetchall()
    num2 = len(result2)
    return render_template('lesson_fee.html', result=result, num=num, lesson_date=lesson_date, result2=result2,
                           num2=num2)


@app.route('/add_invoice', methods=['POST', 'GET'])
def add_invoice():
    student_id = request.form['student_id']
    method = request.form['pay']
    d = request.form['month']
    print(student_id)
    cur.execute("select c.course_name from coursestudent b, course c where"
                " b.courseid=c.courseid and b.studentid='%s'"
                % student_id)

    course_name_list = cur.fetchall()
    name_num = len(course_name_list)

    cur.execute("INSERT INTO invoice (invoiceid, paymethod, paytime, lesson_month) VALUES ("
                "invoiceid_seq.nextval, '%s', Current_Timestamp,TimeStamp'%s') " % (
                    method, d))
    cur.execute('commit')

    total = 0
    for i in range(name_num):
        teacher = 'teacher' + course_name_list[i][0]
        TeacherID = request.form[teacher]

        date = 'date' + course_name_list[i][0]
        time = request.form[date]

        course_id = 'course' + course_name_list[i][0]
        course_id = request.form[course_id]

        level_id = 'level' + course_name_list[i][0]
        level = request.form[level_id]

        price = 'price' + course_name_list[i][0]
        price = float(request.form[price])

        qty = 'qty' + course_name_list[i][0]
        qty = int(request.form[qty])

        total += price

        cur.execute("INSERT INTO invoiceitem (invoiceitemid, invoiceid, courseid, qty, totalprice, levelid) VALUES ("
                    "invoiceitemid_seq.nextval, invoiceid_seq.currval, '%s', '%s', '%s', '%s') " % (
                        course_id, qty, price, level))
        cur.execute('commit')
        # __________Insert attendance details (Base on the number of courses they have)_______________

        for a in range(qty):

            cur.execute("INSERT INTO studentattent (attentid, studentid, teacherid, levelid, coursetime, courseid) "
                        "VALUES (attentid_seq.nextval,'%s', '%s' , '%s', TimeStamp'%s', '%s') " % (
                            student_id, TeacherID, level, time, course_id))
            cur.execute('commit')
            cur.execute("select coursetime+7 from studentattent "
                        "where attentid=(select max(attentid) from studentattent)")
            time_list = cur.fetchone()
            time = time_list[0]
    # _____________________________insert invoice details__________________________________
    cur.execute("Update invoice set totalprice='%s' where invoiceid= (select max(invoiceid) from invoice)" % (
                    total))
    cur.execute('commit')

    cur.execute("INSERT INTO student_invoice(studentid, invoiceid) VALUES ("
                "'%s', invoiceid_seq.currval)" % student_id)
    cur.execute('commit')

    cur.execute("INSERT INTO invoice_staff(staffid, invoiceid) VALUES ("
                "'%s', invoiceid_seq.currval)" % (session['staff']))
    cur.execute('commit')

    return render_template('make_invoice.html')


if __name__ == '__main__':
    app.run(debug=True)
