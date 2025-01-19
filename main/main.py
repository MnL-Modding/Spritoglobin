from ui_scripts import *
from sys import argv

# files that work so far:
# BObjMap           YES
# BObjMon           YES
# BObjPc            YES
# BObjUI            YES
# EObjSave          YES (?)
# FObj              YES
# FObjMap           YES
# FObjMon           YES
# FObjPc            YES
# MObj              YES

# groups that are fully understood:
# type 0: BObjMap               NO
# type 1: BObj (general)        NO
# type 2: BObjUI                NO
# type 3: EObjSave/FObj/MObj    NO
# palette groups                NO

# files that are fully understod:
# animation files   NO
# graphics files    YES
# palette files     YES
# palette anims     NO
# Bcollision files  NO
# Fcollision files  NO

# files to work on after all those are done:
# EObjSR
# BRfx
# FRfx
# MRfx

# files to maybe work on some day:
# BDataMap (?)
# BMap
# BMapG (?)
# EMapMic
# EMapSave
# FMapData
# MMap

app = QtWidgets.QApplication(argv)

window = MainWindow()
window.show()

window.update_sprite_group_selector()

app.exec()