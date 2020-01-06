import sys
import os
from Qt import QtCompat, __binding__, QtCore, QtGui
from Qt import QtWidgets

import maya.cmds as cmds

mainPath = os.path.dirname(__file__)
ui_path = os.path.join(mainPath, 'qt', 'submitter.ui')

paths = ['', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\site-packages\\setuptools-0.6c11-py2.7.egg', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\DLLs\\python27.zip', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\DLLs', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\plat-win', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\lib-tk', 'C:\\Program Files\\Pixar\\Tractor-2.3\\bin', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\site-packages']

for path in paths:
    sys.path.append(path)

import tractor.api.author as author


class SubmitterMaya(QtWidgets.QMainWindow):

    def __init__(self):
        super(SubmitterMaya, self).__init__()
        # setup ui
        QtCompat.loadUi(ui_path, self)
        self.bt_render.clicked.connect(self.submit)
        self.widget_frame.setVisible(False)
        self.rb_frame_range.clicked.connect(self.toggle)
        self.rb_frame.clicked.connect(self.toggle)
        self.input_frame_per_task.setText('10')
        self.input_frame_increment.setText('1')
        self.input_frame_start.setText('1')
        self.input_frame_end.setText('2')

    def toggle(self):
        if self.rb_frame_range.isChecked():
            self.widget_frame.setVisible(True)
        else:
            self.widget_frame.setVisible(False)
            self.input_frame_start.setText('1')
            self.input_frame_end.setText('2')

    def submit(self):
        job_name = str(self.input_job_name.text())
        start = int(self.input_frame_start.text())
        end = int(self.input_frame_end.text())
        increment = int(self.input_frame_increment.text())
        frames_per_task = int(self.input_frame_per_task.text())

        file_path = cmds.file(query=True, sceneName=True)
        print(file_path)

        job = author.Job(title=job_name, priority=100, service="s111")
        ##### DIR MAP MARVIN #####
        job.newDirMap(src="I:/SynologyDrive/ARAL", dst="//marvin/PFE_RN_2020/ARAL", zone="UNC")
        job.newDirMap(src="I:/SynologyDrive/CLAIR_DE_LUNE", dst="//marvin/PFE_RN_2020/CLAIR_DE_LUNE", zone="UNC")
        job.newDirMap(src="I:/SynologyDrive/FORGOT_YOUR_PASSWORD", dst="//marvin/PFE_RN_2020/FORGOT_YOUR_PASSWORD",
                      zone="UNC")
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

        ########################
        ##### DIR MAP PIPE #####
        ########################
        ##### DIR MAP MARVIN #####
        job.newDirMap(src="i:/synologydrive/ARAL", dst="//marvin/PFE_RN_2020/ARAL", zone="UNC")
        job.newDirMap(src="i:/synologydrive/CLAIR_DE_LUNE", dst="//marvin/PFE_RN_2020/CLAIR_DE_LUNE", zone="UNC")
        job.newDirMap(src="i:/synologydrive/FORGOT_YOUR_PASSWORD", dst="//marvin/PFE_RN_2020/FORGOT_YOUR_PASSWORD",
                      zone="UNC")
        job.newDirMap(src="i:/synologydrive/LOREE", dst="//marvin/PFE_RN_2020/LOREE", zone="UNC")
        job.newDirMap(src="i:/synologydrive/RESURGENCE", dst="//marvin/PFE_RN_2020/RESURGENCE", zone="UNC")
        job.newDirMap(src="i:/synologydrive/TIMES_DOWN", dst="//marvin/PFE_RN_2020/TIMES_DOWN", zone="UNC")

        ##### DIR MAP TARS #####
        job.newDirMap(src="i:/synologydrive/ASCEND", dst="//tars/PFE_RN_2020/ASCEND", zone="UNC")
        job.newDirMap(src="i:/synologydrive/ISSEN_SAMA", dst="//tars/PFE_RN_2020/ISSEN_SAMA", zone="UNC")
        job.newDirMap(src="i:/synologydrive/LONE", dst="//tars/PFE_RN_2020/LONE", zone="UNC")
        job.newDirMap(src="i:/synologydrive/MOON_KEEPER", dst="//tars/PFE_RN_2020/MOON_KEEPER", zone="UNC")

        ##### DIR MAP ANA #####
        job.newDirMap(src="i:/synologydrive/BREACH", dst="//ana/PFE_RN_2020/BREACH", zone="UNC")
        job.newDirMap(src="i:/synologydrive/HARU", dst="//ana/PFE_RN_2020/HARU", zone="UNC")
        job.newDirMap(src="i:/synologydrive/VERLAN", dst="//ana/PFE_RN_2020/VERLAN", zone="UNC")

        # job.newDirMap(src="I:/SynologyDrive", dst="//marvin/PFE_RN_2020", zone="NFS")
        # print 'range', range(start, end, frames_per_task)
        for i in range(start, end, frames_per_task):
            task_command = ["C:/Maya2019/bin/Render.exe -r sw", "%D({file_path})".format(file_path=file_path), "-d"]

            task_command.extend(["-e", "-f", str(i), str(i + frames_per_task - 1)])
            task_name = "frame {start}-{end}".format(start=str(i), end=str(i + frames_per_task - 1))

            task = author.Task(title=task_name, argv=task_command, service="s111")
            job.addChild(task)

        # print(job.asTcl())
        newJid = job.spool()


if __name__ == '__main__':

    sub = SubmitterMaya()
    sub.show()
