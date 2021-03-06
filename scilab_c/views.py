import subprocess
import simplejson as json
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import HttpRequest
from django.shortcuts import render_to_response
from django.contrib.sites.models import Site
import MySQLdb as mdb
import re
import os
from reportlab.pdfgen import canvas
import datetime
from reportlab.lib.units import inch
from django.views.decorators.csrf import csrf_exempt
from collections import OrderedDict

api_keys={'scilab':'zdFmTjX98.'}
@csrf_exempt
def upload_file(request):
	if request.method=="GET":
		return render_to_response('../public/upload.html')

    	try:
        	uploaded_file = request.FILES['scilab_code']
	        filename=datetime.datetime.now().strftime("%Y-%m-%d%H-%M-%S")
	        cwd = "/home/cfduser/SANDBOX/scilab_cloud" + "/graphs/" + "3"
        	if not os.path.exists(cwd):
	            os.makedirs(cwd)
       
        	filetowrite = open(cwd+"/"+filename+".sce","wb+")
		filetowrite.write("mode(2);\n")

		for chunks in uploaded_file.chunks():
			filetowrite.write(chunks)
	
		filetowrite.write("\nquit;")	        
	        filetowrite.close()
        	filetoread = cwd+"/"+filename+".sce"
	        p=subprocess.Popen("scilab-cli -nb -nwni -f "+ filetoread , shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        	out, err = p.communicate()
		try:
			from_web = request.POST.get('from_web')
		except: 	
			from_web = None
		if from_web:
			return render_to_response('../public/upload.html',{'output':out})
		else:
			
			try:
				api_user = request.POST.get('api_user')
			except:
				api_user = None
			try:
				api_key = request.POST.get('api_key')
			except:
				api_key = None
			if api_user not in api_keys.keys():
				return HttpResponse(json.dumps({"response":{},"message":{"code":"401","description":"API user not defined"}}),"application/json")
			elif api_key!= api_keys[api_user]:
				
				return HttpResponse(json.dumps({"response":{},"message":{"error":"401","description":"API key does not match"}}),"application/json")
	        return HttpResponse(json.dumps({"response":{"input":"original_code","output":out,"graph":"","user_id":"3"},"type":{"code":"200","description":"success"}}),'application/json')
	except:
		return HttpResponse(json.dumps({"response":{},"message":{"code":"500","description":"error running code"}}),"application/json")
@csrf_exempt
def get_books(request):
	try:
		api_user = request.POST.get('api_user')
	except:
		api_user = None
	try:
		api_key = request.POST.get('api_key')
	except:
		api_key = None
	if api_user not in api_keys.keys():
		return HttpResponse(json.dumps({"response":{},"message":{"code":"401","description":"API user not defined"}}),"application/json")
	elif api_key!= api_keys[api_user]:
			
		return HttpResponse(json.dumps({"response":{},"message":{"error":"401","description":"API key does not match"}}),"application/json")
	all_books={}
	books=[]
	books_id=[]
	con = mdb.connect("localhost","root","fedora13","scilab")
	#con.charset="utf-8"
	with con:
		cur = con.cursor()
		query = "SELECT id,book,author FROM  textbook_companion_preference where approval_status=1 ORDER BY book ASC"
		cur.execute(query)
		rows = cur.fetchall()
		for row in rows:
			r1 = str(row[1].strip())
			r0 = row[0]
			r2 = row[2].decode("ascii","ignore").encode("utf-8")
			if row[1]!="" and row[2]!="":
				all_books[r0]=r1.replace("  "," ").replace("\\xa0","")+"(" + r2.replace(u'\\xa0',u' ').replace(u'\\xc7',u' ')+")"

	d_sorted_by_value = OrderedDict(sorted(all_books.items(), key=lambda x: x[1]))
	return HttpResponse(json.dumps({"response":{"books":(d_sorted_by_value)},"message":{"code":"200","description":"success"}}),"application/json")

def default_view(request):
	try:
		user_id = request.session['user_id']
	except:
		return HttpResponseRedirect("/login")
	all_books={}
	books=[]
	books_id=[]
	con = mdb.connect("localhost","root","fedora13","scilab")
	with con:
		cur = con.cursor()
		query = "SELECT id,book,author FROM  textbook_companion_preference where approval_status=1 ORDER BY book ASC"
		cur.execute(query)
		rows = cur.fetchall()
		for row in rows:
			if row[1]!="" and row[2]!="":
				all_books[row[0]]=row[1].replace("  "," ")+"(" + row[2].replace("  "," ")+")"
	d_sorted_by_value = OrderedDict(sorted(all_books.items(), key=lambda x: x[1]))
	return render_to_response('../public/default.html',{'input':'Type Code Here','uid':user_id,'username':request.session['username'],'all_books':d_sorted_by_value})
@csrf_exempt
def scilab_new_evaluate(request):
    
    current_site = HttpRequest.build_absolute_uri(request)
    try:
        api_key = request.POST.get('api_key')
    except:
        api_key = None
    try:
	api_user = request.POST.get('api_user')
    except:
	api_user = None
	
    if api_user not in api_keys.keys():
        return HttpResponse(json.dumps({"response":{},"message":{"code":"401","description":"API user not defined"}}),"application/json")
    elif api_key!= api_keys[api_user]:
        return HttpResponse(json.dumps({"response":{},"message":{"error":"401","description":"API key does not match"}}),"application/json")
    
    if request.method =="GET":

        return render_to_response('../public/default.html',{'input':'//Type Code Here','uid':request.session['user_id'],'username':request.session['username']})

    
    try:
        all_code = request.POST.get('scilab_code')
    except:
        all_code = None
    if  not all_code:
        return HttpResponse(json.dumps({"response":{},"message":{"code":"500","description":"API user not defined"}}),"application/json")
        
    all_code = all_code.replace("clc;","")
    all_code = all_code.replace("clear;","")
    all_code = all_code.replace("clear all;","")
    all_code = "mode(2)\nlines(0) \n"+all_code
    try:
        user=request.POST.get('external_user')
        request.session['user_id']='3'
    except:
        print "do notbhing"
    filter_for_system = re.compile("unix_g|unix_x|unix_w|unix_s|host|newfun|execstr|ascii|mputl|dir\(\)")
    if  (filter_for_system.findall(all_code)):
        return HttpResponse(json.dumps({"response":{'input':'System commnads are not supported','uid':request.session['user_id'],'username':request.session['username'],'output':'System commands are disabled','graph':'','graphs':''} , "type":{"code":"500","description":"system commands are disabled" }}),'application/json')
    graphics_mode = request.POST.get('graphicsmode')
    if not graphics_mode:
        cwd = "/home/cfduser/SANDBOX/scilab_cloud" + "/graphs/" + str(request.session['user_id'])
        if not os.path.exists(cwd):
            os.makedirs(cwd)
        filename=datetime.datetime.now().strftime("%Y-%m-%d%H-%M-%S")
        all_code  = all_code +"\n"+"\n quit();"
        filetowrite = open(cwd+"/"+filename+".sce","w")
        filetowrite.write(all_code)
        filetowrite.close()
        filetoread = cwd+"/"+filename+".sce"
        process = subprocess.Popen('scilab-cli -nb -nwni -f '+filetoread ,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
	soutput = process.communicate()[0]
        soutput = soutput.strip()
        return HttpResponse(json.dumps({"response":{"input":all_code,"output":soutput,"graph":""},"type":{"code":"200","description":"success"}}),'application/json')

    original_code = all_code
    cwd = "/home/cfduser/SANDBOX/scilab_cloud" + "/graphs/" + str(request.session['user_id'])
    filename=datetime.datetime.now().strftime("%Y-%m-%d%H-%M-%S")
    cwdsf = cwd +"/"+ filename +"-code.sce"
    if not os.path.exists(cwd):
        os.makedirs(cwd)
    f = open(cwdsf,"w")
    user_id = str(request.session['user_id'])
    graph = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(" ","")
    all_code = "driver(\"PNG\");\n" + "\n xinit(\""+cwd+"/"+graph+".png\");\n" + all_code+ "\nxend();\n" + "\nquit();"
    f.write(all_code)
    f.close()
    p=subprocess.Popen("/opt/scilab/bin/scilab-adv-cli -nb -f "+ cwdsf , shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = p.communicate()
    return HttpResponse(json.dumps({"response":{"input":original_code,"output":out,"graph":graph,"user_id":user_id},"type":{"code":"200","description":"success"}}),'application/json')

def download(request,graphname):
	response = HttpResponse(mimetype='application/pdf')
	response['Content-Disposition'] = 'attachment; filename='+str(graphname)+'.pdf'
	p = canvas.Canvas(response)
	cwd = "/home/cfduser/SANDBOX/scilab_cloud" + "/graphs/" + str(request.session['user_id'])+"/"
	p.drawImage(cwd+str(graphname)+".png", 1*inch,1*inch, width=5*inch,height=5*inch,mask=None)
        p.showPage()
 	p.save()
        return response
@csrf_exempt
def get_chapters(request):
	book_id = request.POST.get('id')
	all_examples = []
#	all_examples="<option value=''>Select a Chapter </option>"
	con = mdb.connect("localhost","root","fedora13","scilab")
	with con:
		cur = con.cursor()
		query = "SELECT id,number,name FROM  textbook_companion_chapter where preference_id="+book_id+" ORDER BY number ASC"
		cur.execute(query)
		rows = cur.fetchall()
		for row in rows:
			if row[1]!="":
				all_examples.append({"value":str(row[0]), "name":str(row[1]).replace("  "," ")+". " + str(row[2]).replace("  "," ")})
	response_data={}
	response_data["data"]=all_examples
	return HttpResponse(json.dumps({"response":{"data":all_examples},"type":{"code":"200","description":"success"}}), mimetype="application/json")


@csrf_exempt
def get_examples(request):
	book_id = request.POST.get('id')
	all_examples=[]#"<option value=''>Select an Example</option>"
	con = mdb.connect("localhost","root","fedora13","scilab")
	with con:
		cur = con.cursor()
		query = "SELECT id,number,caption FROM  textbook_companion_example where chapter_id="+book_id+" ORDER BY number ASC"
		cur.execute(query)
		rows = cur.fetchall()
		for row in rows:
			if row[1]!="":
				all_examples.append({"value":str(row[1]), "name":str(row[1]).replace("  "," ")+". " + str(row[2]).replace("  "," ")})
	response_data={}
	response_data["data"]=all_examples
	return HttpResponse(json.dumps({"response":{"data":all_examples},"type":{"code":"200","description":"success"}}), mimetype="application/json")

	#return HttpResponse(json.dumps(response_data), mimetype="application/json")

@csrf_exempt
def get_code(request):
	example = request.POST.get('example')
	chapter = "CH"+example.split(".")[0]
	folder = request.POST.get('folder')
	content=""
	con = mdb.connect("localhost","root","fedora13","scilab")
	with con:
		cur = con.cursor()
		query = "SELECT filepath FROM textbook_companion_dependency_files where preference_id="+folder
		cur.execute(query)
		rows = cur.fetchall()
		for row in rows:
			f=open("/var/www/scilab_in/uploads/"+row[0],'r')
			
			content+=f.read()+"\n";
			print query
			f.close()
		os.chdir("/var/www/scilab_in/uploads/"+folder+"/"+chapter+"/"+"EX"+example+"/")
		for files in os.listdir("."):
			if files.endswith(".sce") or files.endswith(".sci"):
				f=open(files,'r')
				content += f.read()
				f.close()
	response_data={}
	response_data["input"]=content	
	return HttpResponse(json.dumps({"response":{"data":content},"type":{"code":"200","description":"success"}}), mimetype="application/json")

	#return HttpResponse(json.dumps(response_data), mimetype="application/json")
			

		
