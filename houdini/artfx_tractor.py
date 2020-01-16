import hou
import sys
import os
from datetime import datetime

paths = ['', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\site-packages\\setuptools-0.6c11-py2.7.egg', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\DLLs\\python27.zip', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\DLLs', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\plat-win', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\lib-tk', 'C:\\Program Files\\Pixar\\Tractor-2.3\\bin', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\site-packages']

for path in paths:
    sys.path.append(path)

import tractor.api.author as author

def submit(node):

    file = hou.hipFile.name()

    job_name = node.parm("job_name").evalAsString()
    output_driver = node.parm("output_driver").evalAsString()
    start = node.parm("f1").evalAsFloat()
    end = node.parm("f2").evalAsFloat()
    # increment = node.parm("f3").evalAsFloat()
    frames_per_task = node.parm("frames_task").evalAsInt()
    simu = node.parm("simu").evalAsInt()
    ram = node.parm("ram").evalAsInt()

    rooms_bitfield = node.parm("rooms").eval()
    rooms_tokens = node.parm("rooms").parmTemplate().menuItems()
    rooms = [token for n, token in enumerate(rooms_tokens) if rooms_bitfield & (1 << n)]

    teams_bitfield = node.parm("teams").eval()
    teams_tokens = node.parm("teams").parmTemplate().menuItems()
    teams = [token for n, token in enumerate(teams_tokens) if teams_bitfield & (1 << n)]

    file_path = file

    service_rooms = " || ".join(rooms)
    service_teams = " || ".join(teams)
    if simu == 0:
        if ram == 0:
            if len(rooms) > 0 and len(teams) > 0:
                service = '(({rooms}) && ram_32) || ({teams})'.format(rooms=service_rooms, teams=service_teams)
            elif len(rooms) > 0:
                service = '({rooms}) && ram_32'.format(rooms=service_rooms, teams=service_teams)
            elif len(teams) > 0:
                service = '{teams}'.format(rooms=service_rooms, teams=service_teams)
        elif ram == 1:
            if len(rooms) > 0 and len(teams) > 0:
                service = '(({rooms}) && !ram_32) || ({teams})'.format(rooms=service_rooms, teams=service_teams)
            elif len(rooms) > 0:
                service = '({rooms}) && !ram_32'.format(rooms=service_rooms, teams=service_teams)
            elif len(teams) > 0:
                service = '{teams}'.format(rooms=service_rooms, teams=service_teams)
        else:
            if len(rooms) > 0 and len(teams) > 0:
                service = '({rooms}) || ({teams})'.format(rooms=service_rooms, teams=service_teams)
            elif len(rooms) > 0:
                service = '{rooms}'.format(rooms=service_rooms, teams=service_teams)
            elif len(teams) > 0:
                service = '{teams}'.format(rooms=service_rooms, teams=service_teams)

        env_job = hou.getenv('JOB')

        if env_job != None:
            env_job = env_job.replace("I:/SynologyDrive/A_PIPE", "/marvin/A_PIPE")
            ##### DIR MAP MARVIN #####
            env_job = env_job.replace("I:/SynologyDrive/ARAL", "/marvin/ARAL")
            env_job = env_job.replace("I:/SynologyDrive/CLAIR_DE_LUNE", "/marvin/CLAIR_DE_LUNE")
            env_job = env_job.replace("I:/SynologyDrive/FORGOT_YOUR_PASSWORD", "/marvin/FORGOT_YOUR_PASSWORD")
            env_job = env_job.replace("I:/SynologyDrive/LOREE", "/marvin/LOREE")
            env_job = env_job.replace("I:/SynologyDrive/RESURGENCE", "/marvin/RESURGENCE")
            env_job = env_job.replace("I:/SynologyDrive/TIMES_DOWN", "/marvin/TIMES_DOWN")

            ##### DIR MAP TARS #####
            env_job = env_job.replace("I:/SynologyDrive/ASCEND", "/tars/ASCEND")
            env_job = env_job.replace("I:/SynologyDrive/ISSEN_SAMA", "/tars/ISSEN_SAMA")
            env_job = env_job.replace("I:/SynologyDrive/LONE", "/tars/LONE")
            env_job = env_job.replace("I:/SynologyDrive/MOON_KEEPER", "/tars/MOON_KEEPER")

            ##### DIR MAP ANA #####
            env_job = env_job.replace("I:/SynologyDrive/BREACH", "/ana/BREACH")
            env_job = env_job.replace("I:/SynologyDrive/HARU", "/ana/HARU")
            env_job = env_job.replace("I:/SynologyDrive/VERLAN", "/ana/VERLAN")


        print(env_vars)
        file_name = hou.hipFile.basename()
        file_split = file_name.split(".")

        path_split = file.split("/")

        render_path = '/'.join(path_split[:-2]) + '/render'
        now = datetime.now()
        timestamp = now.strftime("%m-%d-%Y_%H-%M-%S")
        new_name = "{version}_{file_name}_{timestamp}.{extension}".format(version=path_split[-2], file_name=file_split[0], timestamp=timestamp, extension=file_split[-1])
        path = os.path.join(render_path, new_name)
        new_name_path = path.replace(os.sep, '/')


        if not os.path.exists(render_path):
            os.mkdir(render_path)

        hou.hipFile.setName(new_name_path)

        file_path = new_name_path

        if env_job != None:
            hou.putenv("JOB", env_job)

        hou.hscript("opchange I:/SynologyDrive/A_PIPE //marvin/PFE_RN_2020/A_PIPE")
        ##### DIR MAP MARVIN #####
        hou.hscript("opchange I:/SynologyDrive/ARAL //marvin/PFE_RN_2020/ARAL")
        hou.hscript("opchange I:/SynologyDrive/CLAIR_DE_LUNE //marvin/PFE_RN_2020/CLAIR_DE_LUNE")
        hou.hscript("opchange I:/SynologyDrive/FORGOT_YOUR_PASSWORD //marvin/PFE_RN_2020/FORGOT_YOUR_PASSWORD")
        hou.hscript("opchange I:/SynologyDrive/LOREE //marvin/PFE_RN_2020/LOREE")
        hou.hscript("opchange I:/SynologyDrive/RESURGENCE //marvin/PFE_RN_2020/RESURGENCE")
        hou.hscript("opchange I:/SynologyDrive/TIMES_DOWN //marvin/PFE_RN_2020/TIMES_DOWN")

        ##### DIR MAP TARS #####
        hou.hscript("opchange I:/SynologyDrive/ASCEND //tars/PFE_RN_2020/ASCEND")
        hou.hscript("opchange I:/SynologyDrive/ISSEN_SAMA //tars/PFE_RN_2020/ISSEN_SAMA")
        hou.hscript("opchange I:/SynologyDrive/LONE //tars/PFE_RN_2020/LONE")
        hou.hscript("opchange I:/SynologyDrive/MOON_KEEPER //tars/PFE_RN_2020/MOON_KEEPER")

        ##### DIR MAP ANA #####
        hou.hscript("opchange I:/SynologyDrive/BREACH //ana/PFE_RN_2020/BREACH")
        hou.hscript("opchange I:/SynologyDrive/HARU //ana/PFE_RN_2020/HARU")
        hou.hscript("opchange I:/SynologyDrive/VERLAN //ana/PFE_RN_2020/VERLAN")

        hou.hipFile.save(file_name=None)
    else:
        service = "simu"
        author.setEngineClientParam(user="hquser")

        env_job = hou.getenv('JOB')

        if env_job != None:
            env_job = env_job.replace("I:/SynologyDrive/A_PIPE", "/marvin/A_PIPE")
            ##### DIR MAP MARVIN #####
            env_job = env_job.replace("I:/SynologyDrive/ARAL", "/marvin/ARAL")
            env_job = env_job.replace("I:/SynologyDrive/CLAIR_DE_LUNE", "/marvin/CLAIR_DE_LUNE")
            env_job = env_job.replace("I:/SynologyDrive/FORGOT_YOUR_PASSWORD", "/marvin/FORGOT_YOUR_PASSWORD")
            env_job = env_job.replace("I:/SynologyDrive/LOREE", "/marvin/LOREE")
            env_job = env_job.replace("I:/SynologyDrive/RESURGENCE", "/marvin/RESURGENCE")
            env_job = env_job.replace("I:/SynologyDrive/TIMES_DOWN", "/marvin/TIMES_DOWN")

            ##### DIR MAP TARS #####
            env_job = env_job.replace("I:/SynologyDrive/ASCEND", "/tars/ASCEND")
            env_job = env_job.replace("I:/SynologyDrive/ISSEN_SAMA", "/tars/ISSEN_SAMA")
            env_job = env_job.replace("I:/SynologyDrive/LONE", "/tars/LONE")
            env_job = env_job.replace("I:/SynologyDrive/MOON_KEEPER", "/tars/MOON_KEEPER")

            ##### DIR MAP ANA #####
            env_job = env_job.replace("I:/SynologyDrive/BREACH", "/ana/BREACH")
            env_job = env_job.replace("I:/SynologyDrive/HARU", "/ana/HARU")
            env_job = env_job.replace("I:/SynologyDrive/VERLAN", "/ana/VERLAN")


        file_name = hou.hipFile.basename()
        file_split = file_name.split(".")

        path_split = file.split("/")

        render_path = '/'.join(path_split[:-2]) + '/render'
        now = datetime.now()
        timestamp = now.strftime("%m-%d-%Y_%H-%M-%S")
        new_name = "{version}_{file_name}_{timestamp}.{extension}".format(version=path_split[-2], file_name=file_split[0], timestamp=timestamp, extension=file_split[-1])
        path = os.path.join(render_path, new_name)
        new_name_path = path.replace(os.sep, '/')


        if not os.path.exists(render_path):
            os.mkdir(render_path)

        hou.hipFile.setName(new_name_path)

        file_path = new_name_path

        if env_job != None:
            hou.putenv("JOB", env_job)

        hou.hscript("opchange I:/SynologyDrive/A_PIPE /marvin/A_PIPE")
        ##### DIR MAP MARVIN #####
        hou.hscript("opchange I:/SynologyDrive/ARAL /marvin/ARAL")
        hou.hscript("opchange I:/SynologyDrive/CLAIR_DE_LUNE /marvin/CLAIR_DE_LUNE")
        hou.hscript("opchange I:/SynologyDrive/FORGOT_YOUR_PASSWORD /marvin/FORGOT_YOUR_PASSWORD")
        hou.hscript("opchange I:/SynologyDrive/LOREE /marvin/LOREE")
        hou.hscript("opchange I:/SynologyDrive/RESURGENCE /marvin/RESURGENCE")
        hou.hscript("opchange I:/SynologyDrive/TIMES_DOWN /marvin/TIMES_DOWN")

        ##### DIR MAP TARS #####
        hou.hscript("opchange I:/SynologyDrive/ASCEND /tars/ASCEND")
        hou.hscript("opchange I:/SynologyDrive/ISSEN_SAMA /tars/ISSEN_SAMA")
        hou.hscript("opchange I:/SynologyDrive/LONE /tars/LONE")
        hou.hscript("opchange I:/SynologyDrive/MOON_KEEPER /tars/MOON_KEEPER")

        ##### DIR MAP ANA #####
        hou.hscript("opchange I:/SynologyDrive/BREACH /ana/BREACH")
        hou.hscript("opchange I:/SynologyDrive/HARU /ana/HARU")
        hou.hscript("opchange I:/SynologyDrive/VERLAN /ana/VERLAN")

        hou.hipFile.save(file_name=None)


    job = author.Job(title=job_name, priority=100, service=str(service))

    job.newDirMap(src="I:/SynologyDrive/A_PIPE", dst="//marvin/PFE_RN_2020/A_PIPE", zone="UNC")
    job.newDirMap(src="i:/synologydrive/A_PIPE", dst="//marvin/PFE_RN_2020/A_PIPE", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/A_PIPE", dst="/marvin/A_PIPE", zone="NFS")
    job.newDirMap(src="i:/synologydrive/A_PIPE", dst="/marvin/A_PIPE", zone="NFS")


    job.newDirMap(src="C:/Houdini17/bin/hython.exe", dst="/opt/hfs17.5/bin/hython", zone="NFS")
    job.newDirMap(src="C:/Houdini17/bin/hrender.py", dst="/opt/hfs17.5/bin/hrender.py", zone="NFS")


    ###########################
    ##### DIR MAP WINDOWS #####
    ###########################

    ##### DIR MAP MARVIN #####
    job.newDirMap(src="I:/SynologyDrive/ARAL", dst="//marvin/PFE_RN_2020/ARAL", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/CLAIR_DE_LUNE", dst="//marvin/PFE_RN_2020/CLAIR_DE_LUNE", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/FORGOT_YOUR_PASSWORD", dst="//marvin/PFE_RN_2020/FORGOT_YOUR_PASSWORD", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/LOREE", dst="//marvin/PFE_RN_2020/LOREE", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/RESURGENCE", dst="//marvin/PFE_RN_2020/RESURGENCE", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/TIMES_DOWN", dst="//marvin/PFE_RN_2020/TIMES_DOWN", zone="UNC")

    ##### DIR MAP TARS #####
    job.newDirMap(src="I:/SynologyDrive/ASCEND", dst="//tars/PFE_RN_2020/ASCEND", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/ISSEN_SAMA", dst="//tars/PFE_RN_2020/ISSEN_SAMA", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/LONE", dst="//tars/PFE_RN_2020/LONE", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/MOON_KEEPER", dst="//tars/PFE_RN_2020/MOON_KEEPER", zone="UNC")

    ##### DIR MAP ANA #####
    job.newDirMap(src="I:/SynologyDrive/BREACH", dst="//ana/PFE_RN_2020/BREACH", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/HARU", dst="//ana/PFE_RN_2020/HARU", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/VERLAN", dst="//ana/PFE_RN_2020/VERLAN", zone="UNC")


    #########################
    ##### DIR MAP LINUX #####
    #########################

    ##### DIR MAP MARVIN #####
    job.newDirMap(src="I:/SynologyDrive/ARAL", dst="/marvin/ARAL", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/CLAIR_DE_LUNE", dst="/marvin/CLAIR_DE_LUNE", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/FORGOT_YOUR_PASSWORD", dst="/marvin/FORGOT_YOUR_PASSWORD", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/LOREE", dst="/marvin/LOREE", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/RESURGENCE", dst="/marvin/RESURGENCE", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/TIMES_DOWN", dst="/marvin/TIMES_DOWN", zone="NFS")

    ##### DIR MAP TARS #####
    job.newDirMap(src="I:/SynologyDrive/ASCEND", dst="/tars/ASCEND", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/ISSEN_SAMA", dst="/tars/ISSEN_SAMA", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/LONE", dst="/tars/LONE", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/MOON_KEEPER", dst="/tars/MOON_KEEPER", zone="NFS")

    ##### DIR MAP ANA #####
    job.newDirMap(src="I:/SynologyDrive/BREACH", dst="/ana/BREACH", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/HARU", dst="/ana/HARU", zone="NFS")
    job.newDirMap(src="I:/SynologyDrive/VERLAN", dst="/ana/VERLAN", zone="NFS")


    for i in range(int(start), int(end+1), frames_per_task):
        task_command = ["%D(C:/Houdini17/bin/hython.exe)", "%D(C:/Houdini17/bin/hrender.py)", "%D({file_path})".format(file_path=file_path), "-d", output_driver]
        task_command.extend(["-e", "-f", str(i), str(i+frames_per_task-1)])
        task_name = "frame {start}-{end}".format(start=str(i), end=str(i+frames_per_task-1))
        #print(task_command)
        task = author.Task(title=task_name, argv=task_command, service=str(service))
        job.addChild(task)

    #print(job.asTcl())
    newJid = job.spool()

    hou.hipFile.load(file, suppress_save_prompt=True)
