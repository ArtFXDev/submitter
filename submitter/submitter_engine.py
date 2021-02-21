import os
import six

from Qt import QtCore
from Qt.QtWidgets import QMainWindow
from Qt.QtWidgets import QRadioButton
from shutil import copyfile

import config
from .submitter_base import Submitter

from pipeline import conf

from Qt.QtWidgets import QComboBox, QHBoxLayout, QRadioButton, QVBoxLayout
import subprocess


class SubmitterEngine(Submitter):

    def __init__(self, parent=None, sid=None):
        print("sid SubmitterEngine __init__ : " + str(sid))
        super(SubmitterEngine, self).__init__(parent, sid)
        self.sid = sid
        if not self.sid or not self.sid.has_a("ext"):
            raise ValueError("Sid incorrect")
        self.engine_name = "engine"
        for soft, exts in six.iteritems(conf.ext_by_soft):
            if self.sid.get("ext") in exts:
                self.engine_name = soft
        if self.engine_name == "engine":
            raise Error("Ext incorrect")

        if self.engine_name == "maya":
            # chose render
            self.layout_renderer = QHBoxLayout()
            self.render_default = QRadioButton("Default")
            self.render_arnold = QRadioButton("Arnold")
            self.render_redshift = QRadioButton("Redshift")
            self.render_vray = QRadioButton("VRay")
            if conf.get("renderEngine") == "arnold":
                self.render_arnold.setChecked(True)
            if conf.get("renderEngine") == "redshift":
                self.render_redshift.setChecked(True)
            if conf.get("renderEngine") == "vray":
                self.render_vray.setChecked(True)
            self.layout_renderer.addWidget(self.render_default)
            self.layout_renderer.addWidget(self.render_arnold)
            self.layout_renderer.addWidget(self.render_redshift)
            self.layout_renderer.addWidget(self.render_vray)
            self.custom_layout.addLayout(self.layout_renderer)

        if self.engine_name == "houdini":
            self.output_nodes = []  # {} Key: name, value: Type
            # Get houdini node
            cmd = 'C:/Houdini18/bin/hbatch.exe -R -i -q -w -c "opfind -p ./out;quit" {}'.format(self.sid.path)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            tmp = proc.stdout.read()
            for line in tmp.split("\n"):
                line = line.replace(" ", "")
                if line.startswith("/out/"):
                    self.output_nodes.append(line)
            self.houdini_layout = QVBoxLayout()
            self.output_node_cb = QComboBox()
            self.output_node_cb.addItems(self.output_nodes)
            self.houdini_layout.addWidget(self.output_node_cb)
            self.rop_node = None
            self.list_rop = []
            # chose render
            self.layout_renderer = QHBoxLayout()
            self.render_mantra = QRadioButton("Mantra")
            self.render_arnold = QRadioButton("Arnold")
            self.render_redshift = QRadioButton("Redshift")
            self.render_vray = QRadioButton("VRay")
            if conf.get("renderEngine") == "arnold":
                self.render_arnold.setChecked(True)
            if conf.get("renderEngine") == "redshift":
                self.render_redshift.setChecked(True)
            if conf.get("renderEngine") == "vray":
                self.render_vray.setChecked(True)
            self.layout_renderer.addWidget(self.render_mantra)
            self.layout_renderer.addWidget(self.render_arnold)
            self.layout_renderer.addWidget(self.render_redshift)
            self.layout_renderer.addWidget(self.render_vray)
            self.houdini_layout.addLayout(self.layout_renderer)
            self.custom_layout.addLayout(self.houdini_layout)

    def default_frame_range(self):
        return (1, 10, 1)

    def pre_submit(self):
        path = self.sid.path
        if self.engine_name == "houdini":
            self.rop_node = self.output_node_cb.currentText()
            if self.render_mantra.isChecked():
                self.submit(path, self.engine_name)
            if self.render_arnold.isChecked():
                self.submit(path, self.engine_name, ["arnold"])
                conf.set("renderEngine", "arnold")
            if self.render_redshift.isChecked():
                self.submit(path, self.engine_name, ["redshift"])
                conf.set("renderEngine", "redshift")
            if self.render_vray.isChecked():
                self.submit(path, self.engine_name, ["vray"])
                conf.set("renderEngine", "vray")
        if self.engine_name == "maya":
            if self.render_default.isChecked():
                self.submit(path, self.engine_name)
            if self.render_arnold.isChecked():
                self.submit(path, self.engine_name, ["arnold"])
                conf.set("renderEngine", "arnold")
            if self.render_redshift.isChecked():
                self.submit(path, self.engine_name, ["redshift"])
                conf.set("renderEngine", "redshift")
            if self.render_vray.isChecked():
                self.submit(path, self.engine_name, ["vray"])
                conf.set("renderEngine", "vray")
        elif self.engine_name == "nuke":
            self.submit(path, "nuke")

    def task_command(self, is_linux, frame_start, frame_end, step, file_path, workspace=""):
        command = ""
        if self.engine_name == "maya":
            command = [
                config.batcher["maya"]["render"]["linux" if is_linux else "win"],
                "-r", "file",
                "-s", str(frame_start),
                "-e", str(frame_end),
                "-b", str(step),
                "-proj", "%D({proj})".format(proj=workspace),
                "%D({file_path})".format(file_path=file_path)
            ]
        elif self.engine_name == "houdini":
            command = [
                config.batcher["houdini"]["hython"]["linux" if is_linux else "win"],
                config.batcher["houdini"]["hrender"]["linux" if is_linux else "win"],
                "%D({file_path})".format(file_path=file_path),
                "-v",
                "-e",
                "-d", self.rop_node,
            ]
            if frame_start == frame_end:
                command.extend(["-F", str(frame_start)])
            else:
                command.extend(["-f", str(frame_start), str(frame_end)])
            if step != 1:
                command.extend(["-i", str(step)])
        elif self.engine_name == "nuke":
             command = [
                 config.batcher["nuke"]["render"]["linux" if is_linux else "win"],
                 "-i",
                 "-x",
                 "%D({file_path})".format(file_path=file_path),
                 "-F", "{start}-{end}x{step}".format(start=str(frame_start), end=str(frame_end), step=str(step)),
             ]
        if not command:
            self.error("Command invalid")
        return command


def run(sid):
    print("sid in run : " + str(sid))
    win = SubmitterEngine(sid=sid)
    win.show()


if __name__ == '__main__':
    sub = SubmitterEngine()
    sub.show()