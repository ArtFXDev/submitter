import os
from datetime import datetime

import config
from pipeline.libs.engine.houdini_engine import HoudiniEngine
from .submitter_base import Submitter

import hou
from Qt.QtWidgets import QComboBox

from .frame_manager import frames_to_framerange

from shutil import copyfile

def get_houdini_window():
    return hou.qt.mainWindow()


class SubmitterHoudini(Submitter):

    def __init__(self, parent=get_houdini_window(), sid=None):
        super(SubmitterHoudini, self).__init__(parent, sid)
        self.output_nodes = HoudiniEngine().get_render_nodes()
        if not self.output_nodes:
            self.error("Have you render node on your scene ?")
            raise ValueError("no output node found")
        self.output_node_cb = QComboBox()
        self.output_node_cb.setEditable(True)
        self.output_node_cb.addItems(self.get_out_nodes())
        self.custom_layout.addWidget(self.output_node_cb)
        self.input_layers_number.setValue(len(self.get_render_layer()))
        self.rop_node = None
        self.list_rop = []

    def get_render_layer(self):
        render_layers = []
        for node in self.output_nodes.keys():
            if "layer" in node.lower():
                render_layers.append(node)
        return render_layers

    def get_out_nodes(self):
        return self.output_nodes.keys()

    def get_path(self):
        return hou.hipFile.path()

    def default_frame_range(self):
        start = int(hou.playbar.frameRange()[0])
        end = int(hou.playbar.frameRange()[1])
        step = 1
        return (start, end, step)

    def pre_submit(self):
        path = hou.hipFile.path()
        hou.hipFile.save(file_name=None)
        # Test output_node_cb
        if not hou.node(str(self.output_node_cb.currentText())):
            self.error("Output node error ! please verify the node path")
        else:
            self.rop_node = hou.node(self.output_node_cb.currentText())
            if self.rop_node not in self.output_nodes.keys():
                if self.rop_node.type().name() == "merge":
                    list_rop = self.rop_node.inputs()
                    for rop in list_rop:
                        self.list_rop.append(rop.path())
                    print("merge detected. Nodes = " + str(self.list_rop))
                else:
                    self.list_rop = [self.rop_node.path()]
                for node in self.list_rop:
                    print("start render for node " + node)
                    self.rop_node = node
                    hou.hipFile.save()
                    _renderer = hou.node(self.rop_node).type().name().lower()
                    use_renderer = False
                    for renderer_loop in ["redshift", "arnold", "vray"]:
                        if _renderer.startswith(renderer_loop):
                            self.submit(path, "houdini", [renderer_loop], [node] if "layer" in node.lower() else [])
                            use_renderer = True
                            break
                    if not use_renderer:
                        self.submit(path, "houdini", layers=[node] if "layer" in node.lower() else [])
            else:
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

    def get_output_dir(self):
        cur_node = hou.node(self.rop_node)
        try:
            out_dir = os.path.dirname(hou.evalParm(cur_node.parm(config.output_img_path_param[cur_node.type().name()]).path()))
        except Exception:
            out_dir = None
        return out_dir

    def task_command(self, is_linux, frame_start, frame_end, step, file_path, workspace="", server=None):
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
        return command

def run(sid=None):
    for x in get_houdini_window().children():
        if x.objectName() == "SubmitterUI":
            x.deleteLater()
    win = SubmitterHoudini(sid=sid)
    win.show()


if __name__ == '__main__':

    sub = SubmitterHoudini()
    sub.show()
