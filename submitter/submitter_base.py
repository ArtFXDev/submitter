import os
from datetime import datetime

from Qt import QtCompat
from Qt import QtCore
from Qt.QtWidgets import QMainWindow
from Qt.QtWidgets import QMessageBox
from Qt.QtWidgets import QDesktopWidget
from Qt.QtWidgets import QRadioButton

import config
from artfx_job import ArtFxJob, set_engine_client
from .frame_manager import framerange_to_frames, frames_to_framerange

import logging

log = logging.getLogger('submitter')
log.setLevel(logging.ERROR)


class Submitter(QMainWindow):
    """
    Default submitter, implement the default working of the submitter.
    """

    def __init__(self, parent=None):
        super(Submitter, self).__init__(parent)
        # setup ui
        QtCompat.loadUi(config.ui_path, self)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.center()
        self.bt_render.clicked.connect(self.pre_submit)
        self.input_frame_per_task.setValue(int(10))
        self.current_project = self.get_project()
        for pool in config.pools:
            self.list_project.addItem(pool)
        for ram in config.rams:
            self.cb_ram.addItem(ram)
        # Set default values
        items = self.list_project.findItems("work", QtCore.Qt.MatchCaseSensitive)
        if items[0]:
            self.list_project.setCurrentItem(items[0])
        frames = self.default_frame_range()
        # range last value is exclusive so +1 needed
        str_frames = frames_to_framerange(list(range(frames[0], frames[1] + 1)))
        log.info("Frames : " + str(str_frames))
        self.input_frame_pattern.setText(str_frames)
        # Dev mode
        self.isDev = True if os.getenv("DEV_PIPELINE") else False
        if self.isDev:
            log.setLevel(logging.DEBUG)
            log.info("Dev mode")
            self.isDev = True
            self._rb_only_logs = QRadioButton("OnlyLogs")
            self.custom_layout.addWidget(self._rb_only_logs)

    def get_path(self):
        return None

    def default_frame_range(self):
        return (1, 10)

    def center(self):
        qRect = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qRect.moveCenter(centerPoint)
        self.move(qRect.topLeft())

    def pre_submit(self):
        """
        Need to get data from dcc and call submit
        self.submit(path, start, end)
        """
        raise NotImplementedError()

    def is_linux(self):
        for project in self.list_project.selectedItems():
            if str(project.text()) == "rackLinux":
                return True
        return False

    def get_project(self, path=None):
        path = path or self.get_path()
        if not path:
            raise ValueError("You need to be in a pipeline scene")
        path = path.replace(os.sep, "/")
        root = os.environ["ROOT_PIPE"] if os.environ["ROOT_PIPE"] else "D:/SynologyDrive"
        if path.startswith('//'):
            project_name = path.split('/')[4].upper()
        else:
            path = path.replace(root + "/", "")
            project_name = path.split('/')[0].upper()
        return [_proj for _proj in config.projects if str(project_name) == _proj["name"]][0] or None

    def submit(self, path, engine, plugins=None):
        log.info("Start submit with : path: {} | engine: {} | plugins: {}".format(path, engine, str(plugins)))
        job_name = str(self.input_job_name.text())
        if not job_name:
            self.info("Job name is needed")
            return 0
        frames_per_task = int(self.input_frame_per_task.value())
        pools_selected = []
        ram_selected = self.cb_ram.currentText()
        path = path.replace(os.sep, "/")

        if int(frames_per_task) < 5:
            self.error("You need to use minimum 5 frame per task")
            return 0

        # # # # # DIRMAP # # # #
        path = self.create_render_file(path)

        # # # # # WORKSPACE # # # # #
        if '/scenes' not in path:
            self.error('No workspace found (/scenes)')
        workspace = path.split('/scenes')[0]

        # # # # # POOLS # # # # #
        isLinux = self.is_linux()
        if len(self.list_project.selectedItems()) < 1:
            self.error("You need to select a pool")
        for project in self.list_project.selectedItems():
            # Linux Rack
            if str(project.text()) == "rackLinux":
                pools_selected = ["rackLinux"]
                break
            # Pool
            pools_selected.append(str(project.text()).lower())

        # # # # # FRAMES # # # # #
        frames_pattern = self.input_frame_pattern.text().replace(" ", "")
        try:
            frames_array = framerange_to_frames(frames_pattern)
            print("Render Frames : " + str(frames_array))
        except Exception as ex:
            self.error("Framerange error, please verify your syntax: {}\n{}".format(frames_pattern, ex.message))
            return 0

        # # # # # SERVICES # # # # #
        if len(pools_selected) == 1:
            services = pools_selected[0]
        else:
            services = "(" + " || ".join(pools_selected) + ")"
        if ram_selected == "ram_lower":
            services = services + " && !ram_32"
        elif ram_selected == "ram_32":
            services = services + " && ram_32"
        if self.isDev:
            services = "td"
        print("Render on : " + services)

        # # # # # ENGINE CLIENT # # # # #
        set_engine_client(user=("artfx" if isLinux else "admin"))

        # # # # # JOB # # # # #
        job = ArtFxJob(title=job_name, priority=100, service=services)

        try:
            for frames_obj in frames_array:
                start = frames_obj["start"]
                step = frames_obj["step"]
                end = frames_obj["end"]
                task_step = frames_per_task * step
                for i in range(start, end + 1, task_step):
                    # # # # # BEFORE TASK # # # #
                    pre_command = None
                    if not isLinux:
                        pre_command = ["cmd", "/c", "//multifct/tools/renderfarm/misc/tractor_add_srv_key.bat"]
                    # # # # # TASKS # # # # #
                    task_end_frame = (i + task_step - 1) if (i + task_step - 1) < end else end
                    log.info("Task: frame {}-{}x{}".format(i, task_end_frame, step))
                    task_command = self.task_command(isLinux, i, task_end_frame, step, path, workspace)
                    task_name = "frame {start}-{end}".format(start=str(i), end=str(task_end_frame))
                    # # # # # CLEAN UP # # # # #
                    executables = config.batcher[engine]["cleanup"]["linux" if isLinux else "win"]
                    if executables:
                        if type(executables) == str:
                            executables = [executables]
                    job.add_task(task_name, task_command, services, path, self.current_project["server"], engine, plugins, executables, isLinux, pre_command)
            job.comment = str(self.current_project["name"])
            job.projects = [str(self.current_project["name"])]
            if self.isDev and self._rb_only_logs.isChecked():
                print(job.asTcl())
            else:
                job.spool(owner=("artfx" if isLinux else str(self.current_project["name"])))
            self.success()
        except Exception as ex:
            self.error(ex.message)

    def task_command(self, is_linux, frame_start, frame_end, step, file_path, workspace=""):
        """
        Command for each task of the job (need to be change for each dcc)
        :param bool is_linux: Is linux ? (true = linux, false = win)
        :param int frame_start: Task start frame
        :param int frame_end: Task end frame
        :param int step: frame step
        :param str file_path: Path to the scene to render
        :param str workspace: Path to the workspace folder
        :return: The command in str or list
        :rtype: str or list
        """
        raise NotImplementedError()

    def success(self):
        """
        Success message box
        """
        msg = QMessageBox()
        msg.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        msg.setIcon(QMessageBox.Information)
        msg.setText("Job Send !")
        msg.setWindowTitle("RenderFarm")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(self.close)
        msg.exec_()

    def error(self, message):
        """
        Error message box
        """
        msg = QMessageBox()
        msg.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("RenderFarm")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(msg.close)
        msg.exec_()
        # raise Exception(message)

    def info(self, message):
        """
        Error message box
        """
        msg = QMessageBox()
        msg.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("RenderFarm")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(self.close)
        msg.exec_()

    def create_render_file(self, path):
        """
        Create a tempory render scene file to avoid scene modification
        """
        proj = self.current_project or self.get_project(path)
        isLinux = self.is_linux()
        local_root = os.environ["ROOT_PIPE"] or "D:/SynologyDrive"
        local_project = '{}/{}'.format(local_root, proj["name"])
        template_server = '/{}/PFE_RN_2021/{}' if isLinux else '//{}/PFE_RN_2021/{}'
        server_project = template_server.format(proj["server"], proj["name"])

        # # # # TEMP FILE # # # #
        file_name = os.path.basename(path)
        file_split = file_name.split(".")
        path_split = path.split("/")
        render_path = '/'.join(path_split[:-2]) + '/render'
        # Submission on the server directly
        # Use windows path becose only windows use submitter
        server_project_win = '//{}/PFE_RN_2021/{}'.format(proj["server"], proj["name"])
        render_path = render_path.replace('D:/SynologyDrive/{}'.format(proj["name"]), server_project_win)
        now = datetime.now()
        timestamp = now.strftime("%m-%d-%Y_%H-%M-%S")
        new_name = "{version}_{file_name}_{timestamp}.{extension}".format(version=path_split[-2], file_name=file_split[0],
                                                                          timestamp=timestamp, extension=file_split[-1])
        new_name_path = os.path.join(render_path, new_name).replace(os.sep, '/')
        print("check if path exist : " + render_path)
        if not os.path.exists(render_path):
            if not os.path.exists(os.path.dirname(render_path)):
                os.makedirs(os.path.dirname(render_path))
            os.mkdir(render_path)

        # # # # DIRMAP # # # #
        self.set_dirmap(local_project, server_project, new_name_path, path)
        # Remap to local path for comand dirmap by tractor
        new_name_path = new_name_path.replace(server_project_win, 'D:/SynologyDrive/{}'.format(proj["name"]))
        return new_name_path

    def set_dirmap(self, local_project, server_project, new_name_path, path):
        pass


def run():
    win = Submitter()
    win.show()


if __name__ == '__main__':

    sub = Submitter()
    sub.show()
