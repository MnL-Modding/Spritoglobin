# dont fucking judge me okay imma rewrite all of this later on i just wanna get this on github for now lol

overlay3 = None
overlay13 = None
overlay14 = None
overlay127 = None
overlay128 = None
overlay132 = None

BObjMap_raw = None
BObjMon_raw = None
BObjPc_raw = None
BObjUI_raw = None
EObjSave_raw = None
FObj_raw = None
FObjMap_raw = None
FObjMon_raw = None
FObjPc_raw = None
MObj_raw = None

import ndspy.rom

def import_files(path):
    rom = ndspy.rom.NintendoDSRom.fromFile(path)
    overlays = rom.loadArm9Overlays([3, 13, 14, 127, 128, 132])

    global overlay3
    global overlay13
    global overlay14
    global overlay127
    global overlay128
    global overlay132

    global BObjMap_raw
    global BObjMon_raw
    global BObjPc_raw
    global BObjUI_raw
    global EObjSave_raw
    global FObj_raw
    global FObjMap_raw
    global FObjMon_raw
    global FObjPc_raw
    global MObj_raw

    overlay3 = overlays[3].data
    overlay13 = overlays[13].data
    overlay14 = overlays[14].data
    overlay127 = overlays[127].data
    overlay128 = overlays[128].data
    overlay132 = overlays[132].data

    BObjMap_raw = rom.getFileByName('BObjMap/BObjMap.dat')
    BObjMon_raw = rom.getFileByName('BObjMon/BObjMon.dat')
    BObjPc_raw = rom.getFileByName('BObjPc/BObjPc.dat')
    BObjUI_raw = rom.getFileByName('BObjUI/BObjUI.dat')
    EObjSave_raw = rom.getFileByName('EObjSave/EObjSave.dat')
    FObj_raw = rom.getFileByName('FObj/FObj.dat')
    FObjMap_raw = rom.getFileByName('FObjMap/FObjMap.dat')
    FObjMon_raw = rom.getFileByName('FObjMon/FObjMon.dat')
    FObjPc_raw = rom.getFileByName('FObjPc/FObjPc.dat')
    MObj_raw = rom.getFileByName('MObj/MObj.dat')