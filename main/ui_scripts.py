import os
from PySide6 import QtCore, QtGui, QtWidgets
from PIL.ImageQt import ImageQt
from playsound import playsound
from functools import partial
from keyboard import is_pressed

from classes import *

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Spritoglobin")
        self.setWindowIcon(QtGui.QIcon('files/spritoglobin.ico'))

        # the widget that controls which graphics file to view
        self.file_selector = QtWidgets.QComboBox()
        self.file_selector.addItems(["BObjMap", "BObjMon", "BObjPc", "BObjUI", "EObjSave", "FObj", "FObjMap", "FObjMon", "FObjPc", "MObj"])
        self.file_selector.currentIndexChanged.connect(self.update_sprite_group_selector)

        # the widget that controls which sprite group ID to view
        self.sprite_group_selector = QtWidgets.QComboBox()
        self.sprite_group_selector.addItems([hex(0)])
        self.sprite_group_selector.currentIndexChanged.connect(self.update_animation_data)

        # the widget that controls current animation
        self.anim_list_box = QtWidgets.QListWidget()
        self.anim_list_box.addItems([hex(0)])
        self.anim_list_box.setCurrentRow(0)
        self.anim_list_box.currentItemChanged.connect(self.update_frame_data)

        # the widget that controls current animation frame
        self.pal_anim_list_box = QtWidgets.QListWidget()
        self.pal_anim_list_box.addItems(["NYI"])
        self.pal_anim_list_box.setCurrentRow(0)
        # self.pal_anim_list_box.currentItemChanged.connect(self.update_sprite_window)

        # the widget that displays assembled sprite graphics
        self.sprite_window = QtWidgets.QLabel()
        # self.sprite_window.setScaledContents(True)
        # self.sprite_window.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.sprite_canvas = QtGui.QPixmap(256 * 2.5, 256 * 2.5)
        self.sprite_canvas.fill(QtCore.Qt.GlobalColor.gray)
        self.sprite_window.setPixmap(self.sprite_canvas)

        # the animation timeline clock
        self.animation_timer = QtCore.QTimer()
        self.animation_timer.setInterval(int(1000 / 60))
        self.animation_timer.timeout.connect(self.update_animation_timeline)
        self.anim_time = 0

        # the animation playback buttons
        self.timeline_buttons_holder = QtWidgets.QWidget()
        self.timeline_buttons = QtWidgets.QHBoxLayout(self.timeline_buttons_holder)
        self.timeline_buttons.setContentsMargins(0, 0, 0, 0)
        self.play_button = QtWidgets.QPushButton()
        self.play_button.pressed.connect(self.update_animation_state)
        self.play_button.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.MediaPlaybackStart))
        self.timeline_buttons.addWidget(self.play_button)
        self.loop_button = QtWidgets.QPushButton()
        self.loop_button.pressed.connect(self.update_loop_state)
        self.loop_button.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewRefresh))
        self.loop_animation = True
        self.timeline_buttons.addWidget(self.loop_button)

        # the animation playback frame counter
        self.timeline_frame_counter = QtWidgets.QLabel()

        # the widget that controls current animation frame
        self.frame_timeline_bar = QtWidgets.QSlider()
        self.frame_timeline_bar.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.frame_timeline_bar.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.frame_timeline_bar.valueChanged.connect(self.update_sprite_window)

        # assemble the timeline widget
        self.timeline_top_bar = QtWidgets.QHBoxLayout()
        self.timeline_top_bar.addWidget(self.timeline_buttons_holder, alignment = QtCore.Qt.AlignmentFlag.AlignLeft)
        self.timeline_top_bar.addWidget(self.timeline_frame_counter, alignment = QtCore.Qt.AlignmentFlag.AlignRight)
        self.timeline_holder = QtWidgets.QWidget()
        self.timeline_holder.setFixedHeight(60)
        self.timeline_layout = QtWidgets.QVBoxLayout(self.timeline_holder)
        self.timeline_layout.setContentsMargins(0, 0, 0, 0)
        self.timeline_layout.addLayout(self.timeline_top_bar)
        self.timeline_layout.addWidget(self.frame_timeline_bar)

        # the widget that displays the sprite part's tile
        self.frame_sprite_window = QtWidgets.QLabel()
        self.frame_sprite_canvas = QtGui.QPixmap(68, 68)
        self.frame_sprite_canvas.fill(QtCore.Qt.transparent)
        self.frame_sprite_window.setPixmap(self.frame_sprite_canvas)

        # the widget that displays the sprite part's transform
        self.sprite_transform_window = QtWidgets.QLabel()
        self.sprite_transform_canvas = QtGui.QPixmap(68, 68)
        self.sprite_transform_canvas.fill(QtCore.Qt.transparent)
        self.sprite_transform_window.setPixmap(self.sprite_transform_canvas)

        # the layout that has all the animation frame customization fields
        self.frame_customization_field_holder = QtWidgets.QWidget()
        self.frame_customization_field = QtWidgets.QGridLayout(self.frame_customization_field_holder)
        self.frame_customization_field.setContentsMargins(0, 0, 0, 0)

        self.frame_sprite_box = QtWidgets.QSpinBox()
        self.frame_sprite_box.setMinimum(0)
        self.frame_sprite_box.setMaximum(0)
        self.frame_sprite_text = QtWidgets.QLabel("Sprite ID")
        self.frame_customization_field.addWidget(self.frame_sprite_box, 0, 0, 3, 1)
        self.frame_customization_field.addWidget(self.frame_sprite_text, 0, 1, 3, 1)
        self.frame_sprite_box.textChanged.connect(partial(self.set_anim_frame_data, 0))

        self.frame_customization_field.addWidget(self.frame_sprite_window, 0, 2, 3, 1)
        
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.VLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_customization_field.addWidget(line, 0, 3, 3, 1)

        self.frame_use_matrix_box = QtWidgets.QCheckBox()
        self.frame_use_matrix_box.setText("Use Sprite Transformation")
        self.frame_customization_field.addWidget(self.frame_use_matrix_box, 0, 4, 1, 3)
        self.frame_use_matrix_box.checkStateChanged.connect(partial(self.set_anim_frame_data, 1))

        self.frame_matrix_a_box = QtWidgets.QDoubleSpinBox()
        self.frame_matrix_a_box.setMinimum(-128)
        self.frame_matrix_a_box.setMaximum(128)
        self.frame_matrix_a_box.setSingleStep(0.05)
        self.frame_matrix_a_text = QtWidgets.QLabel("X Scale")
        self.frame_customization_field.addWidget(self.frame_matrix_a_box, 1, 4)
        self.frame_customization_field.addWidget(self.frame_matrix_a_text, 1, 5)
        self.frame_matrix_a_box.textChanged.connect(partial(self.set_anim_frame_data, 2))

        self.frame_matrix_b_box = QtWidgets.QDoubleSpinBox()
        self.frame_matrix_b_box.setMinimum(-128)
        self.frame_matrix_b_box.setMaximum(128)
        self.frame_matrix_b_box.setSingleStep(0.05)
        self.frame_matrix_b_text = QtWidgets.QLabel("Y Shear")
        self.frame_customization_field.addWidget(self.frame_matrix_b_box, 1, 6)
        self.frame_customization_field.addWidget(self.frame_matrix_b_text, 1, 7)
        self.frame_matrix_b_box.textChanged.connect(partial(self.set_anim_frame_data, 3))

        self.frame_matrix_c_box = QtWidgets.QDoubleSpinBox()
        self.frame_matrix_c_box.setMinimum(-128)
        self.frame_matrix_c_box.setMaximum(128)
        self.frame_matrix_c_box.setSingleStep(0.05)
        self.frame_matrix_c_text = QtWidgets.QLabel("X Shear")
        self.frame_customization_field.addWidget(self.frame_matrix_c_box, 2, 4)
        self.frame_customization_field.addWidget(self.frame_matrix_c_text, 2, 5)
        self.frame_matrix_c_box.textChanged.connect(partial(self.set_anim_frame_data, 4))

        self.frame_matrix_d_box = QtWidgets.QDoubleSpinBox()
        self.frame_matrix_d_box.setMinimum(-128)
        self.frame_matrix_d_box.setMaximum(128)
        self.frame_matrix_d_box.setSingleStep(0.05)
        self.frame_matrix_d_text = QtWidgets.QLabel("Y Scale")
        self.frame_customization_field.addWidget(self.frame_matrix_d_box, 2, 6)
        self.frame_customization_field.addWidget(self.frame_matrix_d_text, 2, 7)
        self.frame_matrix_d_box.textChanged.connect(partial(self.set_anim_frame_data, 5))

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.VLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_customization_field.addWidget(line, 1, 8, 2, 1)

        self.frame_x_pos_box = QtWidgets.QSpinBox()
        self.frame_x_pos_box.setMinimum(-32768)
        self.frame_x_pos_box.setMaximum(32767)
        self.frame_x_pos_box.setWrapping(True)
        self.frame_x_pos_text = QtWidgets.QLabel("X Position")
        self.frame_customization_field.addWidget(self.frame_x_pos_box, 1, 9)
        self.frame_customization_field.addWidget(self.frame_x_pos_text, 1, 10)
        self.frame_x_pos_box.textChanged.connect(partial(self.set_anim_frame_data, 6))

        self.frame_y_pos_box = QtWidgets.QSpinBox()
        self.frame_y_pos_box.setMinimum(-32768)
        self.frame_y_pos_box.setMaximum(32767)
        self.frame_y_pos_box.setWrapping(True)
        self.frame_y_pos_text = QtWidgets.QLabel("Y Position")
        self.frame_customization_field.addWidget(self.frame_y_pos_box, 2, 9)
        self.frame_customization_field.addWidget(self.frame_y_pos_text, 2, 10)
        self.frame_y_pos_box.textChanged.connect(partial(self.set_anim_frame_data, 7))

        self.frame_customization_field.addWidget(self.sprite_transform_window, 0, 11, 3, 1)

        # the widget that controls which sprite to view
        self.sprite_selector = QtWidgets.QComboBox()
        self.sprite_selector.addItems([hex(0)])
        self.sprite_selector.currentIndexChanged.connect(self.update_sprite_part_data)

        # the widget that displays the sprite part's tile
        self.part_tile_window = QtWidgets.QLabel()
        self.part_tile_canvas = QtGui.QPixmap(68, 68)
        self.part_tile_canvas.fill(QtCore.Qt.transparent)
        self.part_tile_window.setPixmap(self.part_tile_canvas)

        # the widget that displays the sprite part's transform
        self.part_transform_window = QtWidgets.QLabel()
        self.part_transform_canvas = QtGui.QPixmap(68, 68)
        self.part_transform_canvas.fill(QtCore.Qt.transparent)
        self.part_transform_window.setPixmap(self.part_transform_canvas)

        # the layout that has all the sprite part customization fields
        self.part_customization_field_holder = QtWidgets.QWidget()
        self.part_customization_field = QtWidgets.QGridLayout(self.part_customization_field_holder)
        self.part_customization_field.setContentsMargins(0, 0, 0, 0)

        self.part_tile_box = QtWidgets.QSpinBox()
        self.part_tile_box.setMinimum(-1)
        self.part_tile_box.setMaximum(0)
        self.part_tile_box.setSpecialValueText("None")
        self.part_tile_text = QtWidgets.QLabel("Tile ID")
        self.part_customization_field.addWidget(self.part_tile_box, 0, 0)
        self.part_customization_field.addWidget(self.part_tile_text, 0, 1)
        self.part_tile_box.textChanged.connect(partial(self.set_sprite_part_data, 0))

        self.part_x_flip_box = QtWidgets.QCheckBox()
        self.part_x_flip_box.setText("X Flip")
        self.part_customization_field.addWidget(self.part_x_flip_box, 0, 2)
        self.part_x_flip_box.checkStateChanged.connect(partial(self.set_sprite_part_data, 1))
        
        self.part_y_flip_box = QtWidgets.QCheckBox()
        self.part_y_flip_box.setText("Y Flip")
        self.part_customization_field.addWidget(self.part_y_flip_box, 0, 3)
        self.part_y_flip_box.checkStateChanged.connect(partial(self.set_sprite_part_data, 2))

        self.part_x_pos_box = QtWidgets.QSpinBox()
        self.part_x_pos_box.setMinimum(-32768)
        self.part_x_pos_box.setMaximum(32767)
        self.part_x_pos_box.setWrapping(True)
        self.part_x_pos_text = QtWidgets.QLabel("X Position")
        self.part_customization_field.addWidget(self.part_x_pos_box, 1, 0)
        self.part_customization_field.addWidget(self.part_x_pos_text, 1, 1)
        self.part_x_pos_box.textChanged.connect(partial(self.set_sprite_part_data, 3))

        self.part_y_pos_box = QtWidgets.QSpinBox()
        self.part_y_pos_box.setMinimum(-32768)
        self.part_y_pos_box.setMaximum(32767)
        self.part_y_pos_box.setWrapping(True)
        self.part_y_pos_text = QtWidgets.QLabel("Y Position")
        self.part_customization_field.addWidget(self.part_y_pos_box, 1, 2)
        self.part_customization_field.addWidget(self.part_y_pos_text, 1, 3)
        self.part_y_pos_box.textChanged.connect(partial(self.set_sprite_part_data, 4))

        self.part_customization_field.addWidget(self.part_tile_window, 0, 4, 2, 2)

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.part_customization_field.addWidget(line, 2, 0, 1, 6)

        self.part_use_matrix_box = QtWidgets.QCheckBox()
        self.part_use_matrix_box.setText("Use Sprite Transformation")
        self.part_customization_field.addWidget(self.part_use_matrix_box, 3, 0, 1, 3)
        self.part_use_matrix_box.checkStateChanged.connect(partial(self.set_sprite_part_data, 5))

        self.part_matrix_a_box = QtWidgets.QDoubleSpinBox()
        self.part_matrix_a_box.setMinimum(-128)
        self.part_matrix_a_box.setMaximum(128)
        self.part_matrix_a_box.setSingleStep(0.05)
        self.part_matrix_a_text = QtWidgets.QLabel("X Scale")
        self.part_customization_field.addWidget(self.part_matrix_a_box, 4, 0)
        self.part_customization_field.addWidget(self.part_matrix_a_text, 4, 1)
        self.part_matrix_a_box.textChanged.connect(partial(self.set_sprite_part_data, 6))

        self.part_matrix_b_box = QtWidgets.QDoubleSpinBox()
        self.part_matrix_b_box.setMinimum(-128)
        self.part_matrix_b_box.setMaximum(128)
        self.part_matrix_b_box.setSingleStep(0.05)
        self.part_matrix_b_text = QtWidgets.QLabel("Y Shear")
        self.part_customization_field.addWidget(self.part_matrix_b_box, 4, 2)
        self.part_customization_field.addWidget(self.part_matrix_b_text, 4, 3)
        self.part_matrix_b_box.textChanged.connect(partial(self.set_sprite_part_data, 7))

        self.part_matrix_c_box = QtWidgets.QDoubleSpinBox()
        self.part_matrix_c_box.setMinimum(-128)
        self.part_matrix_c_box.setMaximum(128)
        self.part_matrix_c_box.setSingleStep(0.05)
        self.part_matrix_c_text = QtWidgets.QLabel("X Shear")
        self.part_customization_field.addWidget(self.part_matrix_c_box, 5, 0)
        self.part_customization_field.addWidget(self.part_matrix_c_text, 5, 1)
        self.part_matrix_c_box.textChanged.connect(partial(self.set_sprite_part_data, 8))

        self.part_matrix_d_box = QtWidgets.QDoubleSpinBox()
        self.part_matrix_d_box.setMinimum(-128)
        self.part_matrix_d_box.setMaximum(128)
        self.part_matrix_d_box.setSingleStep(0.05)
        self.part_matrix_d_text = QtWidgets.QLabel("Y Scale")
        self.part_customization_field.addWidget(self.part_matrix_d_box, 5, 2)
        self.part_customization_field.addWidget(self.part_matrix_d_text, 5, 3)
        self.part_matrix_d_box.textChanged.connect(partial(self.set_sprite_part_data, 9))

        self.part_customization_field.addWidget(self.part_transform_window, 3, 4, 3, 2)

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.part_customization_field.addWidget(line, 6, 0, 1, 6)

        self.part_pixel_mode_box = QtWidgets.QSpinBox()
        self.part_pixel_mode_box.setMinimum(0)
        self.part_pixel_mode_box.setMaximum(1)
        self.part_pixel_mode_text = QtWidgets.QLabel("unk0") #pix mode
        self.part_customization_field.addWidget(self.part_pixel_mode_box, 8, 0)
        self.part_customization_field.addWidget(self.part_pixel_mode_text, 8, 1)

        self.part_unk0_box = QtWidgets.QSpinBox()
        self.part_unk0_box.setMinimum(0)
        self.part_unk0_box.setMaximum(1)
        self.part_unk0_text = QtWidgets.QLabel("unk1") #unk0
        self.part_customization_field.addWidget(self.part_unk0_box, 8, 2)
        self.part_customization_field.addWidget(self.part_unk0_text, 8, 3)

        self.part_unk1_box = QtWidgets.QSpinBox()
        self.part_unk1_box.setMinimum(0)
        self.part_unk1_box.setMaximum(3)
        self.part_unk1_text = QtWidgets.QLabel("unk2") #unk1
        self.part_customization_field.addWidget(self.part_unk1_box, 9, 0)
        self.part_customization_field.addWidget(self.part_unk1_text, 9, 1)

        self.part_unk2_box = QtWidgets.QSpinBox()
        self.part_unk2_box.setMinimum(0)
        self.part_unk2_box.setMaximum(3)
        self.part_unk2_text = QtWidgets.QLabel("unk3") #unk2
        self.part_customization_field.addWidget(self.part_unk2_box, 9, 2)
        self.part_customization_field.addWidget(self.part_unk2_text, 9, 3)

        # the widget that controls which sprite part to view
        self.sprite_part_selector = QtWidgets.QComboBox()
        self.sprite_part_selector.addItems([hex(0)])
        self.sprite_part_selector.currentIndexChanged.connect(self.update_sprite_part_editor_field)

        # the widget that displays assembled sprite graphics
        self.sprite_part_editor_window = DraggableQLabel()
        self.sprite_part_editor_canvas = QtGui.QPixmap(320, 320)
        self.sprite_part_editor_canvas.fill(QtCore.Qt.GlobalColor.gray)
        self.sprite_part_editor_window.setPixmap(self.sprite_part_editor_canvas)
        self.sprite_part_editor_window.mouseDragged.connect(partial(self.set_sprite_part_data, 10))
        self.sprite_part_editor_window.mouseReleased.connect(self.update_sprite_window)

        # the widget that displays the grid of tile graphics
        self.tile_grid = QtWidgets.QListWidget()
        self.tile_grid.setItemAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.tile_grid.setFlow(QtWidgets.QListWidget.Flow.LeftToRight)
        self.tile_grid.setWrapping(True)
        self.tile_grid.setIconSize(QtCore.QSize(64, 64))
        self.scrollable_tile_grid = QtWidgets.QScrollArea()
        self.scrollable_tile_grid.setWidget(self.tile_grid)
        self.scrollable_tile_grid.setWidgetResizable(True)
        self.tile_grid.currentItemChanged.connect(self.update_tile_painter)

        # the widget that displays the tile painter
        self.tile_painter = QtWidgets.QLabel()
        self.tile_canvas = QtGui.QPixmap(324, 324)
        self.tile_canvas.fill(QtCore.Qt.transparent)
        self.tile_painter.setPixmap(self.tile_canvas)

        # the widget that displays the palette picker
        self.palette_picker = QtWidgets.QLabel()
        self.palette_canvas = QtGui.QPixmap((16 * 12) + 3, (16 * 12) + 3)
        self.palette_canvas.fill(QtCore.Qt.GlobalColor.black)
        self.palette_picker.setPixmap(self.palette_canvas)
        # self.palette_picker.mousePressEvent = self.label_clicked

        # the widget to enable collision boxes
        self.enable_collision_box = QtWidgets.QCheckBox()
        self.enable_collision_box.setText("Enable Hitbox View (EXPERIMENTAL)")
        self.enable_collision_box.checkStateChanged.connect(self.update_sprite_window)

        # the text widgets
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.file_selector_label = QtWidgets.QLabel("Graphics File:")
        self.sprite_group_selector_label = QtWidgets.QLabel("Sprite Group ID:")
        self.anim_list_box_label = QtWidgets.QLabel("Sprite Animation ID:")
        self.pal_anim_list_box_label = QtWidgets.QLabel("Palette Animation ID:")
        self.sprite_selector_label = QtWidgets.QLabel("Sprite:")
        self.sprite_selector_label.setSizePolicy(size_policy)
        self.sprite_part_selector_label = QtWidgets.QLabel("Sprite Part:")
        self.sprite_part_selector_label.setSizePolicy(size_policy)
        self.tile_grid_label = QtWidgets.QLabel("Tile Data:")

        # fill out the left margin
        left_margin_holder = QtWidgets.QWidget()
        left_margin_holder.setFixedWidth(136)
        left_margin = QtWidgets.QVBoxLayout(left_margin_holder)
        left_margin.setContentsMargins(0, 0, 0, 0)
        left_margin.addWidget(self.file_selector_label, alignment = QtCore.Qt.AlignmentFlag.AlignLeft)
        left_margin.addWidget(self.file_selector)
        left_margin.addWidget(self.sprite_group_selector_label, alignment = QtCore.Qt.AlignmentFlag.AlignLeft)
        left_margin.addWidget(self.sprite_group_selector)
        left_margin.addWidget(self.anim_list_box_label, alignment = QtCore.Qt.AlignmentFlag.AlignLeft)
        left_margin.addWidget(self.anim_list_box)
        #left_margin.addWidget(self.pal_anim_list_box_label, alignment = QtCore.Qt.AlignmentFlag.AlignLeft)
        #left_margin.addWidget(self.pal_anim_list_box)

        # fill out the right margin (tile view mode)
        right_margin_tile_view_holder = QtWidgets.QWidget()
        right_margin_tile_view = QtWidgets.QVBoxLayout(right_margin_tile_view_holder)
        right_margin_tile_view.addWidget(self.tile_grid_label, alignment = QtCore.Qt.AlignmentFlag.AlignLeft)
        right_margin_tile_view.addWidget(self.scrollable_tile_grid)
        right_margin_tile_view.addWidget(self.tile_painter, alignment = QtCore.Qt.AlignmentFlag.AlignCenter)
        right_margin_tile_view.addWidget(self.palette_picker, alignment = QtCore.Qt.AlignmentFlag.AlignRight)

        # fill out the right margin (sprite view mode)
        right_margin_sprite_view_holder = QtWidgets.QWidget()
        right_margin_sprite_view = QtWidgets.QVBoxLayout(right_margin_sprite_view_holder)
        right_margin_sprite_view.addWidget(self.sprite_selector_label, alignment = QtCore.Qt.AlignmentFlag.AlignLeft)
        right_margin_sprite_view.addWidget(self.sprite_selector)
        right_margin_sprite_view.addWidget(self.sprite_part_editor_window, alignment = QtCore.Qt.AlignmentFlag.AlignCenter)
        right_margin_sprite_view.addWidget(self.sprite_part_selector_label, alignment = QtCore.Qt.AlignmentFlag.AlignLeft)
        right_margin_sprite_view.addWidget(self.sprite_part_selector)
        right_margin_sprite_view.addWidget(self.part_customization_field_holder)

        # fill out the right margin (collision view mode)
        right_margin_collision_view_holder = QtWidgets.QWidget()
        right_margin_collision_view = QtWidgets.QVBoxLayout(right_margin_collision_view_holder)
        right_margin_collision_view.addWidget(self.enable_collision_box, alignment = QtCore.Qt.AlignmentFlag.AlignTop)

        # create the tab widget for the right margin
        right_margin_tabs = QtWidgets.QTabWidget()
        right_margin_tabs.addTab(right_margin_sprite_view_holder, "Sprite View")
        right_margin_tabs.addTab(right_margin_tile_view_holder, "Tile View")
        right_margin_tabs.addTab(right_margin_collision_view_holder, "Hitbox View")

        # TEMPORARY GIF EXPORT SOLUTION
        self.gif_export_button = QtWidgets.QPushButton()
        self.gif_export_button.pressed.connect(self.export_gif)
        self.gif_export_button.setText("Export GIF")
        left_margin.addWidget(self.gif_export_button)

        main = QtWidgets.QGridLayout()
        main.addWidget(left_margin_holder, 0, 0, 1, 1)
        main.addWidget(self.sprite_window, 0, 1, 1, 1)
        main.addWidget(self.frame_customization_field_holder, 2, 0, 1, 2)
        main.addWidget(self.timeline_holder, 1, 0, 1, 2, alignment = QtCore.Qt.AlignmentFlag.AlignBottom)
        main.addWidget(right_margin_tabs, 0, 2, 3, 1)

        widget = QtWidgets.QWidget()
        widget.setLayout(main)

        self.setCentralWidget(widget)


        for file in os.listdir("files"):
            if file.endswith(".nds"):
                rom = import_files.ndspy.rom.NintendoDSRom.fromFile("files/" + file)
                if rom.name == bytearray("MARIO&LUIGI3", 'utf-8') and (rom.idCode[3] == 69 or rom.idCode[3] == 80):
                    rom_name = file
        
        try:
            path = "files/" + rom_name
        except:
            dlg = QtWidgets.QMessageBox(self)
            dlg.setWindowTitle("Choose a ROM")
            dlg.setText("Please choose a North American or European Bowser's Inside Story ROM to open.\n\nAlternatively, put a Bowser's Inside Story ROM in the program's 'files' directory to skip this prompt next time the program is opened.")
            dlg.exec()

            path, h = QtWidgets.QFileDialog.getOpenFileName(
                parent=self,  # or None if the main window doesn't exist yet
                caption="Open ROM",
                filter="NDS ROMs (*.nds);;All Files (*)",
            )
        finally:
            import_files.import_files(path)

    def update_sprite_group_selector(self):
        #print("update_sprite_group_selector")
        self.animation_data = AnimationData(self.file_selector.currentText(), 0)
        self.sprite_group_selector.blockSignals(True)
        self.sprite_group_selector.clear()
        self.sprite_group_selector.blockSignals(False)
        for i in range(self.animation_data.all_sprites):
            if (self.animation_data.sprite_is_valid(i)):
                self.sprite_group_selector.addItems([hex(i)])
        self.sprite_group_selector.setCurrentText("0x0")

    def update_animation_data(self):
        #print("update_animation_data")
        self.animation_data = AnimationData(self.file_selector.currentText(), int(self.sprite_group_selector.currentText(), 0))
        self.animation_data.generate_anim_data()
        self.anim_list_box.blockSignals(True)
        self.anim_list_box.clear()
        self.anim_list_box.blockSignals(False)
        for i in range(self.animation_data.header.animation_amt):
            self.anim_list_box.addItems([hex(i)])
        self.anim_list_box.setCurrentRow(0)
        self.frame_timeline_bar.setValue(0)

        self.sprite_selector.blockSignals(True)
        self.sprite_selector.clear()
        self.sprite_selector.blockSignals(False)
        for i in range(len(self.animation_data.all_sprites)):
            self.sprite_selector.addItems([str(i)])
        self.sprite_selector.setCurrentText("0")

        self.tile_grid.blockSignals(True)
        self.tile_grid.clear()
        self.tile_grid.blockSignals(False)
        for current_tile in self.animation_data.all_tiles:
            current_img = QtWidgets.QListWidgetItem()
            img = current_tile.cached_tile.copy()
            if (self.animation_data.header.sprite_mode == 0 or self.animation_data.header.sprite_mode == 3):
                img.putalpha(255)
            tile_pixmap = QtGui.QPixmap(QtGui.QImage(ImageQt(img)))
            current_img.setIcon(QtGui.QIcon(tile_pixmap))
            self.tile_grid.addItem(current_img)
        self.tile_grid.setCurrentRow(0)

        self.frame_sprite_box.blockSignals(True)
        self.frame_sprite_box.setValue(0)
        self.frame_sprite_box.blockSignals(False)
        self.frame_sprite_box.setMaximum(len(self.animation_data.all_sprites) - 1)
    
    def update_frame_data(self):
        #print("update_frame_data")
        self.frame_timeline_bar.setMaximum(self.animation_data.all_anims[self.anim_list_box.currentRow()].frame_amt - 1)
        self.frame_timeline_bar.blockSignals(True)
        self.frame_timeline_bar.setValue(0)
        self.frame_timeline_bar.blockSignals(False)
        self.update_sprite_window()
        self.anim_time = 0
    
    def update_sprite_window(self):
        #print("update_sprite_window")
        
        scale = 2

        self.sprite_canvas.fill(QtCore.Qt.GlobalColor.gray)
        qp = QtGui.QPainter(self.sprite_canvas)

        qp.setPen(QtGui.QPen(QtGui.QColor(23, 250, 101), 2))
        qp.drawLine(self.sprite_canvas.width() // 2, 0, self.sprite_canvas.width() // 2, self.sprite_canvas.height())

        qp.setPen(QtGui.QPen(QtGui.QColor(246, 25, 17), 2))
        qp.drawLine(0, self.sprite_canvas.height() // 2, self.sprite_canvas.width(), self.sprite_canvas.height() // 2)

        current_anim = self.animation_data.all_anims[self.anim_list_box.currentRow()]
        current_frame = current_anim.frame_list[self.frame_timeline_bar.value()]

        img_size = (self.sprite_canvas.width() // scale, self.sprite_canvas.height() // scale)
        img_part_list = self.animation_data.all_sprites[current_frame.sprite_index].part_list
        img_all_tiles = self.animation_data.all_tiles

        img = create_assembled_sprite(img_size, img_part_list, img_all_tiles, -1)
        
        if (current_frame.rot_scale_flag):
            matrix = calculate_from_matrix(current_frame.matrix, (-img.width // 2, -img.height // 2), True)
            img = img.transform(img.size, Image.AFFINE, matrix)

        img = ImageOps.scale(img, scale, 0)

        qimg = ImageQt(img)
        qp.drawImage(0, 0, qimg)

        if (self.animation_data.sprite_group_data.has_collision and self.enable_collision_box.isChecked()):
            if (current_frame.collision_group_ext):
                col_box, col_bottom = define_collision_box(True, self.animation_data.collision_type, current_frame.collision_group_ext, (self.sprite_canvas.width() // (scale * 2), self.sprite_canvas.height() // (scale * 2)), scale)
                for current_box in col_box:
                    qp.setPen(QtGui.QPen(QtGui.QColor(168, 255, 15), 2))
                    qp.drawRect(*current_box)
                for current_box in col_bottom:
                    qp.fillRect(*current_box, QtGui.QColor(168, 255, 15, 102))
            if (current_frame.collision_group):
                col_box, col_bottom = define_collision_box(False, self.animation_data.collision_type, current_frame.collision_group, (self.sprite_canvas.width() // (scale * 2), self.sprite_canvas.height() // (scale * 2)), scale)
                for current_box in col_box:
                    qp.setPen(QtGui.QPen(QtGui.QColor(248, 56, 113), 2))
                    qp.drawRect(*current_box)
                for current_box in col_bottom:
                    qp.fillRect(*current_box, QtGui.QColor(248, 56, 113, 102))
        
        qp.end()
        self.sprite_window.setPixmap(self.sprite_canvas)

        self.timeline_frame_counter.setText(f"{self.frame_timeline_bar.value() + 1} / {self.frame_timeline_bar.maximum() + 1}")

        self.update_anim_frame_editor_field() # to do: remove this once the timeline is overhauled
    
    def set_anim_frame_data(self, param_num, input_data):
        current_anim = self.animation_data.all_anims[self.anim_list_box.currentRow()]
        current_frame = current_anim.frame_list[self.frame_timeline_bar.value()]

        if (input_data != "" and input_data != "-"):
            match param_num:
                case 0: # sprite ID
                    current_frame.sprite_index = int(input_data, 0)
                case 1:  # use matrix
                    current_frame.rot_scale_flag = input_data == QtCore.Qt.Checked
                case 2:  # matrix 0
                    current_frame.matrix[0] = float(input_data)
                case 3:  # matrix 1
                    current_frame.matrix[1] = float(input_data)
                case 4:  # matrix 3
                    current_frame.matrix[3] = float(input_data)
                case 5:  # matrix 4
                    current_frame.matrix[4] = float(input_data)
                case 6:  # X pos
                    current_frame.matrix[2] = int(input_data, 0)
                case 7:  # Y pos
                    current_frame.matrix[5] = int(input_data, 0)

            self.update_anim_frame_editor_field()
        
        self.update_sprite_window()
        return

    def update_anim_frame_editor_field(self):
        # update the customization fields
        current_anim = self.animation_data.all_anims[self.anim_list_box.currentRow()]
        current_frame = current_anim.frame_list[self.frame_timeline_bar.value()]

        self.frame_sprite_box.setValue(current_frame.sprite_index)
        self.frame_use_matrix_box.setChecked(current_frame.rot_scale_flag)
        self.frame_use_matrix_box.setEnabled(True)
        if (self.frame_use_matrix_box.isChecked()):
            self.frame_matrix_a_box.setValue(current_frame.matrix[0])
            self.frame_matrix_a_box.setEnabled(True)
            self.frame_matrix_a_text.setEnabled(True)
            self.frame_matrix_b_box.setValue(current_frame.matrix[1])
            self.frame_matrix_b_box.setEnabled(True)
            self.frame_matrix_b_text.setEnabled(True)
            self.frame_matrix_c_box.setValue(current_frame.matrix[3])
            self.frame_matrix_c_box.setEnabled(True)
            self.frame_matrix_c_text.setEnabled(True)
            self.frame_matrix_d_box.setValue(current_frame.matrix[4])
            self.frame_matrix_d_box.setEnabled(True)
            self.frame_matrix_d_text.setEnabled(True)

            self.frame_x_pos_box.setValue(current_frame.matrix[2])
            self.frame_x_pos_box.setEnabled(True)
            self.frame_x_pos_text.setEnabled(True)
            self.frame_y_pos_box.setValue(current_frame.matrix[5])
            self.frame_y_pos_box.setEnabled(True)
            self.frame_y_pos_text.setEnabled(True)
        else:
            self.frame_matrix_a_box.setValue(1)
            self.frame_matrix_a_box.setEnabled(False)
            self.frame_matrix_a_text.setEnabled(False)
            self.frame_matrix_b_box.setValue(0)
            self.frame_matrix_b_box.setEnabled(False)
            self.frame_matrix_b_text.setEnabled(False)
            self.frame_matrix_c_box.setValue(0)
            self.frame_matrix_c_box.setEnabled(False)
            self.frame_matrix_c_text.setEnabled(False)
            self.frame_matrix_d_box.setValue(1)
            self.frame_matrix_d_box.setEnabled(False)
            self.frame_matrix_d_text.setEnabled(False)

            self.frame_x_pos_box.setValue(0)
            self.frame_x_pos_box.setEnabled(False)
            self.frame_x_pos_text.setEnabled(False)
            self.frame_y_pos_box.setValue(0)
            self.frame_y_pos_box.setEnabled(False)
            self.frame_y_pos_text.setEnabled(False)

        # update the sprite viewer
        self.frame_sprite_canvas.fill(QtCore.Qt.transparent)
        qp = QtGui.QPainter(self.frame_sprite_canvas)

        current_sprite = self.frame_sprite_box.value()
        part_list = self.animation_data.all_sprites[current_sprite].part_list

        img_size = (192, 192)
        img_all_tiles = self.animation_data.all_tiles

        img = create_assembled_sprite(img_size, part_list, img_all_tiles, -1)
        bounding_box = img.getbbox()
        img = img.crop(bounding_box)
        img.thumbnail((64, 64), 1)

        img_hfill = 64 - img.width
        img_vfill = 64 - img.height
        img = ImageOps.expand(img, border = (floor(img_hfill / 2), floor(img_vfill / 2), ceil(img_hfill / 2), ceil(img_vfill / 2)))

        img = ImageOps.expand(img, border = (1, 1), fill = (255, 255, 255, 255))
        img = ImageOps.expand(img, border = (1, 1), fill = (243, 151, 16, 255))

        qimg = ImageQt(img)
        qp.drawImage(0, 0, qimg)

        qp.end()
        self.frame_sprite_window.setPixmap(self.frame_sprite_canvas)

        # update the transform viewer
        self.sprite_transform_canvas.fill(QtCore.Qt.GlobalColor.gray)
        qp = QtGui.QPainter(self.sprite_transform_canvas)

        tex = Image.open("files/missing texture.png")
        tex = ImageOps.scale(tex, 2, 0)

        img = Image.new("RGBA", (64, 64))
        img.paste(tex, (16, 16))

        if (self.frame_use_matrix_box.isChecked()):
            input_matrix = [float(self.frame_matrix_a_box.text()), float(self.frame_matrix_b_box.text()), 0, float(self.frame_matrix_c_box.text()), float(self.frame_matrix_d_box.text()), 0]
            matrix = calculate_from_matrix(input_matrix, (-img.width // 2, -img.height // 2), True)
            img = img.transform(img.size, Image.AFFINE, matrix)
    
        img = ImageOps.expand(img, border = (1, 1), fill = (255, 255, 255, 255))
        img = ImageOps.expand(img, border = (1, 1), fill = (243, 151, 16, 255))

        qimg = ImageQt(img)
        qp.drawImage(0, 0, qimg)

        qp.end()
        self.sprite_transform_window.setPixmap(self.sprite_transform_canvas)
        return
    
    def update_sprite_part_data(self):
        current_sprite = int(self.sprite_selector.currentText(), 0)
        img_part_list = self.animation_data.all_sprites[current_sprite].part_list

        part_selector_save = self.sprite_part_selector.currentIndex()
        self.sprite_part_selector.blockSignals(True)
        self.sprite_part_selector.clear()
        self.sprite_part_selector.blockSignals(False)
        self.sprite_part_selector.addItems(["None"])
        for i in range(len(img_part_list)):
            self.sprite_part_selector.addItems([str(i)])
        if (part_selector_save < self.sprite_part_selector.count() - 1):
            self.sprite_part_selector.setCurrentIndex(part_selector_save)
        else:
            self.sprite_part_selector.setCurrentIndex(self.sprite_part_selector.count() - 1)
    
    def set_sprite_part_data(self, param_num, input_data):
        current_sprite = int(self.sprite_selector.currentText(), 0)
        part_list = self.animation_data.all_sprites[current_sprite].part_list

        if (self.sprite_part_selector.currentText() != "None"):
            current_sprite_part = part_list[int(self.sprite_part_selector.currentText(), 0)]
            
            if (input_data != "" and input_data != "-"):
                match param_num:
                    case 0: # tile ID
                        if (input_data == "None"):
                            current_sprite_part.tile_index = -1
                        else:
                            current_sprite_part.tile_index = int(input_data, 0)
                    case 1:  # X flip
                        current_sprite_part.x_flip = input_data == QtCore.Qt.Checked
                    case 2:  # Y flip
                        current_sprite_part.y_flip = input_data == QtCore.Qt.Checked
                    case 3:  # X pos
                        current_sprite_part.x_offset = int(input_data, 0)
                    case 4:  # Y pos
                        current_sprite_part.y_offset = int(input_data, 0)
                    case 5:  # use matrix
                        current_sprite_part.rot_scale_flag = input_data == QtCore.Qt.Checked
                    case 6:  # matrix 0
                        current_sprite_part.matrix[0] = float(input_data)
                    case 7:  # matrix 1
                        current_sprite_part.matrix[1] = float(input_data)
                    case 8:  # matrix 3
                        current_sprite_part.matrix[3] = float(input_data)
                    case 9:  # matrix 4
                        current_sprite_part.matrix[4] = float(input_data)
                    case 10: # mouse input
                        modifiers = QtGui.QGuiApplication.keyboardModifiers()
                        if (QtCore.Qt.ShiftModifier in modifiers):
                            current_sprite_part.matrix[0] += input_data.x() / 20
                            current_sprite_part.matrix[4] += input_data.y() / 20
                        elif (QtCore.Qt.ControlModifier in modifiers):
                            current_sprite_part.matrix[1] += input_data.x() / 20
                            current_sprite_part.matrix[3] += input_data.y() / 20
                        else:
                            current_sprite_part.x_offset += input_data.x()
                            current_sprite_part.y_offset += input_data.y()
            
                self.update_sprite_part_editor_field()
        
        current_anim = self.animation_data.all_anims[self.anim_list_box.currentRow()]
        current_frame = current_anim.frame_list[self.frame_timeline_bar.value()]

        if (current_frame.sprite_index == current_sprite):
            self.update_sprite_window()
        return
    
    def update_sprite_part_editor_field(self):
        #print("update_sprite_part_editor_field")

        # update the customization fields
        current_sprite = int(self.sprite_selector.currentText(), 0)
        part_list = self.animation_data.all_sprites[current_sprite].part_list
        
        if (self.sprite_part_selector.currentText() != "None"):
            current_sprite_part = int(self.sprite_part_selector.currentText(), 0)
        else:
            current_sprite_part = -1

        if (self.sprite_part_selector.currentText() != "None"):
            self.part_tile_box.setValue(part_list[current_sprite_part].tile_index)
            self.part_tile_box.setEnabled(True)
            self.part_tile_text.setEnabled(True)
            self.part_x_flip_box.setChecked(part_list[current_sprite_part].x_flip)
            self.part_x_flip_box.setEnabled(True)
            self.part_y_flip_box.setChecked(part_list[current_sprite_part].y_flip)
            self.part_y_flip_box.setEnabled(True)
            self.part_x_pos_box.setValue(part_list[current_sprite_part].x_offset)
            self.part_x_pos_box.setEnabled(True)
            self.part_x_pos_text.setEnabled(True)
            self.part_y_pos_box.setValue(part_list[current_sprite_part].y_offset)
            self.part_y_pos_box.setEnabled(True)
            self.part_y_pos_text.setEnabled(True)

            self.part_use_matrix_box.setChecked(part_list[current_sprite_part].rot_scale_flag)
            self.part_use_matrix_box.setEnabled(True)
            if (self.part_use_matrix_box.isChecked()):
                self.part_matrix_a_box.setValue(part_list[current_sprite_part].matrix[0])
                self.part_matrix_a_box.setEnabled(True)
                self.part_matrix_a_text.setEnabled(True)
                self.part_matrix_b_box.setValue(part_list[current_sprite_part].matrix[1])
                self.part_matrix_b_box.setEnabled(True)
                self.part_matrix_b_text.setEnabled(True)
                self.part_matrix_c_box.setValue(part_list[current_sprite_part].matrix[3])
                self.part_matrix_c_box.setEnabled(True)
                self.part_matrix_c_text.setEnabled(True)
                self.part_matrix_d_box.setValue(part_list[current_sprite_part].matrix[4])
                self.part_matrix_d_box.setEnabled(True)
                self.part_matrix_d_text.setEnabled(True)
            else:
                self.part_matrix_a_box.setValue(1)
                self.part_matrix_a_box.setEnabled(False)
                self.part_matrix_a_text.setEnabled(False)
                self.part_matrix_b_box.setValue(0)
                self.part_matrix_b_box.setEnabled(False)
                self.part_matrix_b_text.setEnabled(False)
                self.part_matrix_c_box.setValue(0)
                self.part_matrix_c_box.setEnabled(False)
                self.part_matrix_c_text.setEnabled(False)
                self.part_matrix_d_box.setValue(1)
                self.part_matrix_d_box.setEnabled(False)
                self.part_matrix_d_text.setEnabled(False)

            self.part_pixel_mode_box.setValue(part_list[current_sprite_part].pixel_mode)
            self.part_pixel_mode_box.setEnabled(True)
            self.part_pixel_mode_text.setEnabled(True)
            self.part_unk0_box.setValue(part_list[current_sprite_part].unk0)
            self.part_unk0_box.setEnabled(True)
            self.part_unk0_text.setEnabled(True)
            self.part_unk1_box.setValue(part_list[current_sprite_part].unk1)
            self.part_unk1_box.setEnabled(True)
            self.part_unk1_text.setEnabled(True)
            self.part_unk2_box.setValue(part_list[current_sprite_part].unk2)
            self.part_unk2_box.setEnabled(True)
            self.part_unk2_text.setEnabled(True)
        else:
            self.part_tile_box.setValue(0)
            self.part_tile_box.setEnabled(False)
            self.part_tile_text.setEnabled(False)
            self.part_x_flip_box.setChecked(False)
            self.part_x_flip_box.setEnabled(False)
            self.part_y_flip_box.setChecked(False)
            self.part_y_flip_box.setEnabled(False)
            self.part_x_pos_box.setValue(0)
            self.part_x_pos_box.setEnabled(False)
            self.part_x_pos_text.setEnabled(False)
            self.part_y_pos_box.setValue(0)
            self.part_y_pos_box.setEnabled(False)
            self.part_y_pos_text.setEnabled(False)

            self.part_use_matrix_box.setChecked(False)
            self.part_use_matrix_box.setEnabled(False)
            self.part_matrix_a_box.setValue(1)
            self.part_matrix_a_box.setEnabled(False)
            self.part_matrix_a_text.setEnabled(False)
            self.part_matrix_b_box.setValue(0)
            self.part_matrix_b_box.setEnabled(False)
            self.part_matrix_b_text.setEnabled(False)
            self.part_matrix_c_box.setValue(0)
            self.part_matrix_c_box.setEnabled(False)
            self.part_matrix_c_text.setEnabled(False)
            self.part_matrix_d_box.setValue(1)
            self.part_matrix_d_box.setEnabled(False)
            self.part_matrix_d_text.setEnabled(False)

            self.part_pixel_mode_box.setValue(0)
            self.part_pixel_mode_box.setEnabled(False)
            self.part_pixel_mode_text.setEnabled(False)
            self.part_unk0_box.setValue(0)
            self.part_unk0_box.setEnabled(False)
            self.part_unk0_text.setEnabled(False)
            self.part_unk1_box.setValue(0)
            self.part_unk1_box.setEnabled(False)
            self.part_unk1_text.setEnabled(False)
            self.part_unk2_box.setValue(0)
            self.part_unk2_box.setEnabled(False)
            self.part_unk2_text.setEnabled(False)

        self.part_tile_box.setMaximum(len(self.animation_data.all_tiles) - 1)

        # update the tile viewer
        self.part_tile_canvas.fill(QtCore.Qt.transparent)
        qp = QtGui.QPainter(self.part_tile_canvas)

        if (self.sprite_part_selector.currentText() != "None"):
            if (part_list[int(self.sprite_part_selector.currentText(), 0)].tile_index != -1):
                current_tile = self.animation_data.all_tiles[part_list[int(self.sprite_part_selector.currentText(), 0)].tile_index]
                tile_x = current_tile.x_size
                tile_y = current_tile.y_size
            else:
                img = Image.open("files/missing texture.png")
                tile_x = 16
                tile_y = 16
            tile_scale = 1
            sprite_part_x_offset = (self.part_tile_canvas.width() // 2) - ((tile_x * tile_scale) // 2) - 2
            sprite_part_y_offset = (self.part_tile_canvas.height() // 2) - ((tile_y * tile_scale) // 2) - 2

            if (part_list[int(self.sprite_part_selector.currentText(), 0)].tile_index != -1):
                img = current_tile.cached_tile.copy()
                if (self.animation_data.header.sprite_mode == 0 or self.animation_data.header.sprite_mode == 3):
                    img.putalpha(255)

            img = ImageOps.scale(img, tile_scale, 0)
            img = ImageOps.expand(img, border = (1, 1), fill = (255, 255, 255, 255))
            img = ImageOps.expand(img, border = (1, 1), fill = (243, 151, 16, 255))

            qimg = ImageQt(img)
            qp.drawImage(int(sprite_part_x_offset), int(sprite_part_y_offset), qimg)

        qp.end()
        self.part_tile_window.setPixmap(self.part_tile_canvas)

        # update the transform viewer
        self.part_transform_canvas.fill(QtCore.Qt.GlobalColor.gray)
        qp = QtGui.QPainter(self.part_transform_canvas)

        tex = Image.open("files/missing texture.png")
        tex = ImageOps.scale(tex, 2, 0)

        img = Image.new("RGBA", (64, 64))
        img.paste(tex, (16, 16))

        if (self.part_use_matrix_box.isChecked()):
            input_matrix = [float(self.part_matrix_a_box.text()), float(self.part_matrix_b_box.text()), 0, float(self.part_matrix_c_box.text()), float(self.part_matrix_d_box.text()), 0]
            matrix = calculate_from_matrix(input_matrix, (-img.width // 2, -img.height // 2), True)
            img = img.transform(img.size, Image.AFFINE, matrix)
    
        img = ImageOps.expand(img, border = (1, 1), fill = (255, 255, 255, 255))
        img = ImageOps.expand(img, border = (1, 1), fill = (243, 151, 16, 255))

        qimg = ImageQt(img)
        qp.drawImage(0, 0, qimg)

        qp.end()
        self.part_transform_window.setPixmap(self.part_transform_canvas)

        # update the part viewing window
        scale = 1

        self.sprite_part_editor_canvas.fill(QtCore.Qt.GlobalColor.gray)
        qp = QtGui.QPainter(self.sprite_part_editor_canvas)

        qp.setPen(QtGui.QPen(QtGui.QColor(23, 250, 101), 2))
        qp.drawLine(self.sprite_part_editor_canvas.width() // 2, 0, self.sprite_part_editor_canvas.width() // 2, self.sprite_part_editor_canvas.height())

        qp.setPen(QtGui.QPen(QtGui.QColor(246, 25, 17), 2))
        qp.drawLine(0, self.sprite_part_editor_canvas.height() // 2, self.sprite_part_editor_canvas.width(), self.sprite_part_editor_canvas.height() // 2)

        img_size = (self.sprite_part_editor_canvas.width() // scale, self.sprite_part_editor_canvas.height() // scale)
        img_all_tiles = self.animation_data.all_tiles

        if (self.sprite_part_selector.currentText() == "None"):
            img_sprite_part = -1
        else:
            img_sprite_part = len(part_list) - current_sprite_part - 1

        img = create_assembled_sprite(img_size, part_list, img_all_tiles, img_sprite_part)

        img = ImageOps.scale(img, scale, 0)

        qimg = ImageQt(img)
        qp.drawImage(0, 0, qimg)
        
        qp.end()
        self.sprite_part_editor_window.setPixmap(self.sprite_part_editor_canvas)

    def update_tile_painter(self):
        #print("update_tile_painter")

        # update the tile painter itself
        self.tile_canvas.fill(QtCore.Qt.transparent)
        qp = QtGui.QPainter(self.tile_canvas)

        try:
            current_tile = self.animation_data.all_tiles[self.tile_grid.currentRow()]
            tile_scale = 5
            sprite_part_x_offset = (self.tile_canvas.width() // 2) - ((current_tile.x_size * tile_scale) // 2) - 2
            sprite_part_y_offset = (self.tile_canvas.height() // 2) - ((current_tile.y_size * tile_scale) // 2) - 2

            img = current_tile.cached_tile.copy()
            if (self.animation_data.header.sprite_mode == 0 or self.animation_data.header.sprite_mode == 3):
                img.putalpha(255)
            
            img = ImageOps.scale(img, tile_scale, 0)
            img = ImageOps.expand(img, border = (1, 1), fill = (255, 255, 255, 255))
            img = ImageOps.expand(img, border = (1, 1), fill = (243, 151, 16, 255))

            qimg = ImageQt(img)
            qp.drawImage(int(sprite_part_x_offset), int(sprite_part_y_offset), qimg)
        except:
            print("tile display error in tile view!")
        finally:
            qp.end()
            self.tile_painter.setPixmap(self.tile_canvas)

        # with open('test_temp.bin', 'wb') as tempwrite:
        #     tempwrite.write(self.animation_data.export_graphics_and_animation_files())

        # update the palette picker
        self.palette_canvas.fill(QtCore.Qt.GlobalColor.gray)
        qp = QtGui.QPainter(self.palette_canvas)

        try:
            pal_scale = 12
            pal = Image.new("RGBA", ((16 * pal_scale) - 1, (16 * pal_scale) - 1))
            pal_shadow = Image.new("RGBA", (pal_scale - 3, pal_scale - 3))
            pal_shadow = ImageOps.expand(pal_shadow, border = (0, 0, 1, 1), fill = (0, 0, 0, 51))
            pal_shadow = ImageOps.expand(pal_shadow, border = (1, 1, 0, 0), fill = (255, 255, 255, 51))

            for i in range(self.animation_data.palette_size // 2):
                pal_color = Image.frombytes("RGBA", (1, 1), bytearray(self.animation_data.current_pal[i] + [255]))

                pal_color = ImageOps.scale(pal_color, pal_scale - 1, 0)
                pal_color.paste(pal_shadow, (0, 0), pal_shadow)

                pal.paste(pal_color, ((i % 16) * pal_scale, (i // 16) * pal_scale))

            pal = ImageOps.expand(pal, border = (1, 1), fill = (0, 0, 0, 0))

            pal_outline_sizes = [(16, 16), (16, 2), (8, 1), (16, 1)]
            shift_x, shift_y = pal_outline_sizes[self.animation_data.header.sprite_mode]
            pal_outline = Image.new("RGBA", ((shift_x * pal_scale) - 1, (shift_y * pal_scale) - 1))
            pal_outline = ImageOps.expand(pal_outline, border = (1, 1), fill = (255, 255, 255, 255))

            pal = ImageOps.expand(pal, border = (1, 1), fill = (0, 0, 0, 0))
            pal_outline = ImageOps.expand(pal_outline, border = (1, 1), fill = (243, 151, 16, 255))

            pal.paste(pal_outline, (0, (current_tile.pal_shift // 16) * pal_scale), pal_outline)

            qpal = ImageQt(pal)
            qp.drawImage(0, 0, qpal)
        except:
            print("palette display error in tile view!")
        finally:
            qp.end()
            self.palette_picker.setPixmap(self.palette_canvas)
    
    def update_animation_state(self):
        #print("update_animation_state")
        if (self.animation_timer.isActive()):
            self.animation_timer.stop()
            self.play_button.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.MediaPlaybackStart))
        else:
            self.frame_timeline_bar.setValue(0)
            self.anim_time = 0
            self.animation_timer.start()
            self.play_button.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.MediaPlaybackStop))
    
    def update_loop_state(self):
        if (self.loop_animation):
            self.loop_button.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.MediaSkipForward))
            self.loop_animation = False
        else:
            self.loop_button.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewRefresh))
            self.loop_animation = True
    
    def update_animation_timeline(self):
        #print("update_animation_timeline")
        current_anim = self.animation_data.all_anims[self.anim_list_box.currentRow()]
        current_frame = current_anim.frame_list[self.frame_timeline_bar.value()]
        
        if (current_frame.frame_timer <= self.anim_time):
            if (self.frame_timeline_bar.value() < self.frame_timeline_bar.maximum()):
                self.frame_timeline_bar.setValue(self.frame_timeline_bar.value() + 1)
            else:
                if (self.loop_animation):
                    self.anim_time = 0
                    self.frame_timeline_bar.setValue(0)
                else:
                    self.animation_timer.stop()
                    self.play_button.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.MediaPlaybackStart))
        
        self.anim_time += 1
    
    def apply_affine_matrix(self, img):
        # TO DO: figure what the fuck this is all about
        # right now i'm not properly getting shear, but that's irrelevant bc this data is not anywhere near precise enough
        # like goddamn, this is tough as FUCK
        # for now i'm just gonna pass the matrix data straight from the game into the sprite drawer
        # i'll worry about abstracting usable values from this shit later
        # fuck matrices

        # m_translation, m_rotation, m_scale, m_shear = calculate_from_matrix(True, bytearray([0xF5, 0x00, 0x48, 0x00, 0xB7, 0xFF, 0xF5, 0x00, 0x00, 0x00, 0xF5, 0xFF]))

        # matrix = Affine.translation(m_translation[0], m_translation[1])
        # matrix *= matrix.rotation(m_rotation)
        # matrix *= matrix.scale(m_scale[0], m_scale[1])
        # matrix *= matrix.shear(m_shear[0], m_shear[1])

        # img = img.transform(img.size, Image.AFFINE, matrix)

        # print(matrix)
        # print(calculate_from_matrix(True, bytearray([0xF5, 0x00, 0x48, 0x00, 0xB7, 0xFF, 0xF5, 0x00, 0x00, 0x00, 0xF5, 0xFF]), True))
        return img

    # def label_clicked(self, event):
    #     x = event.pos().x()
    #     y = event.pos().y()
    #     print(f"Clicked at ({x}, {y})")

    def export_gif(self):
        scale = 1

        current_anim = self.animation_data.all_anims[self.anim_list_box.currentRow()]
        sprite_list = []
        img_size = (1024, 1024)

        for current_frame in current_anim.frame_list:
            img_part_list = self.animation_data.all_sprites[current_frame.sprite_index].part_list
            img_all_tiles = self.animation_data.all_tiles

            img = create_assembled_sprite(img_size, img_part_list, img_all_tiles, -1)

            if (current_frame.rot_scale_flag):
                matrix = calculate_from_matrix(current_frame.matrix, (-img.width // 2, -img.height // 2), True)
                img = img.transform(img.size, Image.AFFINE, matrix)

            img = ImageOps.scale(img, scale, 0)
            sprite_list.append(img)
        
        test_img = Image.new("RGBA", img_size)
        test_img = ImageOps.scale(test_img, scale, 0)
        for image in sprite_list:
            test_img.alpha_composite(image)
        img_crop = test_img.getbbox()
        sprite_list_out = []
        for image in sprite_list:
            sprite_list_out.append(image.crop(img_crop))

        timer = 0
        frame_number = 0
        image_list = []

        for current_time in range(current_anim.frame_list[len(current_anim.frame_list) - 1].frame_timer):
            current_frame = current_anim.frame_list[frame_number]

            if current_frame.frame_timer == timer:
                frame_number += 1
                current_frame = current_anim.frame_list[frame_number]

            image_list.append(sprite_list_out[frame_number])
            # image_list.append(sprite_list_out[current_frame.sprite_index]) # for the funny version of the export

            timer += 1

        os.makedirs('gif exports', exist_ok=True)

        file_name = f'gif exports/{self.file_selector.currentText()}_group{int(self.sprite_group_selector.currentText(), 0):04x}_anim{self.anim_list_box.currentRow():04x}.gif'
        image_list[0].save(file_name, save_all = True, append_images = image_list[1:], optimize = True, duration = 20, loop = 0, disposal = 2)

        playsound("files/special_attack_piece_jingle.mp3", False)

        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle("GIF Exported")
        dlg.setText("GIF successfully exported!\n\nThe file has been placed in the program's 'gif exports' directory.")
        dlg.exec()
    
class DraggableQLabel(QtWidgets.QLabel):
    mouseDragged = QtCore.Signal(QtCore.QPoint)
    mouseReleased = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dragging = False
        self.last_pos = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = True
            self.last_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = event.globalPos() - self.last_pos
            self.mouseDragged.emit(delta)
            self.last_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = False
            self.mouseReleased.emit()
