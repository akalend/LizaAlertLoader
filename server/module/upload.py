import os
import shutil
from pyramid.response import Response
from module.template import Template
from module.config import conf
from module.cache import Cache
import subprocess

def upload(request):
    uid = request.matchdict['uid']

    if request.method == 'GET':
        tpl = Template()

        out = tpl.render('upload.htm')

        return Response(out)


    filename = request.POST['photo'].filename

    input_file = request.POST['photo'].file
    folder = conf['photo_dir'][conf['mode']]

    folder_dir = os.path.join(folder, uid)

    if not os.path.isdir(folder_dir):
        os.mkdir(folder_dir) 

    file_path = os.path.join(folder_dir,filename)
    with open(file_path, 'wb') as output_file:
        shutil.copyfileobj(input_file, output_file)

    return Response('upload:' + uid)


def finish(request):
    uid = request.matchdict['uid']

    if request.method != 'GET':
        return Response('Ok')

    folder = conf['photo_dir'][conf['mode']]
    files_folder = os.path.join(folder,uid)
    key = 'in_' + uid;


    files = os.listdir(files_folder)
    cache = Cache()

    # file_list = ','.join(files)    
    for file in files:
        cache.push('in', '"{{uid":{},"name":"{}"}}'.format(uid,file) )

        # cache.push(key, photo)
        # print(photo, key  )

    

    # subprocess.call([work_home + '/api', 'start', str(i) ])
    return Response('Ok')

