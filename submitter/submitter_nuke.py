import os
import nuke
import config
from .submitter_base import Submitter
from Qt.QtWidgets import QApplication, QComboBox, QLabel

app = QApplication.instance()


def get_nuke_window():
    for widget in app.topLevelWidgets():
        if widget.metaObject().className() == 'Foundry::UI::DockMainWindow':
            return widget
    return None


class SubmitterNuke(Submitter):

    def __init__(self, parent=get_nuke_window(), sid=None):
        super(SubmitterNuke, self).__init__(parent, sid)
        self.output_node_cb = QComboBox()
        self.output_node_cb.setMinimumWidth(200)
        self.output_node_cb.setEditable(True)
        writeList = []
        for node in nuke.allNodes('Write'):
            writeList.append(node.name())
        self.output_node_cb.addItems(writeList)
        self.custom_layout.addWidget(QLabel("Output node : "))
        self.custom_layout.addWidget(self.output_node_cb)
        self.rop_node = None

    def get_path(self):
        return nuke.root()["name"].value()

    def default_frame_range(self):
        start = int(nuke.root().firstFrame())
        end = int(nuke.root().lastFrame())
        step = 1
        return (start, end, step)

    def pre_submit(self):
        path = nuke.root()["name"].value()
        nuke.scriptSave()
        self.rop_node = self.output_node_cb.currentText()
        self.submit(path, "nuke")

    def task_command(self, is_linux, frame_start, frame_end, step, file_path, workspace="", server=None):
        command = [
            config.batcher["nuke"]["render"]["linux" if is_linux else "win"],
            "-X", self.rop_node,
            "-F", "{start}-{end}x{step}".format(start=str(frame_start), end=str(frame_end), step=str(step)),
            "-remap", "{source},{target}".format(source=os.getenv("ROOT_PIPE"), target="//{}/PFE_RN_2021".format(server)),
            "%D({file_path})".format(file_path=file_path),
        ]
        return command


def run(sid=None):
    for x in get_nuke_window().children():
        if x.objectName() == "SubmitterUI":
            x.deleteLater()
    win = SubmitterNuke(sid=sid)
    win.show()


if __name__ == '__main__':

    sub = SubmitterNuke()
    sub.show()
