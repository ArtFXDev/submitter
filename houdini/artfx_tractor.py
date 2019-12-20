import hou
import sys

paths = ['', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\site-packages\\setuptools-0.6c11-py2.7.egg', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\DLLs\\python27.zip', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\DLLs', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\plat-win', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\lib-tk', 'C:\\Program Files\\Pixar\\Tractor-2.3\\bin', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\site-packages']

for path in paths:
    sys.path.append(path)

import tractor.api.author as author

def submit(node):
    job_name = node.parm("job_name").evalAsString()
    output_driver = node.parm("output_driver").evalAsString()
    start = node.parm("f1").evalAsFloat()
    end = node.parm("f2").evalAsFloat()
    # increment = node.parm("f3").evalAsFloat()
    frames_per_task = node.parm("frames_task").evalAsInt()

    file_path = hou.hipFile.name()
    print(file_path)

    # base_command = ["C:/Houdini17/bin/hython.exe", "C:/Houdini17/bin/hrender.py", file_path, "-d", output_driver]

    job = author.Job(title=job_name, priority=100, service="room_111")


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
    job.newDirMap(src="i:/synologydrive/BREACH", dst="//ana/PFE_RN_2020/BREACH", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/HARU", dst="//ana/PFE_RN_2020/HARU", zone="UNC")
    job.newDirMap(src="I:/SynologyDrive/VERLAN", dst="//ana/PFE_RN_2020/VERLAN", zone="UNC")

    #job.newDirMap(src="I:/SynologyDrive", dst="//marvin/PFE_RN_2020", zone="NFS")

    for i in range(int(start), int(end), frames_per_task):
        task_command = ["C:/Houdini17/bin/hython.exe", "C:/Houdini17/bin/hrender.py", "%D({file_path})".format(file_path=file_path), "-d", output_driver]
        task_command.extend(["-e", "-f", str(i), str(i+frames_per_task-1)])
        task_name = "frame {start}-{end}".format(start=str(i), end=str(i+frames_per_task-1))
        #print(task_command)
        task = author.Task(title=task_name, argv=task_command, service="room_111")
        job.addChild(task)

    #print(job.asTcl())
    newJid = job.spool()
