import sys
import os
from Qt import QtCompat, __binding__, QtCore, QtGui
from Qt import QtWidgets
from Qt.QtWidgets import QMessageBox

import maya.cmds as cmds

mainPath = os.path.dirname(__file__)
ui_path = os.path.join(mainPath, 'qt', 'submitter.ui')

paths = ['', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\site-packages\\setuptools-0.6c11-py2.7.egg', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\DLLs\\python27.zip', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\DLLs', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib',
         'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\plat-win', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\lib-tk', 'C:\\Program Files\\Pixar\\Tractor-2.3\\bin', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\site-packages']

for path in paths:
    sys.path.append(path)

import tractor.api.author as author

rams = ["All ram", "ram_32", "ram_lower"]
projects = ["aral", "ascend", "breach", "clair_de_lune", "fyp", "haru", "issen_sama",
            "lone", "loree", "moon_keeper", "resurgence", "times_down", "verlan", "rack"]


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
        for project in projects:
            self.list_project.addItem(project)
        for ram in rams:
            self.cb_ram.addItem(ram)

    def toggle(self):
        if self.rb_frame_range.isChecked():
            self.widget_frame.setVisible(True)
        else:
            self.widget_frame.setVisible(False)
            self.input_frame_start.setText('1')
            self.input_frame_end.setText('2')

    def submit(self):
        job_name = str(self.input_job_name.text())
        increment = int(self.input_frame_increment.text())
        frames_per_task = int(self.input_frame_per_task.text())
        projects_selected = []
        ram_selected = self.cb_ram.currentText()
        proj = cmds.file(query=True, sceneName=True).replace(
            os.sep, '/').split('/scenes')[0]

        for project in self.list_project.selectedItems():
            projects_selected.append("p_" + str(project.text()).lower())
        if self.rb_frame.isChecked():
            start = int(cmds.currentTime(query=True))
            end = int(cmds.currentTime(query=True)) + 1
            frames = str(cmds.currentTime(query=True))
        else:
            start = int(self.input_frame_start.text())
            end = int(self.input_frame_end.text())
            frames = str(start) + "-" + str(end)

        print("Render Frames : " + frames)

        file_path = cmds.file(query=True, sceneName=True)

        path = cmds.file(query=True, sceneName=True).replace(os.sep, '/')
        if '/scenes' not in path:
            raise Exception('Pas de project Maya (/scenes)')
        proj = path.split('/scenes')[0]

        services = "(" + " || ".join(projects_selected) + ")"
        if ram_selected == "ram_lower":
            services = services + " && !ram_32"
        elif ram_selected == "ram_32":
            services = services + " && ram_32"
        print("Render on : " + services)

        job = author.Job(title=job_name, priority=100, service=services)

        job.newDirMap(src="I:/SynologyDrive/A_PIPE",
                      dst="//marvin/PFE_RN_2020/A_PIPE", zone="UNC")
        job.newDirMap(src="i:/synologydrive/A_PIPE",
                      dst="//marvin/PFE_RN_2020/A_PIPE", zone="UNC")

        ##### DIR MAP MARVIN #####
        job.newDirMap(src="I:/SynologyDrive/ARAL",
                      dst="//marvin/PFE_RN_2020/ARAL", zone="UNC")
        job.newDirMap(src="I:/SynologyDrive/CLAIR_DE_LUNE",
                      dst="//marvin/PFE_RN_2020/CLAIR_DE_LUNE", zone="UNC")
        job.newDirMap(src="I:/SynologyDrive/FORGOT_YOUR_PASSWORD", dst="//marvin/PFE_RN_2020/FORGOT_YOUR_PASSWORD",
                      zone="UNC")
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

        proj_name = file_path.split('/')[2]
        serv_name = project_server[proj_name]
        print "serv : ", serv_name
        # job.newDirMap(src="I:/SynologyDrive", dst="//marvin/PFE_RN_2020", zone="NFS")
        # print 'range', range(start, end, frames_per_task)
        try:
            if frames_per_task > (end - start):
                frames_per_task = (end - start + 1)
            for i in range(start, end + 1, frames_per_task):
                if (i + frames_per_task - 1) < end:
                    task_name = "frame {start}-{end}".format(
                        start=str(i), end=str(i + frames_per_task - 1))
                else:
                    task_name = "frame {start}-{end}".format(
                        start=str(i), end=str(end))
                if (i + frames_per_task - 1) < end:
                    task_command = [
                        "C:/Maya2019/bin/Render.exe",
                        "-r", "file",
                        "-s", "{start}".format(start=str(i)),
                        "-e", "{end}".format(end=str(i + frames_per_task - 1)),
                        "-preRender", 'dirmap -en true; dirmap -m "I:/SynologyDrive/" "//' +
                        serv_name + '/PFE_RN_2020/";',
                        "-proj", "%D({proj})".format(proj=proj),
                        "%D({file_path})".format(file_path=file_path)]
                else:
                    task_command = [
                        "C:/Maya2019/bin/Render.exe",
                        "-r", "file",
                        "-s", "{start}".format(start=str(i)),
                        "-e", "{end}".format(end=str(end)),
                        "-preRender", 'dirmap -en true; dirmap -m "I:/SynologyDrive/" "//' +
                        serv_name + '/PFE_RN_2020/";',
                        "-proj", "%D({proj})".format(proj=proj),
                        "%D({file_path})".format(file_path=file_path)]
                # "-preRender", 'dirmap -en true; dirmap -m "I:\\SynologyDrive\\" "//' + serv_name + '/PFE_RN_2020/";',
                task_name = "frame {start}-{end}".format(
                    start=str(i), end=str(i + frames_per_task - 1))

                task = author.Task(
                    title=task_name, argv=task_command, service=services)
                job.addChild(task)

            # print(job.asTcl())
            newJid = job.spool()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Job Send !")
            msg.setWindowTitle("RenderFarm")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(self.close)
            msg.exec_()
        except Exception as ex:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(ex.message)
            msg.setWindowTitle("RenderFarm")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(self.close)
            msg.exec_()


if __name__ == '__main__':

    sub = SubmitterMaya()
    sub.show()
