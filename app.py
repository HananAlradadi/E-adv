# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# render_template عشان اقدر اسوي رن لصفحة html
import time
from datetime import timedelta, datetime
from re import search
import os
from pathlib import Path
import numpy as np
import pandas
import requests
from flask import Flask, render_template, request, redirect, url_for, session, send_file, Response

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import math

import pandas as pd
import json
from threading import Thread

E_ADVISOR_APP = Flask(__name__)
chrome_options = webdriver.ChromeOptions()
gohome = False
#chrome_options.headless = True

class ReverseProxied(object):

    def __init__(self, E_ADVISOR_APP):
            self.E_ADVISOR_APP = E_ADVISOR_APP

    def __call__(self, environ, start_response):
            # if one of x_forwarded or preferred_url is https, prefer it.
            forwarded_scheme = environ.get("HTTP_X_FORWARDED_PROTO", None)
            preferred_scheme = E_ADVISOR_APP.config.get("PREFERRED_URL_SCHEME", None)
            if "https" in [forwarded_scheme, preferred_scheme]:
                environ["wsgi.url_scheme"] = "https"
            return self.E_ADVISOR_APP(environ, start_response)

E_ADVISOR_APP = Flask(__name__)
shared_var = None
req_counter = 0
E_ADVISOR_APP.wsgi_app = ReverseProxied(E_ADVISOR_APP.wsgi_app)
chrome_options = webdriver.ChromeOptions()
settings = {
       "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local",
            "account": "",
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2
    }
prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings)}
chrome_options.add_experimental_option('prefs', prefs)
chrome_options.add_argument('--kiosk-printing')
driver = webdriver.Chrome(options=chrome_options)
firstReq = True
# تسجيل الدخول لاالخدمات الاكاديمية
def login(AS_USERNAME , AS_PASSWORD , user_type):

    if user_type == 'طالب':
        driver.get('https://eas.taibahu.edu.sa/TaibahReg/student_login.jsp')
    else:
        driver.get('https://eas.taibahu.edu.sa/TaibahReg/teachers_login.jsp')
    driver.find_element_by_xpath('/html/body/table/tbody/tr[4]/td/table[1]/tbody/tr[2]/td/form/table/tbody/tr[2]/td[2]/input').send_keys(AS_USERNAME)
    driver.find_element_by_xpath('/html/body/table/tbody/tr[4]/td/table[1]/tbody/tr[2]/td/form/table/tbody/tr[3]/td[2]/input').send_keys(AS_PASSWORD)
    driver.find_element_by_xpath('/html/body/table/tbody/tr[4]/td/table[1]/tbody/tr[2]/td/form/table/tbody/tr[4]/td[2]/div/input[1]').click()

def transcript_extraction ():
    transcript = driver.page_source
    soup = BeautifulSoup(transcript, "lxml")
    transcriptData = soup.findAll("table", {"border": "1"})
    tr = pd.read_html(str(transcriptData[1]), header=0, skiprows=(1))
    tr[0].drop(tr[0].tail(2).index, inplace=True)
    Studenttranscripts = tr[0]
    # transcriptsOfStudent
    for i in range(2, len(transcriptData)):
        tr = pd.read_html(str(transcriptData[i]), header=0, skiprows=(1))
        tr[0].drop(tr[0].tail(2).index, inplace=True)
        Studenttranscripts = pd.concat([Studenttranscripts, tr[0]], ignore_index=True)
    return [Studenttranscripts , tr]
def schedule_extraction() :
    Schedulepage = driver.page_source
    soup = BeautifulSoup(Schedulepage, "lxml")
    studentScheduleData = soup.findAll("table", {"border": "1", "width": "90%"})
    registerdeCreditsSchedule = 0
    if len(studentScheduleData) > 0:
        scheduleOfstudent = pd.read_html(str(studentScheduleData[0]))[0]
        registerdeCreditsSchedule = int(scheduleOfstudent.loc[scheduleOfstudent.index[-1], 'وحده'])
        scheduleOfstudent.drop(scheduleOfstudent.tail(1).index, inplace=True)
    return [scheduleOfstudent,registerdeCreditsSchedule]
def plan_extraction ():
    plan = driver.page_source
    soup = BeautifulSoup(plan, "lxml")
    planData = soup.findAll("table", {"border": "1"})
    tr = pd.read_html(str(planData[1]), header=0, skiprows=(1))
    Studentplan = tr[0]
    for i in range(2, len(planData)):
        tr = pd.read_html(str(planData[i]), header=0, skiprows=(1))
        Studentplan = pd.concat([Studentplan, tr[0]], ignore_index=True)
    return Studentplan
def Student_data_extraction() :
    global Advisor_Email
    global Student_Email
    global Studentsplan
    global GPA
    global studentclass
    global transcriptsOfStudent
    global studentSchedule
    global timeTableData
    global semester
    global registerdeCreditsSchedule
    global major
    major = driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/p/table[2]/tbody/tr[4]/td[2]').text
    Advisor_Email = driver.find_element_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/p/table[2]/tbody/tr[9]/td[2]").text
    Student_Email = driver.find_element_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/p/table[2]/tbody/tr[9]/td[1]").text
    GPA = float(driver.find_element_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/p/table[2]/tbody/tr[8]/td[2]").text)
    studentclass = driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/p/table[2]/tbody/tr[2]/td[2]').text
    semester = driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/p/table[2]/tbody/tr[5]/td[1]').text
    driver.find_element_by_link_text('عمليات أكاديمية').click()
    driver.find_element_by_link_text('السجل الاكاديمى').click()
    # سحب السجل الكاديمي
    transcriptsOfStudent = transcript_extraction()[0]
    # نهاية سحب السجل الاكاديمي
    driver.find_element_by_link_text('عمليات أكاديمية').click()
    driver.find_element_by_link_text('الخطة الدراسية').click()
    Studentsplan = plan_extraction()
        # الجدول الدراسي
    driver.find_element_by_link_text('عمليات أكاديمية').click()
    driver.find_element_by_link_text('الجدول الدراسي').click()
    studentSchedule = schedule_extraction()
    registerdeCreditsSchedule = studentSchedule[1]
    studentSchedule = studentSchedule[0]

    driver.get("https://eas.taibahu.edu.sa/TaibahReg/studentReplaceOptionalFreeCourses.do?ex=getCompSections&type=init")
    timeTable = driver.page_source
    soup1 = BeautifulSoup(timeTable, "lxml")
    timeTableData = soup1.findAll("table", {"border": "1"})
def timeTableDatas() :
        login(session.get('AS_USERNAME'), session.get('AS_PASSWORD'), session.get('user_type'))
        global avlbelAddDreap
        avlbelAddDreap = 'true'
        if session.get('user_type') == 'طالب':
         driver.get('https://eas.taibahu.edu.sa/TaibahReg/studentBasicData.do?ex=preEx')
         driver.find_element_by_link_text('عمليات أكاديمية').click()
         driver.find_element_by_link_text('الحذف والاضافة').click()
         if len(driver.find_elements_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table/tbody/tr/td/p')) > 0:
             avlbelAddDreap = 'false'
         driver.get("https://eas.taibahu.edu.sa/TaibahReg/studentReplaceOptionalFreeCourses.do?ex=getCompSections&type=init")


        elif session.get('user_type') == 'مرشد':

            driver.find_element_by_link_text('المرشدين الأكاديميين').click()

            driver.find_element_by_link_text('الحذف والاضافة لطالب').click()

            # ادخال معلومات الطالب stdNumber
            driver.find_element_by_id("stdNumber").send_keys(listOfStudenstID[0])
            driver.find_element_by_name("send").click()
            if len(driver.find_elements_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table/tbody/tr/td/p')) > 0:
                avlbelAddDreap = 'false'

            driver.find_element_by_link_text('المرشدين الأكاديميين').click()
            driver.find_element_by_link_text('مواعيد المقررات لقسم').click()
            # studyYear
            Select(driver.find_element_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table/tbody/tr[1]/td/select")).select_by_visible_text(studyYear)
            Select(driver.find_element_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table/tbody/tr[2]/td/select")).select_by_visible_text(semester)
            Select(driver.find_element_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table/tbody/tr[3]/td/select")).select_by_visible_text(StudyType)
            driver.find_element_by_xpath('//*[@id="faculty"]').click()
            #driver.find_element_by_xpath('//*[@id="faculty"]/select')
            Select(WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='faculty']/select")))).select_by_visible_text(college)
            Select(WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='branch']/select"))))
            #driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table/tbody/tr[4]/td/div/select')
            driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table/tbody/tr[6]/td/input').click()

            #/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table/tbody/tr[4]/td/div/select
        timeTable = driver.page_source
        soup1 = BeautifulSoup(timeTable, "lxml")
        timeTableData = soup1.findAll("table", {"border": "1"})
        allOfferedCourses = pd.read_html(str(timeTableData[1]))[0]

        return allOfferedCourses
def advisor_data_extraction() :
        global plansOfStudents
        global studentsClass
        global transcriptsOfStudents
        global college
        global StudyType
        global NamesOfStudents
        global listOfStudenstID
        global studentScheduleAndregisterdeCreditsList
        global studyYear
        global semester
        global studentsSchedule
        global studentZARorNot
        global major
        major = driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table/tbody/tr[2]/td[1]').text
        print(major)
        studentZARorNot = []
        plans = pd.read_csv('aa.csv')
        college = driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table/tbody/tr[2]/td[2]').text
            # المرشدين الأكاديميين
        driver.find_element_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[7]/th/a").click()
            # كشف الطلاب للمرشد
        driver.find_element_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[8]/td/div/table/tbody/tr[5]/td/div/a").click()
            # الدروب ليست حقت اختيار الفرع
        options = Select(driver.find_element_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table/tbody/tr[1]/td/select")).options
        for i in range(len(options)):
            try:
                Select(driver.find_element_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table/tbody/tr[1]/td/select")).select_by_index(i)
                driver.find_element_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table/tbody/tr[3]/td/input").click()
                NamesOfStudents = BeautifulSoup(driver.page_source, "lxml").find("table",{"align": "center", "border": "1"})
                name = driver.find_element_by_xpath( "/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table/tbody/tr[2]/td/table/tbody/tr[1]/td[1]").text.split(" ")
                #session['advisorName'] = name[0] + " " + name[-1]
                break
            except:
                # رجعنا لصفحة الدروب ليست نظرا لعدم وجود كشف الطلاب
                driver.back()
        studentsClass = []
        IDSOfStudents = NamesOfStudents.findAll("a", {"target": "_blank"})
        listOfStudenstID = []
        for i in range(len(IDSOfStudents)):
            listOfStudenstID.append(IDSOfStudents[i].text)
        plansOfStudents = []
        for i in range(len(listOfStudenstID)):
            driver.find_element_by_link_text(listOfStudenstID[i]).click()
            driver.switch_to.window(driver.window_handles[1])
            plansOfStudents.append(plan_extraction())
            studentsClass.append(driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr[1]/td/table[1]/tbody/tr[1]/td[2]').text)
            studentZARorNot.append(driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr[1]/td[1]/table[1]/tbody/tr[1]/td[2]').text)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        transcriptsOfStudents = []
        for i in range(len(listOfStudenstID)):
            # سحب السجل الاكاديمي للطالب
            driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[9]/th/a').click()
            driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[10]/td/div/table/tbody/tr[5]/td/div/a').click()
            driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table/tbody/tr[2]/td/div/input').send_keys(listOfStudenstID[i])
            driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table/tbody/tr[3]/td/div/input').click()
            # save a source of the trans Cript and get data
            transcriptTAM = transcript_extraction()
            tr = transcriptTAM[1]
            transcriptsOfStudents.append(transcriptTAM[0])
            SRC = pd.read_csv("مقررات اختياري في التخصص.csv")
            numsrc = len(tr[0].loc[tr[0]['أسم المادة'].isin(SRC['اسـم المقرّر'])])
            if numsrc > 0:
                for j in range(numsrc):
                    plansOfStudents[i].loc[plansOfStudents[i][plansOfStudents[i]['أسم المادة'].str.contains("مقرر اختياري في التخصص") & (plansOfStudents[i]['التقدير'].isna())].index[0], 'التقدير'] = 'مسجل'
            numre = len(tr[0].loc[(~tr[0]['أسم المادة'].isin(plans['أسم المادة'])) & tr[0]['رمز المادة'].str.contains("GS")])
            if numre > 0:
                for j in range(numre):
                    plansOfStudents[i].loc[plansOfStudents[i][plansOfStudents[i]['أسم المادة'].str.contains("متطلب جامعة اختياري") & (plansOfStudents[i]['التقدير'].isna())].index[0], 'التقدير'] = 'مسجل'
            numfre = len(tr[0].loc[(~tr[0]['أسم المادة'].isin(plans['أسم المادة'])) & (~tr[0]['رمز المادة'].str.contains("GS")) & (tr[0]['و.م'] == 2)])
            if numfre > 0:
                for j in range(numfre):
                    plansOfStudents[i].loc[plansOfStudents[i][plansOfStudents[i]['أسم المادة'].str.contains("مقرر اختياري حر") & (plansOfStudents[i]['التقدير'].isna())].index[0], 'التقدير'] = 'مسجل'

            if len(tr[0].loc[(~tr[0]['أسم المادة'].isin(plans['أسم المادة'])) & (~tr[0]['رمز المادة'].str.contains("GS")) & (tr[0]['و.م'] == 3) & (~tr[0]['أسم المادة'].isin(SRC['اسـم المقرّر']))]) > 0:
                plansOfStudents[i].loc[plansOfStudents[i][plansOfStudents[i]['أسم المادة'].str.contains("اختياري علوم طبيعية")].index[0], 'التقدير'] = 'مسجل'

        studentScheduleAndregisterdeCreditsList = []
        for i in range(len(listOfStudenstID)):
            driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[9]/th/a').click()

            driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[10]/td/div/table/tbody/tr[1]/td/div/a').click()

            driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table/tbody/tr[2]/td/div/input').send_keys(listOfStudenstID[i])

            driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table/tbody/tr[3]/td/div/input').click()
            Schedulepage = driver.page_source
            soup = BeautifulSoup(Schedulepage, "lxml")
            # ScheduleData = soup.findAll("table", {"border": "1"})
            studentScheduleData = soup.findAll("table", {"border": "1"})
            studentsSchedule = pd.read_html(str(studentScheduleData[1]))[0]
            studentsSchedule.drop(studentsSchedule.tail(1).index, inplace=True)
            registerdeCreditsSchedule = 0
            if len(studentScheduleData) == 2:
                studentsSchedule = pd.read_html(str(studentScheduleData[1]))[0]
                registerdeCreditsSchedule = int(studentsSchedule.loc[studentsSchedule.index[-1], 'وحده'])
                studentsSchedule.drop(studentsSchedule.tail(1).index, inplace=True)
                studentScheduleAndregisterdeCreditsList.append([studentsSchedule,registerdeCreditsSchedule])
            else :
                studentScheduleAndregisterdeCreditsList.append(['', registerdeCreditsSchedule])
        semester = driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table[1]/tbody/tr[4]/td[1]').text
        StudyType = driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table[1]/tbody/tr[5]/td[1]').text
        studyYear = driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table[1]/tbody/tr[3]/td[1]').text
def HeadOf_data_extraction():
    global plansOfStudents
    plansOfStudents = []
    plans = pd.read_csv('aa.csv')
    global transcriptsOfStudents
    transcriptsOfStudents = []
    driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[9]/th/a').click()
    driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[10]/td/div/table/tbody/tr[2]/td/div/a').click()
    for i in range(len(listOfStudenstID)):
        driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table/tbody/tr[2]/td/div/input').send_keys(listOfStudenstID[i])
        driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table/tbody/tr[3]/td/div/input').click()
        plansOfStudents.append(plan_extraction())
        driver.back()
        driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table/tbody/tr[2]/td/div/input').clear()
    driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[9]/th/a').click()
    driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[10]/td/div/table/tbody/tr[5]/td/div/a').click()
    for i in range(len(listOfStudenstID)):
            # سحب السجل الاكاديمي للطالب
            driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table/tbody/tr[2]/td/div/input').send_keys(listOfStudenstID[i])
            driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table/tbody/tr[3]/td/div/input').click()
            # save a source of the trans Cript and get data
            transcriptTAM = transcript_extraction()
            tr = transcriptTAM[1]
            transcriptsOfStudents.append(transcriptTAM[0])
            SRC = pd.read_csv("مقررات اختياري في التخصص.csv")
            numsrc = len(tr[0].loc[tr[0]['أسم المادة'].isin(SRC['اسـم المقرّر'])])
            if numsrc > 0:
                for j in range(numsrc):
                    plansOfStudents[i].loc[plansOfStudents[i][plansOfStudents[i]['أسم المادة'].str.contains("مقرر اختياري في التخصص") & (plansOfStudents[i]['التقدير'].isna())].index[0], 'التقدير'] = 'مسجل'
            numre = len(tr[0].loc[(~tr[0]['أسم المادة'].isin(plans['أسم المادة'])) & tr[0]['رمز المادة'].str.contains("GS")])
            if numre > 0:
                for j in range(numre):
                    plansOfStudents[i].loc[plansOfStudents[i][plansOfStudents[i]['أسم المادة'].str.contains("متطلب جامعة اختياري") & (plansOfStudents[i]['التقدير'].isna())].index[0], 'التقدير'] = 'مسجل'
            numfre = len(tr[0].loc[(~tr[0]['أسم المادة'].isin(plans['أسم المادة'])) & (~tr[0]['رمز المادة'].str.contains("GS")) & (tr[0]['و.م'] == 2)])
            if numfre > 0:
                for j in range(numfre):
                    plansOfStudents[i].loc[plansOfStudents[i][plansOfStudents[i]['أسم المادة'].str.contains("مقرر اختياري حر") & (plansOfStudents[i]['التقدير'].isna())].index[0], 'التقدير'] = 'مسجل'

            if len(tr[0].loc[(~tr[0]['أسم المادة'].isin(plans['أسم المادة'])) & (~tr[0]['رمز المادة'].str.contains("GS")) & (tr[0]['و.م'] == 3) & (~tr[0]['أسم المادة'].isin(SRC['اسـم المقرّر']))]) > 0:
                plansOfStudents[i].loc[plansOfStudents[i][plansOfStudents[i]['أسم المادة'].str.contains("اختياري علوم طبيعية")].index[0], 'التقدير'] = 'مسجل'

            driver.back()
            driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/form/table/tbody/tr[2]/td/div/input').clear()
def data_extraction():
    time.sleep(5)
    if user_type == 'طالب':
        Student_data_extraction()
    elif user_type == 'مرشد':
        advisor_data_extraction()
    global gohome
    gohome = True
    #return redirect('home')

def srndReq() :
    while not gohome :
        global shared_var
        time.sleep(2)
        response = requests.get(url)
        print(url)
        shared_var = response.text

def OptimalPlans(Studentsplan, sm):
        passedCourses = Studentsplan.loc[~(Studentsplan['التقدير'].isna() | Studentsplan['التقدير'].str.contains('F'))]['أسم المادة'].tolist()
        remainingCourses = Studentsplan.loc[Studentsplan['التقدير'].isna() | Studentsplan['التقدير'].str.contains('F')]['أسم المادة'].tolist()
        plan = []
        global hhh
        hhh = 0
        while len(remainingCourses) > 0:
            hhh = hhh+1
            if sm == 'الفصل الأول':
                sm = 'الفصل الثاني'
            elif sm == 'الفصل الثاني':
                sm = 'الفصل الثالث'
            else:
                sm = 'الفصل الأول'
            academicPlan = pd.read_csv('aa.csv')
            academicPlan = academicPlan.loc[(academicPlan['توفر المقرر'] == sm ) | (academicPlan['توفر المقرر'] == 'كلهم')]
            academicPlan = academicPlan.reset_index(drop=True)
            coursesForNextSemester = nextSemesterCourses(passedCourses, remainingCourses, academicPlan)



            remainingCourses = [i for i in remainingCourses if i not in coursesForNextSemester]

            passedCourses.extend(coursesForNextSemester)
            if len(coursesForNextSemester) == 0 :
                coursesForNextSemester.append('بناء على سياسة القسم بتقديم المقررات والخطة الدراسية لا يوجد مقررات يمكن دراستها في هذا المستوى')
            plan.append(coursesForNextSemester)

        return plan
def nextSemesterCourses(passedCourses, remainingCourses, academicPlan):
            maxCreditsForStudentGPA = pd.read_csv('max.csv')
            for i in range(len(maxCreditsForStudentGPA)):
                if (semester in maxCreditsForStudentGPA['الفصل الدراسي'].iloc[i]):
                    maxCredits = maxCreditsForStudentGPA['الحد الأعلى من الوحدات المسجلة '].iloc[i]
                    avaCoursesOf4Credits = maxCreditsForStudentGPA['اعلى عدد مقررات  التي وحداتها 4'].loc[i]
                    avaCoursesOf3Credits = maxCreditsForStudentGPA['اعلى عدد مقررات  التي وحداتها 3'].loc[i]
                    avaCoursesOf2Credits = maxCreditsForStudentGPA['اعلى عدد مقررات  التي وحداتها 2'].loc[i]
                    remainingCreditsForCurrentSemesterGraduate = maxCreditsForStudentGPA['الحد الأعلى من الوحدات المسجلة  لخريج الفصل الحالي'].loc[i]
                    remainingForGPNextSum = maxCreditsForStudentGPA['الحد الأعلى من الوحدات المتبقية لاخذ مشروع التخرج الفصل القادم'].loc[i]
                    break
            passGraduationProject1 = "مشروع التخرج(1)" not in remainingCourses
            isRemingGraduationProject1 = "مشروع التخرج(1)" in passedCourses
            #remainingCreditsForCurrentSemesterGraduate = maxCreditsForStudentGPA[maxCreditsForStudentGPA.columns[-5]].loc[0]
            if Studentsplan.loc[~Studentsplan['أسم المادة'].isin(passedCourses)]['وحدات معتمدة'].sum() <= remainingCreditsForCurrentSemesterGraduate and passGraduationProject1 and not isRemingGraduationProject1:
                return remainingCourses

            countOf4Credits = 0
            countOf3Credits = 0
            countOf2Credits = 0
            academicPlan = academicPlan.reset_index(drop=True)
            academicPlan.loc[academicPlan['أسم المادة'].isin(passedCourses), 'اجتاز المقرر'] = True

            Studentsleve = academicPlan.loc[academicPlan['اجتاز المقرر'] == False]['المستوى'].min()

            num = academicPlan.loc[(academicPlan['اجتاز المقرر'] == False) & (academicPlan['المستوى'] < Studentsleve)][
                'اجتاز المقرر'].count()
            num1 = academicPlan.loc[(academicPlan['اجتاز المقرر'] == True) & (academicPlan['المستوى'] > Studentsleve)][
                'اجتاز المقرر'].count()
            num2 = academicPlan.loc[(academicPlan['اجتاز المقرر'] == True) & (academicPlan['المستوى'] == Studentsleve)][ 'اجتاز المقرر'].count()
            if (num + num1 + num2) == 0 and semester not in "الصيفي":
                return  academicPlan.loc[academicPlan['المستوى'] == Studentsleve]['أسم المادة'].tolist()

            # ***************
            else:
                for i in range(len(remainingCourses)):
                    academicPlan.at[(academicPlan[academicPlan['سلسلة المتطلبات'].str.contains(remainingCourses[i], na=False,regex=False)].index.values), 'اجتاز سلسلة المتطلبات'] = False
                academicPlan = academicPlan.loc[ (academicPlan['اجتاز سلسلة المتطلبات'] == True) & (academicPlan['اجتاز المقرر'] == False) ]
                remainingCredits = academicPlan['وحدات معتمدة'].sum()
                academicPlan['أولية'] = academicPlan['طول سلسلة المتطلبات'] + academicPlan['عدد المواد المتطلبة']
                academicPlan.loc[academicPlan['المستوى'] == Studentsleve, 'أولية'] = academicPlan['أولية'] + 1
                academicPlan.loc[academicPlan['المستوى'] <= (Studentsleve + 1), 'أولية'] = academicPlan['أولية'] + 1
                academicPlan.loc[academicPlan['المستوى'] <= (Studentsleve + 2), 'أولية'] = academicPlan['أولية'] + 1
                academicPlan.loc[academicPlan['المستوى'] <= (Studentsleve + 3), 'أولية'] = academicPlan['أولية'] + 1
                academicPlan.loc[academicPlan['هل لها متطلب المستوى التالي'] == True, 'أولية'] = academicPlan['أولية'] + 1
                if remainingCredits - maxCredits <= remainingForGPNextSum:
                    maxpre = academicPlan['أولية'].max()
                    academicPlan.loc[academicPlan['متطلب لمشروع التخرج'] == True, 'أولية'] = maxpre + 1
                academicPlan = academicPlan.reset_index(drop=True)
                academicPlan = academicPlan.sort_values(by=['أولية', 'المستوى'], ascending=[False, True])

                registerdeCredits = 0
                optimalCourses = []
                academicPlan = academicPlan.reset_index(drop=True)
                i = 0
                while (registerdeCredits + academicPlan['وحدات معتمدة'].min()) <= maxCredits and not academicPlan.empty:
                    drop = True
                    if (registerdeCredits + academicPlan['وحدات معتمدة'].iloc[0]) <= maxCredits:
                        optimalCourses.append(academicPlan['أسم المادة'].iloc[0])
                        registerdeCredits = registerdeCredits + academicPlan['وحدات معتمدة'].iloc[0]

                        if academicPlan['وحدات معتمدة'].iloc[0] == 4:
                            countOf4Credits = countOf4Credits + 1
                            if countOf4Credits == avaCoursesOf4Credits and not academicPlan.loc[
                                academicPlan['وحدات معتمدة'] != 4].empty:
                                academicPlan = academicPlan.loc[academicPlan['وحدات معتمدة'] != 4]
                                academicPlan = academicPlan.reset_index(drop=True)
                                drop = False
                        if academicPlan['وحدات معتمدة'].iloc[0] == 3:
                            countOf3Credits = countOf3Credits + 1
                            if countOf3Credits == avaCoursesOf3Credits and not academicPlan.loc[
                                academicPlan['وحدات معتمدة'] != 3].empty:
                                academicPlan = academicPlan.loc[academicPlan['وحدات معتمدة'] != 3]
                                academicPlan = academicPlan.reset_index(drop=True)
                                drop = False
                        if academicPlan['وحدات معتمدة'].iloc[0] == 2:
                            countOf2Credits = countOf2Credits + 1
                            if countOf2Credits == avaCoursesOf2Credits and not academicPlan.loc[
                                academicPlan['وحدات معتمدة'] != 2].empty:
                                academicPlan = academicPlan.loc[academicPlan['وحدات معتمدة'] != 2]
                                academicPlan = academicPlan.reset_index(drop=True)
                                drop = False
                        if drop  :
                            academicPlan.drop(index=academicPlan.index[0], axis=0, inplace=True)

                    else:
                        cared = academicPlan['وحدات معتمدة'].iloc[0]
                        academicPlan = academicPlan.loc[academicPlan['وحدات معتمدة'] != cared]

            return optimalCourses
def SpecializationNaturalsciencesCoursess(offeredCourses, Studentsplan):
    specializationNaturalsciencesCourses = offeredCourses.loc[(offeredCourses['الشعبة'].isin(
        offeredCourses['الشعبة'].loc[offeredCourses['اسم المادة'].str.contains('اختياري علوم طبيعية' , na=False)].tolist())) & ( ~offeredCourses['اسم المادة'].str.contains('اختياري علوم طبيعية', na=False)) & (  ~ offeredCourses['اسم المادة'].isin( Studentsplan['أسم المادة']))]
    specializationNaturalsciencesCourses = specializationNaturalsciencesCourses.reset_index(drop=True)
    specializationNaturalsciencesCourses['lecture time'] = datetime.strptime(("00:00:00"), "%H:%M:%S")
    dayList = ['الاحد', 'الاثنين', 'الثلاثاء', 'الاربعاء', 'الخميس'];
    for i in range(len(specializationNaturalsciencesCourses)):
        for j in range(len(dayList)):
            s = specializationNaturalsciencesCourses[dayList[j]].iloc[i]
            if s != "-":
                a = s.split('-')
                specializationNaturalsciencesCourses.at[i, 'lecture time'] += datetime.strptime((a[1] + ":00"),
                                                                                                "%H:%M:%S") - datetime.strptime(
                    (a[0] + ":00"), "%H:%M:%S")
    specializationNaturalsciencesCourses['lecture time'] = specializationNaturalsciencesCourses[
        'lecture time'].dt.strftime("%H:%M:%S")
    specializationNaturalsciencesCourses = specializationNaturalsciencesCourses.loc[
        specializationNaturalsciencesCourses['lecture time'] == specializationNaturalsciencesCourses[
            'lecture time'].max()]
    specializationNaturalsciencesCourses = specializationNaturalsciencesCourses.reset_index(drop=True)
    return specializationNaturalsciencesCourses
def universityRequirementsCoursess(offeredCourses, transcripDF):
        universityRequirements = offeredCourses.loc[(offeredCourses['الشعبة'].isin(offeredCourses['الشعبة'].loc[
                                                                                       offeredCourses[
                                                                                           'اسم المادة'].str.contains(
                                                                                           'متطلب جامعة اختياري',
                                                                                           na=False)].tolist())) & (
                                                        ~offeredCourses['اسم المادة'].str.contains(
                                                            'متطلب جامعة اختياري', na=False)) & (
                                                        ~ offeredCourses['اسم المادة'].isin(transcripDF['أسم المادة']))]
        universityRequirements = universityRequirements.loc[(~ universityRequirements['الشعبة'].str.startswith('I')) & (
            ~ universityRequirements['الشعبة'].str.endswith('G'))]
        universityRequirements = universityRequirements.reset_index(drop=True)
        return universityRequirements
def FreeElectiveCoursess(offeredCourses, transcripDF):
    freeElective = offeredCourses.loc[(offeredCourses['الشعبة'].isin(offeredCourses['الشعبة'].loc[ offeredCourses['اسم المادة'].str.contains( 'مقرر اختياري حر', na=False,  regex=False)].tolist())) & (  ~offeredCourses['اسم المادة'].str.contains('مقرر اختياري حر', na=False,  regex=False)) & ( ~offeredCourses['اسم المادة'].str.contains('اختياري علوم طبيعية', na=False, regex=False)) & ( ~ offeredCourses['اسم المادة'].isin(transcripDF['أسم المادة']))]
    freeElective = freeElective.loc[~(freeElective['اسم المادة'].isin(Studentsplan['أسم المادة']))]
    # freeElective = freeElective.loc[(~ freeElective['الشعبة'].str.startswith('I')) & (~ freeElective['الشعبة'].str.endswith('G'))]
    freeElective['lecture time'] = datetime.strptime(("00:00:00"), "%H:%M:%S")
    freeElective = freeElective.reset_index(drop=True)
    dayList = ['الاحد', 'الاثنين', 'الثلاثاء', 'الاربعاء', 'الخميس'];
    for i in range(len(freeElective)):
        for j in range(len(dayList)):
            s = freeElective[dayList[j]].iloc[i]
            if s != "-":
                a = s.split('-')
                freeElective.at[i, 'lecture time'] += datetime.strptime((a[1] + ":00"), "%H:%M:%S") - datetime.strptime(
                    (a[0] + ":00"), "%H:%M:%S")
    freeElective['lecture time'] = freeElective['lecture time'].dt.strftime("%H:%M:%S")
    freeElective = freeElective.loc[freeElective['lecture time'] == freeElective['lecture time'].min()]
    freeElective = freeElective.reset_index(drop=True)
    return freeElective

def SpecializationElectivesSpecializationElectives(offeredCourses, transcripDF, remainingCourses, passedCourses):
        specializationElectivesCourses = pd.read_csv("مقررات اختياري في التخصص.csv")
        transcripDF = transcripDF.loc[(~transcripDF['المعدل'].isna())]
        specializationElectivesCourses = specializationElectivesCourses.loc[
            ~ specializationElectivesCourses['اسـم المقرّر'].isin(transcripDF['أسم المادة']) &
            specializationElectivesCourses['اسـم المقرّر'].isin(offeredCourses['اسم المادة'])]
        if studentclass == 'محول من مجتمع الى انتظام':
            specializationElectivesCourses.drop(specializationElectivesCourses.index[specializationElectivesCourses[
                                                                                         'اسـم المقرّر'] == 'تطوير تطبيقات الحوسبة المتنقلة'],
                                                inplace=True)
        specializationElectivesCourses['اجتاز سلسلة المتطلبات'] = True
        for i in range(len(remainingCourses)):
            specializationElectivesCourses.at[(specializationElectivesCourses[
                                                   specializationElectivesCourses['سلسلة المتطلبات'].str.contains(
                                                       remainingCourses.loc[i, "أسم المادة"],
                                                       na=False)].index.values), 'اجتاز سلسلة المتطلبات'] = False
        specializationElectivesCourses = specializationElectivesCourses.loc[
            ~ specializationElectivesCourses['اجتاز سلسلة المتطلبات'] == False]
        specializationElectivesCourses = specializationElectivesCourses.reset_index(drop=True)
        specializationElectivesCourses["متوسط درجات سلسله المتطلبات"] = 0.00
        for i in range(len(specializationElectivesCourses)):
            c = specializationElectivesCourses.loc[i, 'سلسلة المتطلبات']
            if not c.__eq__(""):
                ca = specializationElectivesCourses.loc[i, 'سلسلة المتطلبات'].split(',')
                ave = transcripDF.loc[transcripDF['أسم المادة'].isin(ca)]['الدرجة'].sum() / len(ca)
                specializationElectivesCourses.loc[i, 'متوسط درجات سلسله المتطلبات'] = ave
        specializationElectivesCourses = specializationElectivesCourses.sort_values(by=['متوسط درجات سلسله المتطلبات'],
                                                                                    ascending=False)
        if specializationElectivesCourses['اسـم المقرّر'].str.contains("التدريب الميداني").sum() == 1 and not \
        passedCourses['وحدات معتمدة'].sum() >= 110:
            specializationElectivesCourses.drop(specializationElectivesCourses.index[specializationElectivesCourses[
                                                                                         'اسـم المقرّر'] == 'التدريب الميداني'],
                                                inplace=False)
        specializationElectivesCourses = specializationElectivesCourses.reset_index(drop=True)
        return specializationElectivesCourses


def CoursesTaken(Studentsplan, offeredCourses, transcripDF):
    academicPlan = pd.read_csv('aa.csv')
    passedCourses = Studentsplan.loc[~ ((Studentsplan['التقدير'].str.contains('F')) | (Studentsplan['التقدير'].str.contains('مسجل')) | (Studentsplan['التقدير'].isna()))]
    remainingCourses = Studentsplan.loc[((Studentsplan['التقدير'].str.contains('F')) | (Studentsplan['التقدير'].str.contains('مسجل')) | (Studentsplan['التقدير'].isna()))]
    print(passedCourses['أسم المادة'].tolist())
    passedCourses.reset_index(inplace=True)
    remainingCourses.reset_index(inplace=True)
    maxCreditsForStudentGPA = pd.read_csv('max.csv')
    offeredCourses = offeredCourses.dropna(how='all', axis=0)
    for i in range(len(maxCreditsForStudentGPA)):
        if (maxCreditsForStudentGPA['المعدل من'].iloc[i] <= GPA and GPA <= maxCreditsForStudentGPA['المعدل الى'].iloc[
            i]) and (semester in maxCreditsForStudentGPA['الفصل الدراسي'].iloc[i]):
            maxCredits = maxCreditsForStudentGPA['الحد الأعلى من الوحدات المسجلة '].iloc[i]
            remainingCreditsForCurrentSemesterGraduate = \
            maxCreditsForStudentGPA[maxCreditsForStudentGPA.columns[-5]].loc[i]
            remainingCreditsForNextSemesterGraduate = maxCreditsForStudentGPA[maxCreditsForStudentGPA.columns[-4]].loc[i]
            break
    academicPlan.loc[academicPlan['أسم المادة'].isin(passedCourses['أسم المادة']), 'اجتاز المقرر'] = True
    for i in range(len(remainingCourses)):
        academicPlan.at[(academicPlan[academicPlan['سلسلة المتطلبات'].str.contains(remainingCourses.loc[i, "أسم المادة"],na=False,regex=False)].index.values), 'اجتاز سلسلة المتطلبات'] = False

    # offeredCourses = offeredCourses.loc[~ ((offeredCourses['الشعبة'].str.startswith('I')) & (offeredCourses['الشعبة'].str.endswith('G')))]

    offeredCourses = offeredCourses.dropna(how='all', axis=0)
    academicPlan = academicPlan.loc[(academicPlan['اجتاز سلسلة المتطلبات'] == True) & (academicPlan['اجتاز المقرر'] == False) & academicPlan['أسم المادة'].isin(offeredCourses['اسم المادة']) & (academicPlan['أسم المادة'].isin(Studentsplan['أسم المادة'])) ]
    print(academicPlan['أسم المادة'].tolist())
    Studentsleve = academicPlan.loc[academicPlan['اجتاز المقرر'] == False]['المستوى'].min()
    academicPlan['أولية'] = academicPlan['طول سلسلة المتطلبات'] + academicPlan['عدد المواد المتطلبة']
    academicPlan.loc[academicPlan['المستوى'] == Studentsleve, 'أولية'] = academicPlan['أولية'] + 1
    academicPlan.loc[academicPlan['المستوى'] <= (Studentsleve + 2), 'أولية'] = academicPlan['أولية'] + 1
    academicPlan.loc[academicPlan['هل لها متطلب المستوى التالي'] == True, 'أولية'] = academicPlan['أولية'] + 1
    academicPlan = academicPlan.reset_index(drop=True)
    academicPlan["متوسط درجات سلسله المتطلبات"] = 0.00
    # مقرر اختياري حر
    for i in range(len(academicPlan)):
        c = academicPlan.loc[i, 'سلسلة المتطلبات']
        if not c.__eq__(""):
            ca = academicPlan.loc[i, 'سلسلة المتطلبات'].split(',')
            ave = passedCourses.loc[passedCourses['أسم المادة'].isin(ca)]['الدرجة'].sum() / len(ca)
            academicPlan.loc[i, 'متوسط درجات سلسله المتطلبات'] = float(format(ave, '.2f'))
    academicPlan = academicPlan.sort_values(by=['أولية', 'المستوى', "متوسط درجات سلسله المتطلبات"], ascending=[False, True, False])
    academicPlan = academicPlan.reset_index(drop=True)
    CoursesCanTaken = academicPlan.loc[~ ((academicPlan['أسم المادة'].str.contains("مقرر اختياري في التخصص", na=False, regex=False)) | (academicPlan['أسم المادة'].str.contains("مقرر اختياري حر")) | (academicPlan['أسم المادة'].str.contains("متطلب جامعة اختياري")) | (academicPlan['أسم المادة'].str.contains("اختياري علوم طبيعية")))]
    CoursesCanTaken = CoursesCanTaken[['أسم المادة','وحدات معتمدة' , 'أولية']]
    
    if academicPlan['أسم المادة'].str.contains("مقرر اختياري في التخصص", na=False, regex=False).sum() > 0:
        specializationElectivesCourses = SpecializationElectivesSpecializationElectives(offeredCourses, transcripDF,remainingCourses, passedCourses)
        specializationElectivesCourses['وحدات معتمدة'] = 3
        specializationElectivesCourses = specializationElectivesCourses[['اسـم المقرّر','وحدات معتمدة']]
        CoursesCanTaken = pd.concat([CoursesCanTaken, specializationElectivesCourses.rename(columns={'اسـم المقرّر': 'أسم المادة'})], axis=0)

    if academicPlan['أسم المادة'].str.contains("مقرر اختياري حر", regex=False).sum() > 0:
        print("انا مقرر حر")
        freeElectiveCourses = FreeElectiveCoursess(offeredCourses, transcripDF)
        freeElectiveCourses['وحدات معتمدة'] = 2
        freeElectiveCourses = freeElectiveCourses[['اسم المادة','وحدات معتمدة' ]]
        
        CoursesCanTaken = pd.concat([CoursesCanTaken, freeElectiveCourses.rename(columns={'اسم المادة': 'أسم المادة'})],axis=0)
    if academicPlan['أسم المادة'].str.contains("متطلب جامعة اختياري").sum() > 0:
        UniversityRequirementsCourses = universityRequirementsCoursess(offeredCourses, transcripDF)
        UniversityRequirementsCourses['وحدات معتمدة'] = 2
        UniversityRequirementsCourses = UniversityRequirementsCourses[['اسم المادة','وحدات معتمدة' ]]
        CoursesCanTaken = pd.concat([CoursesCanTaken, UniversityRequirementsCourses.rename(columns={'اسم المادة': 'أسم المادة'})], axis=0)
    if academicPlan['أسم المادة'].str.contains("اختياري علوم طبيعية").sum() > 0:

        SpecializationNaturalsciencesCourse = SpecializationNaturalsciencesCoursess(offeredCourses, Studentsplan)
        SpecializationNaturalsciencesCourse['وحدات معتمدة'] = 3
        SpecializationNaturalsciencesCourse = SpecializationNaturalsciencesCourse[['اسم المادة','وحدات معتمدة']]
        CoursesCanTaken = pd.concat([CoursesCanTaken, SpecializationNaturalsciencesCourse.rename(columns={'اسم المادة': 'أسم المادة'})], axis=0)
    CoursesCanTaken = CoursesCanTaken.drop_duplicates(subset=['أسم المادة'])
    
    return CoursesCanTaken


def FindTable(CTable, ListOfCoursesSections, nocCnflict=True):
    table = []
    dayList = ['الاحد', 'الاثنين', 'الثلاثاء', 'الاربعاء', 'الخميس'];
    for i in range(len(CTable)):

        for j in range(len(ListOfCoursesSections)):
            CnflictCourses = pd.DataFrame(columns=CTable[0].columns)
            t = True
            for d in range(len(dayList)):
                if ListOfCoursesSections[dayList[d]].iloc[j] != '-':
                    s1 = ListOfCoursesSections[dayList[d]].iloc[j]
                    a2 = s1.split('-')
                    a2[0] = datetime.strptime((a2[0] + ":00"), "%H:%M:%S")
                    a2[1] = datetime.strptime((a2[1] + ":00"), "%H:%M:%S")
                    for k in range(len(CTable[i])):
                        # print(CTable[i]['الشعبة'].iloc[k])
                        if CTable[i][dayList[d]].iloc[k] != '-':

                            s = CTable[i][dayList[d]].iloc[k]
                            a = s.split('-')
                            a[0] = datetime.strptime((a[0] + ":00"), "%H:%M:%S")
                            a[1] = datetime.strptime((a[1] + ":00"), "%H:%M:%S")
                            # print(s1)
                            # if isTable(a[0],a2[0],a[1])  or  isTable(a[0],a2[1],a[1]):
                            # print(s1)
                            # if a2[0] < a[0] :
                            #  y = a2[0]
                            # a2[0] = a[0]
                            # a[0] = y
                            # y = a2[1]
                            # a2[1] = a[1]
                            # a[1] = y

                            if (a[0] <= a2[0] <= a[1]) or (a[0] <= a2[1] <= a[1]) or (a2[0] <= a[0] <= a2[1]) or (
                                    a2[0] <= a[1] <= a2[1]):
                                if not nocCnflict:
                                    CnflictCourses = CnflictCourses.append(CTable[i].iloc[k], ignore_index=True)
                                t = False

            if not t and not nocCnflict:
                CnflictCourses = CnflictCourses.drop_duplicates()
                CnflictCourses = CnflictCourses.append(ListOfCoursesSections.iloc[j], ignore_index=True)
                table.append(CnflictCourses)

            if t and nocCnflict:
                newT = CTable[i].append(ListOfCoursesSections.iloc[j], ignore_index=True)
                table.append(newT)

    return table

def CoursesTakenSchedule( offeredCourses,nameCoursesCanTaken,maxCredits):
    global mes
    mes = ''
    nameCoursesCanTakencapy = nameCoursesCanTaken
    nameCoursesCanTaken = nameCoursesCanTaken.loc[( ((nameCoursesCanTaken['وحدات معتمدة'] + registerdeCreditsSchedule) <= maxCredits) & (~(nameCoursesCanTaken['أسم المادة'].isin(studentSchedule['المادة']))))]
    if len(nameCoursesCanTaken) > 0:
        nameCoursesCanTaken = nameCoursesCanTaken['أسم المادة'].tolist()
        print(nameCoursesCanTaken)
        table = []
        studentScheduleteamp = studentSchedule
        studentScheduleteamp = studentScheduleteamp[ ['أحد', 'اثنين', 'ثلاثاء', 'أربعاء', 'خميس', 'المادة', 'رمز', 'رقم', 'شعبة']]
        offeredCoursestamp = pd.merge(offeredCourses,studentScheduleteamp.rename(columns={'المادة': 'اسم المادة', 'شعبة': 'الشعبة'}),on=['اسم المادة', 'الشعبة'], how='inner', indicator=False)
        studentScheduleteamp = studentSchedule.loc[(~studentSchedule['المادة'].isin(offeredCoursestamp['اسم المادة']))]
        # y = studentSchedule
        days = ['أحد', 'اثنين', 'ثلاثاء', 'أربعاء', 'خميس']
        for i in range(len(days)):
            studentScheduleteamp.loc[studentScheduleteamp[days[i]].isnull(), days[i]] = studentScheduleteamp[ 'بداية'] + '-' +  studentScheduleteamp['نهاية']
        studentScheduleteamp.reset_index(inplace=True, drop=True)
        for i in range(len(studentScheduleteamp)):
            if studentScheduleteamp['المادة'].iloc[i] != '-':
                for j in range(i + 1, len(studentScheduleteamp)):
                    if studentScheduleteamp['المادة'].iloc[j] != '-':
                        break
                    for d in range(len(days)):
                        if studentScheduleteamp[days[d]].iloc[j] != '-':
                            studentScheduleteamp.loc[i, days[d]] = studentScheduleteamp['بداية'].iloc[j] + '-' + studentScheduleteamp['نهاية'].iloc[j]
        studentScheduleteamp = studentScheduleteamp.loc[studentScheduleteamp['المادة'] != '-']
        studentScheduleteamp = studentScheduleteamp[['أحد', 'اثنين', 'ثلاثاء', 'أربعاء', 'خميس', 'المادة', 'رمز', 'رقم']]
        studentScheduleteamp = studentScheduleteamp.rename(columns={'أحد': 'الاحد', 'اثنين': 'الاثنين', 'ثلاثاء': 'الثلاثاء', 'أربعاء': 'الاربعاء', 'خميس': 'الخميس','المادة': 'اسم المادة', 'رمز': 'رمز المادةو الرقم.1', 'رقم': 'رمز المادةو الرقم'})
        table.append(pd.concat([offeredCoursestamp, studentScheduleteamp]))
        #table.append(pd.merge(offeredCourses, studentSchedule.rename(columns={'المادة': 'اسم المادة', 'شعبة': 'الشعبة'}),on=['اسم المادة', 'الشعبة'], how='inner', indicator=False))
        listofCoursesAndSections = pd.DataFrame(columns=offeredCourses.columns)
        for i in range(len(nameCoursesCanTaken)):
            CoursesSections = offeredCourses.loc[offeredCourses['اسم المادة'].str.contains(nameCoursesCanTaken[i], na=False, regex=False)]
            tampTable = FindTable(table, CoursesSections)
            if len(tampTable) > 0:
                for j in range(len(tampTable)):
                    listofCoursesAndSections = listofCoursesAndSections.append(tampTable[j].loc[tampTable[j]['اسم المادة'].str.contains(nameCoursesCanTaken[i], na=False,regex=False)])

        listofCoursesAndSections['وحده'] = 0

        for i in range(len(nameCoursesCanTakencapy)):
            for j in range(len(listofCoursesAndSections)):
                if nameCoursesCanTakencapy['أسم المادة'].iloc[i] == listofCoursesAndSections['اسم المادة'].iloc[j]:
                    listofCoursesAndSections['وحده'].iloc[j] = nameCoursesCanTakencapy['وحدات معتمدة'].iloc[i]
        if len(listofCoursesAndSections) == 0 :
            mes = 'لا يوجد مقررات يمكن اضافتها بناء على الجدول الدراسي'
        return listofCoursesAndSections
    else :

        mes = 'لا يوجد مقررات يمكن اضافتها بناء على النصاب الدراسي'
        return []

def CoursesNotTakenSchedule(offeredCourses,nameCoursesCanTaken,maxCredits):
    nameCoursesCanTakencapy = nameCoursesCanTaken
    global mes1
    mes1 = ''

    nameCoursesCanTaken = nameCoursesCanTaken.loc[(((nameCoursesCanTaken['وحدات معتمدة'] + registerdeCreditsSchedule) <= maxCredits) & ( ~(nameCoursesCanTaken['أسم المادة'].isin(studentSchedule['المادة']))))]

    if len(nameCoursesCanTaken) > 0  :

        nameCoursesCanTaken = nameCoursesCanTaken['أسم المادة'].tolist()
        table = []
        studentScheduleteamp = studentSchedule
        studentScheduleteamp = studentScheduleteamp[
            ['أحد', 'اثنين', 'ثلاثاء', 'أربعاء', 'خميس', 'المادة', 'رمز', 'رقم', 'شعبة']]
        offeredCoursestamp = pd.merge(offeredCourses,studentScheduleteamp.rename(columns={'المادة': 'اسم المادة', 'شعبة': 'الشعبة'}),on=['اسم المادة', 'الشعبة'], how='inner', indicator=False)
        studentScheduleteamp = studentSchedule.loc[(~studentSchedule['المادة'].isin(offeredCoursestamp['اسم المادة']))]
        # y = studentSchedule
        days = ['أحد', 'اثنين', 'ثلاثاء', 'أربعاء', 'خميس']
        for i in range(len(days)):
            studentScheduleteamp.loc[studentScheduleteamp[days[i]].isnull(), days[i]] = studentScheduleteamp[
                                                                                            'بداية'] + '-' + \
                                                                                        studentScheduleteamp['نهاية']
        studentScheduleteamp.reset_index(inplace=True, drop=True)
        for i in range(len(studentScheduleteamp)):
            if studentScheduleteamp['المادة'].iloc[i] != '-':
                for j in range(i + 1, len(studentScheduleteamp)):
                    if studentScheduleteamp['المادة'].iloc[j] != '-':
                        break
                    for d in range(len(days)):
                        if studentScheduleteamp[days[d]].iloc[j] != '-':
                            studentScheduleteamp.loc[i, days[d]] = studentScheduleteamp['بداية'].iloc[j] + '-' + studentScheduleteamp['نهاية'].iloc[j]
        studentScheduleteamp = studentScheduleteamp.loc[studentScheduleteamp['المادة'] != '-']
        studentScheduleteamp = studentScheduleteamp[['أحد', 'اثنين', 'ثلاثاء', 'أربعاء', 'خميس', 'المادة', 'رمز', 'رقم']]
        studentScheduleteamp = studentScheduleteamp.rename(columns={'أحد': 'الاحد', 'اثنين': 'الاثنين', 'ثلاثاء': 'الثلاثاء', 'أربعاء': 'الاربعاء', 'خميس': 'الخميس','المادة': 'اسم المادة', 'رمز': 'رمز المادةو الرقم.1', 'رقم': 'رمز المادةو الرقم'})
        table.append(pd.concat([offeredCoursestamp, studentScheduleteamp]))
        listofCoursesAndSections = []
        for i in range(len(nameCoursesCanTaken)):
            CoursesSections = offeredCourses.loc[offeredCourses['اسم المادة'].str.contains(nameCoursesCanTaken[i], na=False, regex=False)]
            tampTable = FindTable(table, CoursesSections, False)
            if len(tampTable) > 0:
                for j in range(len(tampTable)):
                    listofCoursesAndSections.append(tampTable[j])
        for j in range(len(listofCoursesAndSections)):
                    listofCoursesAndSections[j]['وحده'] =0
        for i in range(len(nameCoursesCanTakencapy)):
            for j in range(len(listofCoursesAndSections)):
                for k in range(len(listofCoursesAndSections[j])):
                    if nameCoursesCanTakencapy['أسم المادة'].iloc[i] == listofCoursesAndSections[j]['اسم المادة'].iloc[k]:
                        listofCoursesAndSections[j]['وحده'].iloc[k] = nameCoursesCanTakencapy['وحدات معتمدة'].iloc[i]
        if len(listofCoursesAndSections) == 0 :
            mes1 = 'لا يوجد مقررات يمكن اضافتها بناء على الجدول الدراسي'
        return listofCoursesAndSections
    else :

        mes1 = 'لا يوجد مقررات يمكن اضافتها بناء على النصاب الدراسي'
        return []
def optimalCourses(Studentsplan, allOfferedCourses, transcripDF):
    global SpecializationElectivesName
    global freeElectiveName
    global UniversityRequirementsName
    global SpecializationNaturalsciencesCoursesName
    global SpecializationNaturalsciencesCoursesName
    SpecializationElectivesName = []
    freeElectiveName  = []
    UniversityRequirementsName  = []
    SpecializationNaturalsciencesCoursesName = []
    global GraduationProject
    haveSpecializationElectives = False
    havefreeElective = False
    haveUniversityRequirements = False
    haveSpecializationNaturalsciencesCourses = False
    studentLevel = False
    currentSemesterGraduate = False
    countOf4Credits = 0
    countOf3Credits = 0
    countOf2Credits = 0
    global haveGraduationProject
    haveGraduationProject = False
    Table = []
    academicPlan = pd.read_csv('aa.csv')
    passedCourses = Studentsplan.loc[~ (
                (Studentsplan['التقدير'].str.contains('F')) | (Studentsplan['التقدير'].str.contains('مسجل')) | (
            Studentsplan['التقدير'].isna()))]
    remainingCourses = Studentsplan.loc[(
                (Studentsplan['التقدير'].str.contains('F')) | (Studentsplan['التقدير'].str.contains('مسجل')) | (
            Studentsplan['التقدير'].isna()))]
    passedCourses.reset_index(inplace=True)
    remainingCourses.reset_index(inplace=True)
    allOfferedCourses = allOfferedCourses.loc[~ allOfferedCourses['الشعبة'].str.contains('del', case=False, na=False)]
    remainingCourses = remainingCourses.reset_index(drop=True)
    passedCourses = passedCourses.reset_index(drop=True)
    maxCreditsForStudentGPA = pd.read_csv('max.csv')
    allOfferedCourses = allOfferedCourses.dropna(how='all', axis=0)
    for i in range(len(maxCreditsForStudentGPA)):
        if (maxCreditsForStudentGPA['المعدل من'].iloc[i] <= GPA and GPA <= maxCreditsForStudentGPA['المعدل الى'].iloc[
            i]) and (semester in maxCreditsForStudentGPA['الفصل الدراسي'].iloc[i]):
            maxCredits = maxCreditsForStudentGPA['الحد الأعلى من الوحدات المسجلة '].iloc[i]
            avaCoursesOf4Credits = maxCreditsForStudentGPA['اعلى عدد مقررات  التي وحداتها 4'].loc[i]
            avaCoursesOf3Credits = maxCreditsForStudentGPA['اعلى عدد مقررات  التي وحداتها 3'].loc[i]
            avaCoursesOf2Credits = maxCreditsForStudentGPA['اعلى عدد مقررات  التي وحداتها 2'].loc[i]
            remainingCreditsForCurrentSemesterGraduate = maxCreditsForStudentGPA['الحد الأعلى من الوحدات المسجلة  لخريج الفصل الحالي'].loc[i]
            remainingForGPNextSum = maxCreditsForStudentGPA['الحد الأعلى من الوحدات المتبقية لاخذ مشروع التخرج الفصل القادم'].loc[i]

            #remainingCreditsForNextSemesterGraduate = maxCreditsForStudentGPA[maxCreditsForStudentGPA.columns[-4]].loc[i]
            break
    remainingCredits = remainingCourses['وحدات معتمدة'].sum()
    passGraduationProject1 = "مشروع التخرج(1)" not in remainingCourses["أسم المادة"].values
    passGraduationProject2 = "مشروع التخرج(2)" not in remainingCourses["أسم المادة"].values
    if remainingCredits <= remainingCreditsForCurrentSemesterGraduate and passGraduationProject2 and semester in "الصيفي":
        currentSemesterGraduate = True
        academicPlan = academicPlan.loc[academicPlan['أسم المادة'].isin(remainingCourses['أسم المادة'])]
    elif remainingCredits <= remainingCreditsForCurrentSemesterGraduate and passGraduationProject1:
        currentSemesterGraduate = True
        if not passGraduationProject2:
            academicPlan = academicPlan.loc[
                ~ (academicPlan['أسم المادة'].str.contains('مشروع التخرج', na=False, regex=False))]
            haveGraduationProject = True

        academicPlan = academicPlan.loc[academicPlan['أسم المادة'].isin(remainingCourses['أسم المادة'])]


    else:

        for i in range(len(passedCourses)):
            academicPlan.at[(academicPlan[academicPlan['أسم المادة'] == passedCourses.loc[
                i, 'أسم المادة']].index.values), 'اجتاز المقرر'] = True
        Studentsleve = academicPlan.loc[academicPlan['اجتاز المقرر'] == False]['المستوى'].min()
        num = academicPlan.loc[(academicPlan['اجتاز المقرر'] == False) & (academicPlan['المستوى'] < Studentsleve)][
            'اجتاز المقرر'].count()
        num1 = academicPlan.loc[(academicPlan['اجتاز المقرر'] == True) & (academicPlan['المستوى'] > Studentsleve)][
            'اجتاز المقرر'].count()
        num2 = academicPlan.loc[(academicPlan['اجتاز المقرر'] == True) & (academicPlan['المستوى'] == Studentsleve)][
            'اجتاز المقرر'].count()
        if (num + num1 + num2) == 0 and semester not in "الصيفي":
            studentLevel = True
            academicPlan = academicPlan.loc[academicPlan['المستوى'] == Studentsleve]
        else:
            # ***************
            for i in range(len(remainingCourses)):
                academicPlan.at[(academicPlan[
                                     academicPlan['سلسلة المتطلبات'].str.contains(remainingCourses.loc[i, "أسم المادة"],
                                                                                  na=False,
                                                                                  regex=False)].index.values), 'اجتاز سلسلة المتطلبات'] = False
            registerdeCredits = 0

            allOfferedCourses = allOfferedCourses.loc[
                ~ ((allOfferedCourses['الشعبة'].str.startswith('I')) & (allOfferedCourses['الشعبة'].str.endswith('G')))]
            allOfferedCourses = allOfferedCourses.dropna(how='all', axis=0)
            academicPlan = academicPlan.loc[ (academicPlan['اجتاز سلسلة المتطلبات'] == True) & (academicPlan['اجتاز المقرر'] == False) &academicPlan['أسم المادة'].isin(allOfferedCourses['اسم المادة'])]

            academicPlan['أولية'] = academicPlan['طول سلسلة المتطلبات'] + academicPlan['عدد المواد المتطلبة']
            academicPlan.loc[academicPlan['المستوى'] == Studentsleve, 'أولية'] = academicPlan['أولية'] + 1
            academicPlan.loc[academicPlan['المستوى'] <= (Studentsleve + 1), 'أولية'] = academicPlan['أولية'] + 1
            academicPlan.loc[academicPlan['المستوى'] <= (Studentsleve + 2), 'أولية'] = academicPlan['أولية'] + 1
            academicPlan.loc[academicPlan['المستوى'] <= (Studentsleve + 3), 'أولية'] = academicPlan['أولية'] + 1
            academicPlan.loc[academicPlan['هل لها متطلب المستوى التالي'] == True, 'أولية'] = academicPlan['أولية'] + 1
            if remainingCredits - maxCredits <= remainingForGPNextSum :
                maxpre = academicPlan['أولية'].max()
                academicPlan.loc[academicPlan['متطلب لمشروع التخرج'] == True, 'أولية'] = maxpre + 1
            academicPlan = academicPlan.reset_index(drop=True)
            academicPlan["متوسط درجات سلسله المتطلبات"] = 0.00

            for i in range(len(academicPlan)):
                c = academicPlan.loc[i, 'سلسلة المتطلبات']
                if not c.__eq__(""):
                    ca = academicPlan.loc[i, 'سلسلة المتطلبات'].split(',')
                    ave = passedCourses.loc[passedCourses['أسم المادة'].isin(ca)]['الدرجة'].sum() / len(ca)

                    print(academicPlan.loc[i, 'أسم المادة'])
                    print(passedCourses.loc[passedCourses['أسم المادة'].isin(ca)]['أسم المادة'].tolist())
                    print('******************************************')
                    academicPlan.loc[i, 'متوسط درجات سلسله المتطلبات'] = float(format(ave, '.2f'))
            academicPlan = academicPlan.sort_values(by=['أولية', 'المستوى', "متوسط درجات سلسله المتطلبات"],ascending=[False, True, False])

            academicPlan = academicPlan.reset_index(drop=True)
            
            registerdeCredits = registerdeCredits + academicPlan['وحدات معتمدة'].iloc[0]
            if 'مقرر اختياري في التخصص' in academicPlan['أسم المادة'].iloc[0]:
                if not haveSpecializationElectives:
                    haveSpecializationElectives = True
                    specializationElectivesCourses = SpecializationElectivesSpecializationElectives(allOfferedCourses,
                                                                                                    transcripDF,
                                                                                                    remainingCourses,
                                                                                                    passedCourses)
                CoursesSections = allOfferedCourses.loc[
                    allOfferedCourses['اسم المادة'].str.contains(specializationElectivesCourses['اسـم المقرّر'].iloc[0],
                                                                 na=False, regex=False)]
                SpecializationElectivesName.append(specializationElectivesCourses['اسـم المقرّر'].iloc[0])
                specializationElectivesCourses.drop(index=specializationElectivesCourses.index[0], axis=0, inplace=True)
            elif 'مقرر اختياري حر' in academicPlan['أسم المادة'].iloc[0]:
                if not havefreeElective:
                    havefreeElective = True
                    freeElectiveCourses = FreeElectiveCoursess(allOfferedCourses, transcripDF)

                CoursesSections = allOfferedCourses.loc[
                    allOfferedCourses['اسم المادة'].str.contains(freeElectiveCourses['اسم المادة'].iloc[0], na=False,
                                                                 regex=False)]
                freeElectiveName.append(freeElectiveCourses['اسم المادة'].iloc[0])
                freeElectiveCourses.drop(index=freeElectiveCourses.index[0], axis=0, inplace=True)

            elif 'اختياري علوم طبيعية' in academicPlan['أسم المادة'].iloc[0]:
                if not haveSpecializationNaturalsciencesCourses:
                    haveSpecializationNaturalsciencesCourses = True
                    SpecializationNaturalsciencesCourse = SpecializationNaturalsciencesCoursess(allOfferedCourses,Studentsplan)
                CoursesSections = allOfferedCourses.loc[allOfferedCourses['اسم المادة'].str.contains(SpecializationNaturalsciencesCourse['اسم المادة'].iloc[0], na=False, regex=False)]
                SpecializationNaturalsciencesCoursesName.append(SpecializationNaturalsciencesCourse['اسم المادة'].iloc[0])
                SpecializationNaturalsciencesCourse.drop(index=SpecializationNaturalsciencesCourse.index[0], axis=0, inplace=True)


            elif 'متطلب جامعة اختياري' in academicPlan['أسم المادة'].iloc[0]:
                if not haveUniversityRequirements:
                    UniversityRequirements = True
                    UniversityRequirementsCourses = universityRequirementsCoursess(allOfferedCourses, transcripDF)
                CoursesSections = allOfferedCourses.loc[
                    allOfferedCourses['اسم المادة'].str.contains(UniversityRequirementsCourses['اسم المادة'].iloc[0],
                                                                 na=False, regex=False)]
                UniversityRequirementsName.append(UniversityRequirementsCourses['اسم المادة'].iloc[0])
                UniversityRequirementsCourses.drop(index=UniversityRequirementsCourses.index[0], axis=0, inplace=True)

            else:
                CoursesSections = allOfferedCourses.loc[allOfferedCourses['اسم المادة'].str.contains(academicPlan['أسم المادة'].iloc[0], na=False,regex=False)]
            academicPlan.drop(index=academicPlan.index[0], axis=0, inplace=True)
            for j in range(len(CoursesSections)):
                Table.append(pd.DataFrame(columns=allOfferedCourses.columns).append(CoursesSections.iloc[j]))
            while not academicPlan.empty and (registerdeCredits + academicPlan['وحدات معتمدة'].min()) <= maxCredits:
                notdrap = False
                if ((registerdeCredits + academicPlan['وحدات معتمدة'].iloc[0]) <= maxCredits):

                    if 'مشروع التخرج' in academicPlan['أسم المادة'].iloc[0]:
                        academicPlan = academicPlan.loc[ ~ (academicPlan['أسم المادة'].str.contains('مشروع التخرج', na=False, regex=False))]
                        haveGraduationProject = True

                    if 'مقرر اختياري في التخصص' in academicPlan['أسم المادة'].iloc[0]:
                        if not haveSpecializationElectives:
                            haveSpecializationElectives = True
                            specializationElectivesCourses = SpecializationElectivesSpecializationElectives(allOfferedCourses, transcripDF, remainingCourses,passedCourses)

                        while True and not specializationElectivesCourses.empty:
                            CoursesSections = allOfferedCourses.loc[allOfferedCourses['اسم المادة'].str.contains(
                                specializationElectivesCourses['اسـم المقرّر'].iloc[0], na=False, regex=False)]
                            tampTable = FindTable(Table, CoursesSections)
                            if len(tampTable )> 0:
                                SpecializationElectivesName.append(specializationElectivesCourses['اسـم المقرّر'].iloc[0])
                                Table = tampTable
                                specializationElectivesCourses.drop(index=specializationElectivesCourses.index[0],axis=0, inplace=True)
                                #registerdeCredits = registerdeCredits + academicPlan['وحدات معتمدة'].iloc[0]
                                break
                            specializationElectivesCourses.drop(index=specializationElectivesCourses.index[0], axis=0,inplace=True)



                    elif 'مقرر اختياري حر' in academicPlan['أسم المادة'].iloc[0]:
                        if not havefreeElective:
                            havefreeElective = True
                            freeElectiveCourses = FreeElectiveCoursess(allOfferedCourses, transcripDF)
                        while True and not freeElectiveCourses.empty:
                            CoursesSections = allOfferedCourses.loc[
                                allOfferedCourses['اسم المادة'].str.contains(freeElectiveCourses['اسم المادة'].iloc[0],na=False, regex=False)]
                            tampTable = FindTable(Table, CoursesSections)


                            if len(tampTable )> 0:
                                Table = tampTable
                                freeElectiveName.append(freeElectiveCourses['اسم المادة'].iloc[0])
                                freeElectiveCourses.drop(index=freeElectiveCourses.index[0], axis=0, inplace=True)
                                #registerdeCredits = registerdeCredits + academicPlan['وحدات معتمدة'].iloc[0]
                                break
                            freeElectiveCourses.drop(index=freeElectiveCourses.index[0], axis=0, inplace=True)
                    elif 'اختياري علوم طبيعية' in academicPlan['أسم المادة'].iloc[0]:
                        if not haveSpecializationNaturalsciencesCourses:
                            haveSpecializationNaturalsciencesCourses = True
                            SpecializationNaturalsciencesCourses = SpecializationNaturalsciencesCoursess(allOfferedCourses,Studentsplan)
                        while True and not SpecializationNaturalsciencesCourses.empty:
                            CoursesSections = allOfferedCourses.loc[allOfferedCourses['اسم المادة'].str.contains(
                                SpecializationNaturalsciencesCourses['اسم المادة'].iloc[0], na=False, regex=False)]
                            tampTable = FindTable(Table, CoursesSections)

                            if len(tampTable )> 0:
                                SpecializationNaturalsciencesCoursesName.append(SpecializationNaturalsciencesCourses['اسم المادة'].iloc[0])
                                Table = tampTable
                                SpecializationNaturalsciencesCourses.drop(index=SpecializationNaturalsciencesCourses.index[0],axis=0, inplace=True)
                                #registerdeCredits = registerdeCredits + academicPlan['وحدات معتمدة'].iloc[0]
                                break
                            SpecializationNaturalsciencesCourses.drop(index=SpecializationNaturalsciencesCourses.index[0],axis=0, inplace=True)
                    elif 'متطلب جامعة اختياري' in academicPlan['أسم المادة'].iloc[0]:
                        if not haveUniversityRequirements:
                            UniversityRequirements = True
                            UniversityRequirementsCourses = universityRequirementsCoursess(allOfferedCourses, transcripDF)
                        while True and not UniversityRequirementsCourses.empty:
                            CoursesSections = allOfferedCourses.loc[allOfferedCourses['اسم المادة'].str.contains(
                                UniversityRequirementsCourses['اسم المادة'].iloc[0], na=False, regex=False)]
                            tampTable = FindTable(Table, CoursesSections)
                            if len(tampTable )> 0:
                                UniversityRequirementsName.append(UniversityRequirementsCourses['اسم المادة'].iloc[0])
                                UniversityRequirementsCourses.drop(index=UniversityRequirementsCourses.index[0], axis=0, inplace=True)
                                Table = tampTable
                                #registerdeCredits = registerdeCredits + academicPlan['وحدات معتمدة'].iloc[0]
                                break
                            UniversityRequirementsCourses.drop(index=UniversityRequirementsCourses.index[0], axis=0,inplace=True)

                    else:
                        CoursesSections = allOfferedCourses.loc[
                            allOfferedCourses['اسم المادة'].str.contains(academicPlan['أسم المادة'].iloc[0], na=False,
                                                                         regex=False)]
                        tampTable = FindTable(Table, CoursesSections)
                        if len(tampTable )> 0:
                            Table = tampTable
                            #registerdeCredits = registerdeCredits + academicPlan['وحدات معتمدة'].iloc[0]
                    if len(tampTable) > 0 :
                        registerdeCredits = registerdeCredits + academicPlan['وحدات معتمدة'].iloc[0]
                        if academicPlan['وحدات معتمدة'].iloc[0] == 4:
                            countOf4Credits = countOf4Credits + 1
                            if countOf4Credits == avaCoursesOf4Credits and not academicPlan.loc[
                                academicPlan['وحدات معتمدة'] != 4].empty:
                                academicPlan = academicPlan.loc[academicPlan['وحدات معتمدة'] != 4]
                                academicPlan = academicPlan.reset_index(drop=True)
                                notdrap = True
                        if academicPlan['وحدات معتمدة'].iloc[0] == 3:
                            countOf3Credits = countOf3Credits + 1
                            if countOf3Credits == avaCoursesOf3Credits and not academicPlan.loc[
                                academicPlan['وحدات معتمدة'] != 3].empty:
                                academicPlan = academicPlan.loc[academicPlan['وحدات معتمدة'] != 3]
                                academicPlan = academicPlan.reset_index(drop=True)
                                notdrap = True
                        if academicPlan['وحدات معتمدة'].iloc[0] == 2:
                            countOf2Credits = countOf2Credits + 1
                            if countOf2Credits == avaCoursesOf2Credits and not academicPlan.loc[
                                academicPlan['وحدات معتمدة'] != 2].empty:
                                academicPlan = academicPlan.loc[academicPlan['وحدات معتمدة'] != 2]
                                academicPlan = academicPlan.reset_index(drop=True)
                                notdrap = True
                    if not notdrap :
                        academicPlan.drop(index=academicPlan.index[0], axis=0, inplace=True)
                else:
                    cared = academicPlan['وحدات معتمدة'].iloc[0]
                    academicPlan = academicPlan.loc[academicPlan['وحدات معتمدة'] != cared]

    if currentSemesterGraduate or studentLevel:
        academicPlan = academicPlan.reset_index(drop=True)
        if 'مقرر اختياري في التخصص' in academicPlan['أسم المادة'].iloc[0]:
            if not haveSpecializationElectives:
                haveSpecializationElectives = True
                specializationElectivesCourses = SpecializationElectivesSpecializationElectives(allOfferedCourses,transcripDF,remainingCourses,passedCourses)
            CoursesSections = allOfferedCourses.loc[allOfferedCourses['اسم المادة'].str.contains(specializationElectivesCourses['اسـم المقرّر'].iloc[0],na=False, regex=False)]
            SpecializationElectivesName.append(specializationElectivesCourses['اسـم المقرّر'].iloc[0])
            specializationElectivesCourses.drop(index=specializationElectivesCourses.index[0], axis=0, inplace=True)
        elif 'مقرر اختياري حر' in academicPlan['أسم المادة'].iloc[0]:
                if not havefreeElective:
                    havefreeElective = True
                    freeElectiveCourses = FreeElectiveCoursess(allOfferedCourses, transcripDF)

                CoursesSections = allOfferedCourses.loc[allOfferedCourses['اسم المادة'].str.contains(freeElectiveCourses['اسم المادة'].iloc[0],na=False, regex=False)]
                freeElectiveName.append(freeElectiveCourses['اسم المادة'].iloc[0])
                freeElectiveCourses.drop(index=freeElectiveCourses.index[0], axis=0, inplace=True)

        elif 'اختياري علوم طبيعية' in academicPlan['أسم المادة'].iloc[0]:
                if not haveSpecializationNaturalsciencesCourses:
                    haveSpecializationNaturalsciencesCourses = True
                    SpecializationNaturalsciencesCourse = SpecializationNaturalsciencesCoursess(allOfferedCourses,Studentsplan)

                CoursesSections = allOfferedCourses.loc[allOfferedCourses['اسم المادة'].str.contains(SpecializationNaturalsciencesCourse['اسم المادة'].iloc[0], na=False, regex=False)]
                SpecializationNaturalsciencesCoursesName.append(SpecializationNaturalsciencesCourse['اسم المادة'].iloc[0])
                SpecializationNaturalsciencesCourses.drop(index=SpecializationNaturalsciencesCourse.index[0], axis=0,inplace=True)


        elif 'متطلب جامعة اختياري' in academicPlan['أسم المادة'].iloc[0]:
                if not haveUniversityRequirements:
                    UniversityRequirements = True
                    UniversityRequirementsCourses = universityRequirementsCoursess(allOfferedCourses, transcripDF)
                CoursesSections = allOfferedCourses.loc[allOfferedCourses['اسم المادة'].str.contains(UniversityRequirementsCourses['اسم المادة'].iloc[0], na=False, regex=False)]
                UniversityRequirementsName.append(UniversityRequirementsCourses['اسم المادة'].iloc[0])
                UniversityRequirementsCourses.drop(index=UniversityRequirementsCourses.index[0], axis=0,inplace=True)

        else:
            CoursesSections = allOfferedCourses.loc[allOfferedCourses['اسم المادة'].str.contains(academicPlan['أسم المادة'].iloc[0], na=False, regex=False)]
        academicPlan.drop(index=academicPlan.index[0], axis=0, inplace=True)
        for j in range(len(CoursesSections)):
            Table.append(pd.DataFrame(columns=allOfferedCourses.columns).append(CoursesSections.iloc[j]))

        while not academicPlan.empty:
            if 'مقرر اختياري في التخصص' in academicPlan['أسم المادة'].iloc[0]:
                if not haveSpecializationElectives:
                    haveSpecializationElectives = True
                    specializationElectivesCourses = SpecializationElectivesSpecializationElectives(allOfferedCourses,transcripDF,remainingCourses, )
                while not specializationElectivesCourses.empty:
                    CoursesSections = allOfferedCourses.loc[allOfferedCourses['اسم المادة'].str.contains(
                        specializationElectivesCourses['اسـم المقرّر'].iloc[0], na=False, regex=False)]
                    tampTable = FindTable(Table, CoursesSections)
                    if len(tampTable) > 0:
                        Table = tampTable
                        SpecializationElectivesName.append(specializationElectivesCourses['اسـم المقرّر'].iloc[0])
                        break
                    specializationElectivesCourses.drop(index=specializationElectivesCourses.index[0], axis=0,inplace=True)


            elif 'مقرر اختياري حر' in academicPlan['أسم المادة'].iloc[0]:
                if not havefreeElective:
                    havefreeElective = True
                    freeElectiveCourses = FreeElectiveCoursess(allOfferedCourses, transcripDF)
                while not freeElectiveCourses.empty:
                    CoursesSections = allOfferedCourses.loc[
                        allOfferedCourses['اسم المادة'].str.contains(freeElectiveCourses['اسم المادة'].iloc[0],
                                                                     na=False, regex=False)]
                    tampTable = FindTable(Table, CoursesSections)
                    if len(tampTable) > 0:
                        Table = tampTable
                        freeElectiveName.append(freeElectiveCourses['اسم المادة'].iloc[0])
                        freeElectiveCourses.drop(index=freeElectiveCourses.index[0], axis=0, inplace=True)
                        break
                    freeElectiveCourses.drop(index=freeElectiveCourses.index[0], axis=0, inplace=True)
            elif 'اختياري علوم طبيعية' in academicPlan['أسم المادة'].iloc[0]:
                if not haveSpecializationNaturalsciencesCourses:
                    haveSpecializationNaturalsciencesCourses = True
                    SpecializationNaturalsciencesCourse = SpecializationNaturalsciencesCoursess(allOfferedCourses,Studentsplan)
                while not SpecializationNaturalsciencesCourses.empty:
                    CoursesSections = allOfferedCourses.loc[allOfferedCourses['اسم المادة'].str.contains(
                        SpecializationNaturalsciencesCourses['اسم المادة'].iloc[0], na=False, regex=False)]
                    tampTable = FindTable(Table, CoursesSections)
                    if len(tampTable) > 0:
                        Table = tampTable
                        SpecializationNaturalsciencesCoursesName.append(SpecializationNaturalsciencesCourses['اسم المادة'].iloc[0])
                        SpecializationNaturalsciencesCourses.drop(index=SpecializationNaturalsciencesCourses.index[0], axis=0,inplace=True)
                        break
                    SpecializationNaturalsciencesCourses.drop(index=SpecializationNaturalsciencesCourses.index[0], axis=0,inplace=True)

            elif 'متطلب جامعة اختياري' in academicPlan['أسم المادة'].iloc[0]:
                if not haveUniversityRequirements:
                    UniversityRequirements = True
                    UniversityRequirementsCourses = universityRequirementsCoursess(allOfferedCourses, transcripDF)
                while not UniversityRequirementsCourses.empty:
                    CoursesSections = allOfferedCourses.loc[allOfferedCourses['اسم المادة'].str.contains(
                        UniversityRequirementsCourses['اسم المادة'].iloc[0], na=False, regex=False)]
                    tampTable = FindTable(Table, CoursesSections)

                    if len(tampTable) > 0:
                        Table = tampTable
                        UniversityRequirementsName.append(UniversityRequirementsCourses['اسم المادة'].iloc[0])
                        UniversityRequirementsCourses.drop(index=UniversityRequirementsCourses.index[0], axis=0,inplace=True)
                        break
                    UniversityRequirementsCourses.drop(index=UniversityRequirementsCourses.index[0], axis=0,inplace=True)

            else:
                CoursesSections = allOfferedCourses.loc[allOfferedCourses['اسم المادة'].str.contains(academicPlan['أسم المادة'].iloc[0], na=False,regex=False)]
                tampTable = FindTable(Table, CoursesSections)
                if len(tampTable) > 0:
                    Table = tampTable
            academicPlan.drop(index=academicPlan.index[0], axis=0, inplace=True)

    return Table
def sortAnddivideTable(tables):

    global fullTables
    global avlTables
    global avlOffTables
    global fullOffTables
    global t
    fullTables = []
    avlTables = []
    avlOffTables = []
    fullOffTables = []
    for i in range(len(tables)):
        t = tables[i]
        t = pd.DataFrame(t)
        t.reset_index(inplace=True)
        #print(t)
        df = t.loc[t['المسجل'] == t['المتاح']]

        numOff = 0
        dayOfweek = ['الاحد', 'الاثنين', 'الثلاثاء', 'الاربعاء', 'الخميس']
        for day in dayOfweek:
           # print(day)
            if (t[day] == '-').all():
                # if  ~(t[day].str.strip() == '-'.sum() == 0 ) :
                numOff = numOff + 1
        if not df.empty:
            fullTables.append([t.values.tolist(), len(df)])
            if numOff > 0:
                fullOffTables.append([t.values.tolist(), len(df), numOff])
            # print(t)
        else:
            # studentSchedulenew = studentSchedule
            numoffeq = len(pd.merge(t, studentSchedule.rename(columns={'المادة': 'اسم المادة', 'شعبة': 'الشعبة'}),on=['اسم المادة', 'الشعبة'], how='inner', indicator=False))
            avlTables.append([t.values.tolist(), numoffeq])
            if numOff > 0:
                avlOffTables.append([t.values.tolist(), numoffeq, numOff])
    fullTables.sort(key=lambda x: x[1])
    fullOffTables.sort(key=lambda x: (x[1],-x[2]))
    avlTables.sort(key=lambda x: x[1], reverse=True)
    avlOffTables.sort(key=lambda x:(x[1],x[2]), reverse=True)

def contADVK(password):
    driver.get("https://eservicesportal.taibahu.edu.sa/Account/Login")
    while len (driver.find_elements_by_xpath('/html/body/section/div/div/div/div/div[2]/a')) == 0 :
        pass
    driver.find_element_by_xpath('/html/body/section/div/div/div/div/div[2]/a').click()
    while True:
        try:
            driver.find_element_by_xpath('/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[3]/div/div/div/div[2]/div[2]/div/input[1]').send_keys(Student_Email)
            break
        except:
            pass

    driver.find_element_by_xpath('/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[3]/div/div/div/div[4]/div/div/div/div/input').click()
    while True:
        try:
            driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/main/div/div/form/div[1]/div[2]/div/span').click()
            break
        except:
            pass

    driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/main/div/div/div/form/div[2]/div[2]/input').send_keys(password)
    driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/main/div/div/div/form/div[2]/div[4]/span').click()
    driver.find_element_by_xpath('/html/body/div/form/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[3]/div[2]/div/div/div[1]/input').click()
    driver.find_element_by_xpath('/html/body/div[2]/div[1]/header/nav/div[2]/ul[1]/li[2]/a').click()
    driver.find_element_by_xpath('/html/body/div[2]/div[1]/aside/div[1]/div[1]/nav/ul/li[5]/a').click()
    driver.get('https://eservicesportal.taibahu.edu.sa/AcademicAdvising/Index')
    driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/form/div[1]/div/div/div[2]/div[1]/div/div/div[1]/div/input').send_keys(messageTitle)
    driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/form/div[1]/div/div/div[2]/div[1]/div/div/div[3]/textarea').send_keys(messageContent)
    downloads_path = str(Path.home() / "Downloads")
    driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/form/div[1]/div/div/div[2]/div[2]/div[2]/div/div/div/input').send_keys(os.path.join(downloads_path, nameOfFile + '.pdf'))
    time.sleep(10)
    while len(driver.find_elements_by_class_name('has-preview')) == 0:
        pass
    #print(5555)
    #driver.find_element_by_link_text('إرسال').click()




@E_ADVISOR_APP.route('/optimalCoursesWithSchedule')
def optimalCoursesWithSchedule ():
    OfferedCourses = timeTableDatas()
    OfferedCourses = OfferedCourses.rename(columns={'رمز المادةو الرقم': 'رقم المادة', 'رمز المادةو الرقم.1': 'رمز المادة'})
    OfferedCourses['رقم المادة'] = OfferedCourses['رقم المادة'].apply(pd.to_numeric).astype('Int64')
    OfferedCourses = OfferedCourses[ ['رمز المادة', 'رقم المادة', 'اسم المادة', 'الشعبة', 'استاذ المادة', 'الاحد', 'الاثنين', 'الثلاثاء', 'الاربعاء','الخميس', 'المتاح', 'المسجل']]
    OfferedCourses['استاذ المادة'] = OfferedCourses['استاذ المادة'].replace(np.nan, 'لم يتم تعين عضو هيئة تدريس')
    sortAnddivideTable(optimalCourses(Studentsplan,OfferedCourses,transcriptsOfStudent))
    global numOfCR
    if len(avlTables) > 0 :
        numOfCR = len(avlTables[0][0])
    else :
        numOfCR = len(fullTables[0][0])
    if session.get('login') and session.get('user_type') == 'طالب' :
        return render_template('ScheduleSt.html', fullTables=fullTables, avlTables=avlTables, avlOffTables=avlOffTables,fullOffTables=fullOffTables,haveGraduationProject = haveGraduationProject , avlbelAddDreap = avlbelAddDreap)
    elif session.get('login') and  session.get('user_type') ==  'مرشد' :
        return render_template('SHOAdv.html', fullTables=fullTables, avlTables=avlTables, avlOffTables=avlOffTables, fullOffTables=fullOffTables,haveGraduationProject = haveGraduationProject, avlbelAddDreap = avlbelAddDreap)
    if session.get('login'):
        redirect('home')
    else :
        return redirect('/')

@E_ADVISOR_APP.route('/optimalPlan')
def optimalPlan():

    if session.get('login') and session.get('user_type') == 'طالب' :
        plan = OptimalPlans(Studentsplan, semester)
        return render_template('palnforste.html', plan=plan)
    elif session.get('login') and  session.get('user_type') ==  'مرشد' :
        plan = OptimalPlans(Studentsplan, semester)
        return render_template('palnforadv.html', plan=plan)
    if session.get('login'):
        redirect('home')
    else :
        return redirect('/')

@E_ADVISOR_APP.route('/prerequset')
def prerequset():

    if session.get('login')  :
        ac = pd.read_csv('aa.csv')
        coursesname = ac['أسم المادة'].tolist()
        prerequset = ac['1سلسلة المتطلبات'].fillna("ليس للمقرر متطلبات").tolist()
        ac = pd.read_csv('مقررات اختياري في التخصص.csv')
        cn = ac['اسـم المقرّر'].tolist()
        pr = ac['1سلسلة المتطلبات'].fillna('ليس للمقرر متطلبات').tolist()
        for i in pr:
            prerequset.append(i)

        for i in cn :
            coursesname.append(i)
        for i in range(len(prerequset)):
             prerequset[i] = prerequset[i].split(',')

        if session.get('login') and session.get('user_type') == 'طالب':
            return render_template('prestd.html' , coursesname = coursesname , pr = prerequset  )
        elif session.get('login') and session.get('user_type') == 'مرشد':
            return render_template('preAdv.html' , coursesname = coursesname , pr = prerequset  )
        if session.get('login'):
            redirect('home')
    return redirect('/')
@E_ADVISOR_APP.route('/lod' ,  methods=[ 'GET' , 'POST'])
def lodingpage () :

    return render_template('loading.html')
@E_ADVISOR_APP.route('/' ,  methods=[ 'GET' , 'POST'])
def loginPage():

        if request.method == "POST":
                global req_counter
                global url
                session['user_type'] = request.form.get("radio-stacked")
                session['AS_USERNAME'] = request.form.get("username")
                session['AS_PASSWORD'] = request.form.get("userpassword")
                #print(len(driver.find_elements_by_xpath("/html/body/table/tbody/tr[4]/td/table[2]/tbody/tr/td/span")))
                login(session.get('AS_USERNAME'), session.get('AS_PASSWORD'), session.get('user_type'))
                if len(driver.find_elements_by_xpath("/html/body/table/tbody/tr[4]/td/table[2]/tbody/tr/td/span")) != 0  or len(driver.find_elements_by_xpath('/html/body/table/tbody/tr[4]/td/table[2]/tbody/tr/td/div[2]/p')) !=0 :
                    return render_template("loginPage.html", error_message="البيانات المدخلة غير صحيحة")
                #/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/p/table[2]/tbody/tr[6]/td[1]
                if session.get('user_type') == 'طالب' :
                    driver.get('https://eas.taibahu.edu.sa/TaibahReg/studentBasicData.do?ex=preEx')
                if session.get('user_type') == 'طالب' and 'بكالوريوس' in driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/p/table[2]/tbody/tr[6]/td[1]').text :
                    return render_template("loginPage.html", error_message="الخدمات غير متاحه للخريجين")
                if session.get('user_type') == 'طالب' and driver.title == 'تقيم المقررات الدراسية' :
                    return render_template("loginPage.html", error_message="لابد من اجراء التقيم للمقررات الدراسية في موقع الجامعة اولا")
                session['login'] = True
                global firstReq
                firstReq = False
                global user_type
                user_type = session.get('user_type')
                thread = Thread(target=data_extraction)
                thread.setDaemon(True)
                thread.start()

        if not gohome and not firstReq  :

            return ('',204)
        elif gohome and not  firstReq :

            return redirect('home')



                #return render_template("loginpage.html", error_message="البيانات المدخلة غير صحيحة")



        return render_template("loginPage.html", error_message="")

@E_ADVISOR_APP.route('/home')
def home() :
    global gohome
    gohome = False
    global firstReq
    firstReq = True
    if True and user_type == 'طالب' :
       return render_template("homePageForSt.html")
    elif session.get('login') and  session.get('user_type') ==  'مرشد' :
         return  render_template('homePageADV.html')
    elif session.get('user_type') == 'لجنه الارشاد'  :

        return render_template('homePageHedADV.html')
    else :
        return redirect('/')

@E_ADVISOR_APP.route('/CoursesCanTaken' ,  methods=[ 'GET' , 'POST'])
def CoursesCanTaken():

    if session.get('login') and session.get('user_type') == 'طالب' or session.get('user_type') == 'مرشد' :
        maxCreditsForStudentGPA = pd.read_csv('max.csv')
        for i in range(len(maxCreditsForStudentGPA)):
            if (semester in maxCreditsForStudentGPA['الفصل الدراسي'].iloc[i]):
                maxCredits = maxCreditsForStudentGPA['الحد الأعلى من الوحدات المسجلة '].iloc[i]
                break
        OfferedCourses = timeTableDatas()
        CoursesSTCanTaken = CoursesTaken(Studentsplan, OfferedCourses, transcriptsOfStudent)
        #CoursesSTCanTaken = CoursesSTCanTaken.loc[(CoursesSTCanTaken['أسم المادة'].str.contains('مشروع التخرج', na=False, regex=False))]
        CoursesSTCanTaken = CoursesSTCanTaken.values.tolist()
        if request.method == "POST":
            OfferedCourses = OfferedCourses.rename(columns={'رمز المادةو الرقم': 'رقم المادة', 'رمز المادةو الرقم.1': 'رمز المادة'})
            OfferedCourses['رقم المادة'] = OfferedCourses['رقم المادة'].apply(pd.to_numeric).astype('Int64')
            OfferedCourses = OfferedCourses[['رمز المادة', 'رقم المادة', 'اسم المادة', 'الشعبة', 'استاذ المادة', 'الاحد', 'الاثنين', 'الثلاثاء','الاربعاء', 'الخميس', 'المتاح', 'المسجل']]
            OfferedCourses['استاذ المادة'] = OfferedCourses['استاذ المادة'].replace(np.nan, 'لم يتم تعين عضو هيئة تدريس')
            Table = []
            crs = request.values.get('CN').split(",")
            crs.pop()

            for i in range(len(crs)):
                CoursesSection = OfferedCourses.loc[OfferedCourses['اسم المادة'].str.contains(crs[i], na=False, regex=False)]
                if i == 0:
                    for j in range(len(CoursesSection)):
                        Table.append(pd.DataFrame(columns=OfferedCourses.columns).append(CoursesSection.iloc[j]))

                else:

                    Table = FindTable(Table, CoursesSection)

            sortAnddivideTable((Table))
            if session.get('user_type') == 'طالب':
             return render_template('CoursesTakenSTAndSH.html', coursesname=CoursesSTCanTaken, max=maxCredits , fullTables=fullTables, avlTables=avlTables, avlOffTables=avlOffTables,fullOffTables=fullOffTables, avlbelAddDreap = avlbelAddDreap , crs = crs)
            if session.get('user_type') == 'طالب':
             return render_template('CoursesTakenSTAndSH.html', coursesname=CoursesSTCanTaken, max=maxCredits , fullTables=fullTables, avlTables=avlTables, avlOffTables=avlOffTables,fullOffTables=fullOffTables, avlbelAddDreap = avlbelAddDreap , crs = crs)

        if session.get('user_type') == 'طالب':
            return render_template('CoursesTakenST.html' , coursesname = CoursesSTCanTaken , max = maxCredits , crs = [] )
        if session.get('user_type') == 'مرشد':
            return render_template('CoursesTakenAdv.html' , coursesname = CoursesSTCanTaken , max = maxCredits , crs = [] )



    return redirect('/')
def CoursesCanTaken():

    if session.get('login') and session.get('user_type') == 'طالب' or session.get('user_type') == 'مرشد' :
        maxCreditsForStudentGPA = pd.read_csv('max.csv')
        for i in range(len(maxCreditsForStudentGPA)):
            if (semester in maxCreditsForStudentGPA['الفصل الدراسي'].iloc[i]):
                maxCredits = maxCreditsForStudentGPA['الحد الأعلى من الوحدات المسجلة '].iloc[i]
                break
        OfferedCourses = timeTableDatas()
        CoursesSTCanTaken = CoursesTaken(Studentsplan, OfferedCourses, transcriptsOfStudent)
        #CoursesSTCanTaken = CoursesSTCanTaken.loc[(CoursesSTCanTaken['أسم المادة'].str.contains('مشروع التخرج', na=False, regex=False))]
        CoursesSTCanTaken = CoursesSTCanTaken.values.tolist()
        if request.method == "POST":
            OfferedCourses = OfferedCourses.rename(columns={'رمز المادةو الرقم': 'رقم المادة', 'رمز المادةو الرقم.1': 'رمز المادة'})
            OfferedCourses['رقم المادة'] = OfferedCourses['رقم المادة'].apply(pd.to_numeric).astype('Int64')
            OfferedCourses = OfferedCourses[['رمز المادة', 'رقم المادة', 'اسم المادة', 'الشعبة', 'استاذ المادة', 'الاحد', 'الاثنين', 'الثلاثاء','الاربعاء', 'الخميس', 'المتاح', 'المسجل']]
            OfferedCourses['استاذ المادة'] = OfferedCourses['استاذ المادة'].replace(np.nan, 'لم يتم تعين عضو هيئة تدريس')
            Table = []
            crs = request.values.get('CN').split(",")
            crs.pop()

            for i in range(len(crs)):
                CoursesSection = OfferedCourses.loc[OfferedCourses['اسم المادة'].str.contains(crs[i], na=False, regex=False)]
                if i == 0:
                    for j in range(len(CoursesSection)):
                        Table.append(pd.DataFrame(columns=OfferedCourses.columns).append(CoursesSection.iloc[j]))

                else:

                    Table = FindTable(Table, CoursesSection)

            sortAnddivideTable((Table))
            if session.get('user_type') == 'طالب':
             return render_template('CoursesTakenSTAndSH.html', coursesname=CoursesSTCanTaken, max=maxCredits , fullTables=fullTables, avlTables=avlTables, avlOffTables=avlOffTables,fullOffTables=fullOffTables, avlbelAddDreap = avlbelAddDreap , crs = crs)
            if session.get('user_type') == 'طالب':
             return render_template('CoursesTakenSTAndSH.html', coursesname=CoursesSTCanTaken, max=maxCredits , fullTables=fullTables, avlTables=avlTables, avlOffTables=avlOffTables,fullOffTables=fullOffTables, avlbelAddDreap = avlbelAddDreap , crs = crs)

        if session.get('user_type') == 'طالب':
            return render_template('CoursesTakenST.html' , coursesname = CoursesSTCanTaken , max = maxCredits , crs = [] )
        if session.get('user_type') == 'مرشد':
            return render_template('CoursesTakenAdv.html' , coursesname = CoursesSTCanTaken , max = maxCredits , crs = [] )



    return redirect('/')


@E_ADVISOR_APP.before_request
def sessionTime():

    session.permanent = True
    E_ADVISOR_APP.permanent_session_lifetime = timedelta(minutes=15)
    session.modified = True

@E_ADVISOR_APP.route('/listOfStudentName' ,methods=[ 'GET' , 'POST'])
def listOfStudentName():
    if session.get('login') and  session.get('user_type') == 'مرشد'  :
        tr = NamesOfStudents.findAll("tr")
        tr.pop(0)
        tr.pop()
        return render_template("StudentDataList.html" ,heads = NamesOfStudents.findAll("th"), rows = tr, AdvName = session.get('advisorName'))
    elif session.get('login') :
        return redirect('home')
    return redirect('/')
@E_ADVISOR_APP.route('/StatisticForNextSemesterStudents')
def StatisticForNextSemesterStudents():
    if session.get('login') and session.get('user_type') == 'مرشد' or session.get('user_type') == 'لجنه الارشاد' :
        if session.get('user_type') == 'لجنه الارشاد' :
            global gohome
            gohome = False
            global firstReq
            firstReq = True
        StatisticTable = pd.read_csv('aa.csv', usecols=['أسم المادة'])
        StatisticTable['عدد طلاب الكلية'] = 0
        StatisticTable['عدد طلاب الزائر'] = 0
        #الحد الأعلى من الوحدات المسجلة  لخريج الفصل التالي1

        IDSOfGraduateStudents = []
        maxCredits1 = pd.read_csv('max.csv')

        if semester == 'الفصل الأول':
            sm = 'الفصل الثاني'
        elif semester == 'الفصل الثاني':
            sm = 'الفصل الثالث'
        else:
            sm = 'الفصل الأول'
        academicPlan = pd.read_csv('aa.csv')
        academicPlan = academicPlan.loc[(academicPlan['توفر المقرر'] == sm) | (academicPlan['توفر المقرر'] == 'كلهم' )]
        academicPlan = academicPlan.reset_index(drop=True)
        specializationElectivesCoursesName = []
        specializationElectivesCourses = pd.read_csv('مقررات اختياري في التخصص.csv')
        remainingCoursesForGraduateStudents = []

        for i in range(len(maxCredits1)):
            if semester in maxCredits1['الفصل الدراسي'].iloc[i]:
                remainingCreditsForNextSemesterGraduate = maxCredits1["الحد الأعلى من الوحدات المسجلة  لخريج الفصل التالي1"].loc[i]
                break
        for i in range(len(listOfStudenstID)):
            passedCourses = plansOfStudents[i].loc[~(plansOfStudents[i]['التقدير'].isna() | plansOfStudents[i]['التقدير'].str.contains('F'))]
            remainingCourses = plansOfStudents[i].loc[((plansOfStudents[i]['التقدير'].isna())  | (plansOfStudents[i]['التقدير'].str.contains('F')))]
            remainingCourses = remainingCourses.reset_index(drop=True)
            if not remainingCourses.empty :
                global transcriptsOfStudent
                global Studentsplan
                global studentSchedule
                global studentclass
                studentclass = studentsClass[i]
                transcriptsOfStudent = transcriptsOfStudents[i]
                Studentsplan = plansOfStudents[i]

                if remainingCourses['وحدات معتمدة'].sum() <= remainingCreditsForNextSemesterGraduate and "مشروع التخرج(1)" not in remainingCourses["أسم المادة"].values and "مشروع التخرج(1)"  in passedCourses["أسم المادة"].values :

                    IDSOfGraduateStudents.append(listOfStudenstID[i])
                    RC = remainingCourses['أسم المادة'].tolist()
                    remainingCoursesForGraduateStudents.append(remainingCourses['أسم المادة'].tolist())
                    for j in range(len(RC)):
                        if 'مقرر اختياري في التخصص' in RC[j]:
                            specializationElectivesCoursesName.append(transcriptsOfStudents[i].loc[transcriptsOfStudents[i]['أسم المادة'].isin(specializationElectivesCourses['اسـم المقرّر']) & (~transcriptsOfStudents[i]['المعدل'].isin(['ه', 'ع']))]['أسم المادة'].tolist())
                            break
                        elif j == len(RC)-1 :
                            specializationElectivesCoursesName.append(['لايوجد للطالب اي مقررات اختياري تخصص متبقية'])

                op = nextSemesterCourses(passedCourses['أسم المادة'].tolist(), remainingCourses['أسم المادة'].tolist(), academicPlan)

                if 'زائر' in studentZARorNot[i] :
                    StatisticTable.loc[StatisticTable['أسم المادة'].isin(op), ('عدد طلاب الزائر')] = StatisticTable['عدد طلاب الزائر'] + 1

                else :
                    StatisticTable.loc[StatisticTable['أسم المادة'].isin(op), ('عدد طلاب الكلية')] = StatisticTable['عدد طلاب الكلية'] + 1
        StatisticTable['المجموع'] = StatisticTable['عدد طلاب الكلية']+StatisticTable['عدد طلاب الزائر']
        StatisticTable =  StatisticTable.loc[(StatisticTable['أسم المادة'].isin(academicPlan['أسم المادة'])) | (StatisticTable['المجموع'] >0) ]
        #StatisticTable = academicPlan.loc[(academicPlan['توفر المقرر'] == sm) | (academicPlan['توفر المقرر'] == 'كلهم')]
        StatisticTable = StatisticTable.values.tolist()
        return render_template("nextSemesterStatistics.html" , StatisticTable = StatisticTable ,specializationElectivesCoursesName = specializationElectivesCoursesName ,remainingCoursesForGraduateStudents=remainingCoursesForGraduateStudents , IDSOfGraduateStudents=IDSOfGraduateStudents )
    elif session.get('login') :
        return redirect('home')
    return redirect('/')

@E_ADVISOR_APP.route('/addr',methods=[ 'GET' , 'POST'])
def addr():
    if request.method == 'POST' :
        if session.get('login') and session.get('user_type') == 'طالب' or session.get('user_type') == 'مرشد':
            CRS = []
            for i in range(0,numOfCR):
                CR = []
                for j in range(1,5):
                    CR.append(request.form.get(str(i)+''+str (j)))
                CRS.append(CR)
            global cosNOTSH
            CRSDE = []


            for i in range(len(studentSchedule)):
                for j in range(len(CRS)) :

                    if studentSchedule['شعبة'].loc[i] in CRS[j][3] and studentSchedule['المادة'].loc[i] in CRS[j][2]:
                        CRS.pop(j)
                        break
                    if j == len(CRS)-1 and 'مشروع التخرج' not in  studentSchedule['المادة'].loc[i] and studentSchedule['المادة'].loc[i] != '-'  :
                        CRSDE.append(studentSchedule['المادة'].loc[i])
            login(session.get('AS_USERNAME'), session.get('AS_PASSWORD'), session.get('user_type'))
            if len(CRSDE) > 0 :
                if session.get('user_type') == 'طالب':
                    deltCourses(CRSDE)
                else:
                    deltCoursesADV(CRSDE)
            for i in range(len(CRS)) :
                if CRS[i][2] in SpecializationElectivesName :
                    if session.get('user_type') == 'طالب':
                        addAGCourses(CRS[i][2], 'مقرر اختياري في التخصص', CRS[i][3])
                    else:
                        addAGCoursesADV(CRS[i][2], 'مقرر اختياري في التخصص', CRS[i][3])
                # هنا اسم الكلية
                elif CRS[i][2] in freeElectiveName :
                    if session.get('user_type') == 'طالب':
                        addAGCourses(CRS[i][2], 'مقرر اختياري حر', CRS[i][3])
                    else:
                        addAGCoursesADV(CRS[i][2], 'مقرر اختياري حر', CRS[i][3])
                elif CRS[i][2] in UniversityRequirementsName :
                    if session.get('user_type') == 'طالب':
                        addAGCourses(CRS[i][2], 'متطلب جامعة اختياري', CRS[i][3])

                    else :
                        addAGCoursesADV(CRS[i][2], 'متطلب جامعة اختياري', CRS[i][3])
                elif CRS[i][2] in SpecializationNaturalsciencesCoursesName:
                    if session.get('user_type') == 'طالب':
                        addAGCourses(CRS[i][2], 'اختياري علوم طبيعية', CRS[i][3])
                    else :
                        addAGCoursesADV(CRS[i][2], 'اختياري علوم طبيعية', CRS[i][3])
                else:
                    if session.get('user_type') == 'طالب':
                        addCourses(CRS[i][0], CRS[i][1], CRS[i][3])
                    else:
                        addCoursesADV(CRS[i][0], CRS[i][1], CRS[i][3])

        if session.get('login'):
            return  redirect('home')
        return redirect('/')

    return redirect('optimalCoursesWithSchedule')

@E_ADVISOR_APP.route('/contADV',methods=[ 'GET' , 'POST'])
def contADV():
    if request.method == 'POST':
         srever = request.form.get("radio-stacked")
         if srever == 'خدمتك طلب حذف واضافة' :
             CRS = []
             for i in range(0, numOfCR):
                 CR = []
                 for j in range(3, 5):
                     CR.append(request.form.get(str(i) + '' + str(j)))
                 CRS.append(CR)
             global cosNOTSH
             CRSDE = []
             for i in range(len(studentSchedule)):
                 for j in range(len(CRS)):

                     if studentSchedule['شعبة'].loc[i] in CRS[j][1] and studentSchedule['المادة'].loc[i] in CRS[j][0]:
                         CRS.pop(j)
                         break
                     if j == len(CRS) - 1 and 'مشروع التخرج' not in studentSchedule['المادة'].loc[i] and \
                             studentSchedule['المادة'].loc[i] != '-':
                         CRSDE.append(studentSchedule['المادة'].loc[i])
             # المقررات المراد حذفها
             st = Studentsplan.loc[((Studentsplan['التقدير'].str.contains('F')) | (Studentsplan['التقدير'].str.contains('مسجل')) | (Studentsplan['التقدير'].isna()))]
             st = st.loc[((st['أسم المادة'].str.contains('متطلب جامعة اختياري' , regex=False)) | (st['أسم المادة'].str.contains( 'مقرر اختياري حر' ,regex=False)) | ((st['أسم المادة'].str.contains('مقرر اختياري في التخصص',regex=False))))]

             for i in range(0, CRS):
                 if SpecializationElectivesName.count(CRS[i][0]) > 0 :
                     CRS[i][0] = st.loc[st['أسم المادة'].str.contains('مقرر اختياري في التخصص', regex=False)]['اسم المادة'].iloc[0]

                 elif freeElectiveName.count(CRS[i][0]) > 0 :
                     CRS[i][0] = st.loc[st['أسم المادة'].str.contains('مقرر اختياري حر', regex=False)]['اسم المادة'].iloc[0]
                 elif UniversityRequirementsName.count(CRS[i][0]) > 0:
                    CRS[i][0] = st.loc[st['أسم المادة'].str.contains('متطلب جامعة اختياري', regex=False)]['اسم المادة'].iloc[0]
                 elif SpecializationNaturalsciencesCoursesName.count(CRS[i][0]) > 0:
                        CRS[i][0] = 'اختياري علوم طبيعية'
             st = st.loc[~st['أسم المادة'].str.contains(CRS[i][0], regex=False)]
             ktmADDRE(CRSDE, CRS, request.form.get("userpassword"))
         else:
            p = pd.read_csv('aa.csv')
            CRS = []
            for i in range(0,numOfCR):
                CR = []
                CR.append(request.form.get(str(i)+'3'))
                for j in range(1,5):
                    if j != 3 :
                        CR.append(request.form.get(str(i)+''+str (j)))
                CR.append(p.loc[p['أسم المادة'].str.contains(CR[0] ,regex=True)]['وحدات معتمدة'].iloc[0])
                CRS.append(CR)
            global cosNOTSH
            CRSDE = []


            for i in range(len(studentSchedule)):
                for j in range(len(CRS)) :

                    if studentSchedule['شعبة'].loc[i] in CRS[j][3] and studentSchedule['المادة'].loc[i] in CRS[j][0]:
                        CRS.pop(j)
                        break
                    if j == len(CRS)-1 and 'مشروع التخرج' not in  studentSchedule['المادة'].loc[i] and studentSchedule['المادة'].loc[i] != '-'  :
                        CRSDE.append(studentSchedule['المادة'].loc[i])
            login(session.get('AS_USERNAME'), session.get('AS_PASSWORD'), session.get('user_type'))
            global ADVName
            ADVName = driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/p/table[2]/tbody/tr[6]/td[2]').text.split(" ")
            ADVName = ADVName[0] + " " + ADVName[-1]
            WritingOnTheAddAndDeleteForm(CRSDE, CRS)
            global messageContent
            global messageTitle
            messageContent = 'السلام عليكم ورحمة الله، أما بعد ….' \
                             ' \n' \
                             ' إلى سعادة الدكتور/ة :' \
                             + ADVName + \
                             '\n بعد التحية \n ….اتقدم بطلب خدمة' + \
                             ' حذف واضافة \nشاكرين لكم حسن تعاونكم . \nمقدم الطلب\n' ' الاسم: ' \
                             + stname + '\n الرقم الجامعي : ' + session.get('AS_USERNAME')
            messageTitle = "طلب حذف واضافة"
            if srever == 'خدمتك التواصل مع المرشد' :
                contADVK(request.form.get("userpassword"))
            else :
                 ContactWithAdvisorEmail(request.form.get("userpassword"))

            downloads_path = str(Path.home() / "Downloads")
            os.remove(os.path.join(downloads_path, nameOfFile + '.pdf'))
    return redirect('home')



def ContactWithAdvisorEmail(Email_Passsword):
        #Student_Email = 'hnan_1418@taibahu.edu.sa'
        try:
            driver.get("https://tufs.taibahu.edu.sa/adfs/ls/?client-request-id=18ff4f73-2df0-c962-f530-17331882a0b8&username=&wa=wsignin1.0&wtrealm=urn%3afederation%3aMicrosoftOnline&wctx=estsredirect%3d2%26estsrequest%3drQIIAY2RPWzTUACE8-LUJKFAhBBko0JMVP55tuPnGIGUH5OSpkkJKdAslf1s1yY4L_5Lmk6IiYGhcyfEmAWJqaqExMJApywsXWCsOlVIldggEQsb3HA63Xbf3aEgC9Xb_B8JzNwZ3rYhg615-kvB1WwubP3KnzHGl3P-hph_9fZgH1yOdNfQnZi1zJgN9Qm46UTRIFQ5jsTRC0J6LLFtF1ssJh5HRjp3AMAUgBMAJkkki0jhBUUoIBkpEiwWeNYwdEuxDIlBugkZSYaYUSxdYBCWdcPCoq3I5nHySqsUR44wNxK4u9aPZMYmgbc1IGG0TwVVHCKNlLarpXKbrzSl6lDe3Gmt9TQNBxXxqTJ02sMYPat5K95m2YlWqlq97A76Y5eUN3jUrTWU-upqtOEUmUf-oNV92OpE4WjWoFLHfN7HdajYjvRkXbIaogCLW0ppNKH-i-EHip5x8Ej_iKLJwOq75jQFvqfAaWqRX1DT6WxuMU8vJX6mwLuFGe735_dPP3PXtZff3pgfv95NHC1wXhCGOGgXdsq9XX850vxw_MBvG_FyY_y4ZvhrzXaniTm_L8vb9yQV7tFgj6YP6UyayiVuUZV1eEKDMxq8vpA4zPzrquPsNYEXZoMEBgpLEKl8URVRd3oRfLqU-A01&RedirectToIdentityProvider=AD+AUTHORITY")
            driver.find_element_by_id("userNameInput").send_keys(Student_Email)
            driver.find_element_by_id("passwordInput").send_keys(Email_Passsword)
            driver.find_element_by_id("submitButton").click()
            driver.find_element_by_id("idBtn_Back").click()
        except:
            pass

        while True:

            try:

                driver.find_element_by_xpath("//span[contains(text(),'رسالة جديدة')]").click()
                break
            except:
                pass

        while True:
            # aria-label="النص الأساسي للرسالة، اضغط على Alt+F10 للخروج"
            try:
                driver.find_element_by_xpath("//div[@aria-label='إلى']").send_keys('hnan_1418@taibahu.edu.sa')

                break
            except:
                pass
        while len(driver.find_elements_by_class_name('AUEUS')) == 0:
            pass
        downloads_path = str(Path.home() / "Downloads")
        driver.find_elements_by_class_name('AUEUS')[0].send_keys(os.path.join(downloads_path, nameOfFile + '.pdf'))
        while len(driver.find_elements_by_class_name('pV4QR')) == 0:
            pass
        while len(driver.find_elements_by_class_name('pV4QR')) > 0:
            pass
        # driver.find_element_by_xpath("/html/body/div[2]/div/div[2]/div[2]/div[1]/div/span/input").send_keys(filename)
        driver.find_element_by_xpath('//div[@aria-label="النص الأساسي للرسالة، اضغط على Alt+F10 للخروج"]').send_keys(messageContent)
        driver.find_element_by_xpath('//input[@aria-label="إضافة موضوع"]').send_keys(messageTitle)
        driver.find_element_by_xpath("//button[@aria-label='إرسال']").click()
        while len(driver.find_elements_by_class_name('VdeRe')) == 0:
            pass
@E_ADVISOR_APP.route('/logout')
def logout():
    session.pop('login', None)
    return redirect('/')

def addCoursesADV(CR_NAME , CR_NUM , SENAME):
    driver.find_element_by_link_text('المرشدين الأكاديميين').click()

    driver.find_element_by_link_text('الحذف والاضافة لطالب').click()

    # ادخال معلومات الطالب stdNumber
    driver.find_element_by_id("stdNumber").send_keys(studentID)
    driver.find_element_by_name("send").click()


    # كتابة رمز المادة
    driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[1]/td/input').send_keys(CR_NAME)
    # كتابة رقم المادة

    driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[2]/td/input').send_keys(CR_NUM)

    driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[3]/td/table/tbody/tr/td[2]/div/select').click()

    # driver.get('file:///C:/Users/Hnana/Desktop/New%20folder%20(8)/ph%20%D8%AA%D8%B9%D8%AF%D9%8A%D9%84%20%D8%A7%D9%84%D8%AC%D8%AF%D9%88%D9%84%20%D8%A7%D9%84%D8%AF%D8%B1%D8%A7%D8%B3%D9%8A.html')
    # اختيار الشعبة
    # /html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[3]/td/table/tbody/tr/td[2]/div/select
    se = Select(driver.find_element_by_xpath(
        '/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[3]/td/table/tbody/tr/td[2]/div/select'))
    options = se.options
    size = se.__sizeof__()
    i = 0
    index = 0
    while i < size:

        if SENAME in options[i].text:
            index = i
            break
        i = i + 1
    se.select_by_index(index)
    # //*[@id="sectionPart"]/select
    # اضافة المقرر
    driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[4]/td/input').click()
def addCourses(CR_NAME , CR_NUM , SENAME):
    driver.find_element_by_link_text('عمليات أكاديمية').click()
    driver.find_element_by_link_text('الحذف والاضافة').click()
    # كتابة رمز المادة
    driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[1]/td/input').send_keys(CR_NAME)
    # كتابة رقم المادة

    driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[2]/td/input').send_keys(CR_NUM)

    driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[3]/td/table/tbody/tr/td[2]/div/select').click()


    # driver.get('file:///C:/Users/Hnana/Desktop/New%20folder%20(8)/ph%20%D8%AA%D8%B9%D8%AF%D9%8A%D9%84%20%D8%A7%D9%84%D8%AC%D8%AF%D9%88%D9%84%20%D8%A7%D9%84%D8%AF%D8%B1%D8%A7%D8%B3%D9%8A.html')
    # اختيار الشعبة
    # /html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[3]/td/table/tbody/tr/td[2]/div/select
    se = Select(driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[3]/td/table/tbody/tr/td[2]/div/select'))
    options = se.options
    size = se.__sizeof__()
    i = 0
    index = 0
    while i < size:

        if SENAME in options[i].text:
            index = i
            se.select_by_index(index)

            break
        i = i + 1

    # //*[@id="sectionPart"]/select
    # اضافة المقرر
    driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[4]/td/input').click()
def addAGCourses(CR_NAME , CR_NUM , SENAME):
    driver.find_element_by_link_text('عمليات أكاديمية').click()

    driver.find_element_by_link_text('تسجيل المواد الاختيارية و الحرة').click()

    COLGNAM = 'علوم وهندسة الحاسب الآلي'
    if "حر" in CR_NUM:
        se = Select(driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[1]/td/select'))

        options = se.options
        size = se.__sizeof__()
        i = 0

        while i < size:

            if COLGNAM in options[i].text:
                se.select_by_index(i)
                break
            i = i + 1

    driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[3]/td/table/tbody/tr/td[2]/div/select').click()
    # اختيار الشعبة
    se = Select(driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[2]/td/select'))
    options = se.options
    size = se.__sizeof__()
    i = 0

    while i < size :

        if CR_NUM in options[i].text :
            se.select_by_index(i)
            break
        i = i + 1

    se = Select(driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[3]/td/table/tbody/tr/td[2]/div/select'))
    options = se.options
    size = se.__sizeof__()
    i = 0

    while i < size:

        if CR_NAME in options[i].text :
            se.select_by_index(i)
            break
        i = i + 1
    # /html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[4]/td/table/tbody/tr/td[2]/div/select
    se = Select(driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[4]/td/table/tbody/tr/td[2]/div/select'))
    options = se.options
    size = se.__sizeof__()
    i = 0
    while i < size :

        if SENAME in options[i].text :
            se.select_by_index(i)
            time.sleep(5)
            break
        i = i + 1

    #driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[5]/td/input').click()

    driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[4]/td/input').click()
def deltCoursesADV (CR_NAME):
    driver.find_element_by_link_text('المرشدين الأكاديميين').click()
    driver.find_element_by_link_text('الحذف والاضافة لطالب').click()
    # ادخال معلومات الطالب stdNumber
    driver.find_element_by_id("stdNumber").send_keys(studentID)

    rows = len(driver.find_elements_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[2]/tbody/tr/td[2]'))
    for i in range(len(CR_NAME)):
        for r in range(2, rows + 1):
            nameCR = driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[2]/tbody/tr[' + str(r) + ']/td[3]').text
            if CR_NAME[i] in nameCR:
                driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[2]/tbody/tr[' + str(r) + ']/td[8]/input').click()
    driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[2]/tbody/tr[6]/th/input').click()
    driver.find_element_by_xpath('//*[@id="Table_01"]/tbody/tr[2]/td/table/tbody/tr/td[1]/table[2]/tbody/tr[7]/td/input').click()
def deltCourses (CR_NAME):
    driver.find_element_by_link_text('عمليات أكاديمية').click()

    driver.find_element_by_link_text('الحذف والاضافة').click()

    rows = len(driver.find_elements_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[2]/tbody/tr/td[2]'))
    for i in range(len(CR_NAME)):
        for r in range(2, rows + 1):
            nameCR = driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[2]/tbody/tr[' + str(r) + ']/td[3]').text
            if CR_NAME[i] in nameCR:
                driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[2]/tbody/tr[' + str(r) + ']/td[8]/input').click()
    driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[2]/tbody/tr[6]/th/input').click()
    driver.find_element_by_xpath('//*[@id="Table_01"]/tbody/tr[2]/td/table/tbody/tr/td[1]/table[2]/tbody/tr[7]/td/input').click()
def addAGCoursesADV(CR_NAME , CR_NUM , SENAME):
    driver.find_element_by_link_text('المرشدين الأكاديميين').click()
    driver.find_element_by_link_text('تسجيل المواد الاختيارية والحرة').click()
    # ادخال معلومات الطالب stdNumber
    driver.find_element_by_id("stdNumber").send_keys(studentID)
    driver.find_element_by_name("send").click()
    COLGNAM = 'علوم وهندسة الحاسب الآلي'
    if "حر" in CR_NUM:
        se = Select(driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[1]/td/select'))

        options = se.options
        size = se.__sizeof__()
        i = 0

        while i < size:

            if COLGNAM in options[i].text:
                se.select_by_index(i)
                break
            i = i + 1

        time.sleep(4)
    driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[3]/td/table/tbody/tr/td[2]/div/select').click()
    # اختيار الشعبة
    se = Select(driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[2]/td/select'))
    options = se.options
    size = se.__sizeof__()
    i = 0

    while i < size :

        if CR_NUM in options[i].text :
            se.select_by_index(i)
            break
        i = i + 1

    se = Select(driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[3]/td/table/tbody/tr/td[2]/div/select'))
    options = se.options
    size = se.__sizeof__()
    i = 0

    while i < size:

        if CR_NAME in options[i].text :
            se.select_by_index(i)
            break
        i = i + 1
    # /html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[4]/td/table/tbody/tr/td[2]/div/select
    se = Select(driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[4]/td/table/tbody/tr/td[2]/div/select'))
    options = se.options
    size = se.__sizeof__()
    i = 0
    while i < size :

        if SENAME in options[i].text :
            se.select_by_index(i)
            time.sleep(5)
            break
        i = i + 1

    #driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[5]/td/input').click()

    driver.find_element_by_xpath('/html/body/form/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table[3]/tbody/tr[4]/td/input').click()

def deltCoursesOnTheAddAndDeleteForm (CR_NAME):
    rows = len(driver.find_elements_by_xpath('/html/body/table/tbody/tr/td/table[5]/tbody/tr/td[2]'))
    for r in range(2, rows + 1):
        nameCR = driver.find_element_by_xpath(
            '/html/body/table/tbody/tr/td/table[5]/tbody/tr[' + str(r) + ']/td[2]').text
        if CR_NAME in nameCR:
            driver.find_element_by_xpath(
                '/html/body/table/tbody/tr/td/table[5]/tbody/tr[' + str(r) + ']/td[7]/input').click()
            break
def WritingOnTheAddAndDeleteForm(CR_NAME , test ):
    driver.find_element_by_link_text('عمليات أكاديمية').click()
    driver.find_element_by_link_text('طباعة طلب حذف واضافة').click()
    # driver.find_element_by_xpath('/html/body/table/tbody/tr/td/table[8]/tbody/tr[2]/td[2]/table/tbody/tr[1]/td[2]')
    # element =driver.find_element_by_id("some-random-number")
    global stname
    stname = driver.find_element_by_xpath('/html/body/table/tbody/tr/td/table[3]/tbody/tr[2]/td[2]').text.split(" ")
    stname = stname[0] + " " + stname[-1]
    driver.execute_script("arguments[0].innerHTML = '%s <br> ........................'" % stname,
                          driver.find_element_by_xpath(
                              '/html/body/table/tbody/tr/td/table[8]/tbody/tr[2]/td[2]/table/tbody/tr[1]/td[2]'))
    rows = len(driver.find_elements_by_xpath('/html/body/table/tbody/tr/td/table[5]/tbody/tr/td[2]'))
    for i in range(len(CR_NAME)):
        for r in range(2, rows + 1):
            nameCR = driver.find_element_by_xpath(
                '/html/body/table/tbody/tr/td/table[5]/tbody/tr[' + str(r) + ']/td[2]').text
            if CR_NAME[i] in nameCR:
                driver.find_element_by_xpath(
                    '/html/body/table/tbody/tr/td/table[5]/tbody/tr[' + str(r) + ']/td[7]/input').click()
                break
    dtodey = datetime.date(datetime.now())
    driver.execute_script("arguments[0].innerHTML = '%s <br> ............ '" % dtodey, driver.find_element_by_xpath(
        '/html/body/table/tbody/tr/td/table[8]/tbody/tr[2]/td[2]/table/tbody/tr[1]/td[6]'))
    numrows = len(driver.find_elements_by_xpath('/html/body/table/tbody/tr/td/table[7]/tbody/tr'))
    numcoluem = len(driver.find_elements_by_xpath('/html/body/table/tbody/tr/td/table[7]/tbody/tr[2]/td'))
    numofaddcor = 2
    numofaddcor = len(test)
    if len(test) > 4:
        trc = '<td align="center">&nbsp;</td><td align="center" width="355">&nbsp;</td><td align="center" width="174">&nbsp;</td><td align="center">&nbsp;</td><td align="center" width="109">&nbsp;</td><td align="center" width="108">&nbsp;</td><td align="center" width="316">&nbsp;</td>'
        ta = driver.find_element_by_xpath('/html/body/table/tbody/tr/td/table[7]')
        for i in range(len(test) - 3):
            driver.execute_script("arguments[0].insertRow(-1)", ta)
            driver.execute_script("arguments[0].innerHTML = '%s'" % str(trc), driver.find_element_by_xpath(
                '/html/body/table/tbody/tr/td/table[7]/tbody/tr[' + str(numrows) + ']'))
            numrows += 1
    for i in range(2, 2 + numofaddcor):
        for j in range(numcoluem - 1):
            if j == 0:
                driver.execute_script("arguments[0].innerHTML = '%s '" % str(i - 1), driver.find_element_by_xpath(
                    '/html/body/table/tbody/tr/td/table[7]/tbody/tr[' + str(i) + ']/td[' + str(j + 1) + ']'))
            else:
                driver.execute_script("arguments[0].innerHTML = '%s '" % test[i - 2][j - 1],
                                      driver.find_element_by_xpath(
                                          '/html/body/table/tbody/tr/td/table[7]/tbody/tr[' + str(i) + ']/td[' + str(
                                              j + 1) + ']'))
            # + str(r) +
    ids = driver.find_element_by_xpath('/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]').text
    global nameOfFile
    nameOfFile = 'نموذج_حذف_واضافة_' + ids
    b = 1
    downloads_path = str(Path.home() / "Downloads")
    while os.path.exists(os.path.join(downloads_path, nameOfFile + '.pdf')):
        if b == 1:
            nameOfFile = 'نموذج_حذف_واضافة_' + ids + "_1"
        else:
            nameOfFile = 'نموذج_حذف_واضافة_' + ids + "_" + str(b)
        b = b + 1

    driver.execute_script('document.title = "%s"' % nameOfFile)
    driver.execute_script('window.print();')
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
@E_ADVISOR_APP.route('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'
@E_ADVISOR_APP.route('/download')
def download():
   return send_file('IDS.csv', as_attachment=True , attachment_filename='IDSOfStudenstsExample.csv')
@E_ADVISOR_APP.route('/HeadOfTheGuidanceCommitteeServices' , methods=['GET','POST'])
def HeadOfTheGuidanceCommitteeServices():
    if session.get('login') and session.get('user_type') == 'لجنه الارشاد':
        if request.method == 'POST' :

            if 'File' not in request.files:

                pass
            else :
                global listOfStudenstID
                listOfStudenstID = request.files['File']
                listOfStudenstID = pd.read_csv(listOfStudenstID)
                listOfStudenstID = listOfStudenstID[listOfStudenstID.columns[0]].values.tolist()
                login(session.get('AS_USERNAME'), session.get('AS_PASSWORD'), session.get('user_type'))
                global firstReq
                firstReq = False
                global user_type
                user_type = session.get('user_type')
                global gohome
                gohome = False
                thread = Thread(target=HeadOf_data_extraction)
                thread.setDaemon(True)
                thread.start()

        if not gohome and not firstReq:
                return ('', 204)
        elif gohome and not firstReq:
             return redirect(url_for('StatisticForNextSemester'))



    if session.get('login') :
        return redirect(url_for('home'))
    return redirect('/')
@E_ADVISOR_APP.route('/studentServices' , methods=[ 'GET' , 'POST'])
def studentServices():
    global studentName
    if session.get('login') and session.get('user_type') == 'مرشد':
        if request.method == "POST":
            global studentID
            studentID = request.values.get('id')
            studentName = request.values.get('name').split(" ")

            global GPA
            GPA = float(request.form.get('GPA'))

                      # /html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[1]/td/table/tbody/tr[3]/td[1]
            # حق الدكتورة
            # /html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table/tbody/tr[1]/td/table/tbody/tr[4]/td[1]
            index = listOfStudenstID.index(studentID)
            global transcriptsOfStudent
            global Studentsplan
            global studentSchedule
            global studentclass
            global registerdeCreditsSchedule
            studentclass = studentsClass[index]
            transcriptsOfStudent = transcriptsOfStudents[index]
            Studentsplan = plansOfStudents[index]
            studentSchedule = studentScheduleAndregisterdeCreditsList[index][0]
            registerdeCreditsSchedule = studentScheduleAndregisterdeCreditsList[index][1]
            return render_template("homePageForStSEV.html"  )
        if request.method == "GET":
                return render_template("homePageForStSEV.html")
        if session.get('login') :
            return redirect('home')
    return redirect('/')

@E_ADVISOR_APP.route('/completionSchedule', methods=[ 'GET' , 'POST'])
def completionSchedule() :
    if session.get('login') and session.get('user_type') == 'طالب' or session.get('user_type') == 'مرشد' :
        global message
        global message1
        message = ''
        message1 = ''
        maxCreditsForStudentGPA = pd.read_csv('max.csv')
        for i in range(len(maxCreditsForStudentGPA)):
            if (semester in maxCreditsForStudentGPA['الفصل الدراسي'].iloc[i]):
                maxCredits = maxCreditsForStudentGPA['الحد الأعلى من الوحدات المسجلة '].iloc[i]
                break
        '''
        driver.get('file:///C:/Users/Hnana/Desktop/CS491/%D8%A7%D9%84%D8%AE%D8%B7%D8%A9kkkk%20%D8%A7%D9%84%D8%AF%D8%B1%D8%A7%D8%B3%D9%8A%D8%A9.html')
        plan = driver.page_source
        soup = BeautifulSoup(plan, "lxml")
        planData = soup.findAll("table", {"border": "1"})
        tr = pd.read_html(str(planData[1]), header=0, skiprows=(1))
        global Studentsplan
        Studentsplan = tr[0]
        for i in range(2, len(planData)):
                tr = pd.read_html(str(planData[i]), header=0, skiprows=(1))
                Studentsplan = pd.concat([Studentsplan, tr[0]], ignore_index=True)
        '''
        OfferedCourses = timeTableDatas()
        CoursesSTCanTaken = CoursesTaken(Studentsplan, OfferedCourses, transcriptsOfStudent)
        # CoursesSTCanTaken = CoursesSTCanTaken.loc[(CoursesSTCanTaken['أسم المادة'].str.contains('مشروع التخرج', na=False, regex=False))]



        #CoursesSTCanTaken = CoursesSTCanTaken.values.tolist()

        ff = OfferedCourses.loc[(OfferedCourses['اسم المادة'].isin(studentSchedule['المادة'])) & (OfferedCourses['الشعبة'].isin(studentSchedule['شعبة']))]

        if len (CoursesSTCanTaken.loc[~CoursesSTCanTaken['أسم المادة'].isin(ff['اسم المادة'])]) > 0 :
            CoursesCanTakenSchedule = CoursesTakenSchedule(OfferedCourses,CoursesSTCanTaken,maxCredits)

            if len(CoursesCanTakenSchedule) > 0 :
                CoursesCanTakenSchedule = CoursesCanTakenSchedule.rename(columns={'رمز المادةو الرقم': 'رقم المادة', 'رمز المادةو الرقم.1': 'رمز المادة'})
                CoursesCanTakenSchedule['رقم المادة'] = CoursesCanTakenSchedule['رقم المادة'].apply(pd.to_numeric).astype('Int64')
                CoursesCanTakenSchedule = CoursesCanTakenSchedule[['رمز المادة', 'رقم المادة', 'اسم المادة', 'الشعبة', 'استاذ المادة', 'الاحد', 'الاثنين', 'الثلاثاء','الاربعاء', 'الخميس',  'المتاح', 'المسجل','وحده']]
                CoursesCanTakenSchedule['استاذ المادة'] = CoursesCanTakenSchedule['استاذ المادة'].replace(np.nan, 'لم يتم تعين عضو هيئة تدريس')
                columnsCoursesCanTaken = CoursesCanTakenSchedule.columns.values.tolist()
                CoursesCanTakenSchedule = CoursesCanTakenSchedule.values.tolist()
                print(CoursesCanTakenSchedule)
                print('****************************************')
            else:
                columnsCoursesCanTaken = []
                CoursesCanTakenSchedule = []
                message = mes

            CoursesCannotTakenSchedule = CoursesNotTakenSchedule(OfferedCourses, CoursesSTCanTaken, maxCredits)

            if len(CoursesCannotTakenSchedule) > 0 :
                CoursesCannotTakenScheduleColumns = CoursesCannotTakenSchedule[0]
                CoursesCannotTakenScheduleColumns = CoursesCannotTakenScheduleColumns.rename(columns={'رمز المادةو الرقم': 'رقم المادة', 'رمز المادةو الرقم.1': 'رمز المادة'})
                CoursesCannotTakenScheduleColumns['رقم المادة'] = CoursesCannotTakenScheduleColumns['رقم المادة'].apply(pd.to_numeric).astype('Int64')
                CoursesCannotTakenScheduleColumns = CoursesCannotTakenScheduleColumns[['رمز المادة', 'رقم المادة', 'اسم المادة', 'الشعبة', 'استاذ المادة', 'الاحد', 'الاثنين', 'الثلاثاء','الاربعاء', 'الخميس', 'المتاح', 'المسجل', 'وحده']]
                CoursesCannotTakenScheduleColumns = CoursesCannotTakenScheduleColumns.columns.values.tolist()
            else :
                CoursesCannotTakenScheduleColumns = []
                message1 = mes1
            for i in range(len(CoursesCannotTakenSchedule)) :
                CoursesCannotTakenSchedule[i] = CoursesCannotTakenSchedule[i].rename(columns={'رمز المادةو الرقم': 'رقم المادة', 'رمز المادةو الرقم.1': 'رمز المادة'})
                CoursesCannotTakenSchedule[i]['رقم المادة'] = CoursesCannotTakenSchedule[i]['رقم المادة'].apply(pd.to_numeric).astype('Int64')
                CoursesCannotTakenSchedule[i] = CoursesCannotTakenSchedule[i][['رمز المادة', 'رقم المادة', 'اسم المادة', 'الشعبة', 'استاذ المادة', 'الاحد', 'الاثنين', 'الثلاثاء','الاربعاء', 'الخميس',  'المتاح', 'المسجل','وحده']]
                CoursesCannotTakenSchedule[i]['استاذ المادة'] = CoursesCannotTakenSchedule[i]['استاذ المادة'].replace(np.nan, 'لم يتم تعين عضو هيئة تدريس')
                CoursesCannotTakenSchedule[i].fillna('',inplace=True)
                CoursesCannotTakenSchedule[i] = CoursesCannotTakenSchedule[i].values.tolist()

                print(CoursesCannotTakenSchedule[i])
            print()
        #.columns.values.tolist()


        else :
             CoursesCanTakenSchedule = []
             CoursesCannotTakenScheduleColumns = []
             CoursesCannotTakenSchedule = []
             columnsCoursesCanTaken = []

             message = 'لا يوجد مقررات يمكن اضافتها بناء على الخطة الدراسية'
             message1 = 'لا يوجد مقررات يمكن اضافتها بناء على الخطة الدراسية'
        if session.get('user_type') == 'طالب' and request.method == "POST" :
             cuoseaddd = request.form.get("cr").split(",")
             cuoseaddd.pop()
             cuoseadddSH = request.form.get("sh").split(",")
             cuoseadddSH.pop()
             cuoseadel = []
             if request.form.get("radio-stacked1") == 'الشعب المتعارضة' :
                 cuoseadel = request.form.get("crd").split(",")
                 cuoseadel.pop()
             login(session.get('AS_USERNAME'), session.get('AS_PASSWORD'), session.get('user_type'))
             global ADVName
             '''
             ADVName = driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[1]/p/table[2]/tbody/tr[6]/td[2]').text.split(" ")
             ADVName = ADVName[0] + " " + ADVName[-1]
             WritingOnTheAddAndDeleteForm(cuoseadel, CRS)
             global messageContent
             global messageTitle
             messageContent = 'السلام عليكم ورحمة الله، أما بعد ….' \
                              ' \n' \
                              ' إلى سعادة الدكتور/ة :' \
                              + ADVName + \
                              '\n بعد التحية \n ….اتقدم بطلب خدمة' + \
                              ' حذف واضافة \nشاكرين لكم حسن تعاونكم . \nمقدم الطلب\n' ' الاسم: ' \
                              + stname + '\n الرقم الجامعي : ' + session.get('AS_USERNAME')
             messageTitle = "طلب حذف واضافة"
             if srever == 'خدمتك التواصل مع المرشد':
                 contADVK(request.form.get("userpassword"))
             else:
                 ContactWithAdvisorEmail(request.form.get("userpassword"))
                 print(4)
             downloads_path = str(Path.home() / "Downloads")
             os.remove(os.path.join(downloads_path, nameOfFile + '.pdf'))
        #return redirect('home')
        '''
        if session.get('user_type') == 'طالب':

            return render_template('CoursesTakenSchedulestd.html', columnsCoursesCanTaken=columnsCoursesCanTaken, CoursesCanTaken = CoursesCanTakenSchedule , columnsCoursesCannotTaken= CoursesCannotTakenScheduleColumns , CoursesCannotTaken = CoursesCannotTakenSchedule, regC =registerdeCreditsSchedule ,maxC = maxCredits , message = message , message1 = message1,avlbelAddDreap=avlbelAddDreap,isStu=True)
        if session.get('user_type') == 'مرشد':
            return render_template('CoursesTakenScheduleAdv.html', columnsCoursesCanTaken=columnsCoursesCanTaken, CoursesCanTaken = CoursesCanTakenSchedule , columnsCoursesCannotTaken= CoursesCannotTakenScheduleColumns , CoursesCannotTaken = CoursesCannotTakenSchedule, regC =registerdeCreditsSchedule ,maxC = maxCredits , message = message , message1 = message1,avlbelAddDreap= avlbelAddDreap,isStu=False)
    elif session.get('login') :
        return redirect('home')
    return redirect('/')






def ktmADDRE(CR_NAME,crs,password):
    driver.get("https://eservicesportal.taibahu.edu.sa/Account/Login")
    while len (driver.find_elements_by_xpath('/html/body/section/div/div/div/div/div[2]/a')) == 0 :
        pass
    driver.find_element_by_xpath('/html/body/section/div/div/div/div/div[2]/a').click()
    while True:
        try:
            driver.find_element_by_xpath('/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[3]/div/div/div/div[2]/div[2]/div/input[1]').send_keys(Student_Email)
            break
        except:
            pass

    driver.find_element_by_xpath('/html/body/div/form[1]/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[3]/div/div/div/div[4]/div/div/div/div/input').click()
    while True:
        try:
            driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/main/div/div/form/div[1]/div[2]/div/span').click()
            break
        except:
            pass

    driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/main/div/div/div/form/div[2]/div[2]/input').send_keys(password)
    driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/main/div/div/div/form/div[2]/div[4]/span').click()
    driver.find_element_by_xpath('/html/body/div/form/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[3]/div[2]/div/div/div[1]/input').click()
    driver.find_element_by_xpath('/html/body/div[2]/div[1]/header/nav/div[2]/ul[1]/li[2]/a').click()
    driver.find_element_by_xpath('/html/body/div[2]/div[1]/aside/div[1]/div[1]/nav/ul/li[5]/a').click()
    driver.get('https://eservicesportal.taibahu.edu.sa/RequestToAddAndDelete/Index')

    rows = len(driver.find_elements_by_xpath('/html/body/div[2]/div[2]/div/form/div[1]/div/div/div[2]/div[2]/div/table/tbody/tr/td[2]'))
    for i in range(len(CR_NAME)):
        for r in range(2, rows + 1):
            nameCR = driver.find_element_by_xpath(
                '/html/body/div[2]/div[2]/div/form/div[1]/div/div/div[2]/div[2]/div/table/tbody/tr[' + str(r) + ']/td[2]/input').text
            if CR_NAME[i] in nameCR:
                driver.find_element_by_xpath(
                    '/html/body/div[2]/div[2]/div/form/div[1]/div/div/div[2]/div[2]/div/table/tbody/tr[' + str(r) + ']/td[2]/input').click()

    j = 2

    for i in range(1, len(crs)+1):
        driver.find_element_by_link_text('إضافة مادة جديدة').click()
        while len(driver.find_elements_by_class_name('d-none')) < i + 1:
            pass
        driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/form/div[1]/div/div/div[2]/div[2]/div/table/tbody/tr[' + str(j) + ']')
        driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/form/div[1]/div/div/div[2]/div[2]/div/table/tbody/tr[' + str(j) + ']/td[1]/select')
        j += 1
    # المقررات
    # /html/body/div[2]/div[2]/div/form/div[1]/div/div/div[2]/div[2]/div/table/tbody/tr[2]/td[1]/select
    # /html/body/div[2]/div[2]/div/form/div[1]/div/div/div[2]/div[2]/div/table/tbody/tr[3]/td[1]/select
    # sh
    # /html/body/div[2]/div[2]/div/form/div[1]/div/div/div[2]/div[2]/div/table/tbody/tr[3]/td[3]/select
    # /html/body/div[2]/div[2]/div/form/div[1]/div/div/div[2]/div[2]/div/table/tbody/tr[2]/td[3]/select

    for i in range(2, len(crs) + 2):
        se = Select(driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/form/div[1]/div/div/div[2]/div[2]/div/table/tbody/tr[' + str(i) + ']/td[1]/select'))
        se.select_by_value(crs[i - 2][0])
    time.sleep(10)
    for i in range(2, len(crs) + 2):
        se = Select(driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/form/div[1]/div/div/div[2]/div[2]/div/table/tbody/tr[' + str( i) + ']/td[3]/select'))
        se.select_by_value(crs[i - 2][1])
    driver.find_element_by_link_text('إرسال').click()

@E_ADVISOR_APP.after_request
def foo(response):

    method = request.method == "GET"
    path = request.path == "/" or request.path == '/HeadOfTheGuidanceCommitteeServices'

    #response = Response(__name__)

    if  path and not firstReq  and not gohome :

        time.sleep(25)
        return redirect('/')
    return response



if __name__ == "__main__":
    E_ADVISOR_APP.secret_key = 'super secret key'
    E_ADVISOR_APP.config['SESSION_ TYPE'] = 'filesystem'

    #E_ADVISOR_APP.config['UPLOAD_FOLDER']
    E_ADVISOR_APP.static_folder = 'static'

#    session(E_ADVISOR_APP)
    #E_ADVISOR_APP.config.update(dict(PREFERRED_URL_SCHEME='https'))
    #E_ADVISOR_APP.run( port=1245 , threaded = True)
    port = int(os.environ.get("PORT", 5000))
    E_ADVISOR_APP.run(host='0.0.0.0', port=port, threaded = True)
