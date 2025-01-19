import io
import mnllib

from data_scripts import *
import import_files

class SpriteGroup: # not fully understood
    def __init__(self, input_data, sprite_type):
        self.sprite_type = sprite_type
        match (self.sprite_type):
            case 0:
                self.unk0 = [0]
                self.animation_file, self.graphics_file, self.palette_group, self.unk0[0] = struct.unpack('<4H', input_data)
                self.has_collision = False
            case 1:
                self.unk0 = [0,0,0,0,0,0,0,0,0]
                self.animation_file, self.graphics_file, self.palette_group, self.unk0[0], self.collision_file, self.unk0[1],self.unk0[2],self.unk0[3],self.unk0[4],self.unk0[5],self.unk0[6],self.unk0[7] = struct.unpack('<12H', input_data)
                self.has_collision = self.collision_file != 0xFFFF
            case 2:
                self.unk0 = [0,0]
                self.animation_file, self.graphics_file, self.palette_group, self.unk0[0],self.unk0[1] = struct.unpack('<5H', input_data)
                self.has_collision = False
            case 3:
                self.unk0 = [0]
                self.animation_file, self.graphics_file, self.palette_group, self.collision_file, self.unk0[0] = struct.unpack('<5H', input_data)
                self.has_collision = self.collision_file != 0xFFFF

    def __str__(self):
        if (self.has_collision):
            collision = f"| collision file: {hex(self.collision_file)} "
        else:
            collision = ""

        unk0 = ""
        for i in self.unk0:
            unk0 += f"{hex(i)} "

        return f"animation file: {hex(self.animation_file)} | graphics file: {hex(self.graphics_file)} | palette group: {hex(self.palette_group)} {collision}| unknown : {unk0}"

class PaletteGroup:
    def __init__(self, input_data):
        self.palette_file, self.palette_anim_file = struct.unpack('<HH', input_data)
        self.has_anim = self.palette_anim_file != 0xFFFF
    
    def __str__(self):
        return f"palette file: {hex(self.palette_file)} | animation file: {hex(self.palette_anim_file)} (has animation = {self.has_anim})"

class AnimHeader: # not fully understood
    def __init__(self, input_data):
        # grab data from static header
        self.extra_table_amt, self.animation_amt, self.settings_byte, self.animations_table, self.parts_table, self.affine_table, self.end_of_indexing = struct.unpack_from('<3Bx4I', buffer = input_data)

        # grab data from settings byte
        self.swizzle_flag = (self.settings_byte >> 3) & 1 == 0
        self.unk0 = (self.settings_byte >> 2) & 1 != 0
        self.sprite_mode = self.settings_byte & 3

        # grab extra table data
        self.extra_tables = []
        for i in range(self.extra_table_amt):
            table_data = bytearray()
            for j in range(8):
                table_data.append(input_data[0x14 + (i * 8) + j])
            self.extra_tables.append(AnimSubHeader(table_data))
        
    def __str__(self):
        self.headerInfo = f"animations: {self.animation_amt} | sprite mode: {self.sprite_mode} | swizzle: {self.swizzle_flag} | tables: animations data offset = {self.animations_table}, parts data offset = {self.parts_table}, affine data offset = {self.affine_table}, end of indexed data = {self.end_of_indexing} | unknown: {self.unk0} | EXTRA TABLES!!"
        return self.headerInfo

class AnimSubHeader: # not fully understood
    def __init__(self, input_data):
        self.data0, self.tex_shift, self.data1, self.data_offset = struct.unpack('<2BHI', input_data)
        self.is_graphics_offset = self.data0 == 0
        self.tex_size = self.data1 << self.tex_shift
        
        # if (self.is_graphics_offset): print(f"graphics offset: {hex(self.tex_shift)} {hex(self.tex_size)}")

class Animation:
    def __init__(self, input_data):
        self.frame_list_offset, self.frame_amt = struct.unpack('<H2xH2x', input_data)
        self.frame_list = []
    
    def __str__(self):
        return f"frame data: list start = {self.frame_list_offset}, amt = {self.frame_amt}"

class AnimFrame:
    def __init__(self, input_data):
        self.part_list_offset, self.part_amt, self.frame_timer, self.frame_affine_offset = struct.unpack('<HxB2H', input_data)

        self.rot_scale_flag = self.frame_affine_offset != 0
        self.collision_group = None
        self.collision_group_ext = None
    
    def __str__(self):
        return f"part data: list start = {self.part_list_offset}, amt = {self.part_amt} | animation timer: {self.frame_timer} | frame affine offset: {self.frame_affine_offset}"

    def set_index(self, index):
        self.sprite_index = index

class Sprite:
    def __init__(self, part_list):
        self.part_list = part_list

class SpritePart: # not fully understood
    def __init__(self, input_data):
        # grab data from the four settings bytes
        # 11100011 11111111 11111111 01100000
        
        self.obj_shape = input_data[0] >> 6
        self.pixel_mode = (input_data[0] >> 5) & 1
        self.unk0 = (input_data[0] >> 2) & 1
        self.rot_scale_flag = input_data[0] & 1

        self.obj_size = (input_data[1] >> 2) & 3
        self.unk1 = (input_data[1] >> 4) & 3
        self.pal_shift_0 = input_data[1] >> 6
        self.x_flip = input_data[1] & 1 != 0
        self.y_flip = input_data[1] & 2 != 0

        self.pal_shift_1 = input_data[2] & 3
        self.part_affine_offset = input_data[2] >> 2

        self.unk2 = (input_data[3] >> 5) & 3

        # self.flag0 = (self.obj_shape << 6) + (self.pixel_mode << 5) + (int(self.unk0) << 2) + self.rot_scale_flag
        # self.flag1 = (self.obj_size << 2) + (self.unk1 << 4) + (self.pal_shift_0 << 6) + int(self.x_flip) + (int(self.y_flip) << 1)
        # self.flag2 = self.pal_shift_1 + (self.part_affine_offset << 2)
        # self.flag3 = self.unk2 << 5
        # self.input_data = input_data

        # grab offset data from the four position bytes
        self.x_offset, self.y_offset = struct.unpack_from('<2h', buffer = input_data, offset = 4)

        self.extra_data = []
    
    def __str__(self):
        return f"size: X = {self.x_size}, Y = {self.y_size} | offset: X = {self.x_offset}, Y = {self.y_offset} | flip: X = {self.x_flip}, Y = {self.y_flip} | palette shift: {self.pal_shift} | pixel mode: {self.pixel_mode} | rotation/scaling flag: {self.rot_scale_flag} | unknown: {self.unk0}"

    def set_index(self, index):
        self.tile_index = index

class Tile:
    SIZING_TABLE = [[(8, 8), (16, 16), (32, 32), (64, 64)], [(16, 8), (32, 8), (32, 16), (64, 32)], [(8, 16), (8, 32), (16, 32), (32, 64)]]

    def __init__(self, data):
        self.data = data
        self.pal_shift = data[2]
        self.x_size, self.y_size = self.SIZING_TABLE[data[0]][data[1]]
        self.graphics_offset = data[3]

class PaletteAnimationData: # not fully understood
    class Header: # not fully understood
        def __init__(self, input_data):
            self.input_data = []
            for i in input_data:
                self.input_data.append(hex(i))
            data_size_0 = 1 + (input_data[1] >> 9)
            data_size_1 = 2 + ((input_data[1] >> 6) & 0b111)

            self.header_data = []
            for i in range(data_size_0):
                data = []
                for j in range(data_size_1):
                    data.append(input_data[2 + (j * (1 + data_size_0)) + i])
                self.header_data.append(data)
    
    class Anim: # not fully understood
        def __init__(self, input_data):
            self.input_data = []
            for i in input_data:
                self.input_data.append(hex(i))

            self.anim_data = []
            anchor = 1
            while (anchor < len(input_data)):
                #print(anchor)
                data_group = []
                data_size_0 = 1 + (input_data[anchor] >> 9)
                data_size_1 = 2 + ((input_data[anchor] >> 6) & 0b111)
                for i in range(data_size_0):
                    data = []
                    for j in range(data_size_1):
                        index_to_append = 1 + anchor + (j * (1 + data_size_0)) + i
                        data.append(input_data[index_to_append])
                    if (data_size_0 > 1):
                        data_group.append(data)
                    else:
                        self.anim_data.append(data)
                anchor = index_to_append + 1
                if (data_size_0 > 1):
                    self.anim_data.append(data_group)

    def __init__(self, input_data):
        input_data = io.BytesIO(input_data)

        pointer_list = [int.from_bytes(input_data.read(2), "little", signed = True)]
        for i in range(pointer_list[0] - 1):
            pointer_list.append(int.from_bytes(input_data.read(2), "little", signed = True))
        
        buffer = []
        for j in range(pointer_list[1] - pointer_list[0]):
            buffer.append(int.from_bytes(input_data.read(2), "little", signed = True))

        self.header = self.Header(buffer)

        self.anim_list = []
        for i in range(len(pointer_list) - 1)[1:]:
            input_data.seek(pointer_list[i] * 2)
            buffer = []
            for j in range(pointer_list[i + 1] - pointer_list[i]):
                buffer.append(int.from_bytes(input_data.read(2), "little", signed = True))
            self.anim_list.append(self.Anim(buffer))
        unk0 = bytearray(input_data.read())
        
        #print(self.header.input_data)
        count = 0
        for i in self.anim_list:
            count += 1
            #print(i.input_data)
        #print(f"header: {self.header.header_data}")
        count = 0
        for i in self.anim_list:
            count += 1
            #print(f"anim {count}: {i.anim_data}")
        #print(f"end padding(?): {unk0}")

class CollisionData: # not fully understood
    class BHeader: # not fully understood
        def __init__(self, input_data):
            data_size_0 = 1 + (input_data[1] >> 9)
            data_size_1 = 2 + ((input_data[1] >> 6) & 0b111)

            self.header_data = []
            for i in range(data_size_0):
                data = []
                for j in range(data_size_1):
                    data.append(input_data[2 + (j * (1 + data_size_0)) + i])
                self.header_data.append(data)

    class BCollisionBoxGroup:
        def __init__(self, input_data):
            data_size_0 = 1 + (input_data[1] >> 9)
            data_size_1 = 2 + ((input_data[1] >> 6) & 0b111)

            self.box_data = []
            for i in range(data_size_0):
                box = []
                for j in range(data_size_1):
                    box.append(input_data[2 + (j * (1 + data_size_0)) + i])
                self.box_data.append(box)
            
            #print(self.box_data)
    
    class FHeader: # not fully understood
        def __init__(self, input_data):
            data_stream = io.BytesIO(input_data)
            data_stream.seek(0)
            data_amt = int.from_bytes(data_stream.read(1), "little")

            self.header_data = []
            for i in range(data_amt):
                self.header_data.append(struct.unpack('6B', data_stream.read(6)))

    class FCollisionBoxGroup:
        def __init__(self, input_data, data_size_1):
            data_size_0 = input_data[0]

            #print(input_data)

            self.box_data = []
            for i in range(data_size_0):
                box = []
                for j in range(data_size_1):
                    box.append(input_data[1 + (i * data_size_1) + j])
                self.box_data.append(box)
            
            #print(self.box_data)

    def __init__(self, input_data, collision_type):
        input_data = io.BytesIO(input_data)

        match collision_type:
            case 0: #BCollision
                pointer_list = [int.from_bytes(input_data.read(2), "little", signed = True)]
                for i in range(pointer_list[0] - 1):
                    pointer_list.append(int.from_bytes(input_data.read(2), "little", signed = True))

                buffer = []
                for j in range(pointer_list[1] - pointer_list[0]):
                    buffer.append(int.from_bytes(input_data.read(2), "little", signed = True))

                self.header = self.BHeader(buffer)

                self.box_group_list = []
                for i in range(len(pointer_list) - 1)[1:]:
                    input_data.seek(pointer_list[i] * 2)
                    buffer = []
                    for j in range(pointer_list[i + 1] - pointer_list[i]):
                        buffer.append(int.from_bytes(input_data.read(2), "little", signed = True))
                    self.box_group_list.append(self.BCollisionBoxGroup(buffer))
                unk0 = bytearray(input_data.read())
            case 1: #FCollision
                #print(binascii.hexlify(input_data.read()))
                input_data.seek(0)

                pointer_list = [int.from_bytes(input_data.read(2), "little", signed = True)]
                for i in range((pointer_list[0] // 2) - 1):
                    pointer_list.append(int.from_bytes(input_data.read(2), "little", signed = True))
    
                self.box_group_list = []
                for i in range(len(pointer_list) - 1):
                    if i < 3: data_size = 5
                    else: data_size = 4
                    input_data.seek(pointer_list[i])
                    buffer = []
                    for j in range(pointer_list[i + 1] - pointer_list[i]):
                        j_mod = (j - 1) % 5
                        no_sign = (data_size == 5) and (j_mod == 2 or j_mod == 4)
                        #print(no_sign)
                        buffer.append(int.from_bytes(input_data.read(1), "little", signed = not no_sign))
                    self.box_group_list.append(self.FCollisionBoxGroup(buffer, data_size))

                self.header = self.FHeader(input_data.read())

                #print(f"header: {self.header.header_data}")
                #count = 0
                #for i in self.box_group_list:
                #    count += 1
                #    print(f"box group {count}: {i.box_data}")
        




class AnimationData:
    OVERLAY14_OFFSET_BObjMap_FILEDATA =   0x0000859C
    OVERLAY13_OFFSET_BObjMap_TEXDATA =    0x0000632C
    OVERLAY13_OFFSET_BObjMap_PALDATA =    0x000061F8
    BObjMap_SPRITE_GROUP_AMT =                 0x026

    OVERLAY14_OFFSET_BObjMon_FILEDATA =   0x00009C18
    OVERLAY13_OFFSET_BObjMon_TEXDATA =    0x000084D8
    OVERLAY13_OFFSET_BObjMon_PALDATA =    0x00006610
    BObjMon_SPRITE_GROUP_AMT =                 0x151
    
    OVERLAY14_OFFSET_BObjPc_FILEDATA =    0x00008C1C
    OVERLAY13_OFFSET_BObjPc_TEXDATA =     0x00007548
    OVERLAY13_OFFSET_BObjPc_PALDATA =     0x00006290
    BObjPc_SPRITE_GROUP_AMT =                  0x0A6

    OVERLAY14_OFFSET_BObjUI_FILEDATA =    0x000091C0
    OVERLAY13_OFFSET_BObjUI_TEXDATA =     0x000069D4
    OVERLAY13_OFFSET_BObjUI_PALDATA =     0x0000645C
    BObjUI_SPRITE_GROUP_AMT =                  0x125

    OVERLAY128_OFFSET_EObjSave_FILEDATA = 0x000056A4
    OVERLAY127_OFFSET_EObjSave_TEXDATA =  0x00003518 # likely correct
    OVERLAY127_OFFSET_EObjSave_PALDATA =  0x000032A4 # probably correct
    EObjSave_SPRITE_GROUP_AMT =                 0x36 # likely correct

    OVERLAY3_OFFSET_FObj_FILEDATA =       0x0000E8A0
    OVERLAY3_OFFSET_FObj_TEXDATA =        0x000165E4
    OVERLAY3_OFFSET_FObj_PALDATA =        0x000150C8
    FObj_SPRITE_GROUP_AMT =                    0x3A7

    OVERLAY3_OFFSET_FObjMap_FILEDATA =    0x0000B88C
    OVERLAY3_OFFSET_FObjMap_TEXDATA =     0x00014884
    OVERLAY3_OFFSET_FObjMap_PALDATA =     0x00014880
    FObjMap_SPRITE_GROUP_AMT =                 0x001

    OVERLAY3_OFFSET_FObjMon_FILEDATA =    0x0000BA3C
    OVERLAY3_OFFSET_FObjMon_TEXDATA =     0x00014A74
    OVERLAY3_OFFSET_FObjMon_PALDATA =     0x00014CCC
    FObjMon_SPRITE_GROUP_AMT =                 0x03C

    OVERLAY3_OFFSET_FObjPc_FILEDATA =     0x0000BDB0
    OVERLAY3_OFFSET_FObjPc_TEXDATA =      0x00015854
    OVERLAY3_OFFSET_FObjPc_PALDATA =      0x000148D4
    FObjPc_SPRITE_GROUP_AMT =                  0x15B

    OVERLAY132_OFFSET_MObj_FILEDATA =     0x000020EC
    OVERLAY132_OFFSET_MObj_TEXDATA =      0x00002E94
    OVERLAY132_OFFSET_MObj_PALDATA =      0x00002C80
    MObj_SPRITE_GROUP_AMT =                    0x10C

    def __init__(self, current_file, current_sprite):
        self.current_file = current_file
        self.current_sprite = current_sprite
        match (self.current_file):
            case "BObjMap":
                self.filedata = self.OVERLAY14_OFFSET_BObjMap_FILEDATA
                self.texdata = self.OVERLAY13_OFFSET_BObjMap_TEXDATA
                self.paldata = self.OVERLAY13_OFFSET_BObjMap_PALDATA
                self.all_sprites = self.BObjMap_SPRITE_GROUP_AMT
                self.sprite_group_interval = 8
                self.sprite_type = 0

                self.overlay_file_offsets = io.BytesIO(import_files.overlay14)
                self.overlay_group_data = io.BytesIO(import_files.overlay13)
                self.file_in = io.BytesIO(import_files.BObjMap_raw)

            case "BObjMon":
                self.filedata = self.OVERLAY14_OFFSET_BObjMon_FILEDATA
                self.texdata = self.OVERLAY13_OFFSET_BObjMon_TEXDATA
                self.paldata = self.OVERLAY13_OFFSET_BObjMon_PALDATA
                self.all_sprites = self.BObjMon_SPRITE_GROUP_AMT
                self.sprite_group_interval = 24
                self.sprite_type = 1

                self.overlay_file_offsets = io.BytesIO(import_files.overlay14)
                self.overlay_group_data = io.BytesIO(import_files.overlay13)
                self.file_in = io.BytesIO(import_files.BObjMon_raw)

            case "BObjPc":
                self.filedata = self.OVERLAY14_OFFSET_BObjPc_FILEDATA
                self.texdata = self.OVERLAY13_OFFSET_BObjPc_TEXDATA
                self.paldata = self.OVERLAY13_OFFSET_BObjPc_PALDATA
                self.all_sprites = self.BObjPc_SPRITE_GROUP_AMT
                self.sprite_group_interval = 24
                self.sprite_type = 1

                self.overlay_file_offsets = io.BytesIO(import_files.overlay14)
                self.overlay_group_data = io.BytesIO(import_files.overlay13)
                self.file_in = io.BytesIO(import_files.BObjPc_raw)
            
            case "BObjUI":
                self.filedata = self.OVERLAY14_OFFSET_BObjUI_FILEDATA
                self.texdata = self.OVERLAY13_OFFSET_BObjUI_TEXDATA
                self.paldata = self.OVERLAY13_OFFSET_BObjUI_PALDATA
                self.all_sprites = self.BObjUI_SPRITE_GROUP_AMT
                self.sprite_group_interval = 10
                self.sprite_type = 2

                self.overlay_file_offsets = io.BytesIO(import_files.overlay14)
                self.overlay_group_data = io.BytesIO(import_files.overlay13)
                self.file_in = io.BytesIO(import_files.BObjUI_raw)
            
            case "EObjSave":
                self.filedata = self.OVERLAY128_OFFSET_EObjSave_FILEDATA
                self.texdata = self.OVERLAY127_OFFSET_EObjSave_TEXDATA
                self.paldata = self.OVERLAY127_OFFSET_EObjSave_PALDATA
                self.all_sprites = self.EObjSave_SPRITE_GROUP_AMT
                self.sprite_group_interval = 10
                self.sprite_type = 3

                self.overlay_file_offsets = io.BytesIO(import_files.overlay128)
                self.overlay_group_data = io.BytesIO(import_files.overlay127)
                self.file_in = io.BytesIO(import_files.EObjSave_raw)

            case "FObj":
                self.filedata = self.OVERLAY3_OFFSET_FObj_FILEDATA
                self.texdata = self.OVERLAY3_OFFSET_FObj_TEXDATA
                self.paldata = self.OVERLAY3_OFFSET_FObj_PALDATA
                self.all_sprites = self.FObj_SPRITE_GROUP_AMT
                self.sprite_group_interval = 10
                self.sprite_type = 3

                self.overlay_file_offsets = io.BytesIO(import_files.overlay3)
                self.overlay_group_data = self.overlay_file_offsets
                self.file_in = io.BytesIO(import_files.FObj_raw)

            case "FObjMap":
                self.filedata = self.OVERLAY3_OFFSET_FObjMap_FILEDATA
                self.texdata = self.OVERLAY3_OFFSET_FObjMap_TEXDATA
                self.paldata = self.OVERLAY3_OFFSET_FObjMap_PALDATA
                self.all_sprites = self.FObjMap_SPRITE_GROUP_AMT
                self.sprite_group_interval = 10
                self.sprite_type = 3

                self.overlay_file_offsets = io.BytesIO(import_files.overlay3)
                self.overlay_group_data = self.overlay_file_offsets
                self.file_in = io.BytesIO(import_files.FObjMap_raw)

            case "FObjMon":
                self.filedata = self.OVERLAY3_OFFSET_FObjMon_FILEDATA
                self.texdata = self.OVERLAY3_OFFSET_FObjMon_TEXDATA
                self.paldata = self.OVERLAY3_OFFSET_FObjMon_PALDATA
                self.all_sprites = self.FObjMon_SPRITE_GROUP_AMT
                self.sprite_group_interval = 10
                self.sprite_type = 3

                self.overlay_file_offsets = io.BytesIO(import_files.overlay3)
                self.overlay_group_data = self.overlay_file_offsets
                self.file_in = io.BytesIO(import_files.FObjMon_raw)

            case "FObjPc":
                self.filedata = self.OVERLAY3_OFFSET_FObjPc_FILEDATA
                self.texdata = self.OVERLAY3_OFFSET_FObjPc_TEXDATA
                self.paldata = self.OVERLAY3_OFFSET_FObjPc_PALDATA
                self.all_sprites = self.FObjPc_SPRITE_GROUP_AMT
                self.sprite_group_interval = 10
                self.sprite_type = 3

                self.overlay_file_offsets = io.BytesIO(import_files.overlay3)
                self.overlay_group_data = self.overlay_file_offsets
                self.file_in = io.BytesIO(import_files.FObjPc_raw)
            
            case "MObj":
                self.filedata = self.OVERLAY132_OFFSET_MObj_FILEDATA
                self.texdata = self.OVERLAY132_OFFSET_MObj_TEXDATA
                self.paldata = self.OVERLAY132_OFFSET_MObj_PALDATA
                self.all_sprites = self.MObj_SPRITE_GROUP_AMT
                self.sprite_group_interval = 10
                self.sprite_type = 3

                self.overlay_file_offsets = io.BytesIO(import_files.overlay132)
                self.overlay_group_data = self.overlay_file_offsets
                self.file_in = io.BytesIO(import_files.MObj_raw)

        self.overlay_group_data.seek(self.texdata + (self.current_sprite * self.sprite_group_interval))
        self.sprite_group_data = SpriteGroup(bytearray(self.overlay_group_data.read(self.sprite_group_interval)), self.sprite_type)

        self.overlay_group_data.seek(self.paldata + (self.sprite_group_data.palette_group * 4))
        self.palette_group_data = PaletteGroup(bytearray(self.overlay_group_data.read(4)))

        # print(self.sprite_group_data)
        # print(self.palette_group_data)

    def generate_anim_data(self):
        # save the current animation file
        self.current_anim = io.BytesIO()
        self.overlay_file_offsets.seek(self.filedata + 4 + (self.sprite_group_data.animation_file * 4))
        animation_file_offset = int.from_bytes(self.overlay_file_offsets.read(4), "little")
        self.file_in.seek(animation_file_offset)
        self.current_anim.write(mnllib.decompress(self.file_in))

        # save the current graphics file
        tex_buffer = io.BytesIO()
        self.overlay_file_offsets.seek(self.filedata + 4 + (self.sprite_group_data.graphics_file * 4))
        graphics_file_offset = int.from_bytes(self.overlay_file_offsets.read(4), "little")
        self.file_in.seek(graphics_file_offset)
        tex_buffer.write(mnllib.decompress(self.file_in))
        tex_buffer.seek(0)
        tex_size = int.from_bytes(tex_buffer.read(4), "little")
        self.current_tex = io.BytesIO()
        self.current_tex.write(tex_buffer.read(tex_size))

        # save the current palette
        self.current_pal = []
        self.overlay_file_offsets.seek(self.filedata + 4 + (self.palette_group_data.palette_file * 4))
        palette_file_offset = int.from_bytes(self.overlay_file_offsets.read(4), "little")
        self.file_in.seek(palette_file_offset)
        self.palette_size = int.from_bytes(self.file_in.read(4), "little")
        for i in range(self.palette_size // 2):
            self.current_pal.append(define_palette_color(self.file_in))

        # save the palette animation file, if it exists
        self.current_pal_anim = None
        if (self.palette_group_data.has_anim):
            self.overlay_file_offsets.seek(self.filedata + 4 + (self.palette_group_data.palette_anim_file * 4))
            palette_anim_file_offset = int.from_bytes(self.overlay_file_offsets.read(4), "little")
            self.file_in.seek(palette_anim_file_offset)
            palette_anim_size = int.from_bytes(self.overlay_file_offsets.read(4), "little") - palette_anim_file_offset
            self.current_pal_anim = PaletteAnimationData(self.file_in.read(palette_anim_size))
            # print(hex(palette_anim_file_offset))
            # print(hex(palette_anim_file_offset + palette_anim_size))

        # save the collision file, if it exists
        self.current_collision = None
        if (self.sprite_group_data.has_collision):
            if (self.sprite_group_data.sprite_type == 1): # BObj
                self.collision_type = 0
                self.overlay_file_offsets.seek(self.filedata + 4 + (self.sprite_group_data.collision_file * 4))
                collision_file_offset = int.from_bytes(self.overlay_file_offsets.read(4), "little")
                self.file_in.seek(collision_file_offset)
                collision_size = int.from_bytes(self.overlay_file_offsets.read(4), "little") - collision_file_offset
                self.current_collision = CollisionData(self.file_in.read(collision_size), 0)
            else: # FObj
                self.collision_type = 1
                self.overlay_file_offsets.seek(self.filedata + 4 + (self.sprite_group_data.collision_file * 4))
                collision_file_offset = int.from_bytes(self.overlay_file_offsets.read(4), "little")
                self.file_in.seek(collision_file_offset)
                collision_size = int.from_bytes(self.overlay_file_offsets.read(4), "little") - collision_file_offset
                self.current_collision = CollisionData(self.file_in.read(collision_size), 1)

        # interpret the header
        self.current_anim.seek(0)
        headerLength = 0x14 + (int.from_bytes(self.current_anim.read(1)) * 8)
        self.current_anim.seek(0)
        self.header = AnimHeader(bytearray(self.current_anim.read(headerLength)))

        # create a list of animations
        self.all_anims = []
        for i in range(self.header.animation_amt):
            self.current_anim.seek(self.header.animations_table + (i * 8))
            current_animation = Animation(bytearray(self.current_anim.read(8)))
            for j in range(current_animation.frame_amt):
                self.current_anim.seek(current_animation.frame_list_offset + (j * 8))
                current_frame = AnimFrame(bytearray(self.current_anim.read(8)))
                if (current_frame.rot_scale_flag):
                    self.current_anim.seek(self.header.affine_table + (current_frame.frame_affine_offset - 1) * 12)
                    current_frame.matrix = interpret_matrix(bytearray(self.current_anim.read(12)), 0)
                else:
                    current_frame.matrix = [1, 0, 0, 0, 1, 0]
                current_frame.collision_group = None
                current_animation.frame_list.append(current_frame)
            self.all_anims.append(current_animation)
        
        # add collision data to animations and frames
        if (self.sprite_group_data.has_collision):
            match self.collision_type:
                case 0: #BCollision
                    for current_collision_data in self.current_collision.header.header_data:
                        if (current_collision_data[0] == 0):
                            if (current_collision_data[1] == -1): # apply to all anims
                                for current_anim in self.all_anims:
                                    for current_frame in current_anim.frame_list:
                                        if (not current_frame.collision_group):
                                            current_frame.collision_group = self.current_collision.box_group_list[current_collision_data[3] - 1].box_data
                            else:
                                if (current_collision_data[2] == -1): # apply to all frames
                                    for current_frame in self.all_anims[current_collision_data[1]].frame_list:
                                        current_frame.collision_group = self.current_collision.box_group_list[current_collision_data[3] - 1].box_data
                                else:
                                    current_frame = self.all_anims[current_collision_data[1]].frame_list[current_collision_data[2]]
                                    current_frame.collision_group = self.current_collision.box_group_list[current_collision_data[3] - 1].box_data
                        else:
                            if (current_collision_data[1] == -1): # apply to all anims
                                for current_anim in self.all_anims:
                                    for current_frame in current_anim.frame_list:
                                        if (not current_frame.collision_group_ext):
                                            current_frame.collision_group_ext = self.current_collision.box_group_list[current_collision_data[3] - 1].box_data
                            else:
                                if (current_collision_data[2] == -1): # apply to all frames
                                    for current_frame in self.all_anims[current_collision_data[1]].frame_list:
                                        current_frame.collision_group_ext = self.current_collision.box_group_list[current_collision_data[3] - 1].box_data
                                else:
                                    current_frame = self.all_anims[current_collision_data[1]].frame_list[current_collision_data[2]]
                                    current_frame.collision_group_ext = self.current_collision.box_group_list[current_collision_data[3] - 1].box_data
                case 1: #FCollision
                    current_collision_data = self.current_collision.header.header_data
                    for i in range(len(self.all_anims)):
                        current_anim = self.all_anims[i]
                        for current_frame in current_anim.frame_list:
                            try:
                                current_collision_data[i]
                            except:
                                ...
                            else:
                                current_frame.collision_group = []
                                current_frame.collision_group_ext = []
                                for j in range(3):
                                    if current_collision_data[i][j] != 255:
                                        current_frame.collision_group.append(self.current_collision.box_group_list[j].box_data[current_collision_data[i][j]],)
                                for j in range(2):
                                    if current_collision_data[i][j + 3] != 255:
                                        current_frame.collision_group_ext.append(self.current_collision.box_group_list[j].box_data[current_collision_data[i][j + 3]],)

        # create a list of sprite parts
        self.all_parts = []
        for i in range((self.header.extra_tables[0].data_offset - self.header.parts_table) // 8):
            self.current_anim.seek(self.header.parts_table + (i * 8))
            current_sprite_part = SpritePart(bytearray(self.current_anim.read(8)))
            for j in range(self.header.extra_table_amt):
                self.current_anim.seek(self.header.extra_tables[j].data_offset + (i * 2))
                current_sprite_part.extra_data.append(int.from_bytes(self.current_anim.read(2), "little"))
            if (current_sprite_part.rot_scale_flag):
                self.current_anim.seek(self.header.affine_table + (current_sprite_part.part_affine_offset) * 8)
                current_sprite_part.matrix = interpret_matrix(bytearray(self.current_anim.read(8)), 1)
            else:
                current_sprite_part.matrix = [1, 0, 0, 0, 1, 0]
            self.all_parts.append(current_sprite_part)
        
        # create a list of sprites
        self.all_sprites = []
        for current_anim in self.all_anims:
            for current_frame in current_anim.frame_list:
                part_list = []
                for k in range(current_frame.part_amt):
                    current_sprite_part = self.all_parts[current_frame.part_list_offset + k]
                    part_list.append(current_sprite_part)
                current_sprite = Sprite(part_list)

                sprite_already_exists = False
                for i in range(len(self.all_sprites)):
                    sprite = self.all_sprites[i]
                    if sprite.part_list == current_sprite.part_list:
                        sprite_already_exists = True
                        current_frame.set_index(i)
                if (sprite_already_exists == False):
                    self.all_sprites.append(current_sprite)
                    current_frame.set_index(len(self.all_sprites) - 1)

        # index tile data
        self.all_tiles = []
        for current_part in self.all_parts:
            tile_already_exists = False
            tile_data = current_part.obj_shape, current_part.obj_size, (0x10 * current_part.pal_shift_0) + (0x40 * current_part.pal_shift_1), current_part.extra_data[0] << (self.header.extra_tables[0].tex_shift)
            for i in range(len(self.all_tiles)):
                if (self.all_tiles[i].data == tile_data):
                    tile_already_exists = True
                    current_part.set_index(i)
                    break
            if (tile_already_exists == False):
                new_tile = Tile(tile_data)
                self.current_tex.seek(tile_data[3])
                graphics_buffer_size = new_tile.x_size * new_tile.y_size
                if (self.header.sprite_mode == 3): graphics_buffer_size = graphics_buffer_size // 2
                graphics_buffer = self.current_tex.read(graphics_buffer_size)
                new_tile.cached_tile = create_sprite_part(graphics_buffer, self.current_pal, new_tile.x_size, new_tile.y_size, self.header.sprite_mode, new_tile.pal_shift, self.header.swizzle_flag, False)
                self.all_tiles.append(new_tile)
                current_part.set_index(len(self.all_tiles) - 1)
            
            
        # for i in range(self.all_sprites):
        #     overlay3.seek(self.texdata + (i * 10))
        #     sprite_test = SpriteGroup(bytearray(overlay3.read(10)))
        #     if ((sprite_test.graphics_file == self.sprite_group_data.graphics_file) & (i != self.current_sprite)):
        #         print(hex(i))

        # print(self.header.has_scaling)
        # print(hex(self.sprite_group_data.animation_file))
        # print(self.header.frames_table)
        # print(self.header.affine_table)

        # print("wow")
        # sprite_count = 0
        # for current_sprite in self.all_sprites:
        #     part_count = 0
        #     for current_part in current_sprite.part_list:
        #         if current_part.unk1 != 0:
        #             print("sprite # " + hex(sprite_count))
        #             print("part # " + hex(part_count))
        #             print(current_part.unk1)
        #         part_count += 1
        #     sprite_count += 1

        # if (self.header.unk0 != 0):
        #     print(self.sprite_group_data.animation_file)
        #     print(self.header.unk0)

    def sprite_is_valid(self, index):
        self.overlay_group_data.seek(self.texdata + (index * self.sprite_group_interval))
        self.sprite_group_data = SpriteGroup(bytearray(self.overlay_group_data.read(self.sprite_group_interval)), self.sprite_type)

        return (self.sprite_group_data.graphics_file != 0)
    
    def export_graphics_and_animation_files(self):
        buffer = io.BytesIO()
        tile_offsets = [0]
        for tile in self.all_tiles:
            tile_buffer = io.BytesIO(tile.graphics_buffer)
            alignment = 1 << self.header.extra_tables[0].tex_shift

            write_current_tile = True
            for i in range(len(tile_offsets) - 1):
                buffer.seek(tile_offsets[i])
                test_length = tile_offsets[i + 1] - tile_offsets[i]
                actual_length = len(tile.graphics_buffer)
                read_amt = min(test_length, actual_length)

                if (tile_buffer.read(read_amt) != buffer.read(read_amt)):
                    tile_buffer.seek(0)
                else:
                    if ((test_length < actual_length) and ((buffer.tell() - read_amt) == tile.graphics_offset)):
                        delta = tile_buffer.getbuffer().nbytes - tile_buffer.tell()
                        for j in tile_offsets:
                            if (j > buffer.tell()):
                                j += delta

                        save_place = buffer.tell()
                        save_contents = buffer.read()
                        buffer.seek(save_place)
                        buffer.write(tile_buffer.read())
                        buffer.write(save_contents)

                        write_current_tile = False
                        tile_buffer.seek(0)
                        print("fuck")
                    elif (((buffer.tell() - read_amt) > tile.graphics_offset) and ((buffer.tell()) <= tile.graphics_offset + tile_buffer.getbuffer().nbytes)):
                        write_current_tile = False
                        tile_buffer.seek(0)
                        print("wow")
                    elif ((buffer.tell() - read_amt) != tile.graphics_offset):
                        print("wat")
                        tile_buffer.seek(0)
                    else:
                        write_current_tile = False
                        tile_buffer.seek(0)
                        break

            if (write_current_tile):
                buffer.seek(buffer.getbuffer().nbytes)
                buffer.write(tile_buffer.read())
                extra_padding = bytes(alignment - (buffer.tell() % alignment))
                if (len(extra_padding) != alignment):
                    buffer.write(extra_padding)
                tile_offsets.append(buffer.tell())
        
        buffer_len = buffer.getbuffer().nbytes
        buffer.seek(0)
        self.current_tex.seek(0)

        if (buffer.read() == self.current_tex.read()):
            print("test passed!!")
        else:
            print("failed... " + hex(self.sprite_group_data.graphics_file))

        buffer.seek(0)
        return buffer_len.to_bytes(4, 'little') + buffer.read()