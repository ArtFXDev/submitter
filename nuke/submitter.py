import sys
import os
from Qt import QtCompat, __binding__, QtCore, QtGui
from Qt import QtWidgets

import nuke

mainPath = os.path.dirname(__file__)
ui_path = os.path.join(mainPath, 'qt', 'submitter.ui')

paths = ['', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\site-packages\\setuptools-0.6c11-py2.7.egg', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\DLLs\\python27.zip', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\DLLs', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib',
         'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\plat-win', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\lib-tk', 'C:\\Program Files\\Pixar\\Tractor-2.3\\bin', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7', 'C:\\Program Files\\Pixar\\Tractor-2.3\\lib\\python2.7\\lib\\site-packages']

for path in paths:
    sys.path.append(path)

import tractor.api.author as author

rams = ["All ram", "ram_32", "ram_lower"]
projects = ["aral", "ascend", "breach", "clair_de_lune", "fyp", "haru", "issen_sama",
            "lone", "loree", "moon_keeper", "resurgence", "times_down", "verlan"]
salles = ["s104", "s110", "s111", "s201", "s202", "s211", "s212", "s213"]


class SubmitterNuke(QtWidgets.QMainWindow):

    def __init__(self):
        super(SubmitterNuke, self).__init__()
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
        for salle in salles:
            self.list_salle.addItem(salle)
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
        salles_selected = []
        projects_selected = []
        ram_selected = self.cb_ram.currentText()

        for select in self.list_salle.selectedItems():
            salles_selected.append(select.text())
        for project in self.list_project.selectedItems():
            projects_selected.append(project.text())
        if self.rb_frame.isChecked():
            start = int(nuke.frame())
            end = int(nuke.frame()) + 1
            frames = str(nuke.frame())
        else:
            start = int(self.input_frame_start.text())
            end = int(self.input_frame_end.text())
            frames = str(start) + "-" + str(end)

        print("Render Frames : " + frames)

        file_path = nuke.root().knob('name').value()

        services = str(" || ".join(salles_selected))
        if ram_selected == "ram_lower":
            services = "(" + services + ") && !ram_32"
        elif ram_selected == "ram_32":
            services = "(" + services + ") && ram_32"
        if len(projects_selected) != 0:
            services = "((" + services + ") || (" + \
                str(' || '.join(projects_selected)) + "))"
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

        ########################
        ##### DIR MAP PIPE #####
        ########################
        ##### DIR MAP MARVIN #####
        job.newDirMap(src="i:/synologydrive/ARAL",
                      dst="//marvin/PFE_RN_2020/ARAL", zone="UNC")
        job.newDirMap(src="i:/synologydrive/CLAIR_DE_LUNE",
                      dst="//marvin/PFE_RN_2020/CLAIR_DE_LUNE", zone="UNC")
        job.newDirMap(src="i:/synologydrive/FORGOT_YOUR_PASSWORD", dst="//marvin/PFE_RN_2020/FORGOT_YOUR_PASSWORD",
                      zone="UNC")
        job.newDirMap(src="i:/synologydrive/LOREE",
                      dst="//marvin/PFE_RN_2020/LOREE", zone="UNC")
        job.newDirMap(src="i:/synologydrive/RESURGENCE",
                      dst="//marvin/PFE_RN_2020/RESURGENCE", zone="UNC")
        job.newDirMap(src="i:/synologydrive/TIMES_DOWN",
                      dst="//marvin/PFE_RN_2020/TIMES_DOWN", zone="UNC")

        ##### DIR MAP TARS #####
        job.newDirMap(src="i:/synologydrive/ASCEND",
                      dst="//tars/PFE_RN_2020/ASCEND", zone="UNC")
        job.newDirMap(src="i:/synologydrive/ISSEN_SAMA",
                      dst="//tars/PFE_RN_2020/ISSEN_SAMA", zone="UNC")
        job.newDirMap(src="i:/synologydrive/LONE",
                      dst="//tars/PFE_RN_2020/LONE", zone="UNC")
        job.newDirMap(src="i:/synologydrive/MOON_KEEPER",
                      dst="//tars/PFE_RN_2020/MOON_KEEPER", zone="UNC")

        ##### DIR MAP ANA #####
        job.newDirMap(src="i:/synologydrive/BREACH",
                      dst="//ana/PFE_RN_2020/BREACH", zone="UNC")
        job.newDirMap(src="i:/synologydrive/HARU",
                      dst="//ana/PFE_RN_2020/HARU", zone="UNC")
        job.newDirMap(src="i:/synologydrive/VERLAN",
                      dst="//ana/PFE_RN_2020/VERLAN", zone="UNC")

        # job.newDirMap(src="I:/SynologyDrive", dst="//marvin/PFE_RN_2020", zone="NFS")
        for i in range(start, end, frames_per_task):
            file_path_start = file_path.split('03_WORK_PIPE')[0]  # Marvin
            i_path_start = "I:/SynologyDrive/" + \
                file_path_start.split('/')[4] + '/'

            task_command = ["C:/Nuke11.3v5/Nuke11.3.exe -x -remap {i_file_path},{file_path_start} -F {frames} %D({file_path})".format(
                file_path=file_path, frames=str(frames), file_path_start=file_path_start, i_file_path=i_path_start)]

            task_name = "frame {start}-{end}".format(
                start=str(i), end=str(i + frames_per_task - 1))

            task = author.Task(
                title=task_name, argv=task_command, service=services)
            job.addChild(task)

        # print(job.asTcl())
        newJid = job.spool()


if __name__ == '__main__':

    sub = SubmitterNuke()
    sub.show()
