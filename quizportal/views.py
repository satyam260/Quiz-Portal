from django.shortcuts import render,redirect
from django.template import loader
from django import forms
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect
from .models import *
from .forms import *
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import timedelta
from datetime import datetime
import pytz
from tzlocal import get_localzone # $ pip install tzlocal
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from random import *




## 		RANDOMIZATION - RICHESH ###
sec1h=[]
sec2h=[]
sec3h=[]
flag = False

def randomize_it():
	global flag
	flag = True
	s1 = list(Section1.objects.all())
	s2 = list(Section2.objects.all())
	s3 = list(Section3.objects.all())
	global sec1h
	global sec2h
	global sec3h
	if len(s1)>0:
		f = s1[0]
		sec1h.append(f.id_no)
		s1.pop(0)
		shuffle(s1)
		for x in s1:
			sec1h.append(x.id_no)
	if len(s2)>0:
		f = s2[0]
		sec2h.append(f.id_no)
		s2.pop(0)
		shuffle(s2)
		for x in s2:
			sec2h.append(x.id_no)
	if len(s3)>0:
		f = s3[0]
		sec3h.append(f.id_no)
		s3.pop(0)
		shuffle(s3)
		for x in s3:
			sec3h.append(x.id_no)			
	

# end randomization




#Change Password
@login_required(login_url='login')
def ftpassch(request):
	user=User.objects.get(username=request.user)
	if(request.method=="POST"):
			
			user.set_password(request.POST.get('password'))
			obj,notif=userpasswords.objects.get_or_create(username=request.user, password=request.POST.get('password'))
			if notif is True:
				obj.save()
			user.last_name='1'
			user.save()
			return HttpResponseRedirect('/logout')
	else:
		if(user.last_name=='1'):
			return HttpResponseRedirect('/detail/Section/1/1/1')
		else:
			return render(request,'quizportal/passchng.html',{'name':user.first_name})



#Questions rendering
@login_required(login_url='login')
def detail(request, section_no, id_no, random_string):
	global flag
	global sec1h
	global sec2h
	global sec3h
	

	if flag is False:
		randomize_it()
	print(sec1h)
	print(sec2h)
	print(sec3h)
	if section_no =='1':
		if len(sec1h)>0:
			id_no = sec1h[0]
		else:
			return HttpResponseRedirect('/detail/Section/2/1/1')
	if section_no=='2':
		if len(sec2h)>0:
			id_no = sec2h[0]
		else:
			return HttpResponseRedirect('/detail/Section/3/1/1')
	if section_no=='3':
		if len(sec3h)>0:
			id_no = sec3h[0]
		else:
			return HttpResponseRedirect('/ended')
	
	#Check if logged in user is Admin
	if(request.user.username=='admin' or request.user.username=='hydra'  or request.user.username=='' or request.user.username=='testadmin'):
		return HttpResponseRedirect('/adminmain')

	else:
		if(section_no=='1'):
			total_questions=len(Section1.objects.all())
			total_time="1 hour"
		elif(section_no=='2'):
			total_questions=len(Section2.objects.all())
			total_time="0 mins"
		elif(section_no=='3'):
			total_questions=len(Section3.objects.all())
			total_time="0 mins"

		if((int)(random_string)>1):
			if(len(Cheat.objects.filter(Q(id_no=request.user)))==0):
				obj,notif=Cheat.objects.get_or_create(id_no=request.user, numberOfAttempts=1)
				if notif is True:
					obj.save()
			else:
				obj=Cheat.objects.get(id_no=request.user)
				if(obj.numberOfAttempts<=5):
					obj.numberOfAttempts=obj.numberOfAttempts+1
					obj.save()
				elif(obj.numberOfAttempts>5):
					return HttpResponseRedirect("/ended")
		
		#Setting time to user given time in minutes from the login to that section , time
		if(len(Time.objects.filter(Q(s_no=(int)(section_no))))==0):
			return HttpResponseRedirect('/ended')


		if(section_no =='1' and len(Time1.objects.filter(Q(id_no=request.user)))==0 and id_no=='1' and len(Section1.objects.all())>0):
			
			
			#tzname = request.session.get('django_timezone')
			#timezone.activate(pytz.timezone(tzname))
			start=timezone.localtime(timezone.now())
			print("start time : ",start)
			print(start, timezone.localtime(timezone.now()))
			timeobj=Time.objects.filter(Q(s_no=1))
			for timeob in timeobj:
				end=timeob.time
				break
			end=str(end).split(":")
			#print(end)
			end2=end[1]
			end1=end[0]
			end3=end[2]
			print(end1, end2)

			obj,notif=Time1.objects.get_or_create(id_no=request.user, start_time=start, end_time=start+timedelta(hours=(int)(end1), minutes=(int)(end2)))
			if notif is True:
				obj.save()
				print('start_time', obj.start_time)
				print('end_time', obj.end_time)

		elif(section_no=='2' and len(Time2.objects.filter(Q(id_no=request.user)))==0 and id_no=='1' and len(Section2.objects.all())>0):
			time=Time1.objects.filter(Q(id_no=request.user))
			if(len(time)>0):
				for i in time:
					endtime=i.end_time
					break
			if(endtime<timezone.localtime(timezone.now())):
				start=timezone.localtime(timezone.now())
				timeobj=Time.objects.filter(Q(s_no=2))
				for timeob in timeobj:
					end=timeob.time
					break
				end=str(end).split(":")
				end=end[1]

				obj,notif=Time2.objects.get_or_create(id_no=request.user,start_time=start, end_time=start+timedelta(minutes=(int)(end)))
				if notif is True:
					obj.save()

		elif(section_no=='3' and len(Time3.objects.filter(Q(id_no=request.user)))==0 and id_no=='1' and len(Section3.objects.all())>0):
			
			time=Time1.objects.filter(Q(id_no=request.user))
			time1=Time2.objects.filter(Q(id_no=request.user))
			if(len(time)>0):
				for i in time:
					endtime=i.end_time
					break
			if(len(time1)>0):
				for i in time1:
					endtime1=i.end_time
					break
			if(endtime<timezone.localtime(timezone.now()) and endtime1<timezone.localtime(timezone.now())):
				start=timezone.localtime(timezone.now())
				timeobj=Time.objects.filter(Q(s_no=3))
				for timeob in timeobj:
					end=timeob.time
					break
				end=str(end).split(":")
				end=end[1]
				obj,notif=Time3.objects.get_or_create(id_no=request.user,start_time=start, end_time=start+timedelta(minutes=(int)(end)))
				if notif is True:
					obj.save()

					
		#Quiz Ended
		if(section_no=='1'):
			time=Time1.objects.filter(Q(id_no=request.user))
		elif(section_no=='2'):
			time=Time2.objects.filter(Q(id_no=request.user))
		else:
			time=Time3.objects.filter(Q(id_no=request.user))

		if(len(time)>0):
			for i in time:
				endtime=i.end_time
				#start=i.start_time
				
				break
			#Time Conversion according to 24hrs clock
			f=(endtime)
			f=timezone.localtime(endtime)
			#print(f)
			f=str(f).split(" ")
			time=f[1]
			print("TIME : ",time)
			time=str(time).split(":")
			h=str(((int)(time[0]))+1)	#time for questions
			m=str(((int)(time[1])))
		else:
			endtime=""

		if(len(time)<=0 and (timezone.localtime(endtime) > timezone.localtime(timezone.now()))):
			print('end 1')
			return HttpResponseRedirect('/ended')


		#Trying to access Section 2 before time
		if(section_no=='2'):
			time2=Time1.objects.filter(Q(id_no=request.user))
			if(len(time2)>0):
				for i in time2:
					endtime=i.end_time
					break
			#print(endtime, timezone.localtime(timezone.now()))
			if( timezone.localtime(endtime) > timezone.localtime(timezone.now())):
				return HttpResponseRedirect('/detail/Section/1/1/1')

		#Trying to access Section 3 before time
		elif(section_no=='3'):
			time3=Time1.objects.filter(Q(id_no=request.user))
			if(len(time3)>0):
				for i in time3:
					endtime=i.end_time
					break
			#print(endtime, timezone.localtime(timezone.now()))
			if(timezone.localtime(endtime) > timezone.localtime(timezone.now())):
				return HttpResponseRedirect('/detail/Section/1/1/1')

			time2=Time2.objects.filter(Q(id_no=request.user))
			if(len(time2)>0):
				for i in time2:
					endtime=i.end_time
					break
			if(timezone.localtime(endtime) > timezone.localtime(timezone.now())):
				if(len(Section2.objects.all())>0):
					return HttpResponseRedirect('/detail/Section/2/1/1')


		#POST request
		if(request.method=='POST'):
			if section_no=='1':
				id_no = sec1h[0]
				sec1h.pop(0)
			elif section_no =='2':
				id_no = sec2h[0]
				sec2h.pop(0)
			elif section_no=='3':
				id_no = sec3h[0]
				sec3h.pop(0)

			id1=(int)(id_no)
			id1=id1-1
			print("id no : ",id_no,"id1 : ",id1)

			if(section_no=='1'):
				id1=(int)(id_no)
				question=Section1.objects.filter(id_no=str(id_no))
				
				question1=Section1.objects.filter(id_no=str(id1))

				p1=SolvedQ1.objects.filter(Q(q_id=question1.get(id_no=id1)) ,Q(id_no=request.user), Q(check=False))
			
			elif(section_no=='2'):
				id1 = (int)(id_no)
				question=Section2.objects.filter(id_no=str(id_no))
				question1=Section2.objects.filter(id_no=str(id1))
				p1=SolvedQ2.objects.filter(Q(q_id=question1.get(id_no=id1)) ,Q(id_no=request.user), Q(check=False))
			
			elif(section_no=='3'):
				id1 = (int)(id_no)
				question=Section3.objects.filter(id_no=str(id_no))
				question1=Section3.objects.filter(id_no=str(id1))
				p1=SolvedQ3.objects.filter(Q(q_id=question1.get(id_no=id1)) ,Q(id_no=request.user), Q(check=False))


			#Choices
			for i in question1:
				correct_choice1=i.correct_choice
				if(len(p1)==0 and correct_choice1==request.POST.get('choice')):
					if(section_no=='1'):
						obj,notif=SolvedQ1.objects.get_or_create(id_no=request.user, q_id=question1.get(id_no=id1), check=True)
					elif(section_no=='2'):
						obj,notif=SolvedQ2.objects.get_or_create(id_no=request.user, q_id=question1.get(id_no=id1), check=True)
					elif(section_no=='3'):
						obj,notif=SolvedQ3.objects.get_or_create(id_no=request.user, q_id=question1.get(id_no=id1), check=True)
						
					if notif is True:
						obj.save()

				else:
					if(len(p1)==0 and correct_choice1!=request.POST.get('choice')):
						if(section_no=='1'):
							obj,notif=SolvedQ1.objects.get_or_create(id_no=request.user, q_id=question1.get(id_no=id1), check=False)
						elif(section_no=='2'):
							obj,notif=SolvedQ2.objects.get_or_create(id_no=request.user, q_id=question1.get(id_no=id1), check=False)
						else:
							obj,notif=SolvedQ3.objects.get_or_create(id_no=request.user, q_id=question1.get(id_no=id1), check=False)
								
						if notif is True:
							obj.save()

			if(len(question)>0):
				args={}
				query = []
				for i in question:
					if(i.image):
						query.append(i)	
						#Image.open('http://127.0.0.1:8000/media/'+str(i.image))
						args={'question':question, 'section_no':section_no, 'timer':h+":"+m+":"+time[2].split("+")[0], 'image1':"image",
						'total_questions':total_questions, 'total_time':total_time}
					else:
						args={'question':question, 'section_no':section_no, 'timer':h+":"+m+":"+time[2].split("+")[0],
						'total_questions':total_questions, 'total_time':total_time}
					break
				return render(request, 'quizportal/questions.html', args)

			else:
				if(len(SolvedQ1.objects.filter(Q(id_no=request.user))) < len(Section1.objects.all())):
					return HttpResponseRedirect('/detail/Section/1/'+str(int(id_no)+1)+"/1")
				elif(len(SolvedQ2.objects.filter(Q(id_no=request.user)))< len(Section2.objects.all()) and section_no=='1'):
					markSection1End(request)
					return HttpResponseRedirect('/detail/Section/2/1/1')
				elif(len(SolvedQ2.objects.filter(Q(id_no=request.user)))< len(Section2.objects.all()) and section_no=='2'):
					return HttpResponseRedirect('/detail/Section/2/'+str(int(id_no)+1)+"/1")
				elif(len(SolvedQ3.objects.filter(Q(id_no=request.user)))< len(Section3.objects.all()) and section_no=='2'):
					markSection2End(request)
					return HttpResponseRedirect('/detail/Section/3/1/1')
				elif(len(SolvedQ3.objects.filter(Q(id_no=request.user)))< len(Section3.objects.all()) and section_no=='3'):
					return HttpResponseRedirect('/detail/Section/2/'+str(int(id_no)+1)+"/1")
				else:
					print("end")
					print('end 2')
					return HttpResponseRedirect('/ended')


		#GET request
		else:
			
			#Check if its the last Question for Section 1 (no prob on reload bug)
			if(section_no=='1'):
				# id_no = randomize(section_no=1)
				print("sec1h initi : ",sec1h[0])
								
				question=Section1.objects.all()
				if(len(question)==0):
					markSection1End(request)
					if(len(Section2.objects.all())>0):
						print('end 4')
						return HttpResponseRedirect('/detail/Section/2/1/1')
					else:
						print("Ended")
						print('end 3')
						return HttpResponseRedirect('/ended')
			
			#Check if its the last Question for Section 2
			elif(section_no=='2'):
				question=Section2.objects.all()
				if(len(question)==0):
					markSection2End(request)
					if(len(Section3.objects.all())>0):
						return HttpResponseRedirect('/detail/Section/3/1/1')
					else:
						return HttpResponseRedirect('/ended')
			
			#Check if its the last Question for Section 3
			elif(section_no=='3'):
				question=Section3.objects.all()
				if(len(question)==0):
					markSection3End(request)
					return HttpResponseRedirect('/ended')



			#If trying to access wrong question_no
			if(section_no=='1'):
				id_no = sec1h[0]
				if id_no =='1':
					sec1h.pop(0)
				id1 = int(id_no)
				print("id no : ",id_no," id1 : ",id1)
				question1=Section1.objects.filter(Q(id_no=str(id1)))
				if(len(question1)==0):
					# print("yes") ( no prob on reload bug)
					print('end 5')
					markSection1End(request)
					return HttpResponseRedirect('/detail/Section/2/1/1')
				else:
					#Attempted Questions
					
					if(len(SolvedQ1.objects.filter(Q(q_id=question1.get(id_no=id1)) ,Q(id_no=request.user)))>0):
						score=SolvedQ1.objects.filter(Q(id_no=request.user))
						return render(request, 'quizportal/attempted.html', {'section_no':section_no, 'id_no':id1})
					else:
						#Unattempted
						question=Section1.objects.filter(Q(id_no__exact=id_no))
						args={}
						for i in question:
							print('line 383') #this is the problem
							if(i.image):
								#Image.open('http://127.0.0.1:8000/media/'+str(i.image))
								args={'question':question, 'section_no':section_no, 'timer':h+":"+m+":"+time[2].split("+")[0], 'image1':"image",
								'total_questions':len(Section1.objects.all()), 'total_time':total_time}
							else:
								args={'question':question, 'section_no':section_no, 'timer':h+":"+m+":"+time[2].split("+")[0],
								'total_questions':len(Section1.objects.all()), 'total_time':total_time}
							break
						return render(request, 'quizportal/questions.html', args)

			#Section 2
			elif(section_no=='2'):
				id_no = sec2h[0]
				if id_no =='2':
					sec2h.pop(0)
				id1 = int(id_no)
				print("id2 no : ",id_no," id1 : ",id1)
				question1=Section2.objects.filter(Q(id_no=str(id1)))
				print("sec2 ques : ",question1)
				print("Question for sec 2 : ",question1)
				if(len(question1)==0):
					print('line 400')
					markSection2End(request)
					return HttpResponseRedirect('/detail/Section/3/1/1')
				else:
					#Attempted Questions
					print('line 405')
					if(len(SolvedQ2.objects.filter(Q(q_id=question1.get(id_no=id1)) ,Q(id_no=request.user)))>0):
						score=SolvedQ2.objects.filter(Q(id_no=request.user))
						return render(request, 'quizportal/attempted.html', {'section_no':section_no, 'id_no':id1})
					else:
						#Unattempted

						question=Section2.objects.filter(Q(id_no__exact=str(id_no)))
						args={}
						for i in question:
							if(i.image):
								#Image.open('http://127.0.0.1:8000/media/'+str(i.image))
								args={'question':question, 'section_no':section_no, 'timer':h+":"+m+":"+time[2].split("+")[0], 'image1':"image",
								'total_questions':len(Section2.objects.all()), 'total_time':total_time}
							else:
								args={'question':question, 'section_no':section_no, 'timer':h+":"+m+":"+time[2].split("+")[0],
								'total_questions':len(Section2.objects.all()), 'total_time':total_time}
							break
						return render(request, 'quizportal/questions.html', args)

			#Section 3
			elif(section_no=='3'):
				id_no = sec3h[0]
				if id_no =='3':
					sec3h.pop(0)
				id1 = int(id_no)
				print("id no3 : ",id_no," id1 : ",id1)
				question1=Section3.objects.filter(Q(id_no=str(id1)))
				print("Question for sec 3 : ",question1)
				if(len(question1)==0):
					print('line 428')
					return HttpResponseRedirect('/ended')
				else:
					#Attempted Questions
					if(len(SolvedQ3.objects.filter(Q(q_id=question1.get(id_no=id1)) ,Q(id_no=request.user)))>0):
						score=SolvedQ3.objects.filter(Q(id_no=request.user))
						return render(request, 'quizportal/attempted.html', {'section_no':section_no, 'id_no':id1})
					else:
						#Unattempted
						question=Section3.objects.filter(Q(id_no__exact=str(id_no)))
						args={}
						for i in question:
							if(i.image):
								#Image.open('http://127.0.0.1:8000/media/'+str(i.image))
								args={'question':question, 'section_no':section_no, 'timer':h+":"+m+":"+time[2].split("+")[0], 'image1':"image",
								'total_questions':len(Section3.objects.all()), 'total_time':total_time}
							else:
								args={'question':question, 'section_no':section_no, 'timer':h+":"+m+":"+time[2].split("+")[0],
								'total_questions':len(Section3.objects.all()), 'total_time':total_time}
							break
						return render(request, 'quizportal/questions.html', args)
			elif(section_no>'3'):
				print('end 6')
				return HttpResponseRedirect('/ended')


#Scorecard
@login_required(login_url='login')
def score(request, section_no, id_no, number):
	if(section_no=='1'):
		score=SolvedQ1.objects.filter(Q(id_no=request.user), Q(check=True))
	elif(section_no=='2'):
		score=SolvedQ2.objects.filter(Q(id_no=request.user), Q(check=True))
	elif(section_no=='3'):
		score=SolvedQ3.objects.filter(Q(id_no=request.user), Q(check=True))
	id1=User.objects.filter(Q(username=request.user)).values('username')
	return render(request, 'quizportal/score.html', {'score':len(score), 'id':id1, 'section_no':section_no, 'id_no':id_no})


#Actual function for ending Section 1
def markSection1End(request):
	question=Section1.objects.all()
	for i in question:
		if(SolvedQ1.objects.filter(Q(id_no=request.user), Q(q_id=question.get(id_no=i.id_no)))):
			continue
		else:
			obj,notif=SolvedQ1.objects.get_or_create(id_no=request.user, q_id=question.get(id_no=i.id_no), check=False)
			if notif is True:
				obj.save()
	times=Time1.objects.filter(Q(id_no=request.user))
	for time1 in times:
		time1.end_time=timezone.localtime(timezone.now())
		time1.save()
		break


#test module, delete before production
def kill(request):
	SolvedQ1.objects.all().delete()
	SolvedQ2.objects.all().delete()
	SolvedQ3.objects.all().delete()
	return HttpResponse('<html><body><h1>Killed</h1></body></html>')

#Actual function for ending Section 2
def markSection2End(request):
	question=Section2.objects.all()
	for i in question:
		if(SolvedQ2.objects.filter(Q(id_no=request.user), Q(q_id=question.get(id_no=i.id_no)))):
			continue
		else:
			obj,notif=SolvedQ2.objects.get_or_create(id_no=request.user, q_id=question.get(id_no=i.id_no), check=False)
			if notif is True:
				obj.save()
	times=Time2.objects.filter(Q(id_no=request.user))
	for time1 in times:
		time1.end_time=timezone.localtime(timezone.now())
		time1.save()
		break


#Actual function for ending Section 3
def markSection3End(request):
	question=Section3.objects.all()
	for i in question:
		if(SolvedQ3.objects.filter(Q(id_no=request.user), Q(q_id=question.get(id_no=i.id_no)))):
			continue
		else:
			obj,notif=SolvedQ3.objects.get_or_create(id_no=request.user, q_id=question.get(id_no=i.id_no), check=False)
			if notif is True:
				obj.save()
	times=Time3.objects.filter(Q(id_no=request.user))
	for time1 in times:
		time1.end_time=timezone.localtime(timezone.now())
		time1.save()
		break


#Ended Quiz
@login_required(login_url='login')
def ended(request):

	#Marking All Questions as Attempted
	markSection1End(request)
	markSection2End(request)
	markSection3End(request)

	#Scores Of All Sections
	score1=SolvedQ1.objects.filter(Q(id_no=request.user), Q(check=True))
	score2=SolvedQ2.objects.filter(Q(id_no=request.user), Q(check=True))
	score3=SolvedQ3.objects.filter(Q(id_no=request.user), Q(check=True))
	id1=User.objects.filter(Q(username=request.user)).values('username')
	scores=[]
	scores.append(len(score1))
	scores.append(len(score2))
	scores.append(len(score3))
	return render(request, 'quizportal/ended.html', {'scores':scores, 'id':id1})


#Ended
@login_required(login_url='login')
def endSection(request, section_no):

	#Marking All Questions as Attempted According to the Sections

	#Section 1
	if(section_no=='1'):
		markSection1End(request)
		if(len(Section2.objects.all())>0):
			return HttpResponseRedirect('/detail/Section/2/1/1')
		else:
			return HttpResponseRedirect('/ended')

	#Section 2
	elif(section_no=='2'):
		markSection2End(request)
		if(len(Section3.objects.all())>0):
			return HttpResponseRedirect('/detail/Section/3/1/1')
		else:
			return HttpResponseRedirect('/ended')

	#Section 3
	elif(section_no=='3'):
		return HttpResponseRedirect('/ended')




#ADMIN ACCESS ONLY

def check_admin(user):
	return user.is_superuser


#Admin Main
@user_passes_test(check_admin)
def adminmain(request):
	return render(request, 'quizportal/adminmain.html')


#All Users' Details
@user_passes_test(check_admin)
def adminall(request):

	#Score of all Users
	admindict={}
	userscore=[]
	users=User.objects.all()

	for j in users:
		if(j.username =='admin'):
			continue
		else:
			
			name=User.objects.filter(Q(username=j))
			for i in name:
				name=i.first_name
				break
			userscore.append(name)
			l1=len(SolvedQ1.objects.filter(Q(id_no=j), Q(check=True)))
			l2=len(SolvedQ2.objects.filter(Q(id_no=j), Q(check=True)))
			l3=len(SolvedQ3.objects.filter(Q(id_no=j), Q(check=True)))
			userscore.append('Ab.' if(l1==0) else l1)
			userscore.append('Ab.' if(l2==0) else l2)
			userscore.append('Ab.' if(l3==0) else l3)

			admindict[j.username]=userscore
			userscore=[]

	return render(request, 'quizportal/adminall.html', {'allusers':admindict})

    
#CSV File Upload
@user_passes_test(check_admin)
def DownloadUserData(request):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="QuizData.csv"'

	writer = csv.writer(response)
	writer.writerow(['S.No', 'Enrollment Number', 'Name', 'Section1 Score', 'Section2 Score', 'Section3 Score'])

	users=User.objects.all()
	usertuple=[]
	userscore=[]

	count=1

	for j in users:
		if(j.username =='admin'):
			continue
		else:
			name=User.objects.filter(Q(username=j))
			for i in name:
				name=i.first_name
				break
			userscore.append(name)
			l1=len(SolvedQ1.objects.filter(Q(id_no=j), Q(check=True)))
			l2=len(SolvedQ2.objects.filter(Q(id_no=j), Q(check=True)))
			l3=len(SolvedQ3.objects.filter(Q(id_no=j), Q(check=True)))
			userscore.append('Ab.' if(l1==0) else l1)
			userscore.append('Ab.' if(l2==0) else l2)
			userscore.append('Ab.' if(l3==0) else l3)

			usertuple=[]
			usertuple.append(count)
			usertuple.append(j.username)
			usertuple.append(name)
			usertuple.append(userscore[1])
			usertuple.append(userscore[2])
			usertuple.append(userscore[3])

			writer.writerow(tuple(usertuple))

			usertuple=[]
			userscore=[]
			count=count+1

	return response


#CSV File Upload
@user_passes_test(check_admin)
def csvupload(request, section_no):
	if request.method == "POST":
		try:
			if(section_no == '1'):
				form = DataInput1(request.POST, request.FILES)
			elif(section_no == '2'):
				form = DataInput2(request.POST, request.FILES)
			else:
				form = DataInput3(request.POST, request.FILES)
			
			print(form)
			if form.is_valid():
				form.save()
				return HttpResponseRedirect('/adminmain')
		except Exception as e:
			#print(e)
			section='/admincsvupload/'+str(section_no)
			return HttpResponseRedirect(section)
	else:
		if(section_no == '1'):
			form = DataInput1()
		elif(section_no == '2'):
			form = DataInput2()
		else:
			form = DataInput3()
		args = {"form": form, 'section_no':section_no}
		return render(request, 'quizportal/csvupload.html', args)
		

#Time Upload
@user_passes_test(check_admin)
def timeupload(request, section_no):
	if request.method == "POST":
		try:
			if(section_no == '1'):
				form = TimeInput1(request.POST)
			elif(section_no == '2'):
				form = TimeInput2(request.POST)
			else:
				form = TimeInput3(request.POST)

			if form.is_valid():
				form.save()
				return HttpResponseRedirect('/adminmain')
		except Exception as e:
			print(e)
			section='/admintimeupload/'+str(section_no)
			return HttpResponseRedirect(section)
	else:
		if(section_no == '1'):
			form =TimeInput1()
		elif(section_no == '2'):
			form = TimeInput2()
		else:
			form = TimeInput3()
	args = {"form": form, 'section_no':section_no}
	return render(request, 'quizportal/timeupload.html', args)
		




@user_passes_test(check_admin)
def admindelete(request, nu):
	#Delete enteries

	if(nu=='1' and len(User.objects.all())>1):
		for user in User.objects.all():
			if(user=='admin'):
				continue
			else:
				user.delete()

	if(nu=='2' and len(Section1.objects.all())>0):
		Section1.objects.all().delete()
	elif(nu=='3' and len(Section2.objects.all())>0):
		Section2.objects.all().delete()
	elif(nu=='4' and len(Section3.objects.all())>0):
		Section3.objects.all().delete()


	elif(nu=='5' and len(Time1.objects.all())>0):
		Time1.objects.all().delete()
	elif(nu=='6' and len(Time2.objects.all())>0):
		Time2.objects.all().delete()
	elif(nu=='7' and len(Time3.objects.all())>0):
		Time3.objects.all().delete()

	elif(nu=='8' and len(Time.objects.all())>0):
		Time.objects.all().delete()

	elif(nu=='9' and len(SolvedQ1.objects.all())>0):
		SolvedQ1.objects.all().delete()
	elif(nu=='10' and len(SolvedQ2.objects.all())>0):
		SolvedQ2.objects.all().delete()
	elif(nu=='11' and len(SolvedQ3.objects.all())>0):
		SolvedQ3.objects.all().delete()

	args = {'message':nu}
	return render(request, 'quizportal/adminmain.html', args)

#Registering Users Manually
@user_passes_test(check_admin)
def regis(request):
	if request.method == "POST":
		try:
			form=RegistrationForm(request.POST, request.FILES)
			print(form)
			if form.is_valid():
				form.save()
				return HttpResponseRedirect('/adminmain')
		except Exception as e:
			section='/regis'
			return HttpResponseRedirect(section)
	else:
		form=RegistrationForm()
	args = {"form": form}
	return render(request, 'quizportal/regis.html', args)


@user_passes_test(check_admin)
def passwords(request):
	obj=userpasswords.objects.all()
	for i in obj:
		if(i.username=='hydra' or i.username=='admin'):
			continue
		else:
			passwords[i.username]=i.password

	args = {'passwords':passwords}
	return render(request, 'quizportal/userpasswords.html', args)