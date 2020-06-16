import hou
import sys
import os
from datetime import datetime
from math import *

paths = ['', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\site-packages\\setuptools-0.6c11-py2.7.egg', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\DLLs\\python27.zip', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\DLLs', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib',
         'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\plat-win', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\lib-tk', 'C:\\Program Files\\Pixar\\Tractor-2.3\\bin', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\site-packages']

for path in paths:
    if not os.path.exists(r'C:\\Program Files\\Pixar\\Tractor-2.3'):
        path = path.replace(r'C:\Program Files\Pixar\Tractor-2.3',
                            '//multifct/tools/pipeline/global/softwares/Tractor-2.3')
    sys.path.append(path)

import tractor.api.author as author

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')
if vendor_dir not in sys.path:
    sys.path.append(vendor_dir)

import fileseq

envs = ['JOB', 'WIPCACHE', 'PUBCACHE', 'ASSET', 'SHOT',
        'PROJECT', 'IMAGES_OUT']  # Hou env variables

project_server = {

    'A_PIPE': 'marvin',
    'ARAL': 'marvin',
    'CLAIR_DE_LUNE': 'marvin',
    'FORGOT_YOUR_PASSWORD': 'marvin',
    'LOREE': 'marvin',
    'RESURGENCE': 'marvin',
    'TIMES_DOWN': 'marvin',

    'ASCEND': 'tars',
    'ISSEN_SAMA': 'tars',
    'LONE': 'tars',
    'MOON_KEEPER': 'tars',

    'BREACH': 'ana',
    'HARU': 'ana',
    'VERLAN': 'ana'

}


def submit(node):

    if hou.hipFile.hasUnsavedChanges():
        hou.ui.displayMessage('Your scene needs to be saved before submission', buttons=(
            'OK',), severity=hou.severityType.Message)
        return

    file = hou.hipFile.name()

    farm_project = node.parm("project").evalAsString()

    job_name = node.parm("job_name").evalAsString(
    ) or hou.expandString('$FARM')
    output_driver = node.parm("output_driver").evalAsString()

    inputs = node.inputs()

    start = node.parm("f1").evalAsFloat()
    end = node.parm("f2").evalAsFloat()

    frames = node.parm("frames").evalAsString()
    frame_set = fileseq.FrameSet(frames)

    # increment = node.parm("f3").evalAsFloat()
    nbFrames = int(end) - int(start)
    # frames_per_task = int(
    #     ceil((nbFrames) / node.parm("frames_task").evalAsInt())) + 1
    frames_per_task = node.parm("frames_task").evalAsInt()
    simu = node.parm("simu").evalAsInt()
    ram = node.parm("ram").evalAsInt()
    gpu = node.parm("gpu").evalAsInt()
    gpu64 = node.parm("gpu_ram").evalAsInt()

    farmType = node.parm("farmType").evalAsInt();

    pools_bitfield = node.parm("pools").eval()
    pools_tokens = node.parm("pools").parmTemplate().menuItems()
    pools = [token for n, token in enumerate(
        pools_tokens) if pools_bitfield & (1 << n)]

    # teams_bitfield = node.parm("teams").eval()
    # teams_tokens = node.parm("teams").parmTemplate().menuItems()
    # teams = [token for n, token in enumerate(
    #     teams_tokens) if teams_bitfield & (1 << n)]

    current_project = os.path.basename(hou.expandString('$PROJECT'))
    current_server = project_server.get(current_project)

    if not current_project and current_server:
        hou.ui.displayMessage('Project could not be identified - check env variables.', buttons=('OK',),
                              severity=hou.severityType.Warning)
        return

    print 'We are on ', current_project, current_server

    file_path = file

    # service_rooms = " || ".join(rooms)
    # service_teams = " || ".join(teams)

    if simu == 0:
        service = None
        if farmType == 0:
            service = "({pools})".format(pools=" || ".join(pools))


        else:
            if(gpu64 == 0):
                service = "gpu && !gpu64"
            elif(gpu64 == 1):
                service = "gpu64"
            else:
                service = "gpu"

        if not service:
            hou.ui.displayMessage('Please check your submission settings.', buttons=('OK',),
            severity=hou.severityType.Warning)
            return

        for var, env_job in [(v, hou.getenv(v)) for v in envs]:
            if not env_job:
                continue
            for project, server in project_server.iteritems():
                env_job = env_job.replace(
                    'I:/SynologyDrive/{}'.format(project), '//{}/PFE_RN_2020/{}'.format(server, project))
            hou.hscript('setenv {}={}'.format(var, env_job))
            print('setenv {}={}'.format(var, env_job))

        for project, server in project_server.iteritems():
            hou.hscript('opchange I:/SynologyDrive/{project} //{server}/PFE_RN_2020/{project}'.format(project=project,
                                                                                                      server=server))
        root_path = '//{server}/PFE_RN_2020/{project}'.format(
            project=current_project, server=current_server)

    else:
        service = "simu"
        author.setEngineClientParam(user="hquser")

        for var, env_job in [(v, hou.getenv(v)) for v in envs]:
            if not env_job:
                continue
            for project, server in project_server.iteritems():
                env_job = env_job.replace(
                    'I:/SynologyDrive/{}'.format(project), '/{}/{}'.format(server, project))
            hou.hscript('setenv {}={}'.format(var, env_job))
            print('setenv {}={}'.format(var, env_job))

        for project, server in project_server.iteritems():
            hou.hscript(
                'opchange I:/SynologyDrive/{project} /{server}/{project}'.format(project=project, server=server))
            hou.hscript('opchange //{server}/PFE_RN_2020/{project} /{server}/{project}'.format(
                project=project, server=server))

        root_path_linux = '/{server}/{project}'.format(
            project=current_project, server=current_server)
        root_path = '//{server}/PFE_RN_2020/{project}'.format(
            project=current_project, server=current_server)

    # Temp file save
    file_name = hou.hipFile.basename()
    file_split = file_name.split(".")

    path_split = file.split("/")

    render_path = '/'.join(path_split[:-2]) + '/render'

    # Submission on the server directly
    # render_path = render_path.replace('I:/SynologyDrive/{project}'.format(project=current_project), root_path)

    now = datetime.now()
    timestamp = now.strftime("%m-%d-%Y_%H-%M-%S")

    new_name = "{version}_{file_name}_{timestamp}.{extension}".format(version=path_split[-2], file_name=file_split[0],
                                                                      timestamp=timestamp, extension=file_split[-1])
    path = os.path.join(render_path, new_name)
    new_name_path = path.replace(os.sep, '/')

    if not os.path.exists(render_path):
        if not os.path.exists(os.path.dirname(render_path)):
            if not hou.ui.displayConfirmation('The scene path does not exist on the server. \n{}\nAre you sure you want to create it ?'.format(render_path),
                                              severity=hou.severityType.Message):

                # reloading user file
                hou.hipFile.load(file, suppress_save_prompt=True)
                return
            else:
                os.makedirs(os.path.dirname(render_path))
        os.mkdir(render_path)

    hou.hipFile.setName(new_name_path)

    file_path = new_name_path
    hou.hipFile.save(file_name=None)

    if simu and service == 'simu':
        file_path = file_path.replace(root_path, root_path_linux)

    job = author.Job(title=job_name, priority=100, service=str(service), projects=[farm_project])

    # job.newDirMap(src="I:/SynologyDrive/A_PIPE", dst="//marvin/PFE_RN_2020/A_PIPE", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/A_PIPE",
                  dst="/marvin/A_PIPE", zone="NFS")

    job.newDirMap(src="C:/Houdini17/bin/hython.exe",
                  dst="/opt/hfs17.5/bin/hython", zone="NFS")
    job.newDirMap(src="C:/Houdini17/bin/hrender.py",
                  dst="/opt/hfs17.5/bin/hrender.py", zone="NFS")

    ###########################
    ##### DIR MAP WINDOWS #####
    ###########################

    ##### DIR MAP MARVIN #####
    job.newDirMap(src="I:/SynologyDrive/ARAL",
                  dst="//marvin/PFE_RN_2020/ARAL", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/CLAIR_DE_LUNE",
                  dst="//marvin/PFE_RN_2020/CLAIR_DE_LUNE", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/FORGOT_YOUR_PASSWORD",
                  dst="//marvin/PFE_RN_2020/FORGOT_YOUR_PASSWORD", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/LOREE",
                  dst="//marvin/PFE_RN_2020/LOREE", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/RESURGENCE",
                  dst="//marvin/PFE_RN_2020/RESURGENCE", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/TIMES_DOWN",
                  dst="//marvin/PFE_RN_2020/TIMES_DOWN", zone="UNC")

    ##### DIR MAP TARS #####
    job.newDirMap(src="I:/SynologyDrive/ASCEND",
                  dst="//tars/PFE_RN_2020/ASCEND", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/ISSEN_SAMA",
                  dst="//tars/PFE_RN_2020/ISSEN_SAMA", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/LONE",
                  dst="//tars/PFE_RN_2020/LONE", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/MOON_KEEPER",
                  dst="//tars/PFE_RN_2020/MOON_KEEPER", zone="UNC")

    ##### DIR MAP ANA #####
    job.newDirMap(src="I:/SynologyDrive/BREACH",
                  dst="//ana/PFE_RN_2020/BREACH", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/HARU",
                  dst="//ana/PFE_RN_2020/HARU", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/VERLAN",
                  dst="//ana/PFE_RN_2020/VERLAN", zone="UNC")

    #########################
    ##### DIR MAP LINUX #####
    #########################

    ##### DIR MAP MARVIN #####
    job.newDirMap(src="I:/SynologyDrive/ARAL", dst="/marvin/ARAL", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/CLAIR_DE_LUNE",
                  dst="/marvin/CLAIR_DE_LUNE", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/FORGOT_YOUR_PASSWORD",
                  dst="/marvin/FORGOT_YOUR_PASSWORD", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/LOREE",
                  dst="/marvin/LOREE", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/RESURGENCE",
                  dst="/marvin/RESURGENCE", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/TIMES_DOWN",
                  dst="/marvin/TIMES_DOWN", zone="NFS")

    ##### DIR MAP TARS #####
    job.newDirMap(src="I:/SynologyDrive/ASCEND",
                  dst="/tars/ASCEND", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/ISSEN_SAMA",
                  dst="/tars/ISSEN_SAMA", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/LONE", dst="/tars/LONE", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/MOON_KEEPER",
                  dst="/tars/MOON_KEEPER", zone="NFS")

    ##### DIR MAP ANA #####
    job.newDirMap(src="I:/SynologyDrive/BREACH", dst="/ana/BREACH", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/HARU", dst="/ana/HARU", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/VERLAN", dst="/ana/VERLAN", zone="NFS")

    job.newDirMap(src="//marvin/PFE_RN_2020", dst="/marvin", zone="NFS")

    if inputs == ():
        if service == "simu":
            task_command = ["%D(C:/Houdini17/bin/hython.exe)", "%D(C:/Houdini17/bin/hrender.py)",
                            "%D({file_path})".format(file_path=file_path), "-d", output_driver]
            l = list(frame_set.items)
            l.sort()
            task_command.extend(["-e", "-f", str(l[0]), str(l[-1])])
            task_name = "frame {start}-{end}".format(
                start=str(l[0]), end=str(l[-1]))
            # print(task_command)
            task = author.Task(
                title=task_name, argv=task_command, service=str(service))
            job.addChild(task)
        else:
            # for i in range(int(start), int(end + 1), frames_per_task):
            for i in range(0, len(frame_set.items), 1 if len(frame_set.items) == frames_per_task else (len(frame_set.items) // frames_per_task) + 1):
                task_command = ["%D(C:/Houdini17/bin/hython.exe)", "%D(//marvin/PFE_RN_2020/_UTILITY/04_FARM/01_HOUDINI/hrender_artfx.py)",
                                "%D({file_path})".format(file_path=file_path), "-d", output_driver]
                if(service == "simu"):
                    task_command = ["%D(C:/Houdini17/bin/hython.exe)", "%D(/marvin/_UTILITY/04_FARM/01_HOUDINI/hrender_artfx.py)",
                                    "%D({file_path})".format(file_path=file_path), "-d", output_driver]
                task_command.extend(["-F"])
                task_name = "frame"
                for j in range((len(frame_set.items) // frames_per_task) + 1):
                    if((i+j) < len(frame_set.items)):
                        l = list(frame_set.items)
                        l.sort()
                        f = str(l[i+j])
                        task_command.extend([f])
                        task_name += " {f}".format(f=f)

                task = author.Task(
                    title=task_name, argv=task_command, service=str(service))
                job.addChild(task)
    else:
        for j in range(len(inputs)):
            driver = inputs[j]
            parent = author.Task(title=driver.name())
            job.addChild(parent)
            for i in range(0, len(frame_set.items), 1 if len(frame_set.items) == frames_per_task else (len(frame_set.items) // frames_per_task) + 1):
                task_command = ["%D(C:/Houdini17/bin/hython.exe)", "%D(//marvin/PFE_RN_2020/_UTILITY/04_FARM/01_HOUDINI/hrender_artfx.py)",
                                "%D({file_path})".format(file_path=file_path), "-d", driver.path()]
                if(service == "simu"):
                    task_command = ["%D(C:/Houdini17/bin/hython.exe)", "%D(/marvin/_UTILITY/04_FARM/01_HOUDINI/hrender_artfx.py)",
                                    "%D({file_path})".format(file_path=file_path), "-d", output_driver]
                task_command.extend(["-F"])
                task_name = "{driver} frame".format(driver=driver.name())
                for j in range((len(frame_set.items) // frames_per_task) + 1):
                    if((i+j) < len(frame_set.items)):
                        l = list(frame_set.items)
                        l.sort()
                        f = str(l[i+j])
                        task_command.extend([f])
                        task_name += " {f}".format(f=f)

                task = author.Task(
                    title=task_name, argv=task_command, service=str(service))
                parent.addChild(task)
            # for i in range(int(start), int(end + 1), frames_per_task):
            #     task_command = ["%D(C:/Houdini17/bin/hython.exe)", "%D(C:/Houdini17/bin/hrender.py)",
            #                     "%D({file_path})".format(file_path=file_path), "-d", driver.path()]
            #     task_command.extend(["-e", "-f", str(i), str(i + frames_per_task - 1)])
            #     task_name = "{driver} frame {start}-{end}".format(
            #         driver=driver.name(), start=str(i), end=str(i + frames_per_task - 1))
            #     # print(task_command)
            #     task = author.Task(
            #         title=task_name, argv=task_command, service=str(service))
            #     parent.addChild(task)

    # print(job.asTcl())
    newJid = job.spool()

    hou.hipFile.load(file, suppress_save_prompt=True)

    hou.ui.displayMessage('Scene was submitted as {}'.format(new_name_path), buttons=('OK',),
                          severity=hou.severityType.Message)
