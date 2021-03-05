import os
from datetime import datetime
import webbrowser
import json
from shutil import copyfile

from Qt import QtCompat
from Qt import QtCore
from Qt.QtWidgets import QMainWindow
from Qt.QtWidgets import QMessageBox
from Qt.QtWidgets import QDesktopWidget
from Qt.QtWidgets import QRadioButton

import config
from artfx_job import ArtFxJob, set_engine_client
from .frame_manager import framerange_to_frames_obj, frames_to_framerange, framerange_to_frames
from pipeline.libs.engine import engine

from pipeline.libs.spil.libs.sid import Sid

import logging
logging.basicConfig()
log = logging.getLogger('submitter')
log.setLevel(logging.ERROR)


class Submitter(QMainWindow):
    """
    Default submitter, implement the default working of the submitter.
    """

    def __init__(self, parent=None, sid=None):
        super(Submitter, self).__init__(parent)
        # setup ui
        QtCompat.loadUi(config.ui_path, self)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.center()
        self.bt_open_tractor.clicked.connect(lambda: webbrowser.open("http://tractor/tv/#"))
        self.bt_help.clicked.connect(lambda: webbrowser.open("https://github.com/ArtFXDev/submitter/wiki"))
        self.bt_render.clicked.connect(self.pre_submit)
        self._engine = engine.get()
        if sid:
            self.sid = sid
        else:
            self.sid = Sid(path=self._engine.get_file_path())
        if not self.sid:
            raise ValueError("You need to be in a pipeline scene")
        log.info("Sid : " + str(self.sid))
        self.current_project = self.get_project(self.sid.path)
        for pool in config.pools:
            self.list_project.addItem(pool)
        for ram in config.rams:
            self.cb_ram.addItem(ram)
        # Set default values
        farm = ""
        if self.sid.is_shot():
            farm = self.sid.get('project').upper() + '_' + self.sid.get('seq') + '_' + self.sid.get('shot')
        elif self.sid.is_asset():
            farm = self.sid.get('project').upper() + '_' + self.sid.get('name')
        self.input_job_name.setText(farm)
        # items = self.list_project.findItems("work", QtCore.Qt.MatchCaseSensitive)
        # if items[0]:
        #     self.list_project.setCurrentItem(items[0])
        frames = self.default_frame_range()
        # range last value is exclusive so +1 needed
        str_frames = frames_to_framerange(list(range(frames[0], frames[1] + 1, frames[2])))
        log.info("Frames : " + str(str_frames))
        self.input_frame_pattern.setText(str_frames)
        # Dev mode
        self.isDev = True if os.getenv("DEV_PIPELINE") else False
        mode_str = ""
        if "beta" in os.path.dirname(__file__):
            mode_str = "BETA"
        if "prod" in os.path.dirname(__file__):
            mode_str = "PROD"
        if self.isDev:
            mode_str = "DEV"
            log.setLevel(logging.DEBUG)
            log.info("Dev mode")
            self.isDev = True
            self._rb_only_logs = QRadioButton("OnlyLogs")
            self.custom_layout.addWidget(self._rb_only_logs)
        self.setWindowTitle("Submitter - " + mode_str)

    def get_sid(self):
        return None

    def default_frame_range(self):
        return (1, 10, 1)

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

    def get_project(self, path):
        path = path
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

    def submit(self, path, engine_name, plugins=None, layers=None):
        log.info("Start submit with : path: {} | engine: {} | plugins: {} | layers: {}".format(path, engine_name, str(plugins), str(layers)))
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

        # # # # # TMP SCENE # # # #
        path = self.create_render_file(path)

        # # # # # WORKSPACE # # # # #
        if '/scenes' not in path:
            self.error('No workspace found (/scenes)')
            return 0
        workspace = path.split('/scenes')[0]

        # # # # # POOLS # # # # #
        isLinux = self.is_linux()
        if len(self.list_project.selectedItems()) < 1:
            self.error("You need to select a pool")
            return 0
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
            frames_array = framerange_to_frames_obj(frames_pattern)
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

        # # # # # METADATA # # # #
        metadata = dict()
        metadata["dcc"] = engine_name
        metadata["renderEngine"] = plugins or "default"
        metadata["layers"] = layers or ["main"]
        metadata["nbLayersMax"] = self.input_layers_number.value() or 1
        # metadata["frames"] = framerange_to_frames(frames_pattern)
        metadata["sendUser"] = os.getenv("COMPUTERNAME", None)
        metadata["renderState"] = "test" if self.rb_test.isChecked() else "final"
        for key in self.sid.keys:
            metadata[key] = self.sid.get(key)
        metadata["project"] = self.current_project["name"]

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
                    # # # # # TASKS # # # # #
                    task_end_frame = (i + task_step - 1) if (i + task_step - 1) < end else end
                    task_frames_pattern = "{}-{}x{}".format(i, task_end_frame, step)
                    log.info("Task: frame {}".format(task_frames_pattern))
                    task_command = self.task_command(isLinux, i, task_end_frame, step, path, workspace)
                    task_name = "frame {start}-{end}x{step}".format(start=str(i), end=str(task_end_frame), step=str(step))
                    # # # # # TASK CLEAN UP # # # # #
                    # executables = config.batcher[engine_name]["cleanup"]["linux" if isLinux else "win"]
                    # if executables:
                    #     if type(executables) == str:
                    #         executables = [executables]
                    job.add_task(task_name, task_command, services, path, self.current_project["server"], task_frames_pattern,
                                 engine_name, plugins, [], isLinux, pre_command)
            job.comment = str(self.current_project["name"])
            job.projects = [str(self.current_project["name"])]
            job.metadata = json.dumps(metadata)
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
        proj = self.current_project
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
        new_name = "{version}_{file_name}_{timestamp}.{ext}".format(version=path_split[-2], file_name=file_split[0],
                                                                          timestamp=timestamp, ext=file_split[-1])
        new_name_path = os.path.join(render_path, new_name).replace(os.sep, '/')
        print("check if path exist : " + render_path)
        try:
            if not os.path.exists(render_path):
                if not os.path.exists(os.path.dirname(render_path)):
                    os.makedirs(os.path.dirname(render_path))
                os.mkdir(render_path)
            copyfile(path, new_name_path)  # Copy scene file into server
        except WindowsError as ex:
            self.error("Can't access to server !\n" + ex.message)
        except Exception as ex:
            self.error("Can't create file !\n" + ex.message)

        # Remap to local path for command dirmap by tractor
        new_name_path = new_name_path.replace(server_project_win, 'D:/SynologyDrive/{}'.format(proj["name"]))
        return new_name_path


def run():
    win = Submitter()
    win.show()


if __name__ == '__main__':

    sub = Submitter()
    sub.show()
