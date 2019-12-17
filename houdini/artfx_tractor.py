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

    # base_command = ["C:/Houdini17/bin/hython.exe", "C:/Houdini17/bin/hrender.py", file_path, "-d", output_driver]

    job = author.Job(title=job_name, priority=100, service="PixarRender")

    for i in range(int(start), int(end), frames_per_task):
        task_command = ["C:/Houdini17/bin/hython.exe", "C:/Houdini17/bin/hrender.py", file_path, "-d", output_driver]
        task_command.extend(["-e", "-f", str(i), str(i+frames_per_task-1)])
        task_name = "frame {start}-{end}".format(start=str(i), end=str(i+frames_per_task-1))
        print(task_command)
        job.newTask(title=task_name, argv=task_command, service="pixarRender")

    newJid = job.spool()
