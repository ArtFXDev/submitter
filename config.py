"""
CONFIG FOR THE SUBMITTER
"""
import os
from os import path

tractor_install = "C:/Program Files/Pixar/Tractor-2.3"

if not path.exists(tractor_install):
    tractor_install = "//multifct/tools/pipeline/global/softwares/Tractor-2.3"

tractor_lib_paths = [
    "{root}/bin".format(root=tractor_install),
    "{root}/lib/python2.7".format(root=tractor_install),
    "{root}/lib/python2.7/lib".format(root=tractor_install),
    "{root}/lib/python2.7/lib/plat-win".format(root=tractor_install),
    "{root}/lib/python2.7/lib/lib-tk".format(root=tractor_install),
    "{root}/lib/python2.7/lib/site-packages".format(root=tractor_install),
    "{root}/lib/python2.7/lib/site-packages/setuptools-0.6c11-py2.7.egg".format(root=tractor_install),
    "{root}/lib/python2.7/DLLs".format(root=tractor_install),
    "{root}/lib/python2.7/DLLs/python27.zip".format(root=tractor_install),
]

ui_path = path.join(path.dirname(__file__), "submitter", "qt", "submitter.ui")

rams = ["All ram", "ram_32", "ram_lower"]

pools = ["rackLinux", "mk12", "mk11", "mk10", "mk9", "mk8", "mk7", "mk6_and_lower", "windows10", "td"]

houdini_envs = ['JOB', 'WIPCACHE', 'PUBCACHE', 'ASSET', 'SHOT', 'PROJECT', 'IMAGES_OUT']

batcher = {
    "maya": {
        "render": {
            "win": "C:/Maya2019/bin/Render.exe",
            "linux": "/usr/autodesk/maya/bin/Render",
        },
        "batch": {
            "win": "C:/Maya2019/bin/mayabatch.exe",
            "linux": "/usr/autodesk/maya/bin/mayabatch",
        },
        "cleanup": {
            "win": ["Render.exe", "mayabatch.exe"],
            "linux": ["Render", "mayabatch"],
        }
    },
    "houdini": {
        "hython": {
            "win": "C:/Houdini18/bin/hython.exe",
            "linux": "/opt/hfs18.0/bin/hython",
        },
        "hrender": {
            "win": path.join(path.dirname(__file__), "hrender.py").replace(os.sep, '/'),
            "linux": path.join(path.dirname(__file__), "hrender.py").replace(os.sep, '/'),  # "/opt/hfs18.0/bin/hrender.py"
        },
        "cleanup": {
            "win": ["hython.exe"],
            "linux": ["hython"],
        }
    },
    "nuke": {
        "render": {
            "win": "C:/Nuke12.2v2/Nuke12.2.exe",
            "linux": "/usr/nuke/bin/Render",
        },
        "cleanup": {
            "win": "Nuke12.2.exe",
            "linux": "Render",
        }
    },
}

projects = [
    # # # # ANA # # # #
    {
        "name": "TEST_PIPE",
        "server": 'ana',
        "short_name": "test pipe",
        "totalFrames": 1000
    },
    {
        "name": "HAKAM",
        "server": 'ana',
        "short_name": "hakam",
        "totalFrames": 1000
    },
    {
        "name": "DIVE",
        "server": 'ana',
        "short_name": "dive",
        "totalFrames": 2405
    },
    {
        "name": "GREEN",
        "server": 'ana',
        "short_name": "green",
        "totalFrames": 1000
    },
    {
        "name": "BARNEY",
        "server": 'ana',
        "short_name": "barney",
        "totalFrames": 1000
    },
    {
        "name": "PIR_HEARTH",
        "server": 'ana',
        "short_name": "pirhearth",
        "totalFrames": 7003
    },
    {
        "name": "GOOD_MORNING_KITTY",
        "server": 'ana',
        "short_name": "kitty",
        "totalFrames": 1000
    },
    # # # # TARS # # # #
    {
        "name": "RELATIVITY",
        "server": 'tars',
        "short_name": "relativity",
        "totalFrames": 10075
    },
    {
        "name": "HOSTILE",
        "server": 'tars',
        "short_name": "hostile",
        "totalFrames": 1000
    },
    {
        "name": "DREAMBLOWER",
        "server": 'tars',
        "short_name": "dreamblower",
        "totalFrames": 1000
    },
    {
        "name": "BACKSTAGE",
        "server": 'tars',
        "short_name": "backstage",
        "totalFrames": 1000
    },
    {
        "name": "COCORICA",
        "server": 'tars',
        "short_name": "cocorica",
        "totalFrames": 1000
    },
    {
        "name": "FROM_ABOVE",
        "server": 'tars',
        "short_name": "from above",
        "totalFrames": 9345
    },
]
