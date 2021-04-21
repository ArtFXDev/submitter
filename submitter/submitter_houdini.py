import os

import config
from pipeline.libs.engine.houdini_engine import HoudiniEngine
from .submitter_base import Submitter

import hou
from Qt.QtWidgets import QComboBox


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

    def check_before(self, _node):
        node = hou.node(_node)
        cam = node.evalParm(config.camera_param[node.type().name()])
        if not cam or not hou.node(cam):
            self.error("You cam is not valid : {}".format(node.path()))
            self.is_cancel = True
        elif cam == "/obj/cam1":
            self.warning("You use a default camera : {}".format(node.path()))
        # Check out path
        if "$JOB" in node.parm(config.output_img_path_param[node.type().name()]).rawValue():
            self.warning("You may use $OUT instead of $JOB ! \n{}".format(node.path()))
        # Check missing resources
        missing_abc = []
        missing_filecache = []
        for filecache in hou.nodeType(hou.nodeTypeCategories()["Sop"], "filecache").instances():
            if filecache.evalParm('loadfromdisk') != 1:
                continue
            if filecache.evalParm('trange') == 0:
                # One frame
                path = filecache.evalParm('file').replace(os.sep, '/').replace('D:/SynologyDrive', '//ana')
                if not os.path.exists(path):
                    missing_filecache.append(filecache)
            else:
                start, end, incr = filecache.evalParmTuple('f')
                path = filecache.evalParm('file').replace(os.sep, '/').replace('D:/SynologyDrive', '//ana')
                for frame in range(int(start), int(end) + 1, int(incr)):
                    if not os.path.exists(path.replace(str(int(hou.frame())), str(frame).zfill(3))):
                        print("Missing : " + path.replace(str(int(hou.frame())), str(frame).zfill(3)))
                        missing_filecache.append(filecache)
                        break
        for alembic in hou.nodeType(hou.nodeTypeCategories()['Sop'], 'alembic').instances():
            path = alembic.evalParm('fileName').replace(os.sep, '/').replace('D:/SynologyDrive', '//ana')
            if not os.path.exists(path):
                missing_abc.append(alembic)
        if missing_abc:
            message = "You have missing alembic file. Please check the nodes : \n"
            for abc in missing_abc:
                message += abc.path() + "\n"
            self.warning(message)
        if missing_filecache:
            message = "You have missing cache file. Please check the nodes : \n"
            for cache in missing_filecache:
                message += cache.path() + "\n"
            self.warning(message)

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
                    self.check_before(node)
                    if self.is_cancel:
                        continue
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
                    self.check_before(node)
                    if self.is_cancel:
                        continue
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
            out_dir = out_dir.replace(os.getenv('ROOT_PIPE'), config.output_server_win)
        except Exception:
            out_dir = None
        return out_dir

    def task_command(self, is_linux, frame_start, frame_end, step, file_path, workspace=""):
        node = hou.node(self.rop_node)
        cur_path = node.parm(config.output_img_path_param[node.type().name()]).rawValue()
        if self.current_project['name'] in cur_path:
            out_path = config.output_server_lin if is_linux else config.output_server_win
            out_path += '/{}'.format(self.current_project['name'])
            cur_path = out_path + cur_path.split(self.current_project['name'])[1]

        command = [
            config.batcher["houdini"]["hython"]["linux" if is_linux else "win"],
            config.batcher["houdini"]["hrender"]["linux" if is_linux else "win"],
            "%D({file_path})".format(file_path=file_path),
            "-v",
            "-e",
            "-o", cur_path,
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
