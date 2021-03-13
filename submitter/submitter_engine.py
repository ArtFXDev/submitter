import os
import six
import json

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
        super(SubmitterEngine, self).__init__(parent, sid)
        self.sid = sid
        if not self.sid or not self.sid.has_a("ext"):
            raise ValueError("Sid incorrect")
        self.engine_name = "engine"
        for soft, exts in six.iteritems(conf.ext_by_soft):
            if self.sid.get("ext") in exts:
                self.engine_name = soft
        if self.engine_name == "engine":
            raise NameError("Ext incorrect")

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
            self.renderer = "file"
        if self.engine_name == "houdini":
            self.output_nodes = {}
            cache_out_node_path = os.path.join(os.path.dirname(self.sid.path), ".out-nodes.json")
            if not os.path.exists(cache_out_node_path):
                cmd = 'C:/Houdini18/bin/hython.exe {} -c "hou.hipFile.save()"'.format(self.sid.path)
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                print("="*30)
                print("Open the selected scene to get output node connection")
                tmp = proc.stdout.read()
                for line in tmp.split("\n"):
                    print(line)
                print("... done")
                print("="*30)
            if not os.path.exists(cache_out_node_path):
                self.error("The out node can't be cached in file")
                raise ValueError("The out node can't be cached in file")

            with open(os.path.join(os.path.dirname(self.sid.path), ".out-nodes.json")) as json_file:
                self.output_nodes = json.load(json_file)
            number_layers = len([node for node in self.output_nodes.keys() if node.lower().startswith("layer")])
            self.input_layers_number.setValue(number_layers)
            self.houdini_layout = QVBoxLayout()
            self.output_node_cb = QComboBox()
            self.output_node_cb.addItems(self.output_nodes.keys())
            self.houdini_layout.addWidget(self.output_node_cb)
            self.rop_node = None
            self.list_rop = []
            self.custom_layout.addLayout(self.houdini_layout)
        if self.engine_name == "nuke":
            self.rop_node = None
            self.output_node_cb = QComboBox()
            self.output_node_cb.setMinimumWidth(200)
            self.output_node_cb.setEditable(True)
            self.custom_layout.addWidget(self.output_node_cb)

    def default_frame_range(self):
        return (1, 10, 1)

    def pre_submit(self):
        path = self.sid.path
        if self.engine_name == "houdini":
            self.rop_node = self.output_node_cb.currentText()

            def get_render_node(node):
                if isinstance(self.output_nodes[node], dict):
                    for key, value in self.output_nodes[node].items():
                        get_render_node(value)
                else:
                    yield (node, self.output_nodes[node])
            for node, type in get_render_node(self.output_node_cb.currentText()):
                use_renderer = False
                self.rop_node = node
                for renderer_loop in ["redshift", "arnold", "vray"]:
                    if type.startswith(renderer_loop):
                        self.submit(path, "houdini", [renderer_loop], [node] if node.lower().startswith("layer") else [])
                        use_renderer = True
                        break
                if not use_renderer:
                    self.submit(path, "houdini", layers=[node] if node.lower().startswith("layer") else [])
        if self.engine_name == "maya":
            if self.render_default.isChecked():
                self.submit(path, self.engine_name)
            if self.render_arnold.isChecked():
                self.renderer = "arnold"
            if self.render_redshift.isChecked():
                self.renderer = "redshift"
            if self.render_vray.isChecked():
                self.renderer = "vray"
            if self.renderer != "file":
                self.submit(path, self.engine_name, [self.renderer])
                conf.set("renderEngine", self.renderer)
        elif self.engine_name == "nuke":
            self.rop_node = self.output_node_cb.currentText()
            self.submit(path, "nuke")

    def task_command(self, is_linux, frame_start, frame_end, step, file_path, workspace="", server=None):
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
            if self.rb_skip_frames.isChecked():
                command.insert(3, "-skipExistingFrames")
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
            if self.rb_skip_frames.isChecked():
                command.append("-S")
        elif self.engine_name == "nuke":
             command = [
                config.batcher["nuke"]["render"]["linux" if is_linux else "win"],
                "-X", self.rop_node,
                "-F", "{start}-{end}x{step}".format(start=str(frame_start), end=str(frame_end), step=str(step)),
                "-remap", "{source},%D({target})".format(source=os.getenv("ROOT_PIPE"), target="//{}/PFE_RN_2021".format(server)),
                "%D({file_path})".format(file_path=file_path),
            ]
        if not command:
            self.error("Command invalid")
        return command


def run(sid):
    win = SubmitterEngine(sid=sid)
    win.show()


if __name__ == '__main__':
    sub = SubmitterEngine()
    sub.show()
