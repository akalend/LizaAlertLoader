import os
import shutil
from pyramid.response import Response
from module.template import Template

def upload(request):
    uid = request.matchdict['uid']

    if request.method == 'GET':
        tpl = Template()

        out = tpl.render('upload.htm')

        return Response(out)


    filename = request.POST['photo'].filename

    # ``input_file`` contains the actual file data which needs to be
    # stored somewhere.
    input_file = request.POST['photo'].file



    file_path = os.path.join('/tmp', filename)
    with open(file_path, 'wb') as output_file:
        shutil.copyfileobj(input_file, output_file)

    return Response('upload:' + uid)
