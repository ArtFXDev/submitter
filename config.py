"""
CONFIG FOR THE SUBMITTER
"""
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

pools = ["rackLinux", "cpu", "gpu", "p_td", "p_xavier"]

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
            "win": "C:/Houdini18/bin/hrender.py",
            "linux": "/opt/hfs18.0/bin/hrender.py",
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
        "short_name": "test pipe"
    },
    {
        "name": "HAKAM",
        "server": 'ana',
        "short_name": "hakam"
    },
    {
        "name": "DIVE",
        "server": 'ana',
        "short_name": "dive"
    },
    {
        "name": "GREEN",
        "server": 'ana',
        "short_name": "green"
    },
    {
        "name": "BARNEY",
        "server": 'ana',
        "short_name": "barney"
    },
    {
        "name": "PIR_HEARTH",
        "server": 'ana',
        "short_name": "pirhearth"
    },
    {
        "name": "GOOD_MORNING_KITTY",
        "server": 'ana',
        "short_name": "kitty"
    },
    # # # # TARS # # # #
    {
        "name": "RELATIVITY",
        "server": 'tars',
        "short_name": "relativity"
    },
    {
        "name": "HOSTILE",
        "server": 'tars',
        "short_name": "hostile"
    },
    {
        "name": "DREAMBLOWER",
        "server": 'tars',
        "short_name": "dreamblower"
    },
    {
        "name": "BACKSTAGE",
        "server": 'tars',
        "short_name": "backstage"
    },
    {
        "name": "COCORICA",
        "server": 'tars',
        "short_name": "cocorica"
    },
    {
        "name": "FROM_ABOVE",
        "server": 'tars',
        "short_name": "from above"
    },
]
