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
projects = ["rack_linux", "Relativity", "Hostile", "Dreamblower", "Backstage", "Cocorica", "From_Above", "Hakam",
            "Dive", "Green", "Barney", "Pirhearth", "Kitty", "Test_Pipe", "rack"]


project_server = {

    'TEST_PIPE': 'ana',
    'HAKAM': 'ana',
    'DIVE': 'ana',
    'GREEN': 'ana',
    'BARNEY': 'ana',
    'PIR_HEARTH': 'ana',
    'GOOD_MORNING_KITTY': 'ana',

    'RELATIVITY': 'tars',
    'HOSTILE': 'tars',
    'DREAMBLOWER': 'tars',
    'BACKSTAGE': 'tars',
    'COCORICA': 'tars',
    'FROM_ABOVE': 'tars',

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

        isRack = False
        for project in self.list_project.selectedItems():
            if str(project.text()).lower() == "rack_linux":
                isRack = True
            projects_selected.append("p_" + str(project.text()).lower())
        if isRack:
            projects_selected = ["rack_linux"]
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

        if isRack:
            services = "rackLinux"
            author.setEngineClientParam(user="artfx")

        job = author.Job(title=job_name, priority=100, service=services)

        ###########################
        ##### DIR MAP WINDOWS #####
        ###########################

        job.newDirMap(src="D:/SynologyDrive/TEST_PIPE",
                      dst="//ana/PFE_RN_2021/TEST_PIPE", zone="UNC")

        ##### DIR MAP TARS #####
        job.newDirMap(src="D:/SynologyDrive/RELATIVITY",
                      dst="//tars/PFE_RN_2021/RELATIVITY", zone="UNC")
        job.newDirMap(src="D:/SynologyDrive/HOSTILE",
                      dst="//tars/PFE_RN_2021/HOSTILE", zone="UNC")
        job.newDirMap(src="D:/SynologyDrive/DREAMBLOWER",
                      dst="//tars/PFE_RN_2021/DREAMBLOWER", zone="UNC")
        job.newDirMap(src="D:/SynologyDrive/BACKSTAGE",
                      dst="//tars/PFE_RN_2021/BACKSTAGE", zone="UNC")
        job.newDirMap(src="D:/SynologyDrive/COCORICA",
                      dst="//tars/PFE_RN_2021/COCORICA", zone="UNC")
        job.newDirMap(src="D:/SynologyDrive/FROM_ABOVE",
                      dst="//tars/PFE_RN_2021/FROM_ABOVE", zone="UNC")

        ##### DIR MAP ANA #####
        job.newDirMap(src="D:/SynologyDrive/HAKAM",
                      dst="//ana/PFE_RN_2021/HAKAM", zone="UNC")
        job.newDirMap(src="D:/SynologyDrive/DIVE",
                      dst="//ana/PFE_RN_2021/DIVE", zone="UNC")
        job.newDirMap(src="D:/SynologyDrive/GREEN",
                      dst="//ana/PFE_RN_2021/GREEN", zone="UNC")
        job.newDirMap(src="D:/SynologyDrive/BARNEY",
                      dst="//ana/PFE_RN_2021/BARNEY", zone="UNC")
        job.newDirMap(src="D:/SynologyDrive/PIR_HEARTH",
                      dst="//ana/PFE_RN_2021/PIR_HEARTH", zone="UNC")
        job.newDirMap(src="D:/SynologyDrive/GOOD_MORNING_KITTY",
                      dst="//ana/PFE_RN_2021/GOOD_MORNING_KITTY", zone="UNC")

        #########################
        ##### DIR MAP LINUX #####
        #########################

        job.newDirMap(src="D:/SynologyDrive/TEST_PIPE",
                      dst="/ana/TEST_PIPE", zone="NFS")

        ##### DIR MAP TARS #####
        job.newDirMap(src="D:/SynologyDrive/RELATIVITY",
                      dst="/tars/RELATIVITY", zone="NFS")
        job.newDirMap(src="D:/SynologyDrive/HOSTILE",
                      dst="/tars/HOSTILE", zone="NFS")
        job.newDirMap(src="D:/SynologyDrive/DREAMBLOWER",
                      dst="/tars/DREAMBLOWER", zone="NFS")
        job.newDirMap(src="D:/SynologyDrive/BACKSTAGE",
                      dst="/tars/BACKSTAGE", zone="NFS")
        job.newDirMap(src="D:/SynologyDrive/COCORICA",
                      dst="/tars/COCORICA", zone="NFS")
        job.newDirMap(src="D:/SynologyDrive/FROM_ABOVE",
                      dst="/tars/FROM_ABOVE", zone="NFS")

        ##### DIR MAP ANA #####
        job.newDirMap(src="D:/SynologyDrive/HAKAM",
                      dst="/ana/HAKAM", zone="NFS")
        job.newDirMap(src="D:/SynologyDrive/DIVE",
                      dst="/ana/DIVE", zone="NFS")
        job.newDirMap(src="D:/SynologyDrive/GREEN",
                      dst="/ana/GREEN", zone="NFS")
        job.newDirMap(src="D:/SynologyDrive/BARNEY",
                      dst="/ana/BARNEY", zone="NFS")
        job.newDirMap(src="D:/SynologyDrive/PIR_HEARTH",
                      dst="/ana/PIR_HEARTH", zone="NFS")
        job.newDirMap(src="D:/SynologyDrive/GOOD_MORNING_KITTY",
                      dst="/ana/GOOD_MORNING_KITTY", zone="NFS")

        job.newDirMap(src="//tars/PFE_RN_2020", dst="/tars", zone="NFS")
        job.newDirMap(src="//ana/PFE_RN_2020", dst="/ana", zone="NFS")


        job.newDirMap(src="C:/Maya2019/bin/Render.exe",
                      dst="/usr/autodesk/maya/bin/Render", zone="NFS")


        if file_path.startswith('//'):
            proj_name = file_path.split('/')[4]
        else:
            proj_name = file_path.split('/')[2]
        serv_name = project_server[proj_name]
        if isRack:
            proj = proj.replace("I:/SynologyDrive/", "/%s/" % serv_name)
            file_path = file_path.replace(
                "I:/SynologyDrive/", "/%s/" % serv_name)
            dirmap = 'dirmap -en true; dirmap -m "I:/SynologyDrive/" "/%s/";' % serv_name
        else:
            proj = proj.replace("I:/SynologyDrive/",
                                "//" + serv_name + "/PFE_RN_2020/")
            file_path = file_path.replace(
                "I:/SynologyDrive/", "//" + serv_name + "/PFE_RN_2020/")
            dirmap = 'dirmap -en true; dirmap -m "I:/SynologyDrive/" "//' + \
                serv_name + '/PFE_RN_2020/";'
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
                        "%D(C:/Maya2019/bin/Render.exe)",
                        "-r", "redshift" if self.rb_render_redshift.isChecked() else "file",
                        "-s", "{start}".format(start=str(i)),
                        "-e", "{end}".format(end=str(i + frames_per_task - 1)),
                        "-preRender", dirmap,
                        "-proj", "{proj}".format(proj=proj),
                        "{file_path}".format(file_path=file_path)]
                else:
                    task_command = [
                        "%D(C:/Maya2019/bin/Render.exe)",
                        "-r", "redshift" if self.rb_render_redshift.isChecked() else "file",
                        "-s", "{start}".format(start=str(i)),
                        "-e", "{end}".format(end=str(end)),
                        "-preRender", dirmap,
                        "-proj", "{proj}".format(proj=proj),
                        "{file_path}".format(file_path=file_path)]

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
