import mimetypes
from wsgiref.util import FileWrapper

from django.http import HttpResponse
from django.shortcuts import render, redirect
import django.conf as conf
from django.utils.encoding import smart_str

from MusicStorage.models import *
from MusicStorage.forms import *
from minio import Minio
import os, time, glob
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.contrib.auth import authenticate
from MusicStorage.settings import AWS_ACCESS_KEY_ID as Admin_ID, AWS_SECRET_ACCESS_KEY as Admin_KEY, MEDIA_ROOT
from django.contrib import messages

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import ast
import datetime
import pytz
GlobalData = {
    'last_date': 0
}
GD=0

# @csrf_exempt
def global_data_update(request):
  global GD
  newdata=request.POST.get('date')
  # print(request)
  # print('NEW DATE:')
  # print(newdata)
  # print(str(request.body))
  body=str(request.body)
  body=(body.replace(' ', ''))[2:-1]
  rawdate=int(body)
  print( datetime.datetime.fromtimestamp(rawdate / 1e3))
  GD=rawdate

  # GD=rawdate
  print(GD)
  # new_body= json.loads(body)
  # print(new_body)
  # print(type(new_body))

  return JsonResponse({})



def start(request):

  return render(request, 'start.html')


def home(request):
  clean_static()

  if request.method == 'POST':
    request.session['access'] = request.POST['access']
    request.session['secret'] = request.POST['secret']
  access = request.session.get('access')
  secret = request.session.get('secret')
  user = authenticate(username=access, password=secret)
  # print(user)
  if user is not None:
    conf.settings.AWS_STORAGE_BUCKET_NAME = access
    client = Minio(endpoint="localhost:9000", access_key=Admin_ID, secret_key=Admin_KEY, secure=False)

    objects = client.list_objects(access)
    # print('Загруженные объекты:')
    objectList=[]
    for object in objects:
      # print(object.__dict__)
      # print(object.object_name)
      objectList.append(object)

    return render(request, 'home.html', {'objects': objectList})
  else:
    return redirect('start')
def model_form_upload(request):
  clean_static()
  if request.method == 'POST':
    form = MyDocumentForm(request.POST, request.FILES)
    if form.is_valid():
      newdoc = MyDocument(doc=request.FILES['doc'])
      newdoc.save()

      for filename, file in request.FILES.items():
        name = request.FILES[filename].name
      request.session['filename'] = name

      access = request.session.get('access')
      client = Minio(endpoint="localhost:9000", access_key=Admin_ID, secret_key=Admin_KEY, secure=False)
      filepath = "MusicStorage/static/music/" + name

      client.fput_object(access, name, filepath)

      return redirect('home')
  else:
    form = MyDocumentForm()

  return render(request, 'model_form_upload.html', {'form': form},)

def object(request, name):
  # clean_static()

  access = request.session.get('access')
  client = Minio(endpoint="localhost:9000", access_key=Admin_ID, secret_key=Admin_KEY, secure=False)

  filepath = "MusicStorage/static/music/" + name
  getobject = client.fget_object(access, name, filepath)
  # getobject=client.get_object(access, name)
  object_info = client.stat_object(access, name)
  # print(type(getobject))
  # print(getobject.__dict__)
  # print(dir(getobject))
  # print(getobject.FILES)
  # print(getobject.data)
  if request.method == 'POST':
    client.remove_object(access, name)
    return redirect('deleted')

  return render(request, 'object.html', {'object_name': name, 'object_info': object_info,
                                         'client': client, 'access': access, 'object':getobject})




def log(request):
  if request.method == 'POST':
    print(request.POST)
    return render(request, 'log.html')
  else:
    return render(request, 'log.html')

def reg(request):
  if request.method == 'POST':
    print(request.POST)
    client = Minio(endpoint="localhost:9000", access_key='minio', secret_key='minio124', secure=False)
    request.session['access'] = request.POST['access']
    request.session['secret'] = request.POST['secret']
    access = request.session.get('access').lower()
    secret = request.session.get('secret')
    # conf.settings.AWS_STORAGE_BUCKET_NAME = access
    if client.bucket_exists(access):
      messages.success(request, 'Ошибка. Неверный логин или пароль.')
      print('ERROR')
    else:
      user = User.objects.create_user(username=access, password=secret)
      user.last_name = 'Смешарик'
      user.save()
      client.make_bucket(access)
      buckets = client.list_buckets()
      messages.success(request, 'Аккаунт создан.')

    return redirect('start')
  else:
    return redirect('start')

def download(request, file_name):
  file_path = MEDIA_ROOT + '/' + file_name
  response = HttpResponse(open(file_path, 'rb').read())
  response['X-Sendfile'] = file_path
  response['Content-Length'] = os.stat(file_path).st_size
  response['Content-Disposition'] = 'attachment; filename='+file_name
  response['Content-Type'] = 'audio/mpeg'

  return response


def delete(request, file_name):
  access = request.session.get('access')
  client = Minio(endpoint="localhost:9000", access_key=Admin_ID, secret_key=Admin_KEY, secure=False)

  if request.method == 'POST':
    client.remove_object(access, file_name)
    messages.success(request, 'Удалено.')

  # return render(request, 'deleted.html', {'object_name': object_name})
  return redirect('home')

def model_form_edit(request, file_name):
    clean_static()
    if request.method == 'POST':
      global GD
      form = MyDocumentForm(request.POST, request.FILES)
      if(request.FILES):
        print(request.FILES['fileList'])
        newdoc = MyDocument(doc=request.FILES['fileList'])
        newdoc.save()
        for filename, file in request.FILES.items():
          name = request.FILES[filename].name
        request.session['filename'] = name

        access = request.session.get('access')
        client = Minio(endpoint="localhost:9000", access_key=Admin_ID, secret_key=Admin_KEY, secure=False)
        filepath = "MusicStorage/static/music/" + name
        object_info = client.stat_object(access, file_name)
        utc = pytz.UTC
        last_date_modified=object_info.last_modified
        new_date_modified=utc.localize(datetime.datetime.fromtimestamp(GD/ 1e3))
        print('ИЗМЕНЯЕМЫЙ ФАЙЛ:')
        print(GD)
        print(new_date_modified)
        print(type(new_date_modified))

        print('ОРИГИНАЛ:')
        print(last_date_modified)
        print(type(last_date_modified))
        if(last_date_modified<new_date_modified):
          client.fput_object(access, file_name, filepath)
        return redirect('home')

      if form.is_valid():
        print('ИЗМЕНЕНИЕ ФАЙЛА:')
        newdoc = MyDocument(doc=request.FILES['doc'])
        newdoc.save()
        print(type(request.FILES['doc']))
        print(request.FILES)

        for filename, file in request.FILES.items():
          name = request.FILES[filename].name
        request.session['filename'] = name

        access = request.session.get('access')
        client = Minio(endpoint="localhost:9000", access_key=Admin_ID, secret_key=Admin_KEY, secure=False)
        filepath = "MusicStorage/static/music/" + name

        client.fput_object(access, file_name, filepath)
        # fileStatsObj=os.stat(filepath)
        # modTimesinceEpoc = os.path.getmtime(filepath)
        # modificationTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modTimesinceEpoc))
        # print("Last Modified Time : ", modificationTime)

        # print(fileStatsObj)

        return redirect('home')
    else:
      form = MyDocumentForm()
    return render(request, 'model_form_edit.html', {'form': form, 'name': file_name}, )

def clean_static():
  files = glob.glob('MusicStorage/static/music/*')
  for f in files:
    os.remove(f)
  return
