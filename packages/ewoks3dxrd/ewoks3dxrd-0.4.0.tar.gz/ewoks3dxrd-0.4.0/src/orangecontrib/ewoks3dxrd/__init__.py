import sysconfig

NAME = "Ewoks 3DXRD"

DESCRIPTION = "Ewoks 3DXRD workflows"

LONG_DESCRIPTION = "Ewoks 3DXRD workflows"

ICON = "icons/3dxrd_logo.png"

BACKGROUND = "light-blue"

WIDGET_HELP_PATH = (
    # Development documentation (make htmlhelp in ./doc)
    ("{DEVELOP_ROOT}/doc/_build/htmlhelp/index.html", None),
    # Documentation included in wheel
    ("{}/help/ewoks3dxrd/index.html".format(sysconfig.get_path("data")), None),
    # Online documentation url
    ("https://ewoks3dxrd.readthedocs.io", ""),
)
