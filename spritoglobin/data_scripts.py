import struct
from math import ceil, floor

from PIL import Image, ImageOps, ImageTransform, ImageEnhance

from spritoglobin.utils import *

def create_sprite_part(buffer_in, current_pal, part_x, part_y, sprite_mode, pal_shift, swizzle, translucent_flag):
    if (swizzle):
        part_size = 8 * 8
        tiles = (part_x * part_y) // 64
        tile_x, tile_y = 8, 8
    else:
        part_size = part_x * part_y
        tile_x, tile_y = part_x, part_y
        tiles = 1
    img_out = Image.new("RGBA", (part_x, part_y))
    for t in range(tiles):
        buffer_out = bytearray()
        match (sprite_mode):
            case 0:
                # 8bpp bitmap
                for i in range(part_size):
                    current_pixel = buffer_in[(t * 64) + i]
                    buffer_out.extend(current_pal[current_pixel + pal_shift])
                    # transparency
                    if (current_pixel == 0): buffer_out.append(0x00)
                    else: buffer_out.append(0xFF)
            case 1:
                # AI35
                for i in range(part_size):
                    current_pixel = buffer_in[(t * 64) + i]
                    buffer_out.extend(current_pal[current_pixel + pal_shift])
                    # transparency
                    alpha = ceil(0xFF * ((current_pixel >> 5) / 7))
                    buffer_out.append(alpha)
            case 2:
                # AI53
                for i in range(part_size):
                    current_pixel = buffer_in[(t * 64) + i]
                    buffer_out.extend(current_pal[current_pixel + pal_shift])
                    # transparency
                    alpha = current_pixel >> 3
                    alpha = (alpha << 3) | (alpha >> 2)
                    buffer_out.append(alpha)
            case 3:
                # 4bpp bitmap
                for i in range(part_size):
                    current_pixel = (buffer_in[((t * 64) + i) // 2] >> ((i % 2) * 4)) & 0xF
                    buffer_out.extend(current_pal[current_pixel + pal_shift])
                    # transparency
                    if (current_pixel == 0): buffer_out.append(0x00)
                    else: buffer_out.append(0xFF)
        # swizzle (if swizzle is disabled, x and y offset will always just be 0 and the image will display normally)
        x = (t % (part_x // tile_x)) * 8
        y = (t // (part_x // tile_x)) * 8
        img_out.paste(Image.frombytes("RGBA", (tile_x, tile_y), buffer_out), (x, y))
    return img_out

def create_assembled_sprite(size, part_list, all_tiles, highlighted_part_index):
    img = Image.new("RGBA", size)
    part_outline_affine = None
    outline_x, outline_y = 0, 0

    current_part_index = 0
    for current_sprite_part in reversed(part_list):
        if (current_sprite_part.tile_index != -1):
            current_tile = all_tiles[current_sprite_part.tile_index]
            tile_x = current_tile.x_size
            tile_y = current_tile.y_size
        else:
            img_part = MISSING_TEXTURE
            tile_x = 16
            tile_y = 16

        sprite_part_x_center = current_sprite_part.x_offset + (img.width // 2)
        sprite_part_y_center = current_sprite_part.y_offset + (img.height // 2)
        sprite_part_x_offset = sprite_part_x_center - (tile_x // 2)
        sprite_part_y_offset = sprite_part_y_center - (tile_y // 2)

        if (current_sprite_part.tile_index != -1):
            img_part = current_tile.cached_tile.copy()
        
        if (highlighted_part_index != -1 and highlighted_part_index != current_part_index):
            alpha = img_part.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(.15)
            img_part.putalpha(alpha)

        if (current_sprite_part.x_flip):
            img_part = ImageOps.mirror(img_part)
        if (current_sprite_part.y_flip):
            img_part = ImageOps.flip(img_part)

        img_part_affine = Image.new("RGBA", img.size)
        img_part_affine.paste(img_part, (sprite_part_x_offset, sprite_part_y_offset))
            
        if (current_sprite_part.rot_scale_flag):
            matrix = calculate_from_matrix(current_sprite_part.matrix, (-sprite_part_x_center, -sprite_part_y_center), True, 1)
            img_part_affine = img_part_affine.transform(img_part_affine.size, Image.AFFINE, matrix)

        if (current_part_index == highlighted_part_index):
            part_outline = Image.new("RGBA", (tile_x, tile_y))
            part_outline = ImageOps.expand(part_outline, border = (2, 2), fill = (255, 255, 255, 255))
            part_outline = ImageOps.expand(part_outline, border = (2, 2), fill = (243, 151, 16, 255))
            outline_x = sprite_part_x_offset - 4
            outline_y = sprite_part_y_offset - 4

            part_outline_affine = Image.new("RGBA", img.size)
            part_outline_affine.paste(part_outline, (outline_x, outline_y))

            if (current_sprite_part.rot_scale_flag):
                part_outline_affine = part_outline_affine.transform(part_outline_affine.size, Image.AFFINE, matrix)

        img = Image.alpha_composite(img, img_part_affine)
        current_part_index += 1

    if (part_outline_affine != None):
        img.paste(part_outline_affine, (0, 0), part_outline_affine)
    
    return img

def define_palette_color(current_pal):
    color_raw = int.from_bytes(current_pal.read(2), "little")
    return_color = []
    for i in range(3):
        x = color_raw >> (i * 5) & 0x1F
        return_color.append((x << 3) | (x >> 2))
    return return_color

def interpret_matrix(buffer_in, matrix_type = 0):
    out = [1, 0, 0, 0, 1, 0]
    match matrix_type:
        case 0:
            out[0], out[3], out[1], out[4], out[2], out[5] = struct.unpack('<hhhhhh', buffer_in)
        case 1:
            out[0], out[3], out[1], out[4] = struct.unpack('<hhhh', buffer_in)
    for i in range(6):
        if (i != 2 and i != 5):
            out[i] /= 0x100
    return out

def calculate_from_matrix(out, center, output_matrix = False, matrix_type = 0):
    if (output_matrix):
        new_center = center[0] - out[2], center[1] - out[5]
        dt = out[0] * out[4] - out[1] * out[3]
        new_out = out.copy()
        new_out[0] = out[4] / dt
        new_out[4] = out[0] / dt
        new_out[1] = -out[1] / dt
        new_out[3] = -out[3] / dt
        match matrix_type:
            case 0:
                new_out[2] = (new_center[0] * new_out[0]) + (new_center[1] * new_out[1]) - center[0]
                new_out[5] = (new_center[0] * new_out[3]) + (new_center[1] * new_out[4]) - center[1]
            case 1:
                new_out[2] = (center[0] * new_out[0]) + (center[1] * new_out[1]) - center[0]
                new_out[5] = (center[0] * new_out[3]) + (center[1] * new_out[4]) - center[1]
        return new_out
    else:
        print("non-matrix output NYI")
    
    # TO DO: figure what the fuck this is all about
    # right now i'm not properly getting shear, but that's irrelevant bc this data is not anywhere near precise enough
    # like goddamn, this is tough as FUCK
    # for now i'm just gonna pass the matrix data straight from the game into the sprite drawer
    # i'll worry about abstracting usable values from this shit later
    # fuck matrices

    # transform = out[2], out[5]
    # rotation = math.atan2(out[3], out[1]) * 2 * math.pi
    # scale = math.sqrt(pow(out[0], 2) + pow(out[3], 2)), math.sqrt(pow(out[1], 2) + pow(out[4], 2)),
    # shear = 0.950000000000, -200
    # return transform, rotation, scale, shear

def define_collision_box(ext, coll_type, input_collision, center, scalar):
    return_data0 = []
    return_data1 = []

    match coll_type:
        case 0: # BCollision
            for current_box in input_collision:
                start_x = (current_box[1] + center[0]) * scalar
                x_size  = (current_box[4]) * scalar

                start_z = ((-current_box[3] + current_box[2] + current_box[5]) + center[1]) * scalar
                z_size  = -current_box[6] * scalar

                start_y = (current_box[2] + center[1]) * scalar
                y_size  = (current_box[5]) * scalar

                return_data0.append((start_x, start_y, x_size, y_size))
                return_data1.append((start_x, start_z, x_size, z_size))
        case 1: # FCollision
            for current_box in input_collision:
                start_x = (current_box[0] + center[0]) * scalar
                x_size  = (current_box[2]) * scalar

                start_z = (current_box[1] + center[1]) * scalar
                z_size  = -current_box[3] * scalar

                start_y = (0 + center[1]) * scalar
                if len(current_box) > 4:
                    y_size  = (-current_box[4]) * scalar
                else:
                    y_size = 0

                return_data0.append((start_x, start_y, x_size, y_size))
                return_data1.append((start_x, start_z, x_size, z_size))
    
    return return_data0, return_data1
