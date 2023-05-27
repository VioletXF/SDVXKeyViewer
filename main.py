from PyQt5 import QtCore, QtGui, QtWidgets

import pygame as pg, os, configparser
config = configparser.ConfigParser()
config.read("settings.ini")

app = QtWidgets.QApplication([])
import math

UNIT_SIZE = config.getint("Size", "unit", fallback=100)
SCROLL_TO_RESIZE = config.getboolean("Size", "scroll_to_resize", fallback=True)

ALWAYS_ON_TOP = config.getboolean("Other", "always_on_top", fallback=False)
RESET_COUNTS_ON_START = config.getboolean("Other", "reset_counts_on_start", fallback=False)
FPS = config.getint("Other", "polling_rate", fallback=240)

BG_OPACITY = int(config.getfloat("Colors", "bg_opacity", fallback=1) * 255)
BUTTON_LED_OPACITY = int(config.getfloat("Colors", "button_led_opacity", fallback=1) * 255)
TEXT_OPACITY = int(config.getfloat("Colors", "text_opacity", fallback=1) * 255)
TSUMAMI_INDICATOR_OFF_OPACITY = int(config.getfloat("Colors", "tsumami_indicator_off_opacity", fallback=0.2) * 255)
TSUMAMI_INDICATOR_ON_OPACITY = int(config.getfloat("Colors", "tsumami_indicator_on_opacity", fallback=1) * 255)
TSUMAMI_LED_OPACITY = int(config.getfloat("Colors", "tsumami_led_opacity", fallback=0.2) * 255)

WINDOW_WIDTH = int(math.ceil(UNIT_SIZE * 7.5))+1
WINDOW_HEIGHT = int(math.ceil(UNIT_SIZE * 4))
WINDOW_RATIO = WINDOW_WIDTH / WINDOW_HEIGHT
font = QtGui.QFont()

START_BG_COLOR = QtGui.QColor(255, 255, 255, BG_OPACITY)
START_LED_COLOR = QtGui.QColor(0, 115, 229, BUTTON_LED_OPACITY)

BT_BG_COLOR = QtGui.QColor(255, 255, 255, BG_OPACITY)
BT_LED_COLOR = QtGui.QColor(0, 115, 229, BUTTON_LED_OPACITY)

FX_BG_COLOR = QtGui.QColor(255, 255, 255, BG_OPACITY)
FX_LED_COLOR = QtGui.QColor(255, 33, 12, BUTTON_LED_OPACITY)

TEXT_COLOR = QtGui.QColor(0, 0, 0, TEXT_OPACITY)
TEXT_PRESSED_COLOR = QtGui.QColor(255, 255, 255, TEXT_OPACITY)

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        if ALWAYS_ON_TOP:
            self.setWindowFlags(
                QtCore.Qt.WindowFlags(QtCore.Qt.WindowType.FramelessWindowHint) | QtCore.Qt.WindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)
            )
        else:
            self.setWindowFlags(
                QtCore.Qt.WindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
            )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.center()

        self.oldPos = self.pos()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        super().closeEvent(a0)
        global running
        running = False
        app.quit()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        qp = QtGui.QPainter()

        qp.begin(self)
        qp.setFont(font)
        self.draw_background(qp)
        self.draw_start(qp)
        for i in range(4):
            self.draw_btn(qp, i)
        for i in range(2):
            self.draw_fx(qp, i)
        self.draw_tsumami(qp, False)
        self.draw_tsumami(qp, True)
        qp.end()

    def draw_background(self, qp: QtGui.QPainter):
        # transparent background
        qp.setPen(QtGui.QColor(0, 0, 0, 1))
        qp.setBrush(QtGui.QColor(0, 0, 0, 1))
        qp.drawRect(0, 0, self.width(), self.height())

    def draw_start(self, qp: QtGui.QPainter):
        x = UNIT_SIZE * 5 // 2 + UNIT_SIZE
        y = UNIT_SIZE //8
        color = (
            START_LED_COLOR if start_pressed else START_BG_COLOR
        )
        qp.setPen(color)
        qp.setBrush(color)
        qp.drawRect(x, y, UNIT_SIZE // 2, UNIT_SIZE // 2)

    def draw_btn(self, qp: QtGui.QPainter, num):
        # draw num-th BT
        pressed = bt_pressed[num]
        x = num * UNIT_SIZE * 3 // 2 + UNIT_SIZE
        y = UNIT_SIZE * 3 // 2
        color = BT_LED_COLOR if pressed else BT_BG_COLOR
        qp.setPen(color)
        qp.setBrush(color)
        qp.drawRect(x, y, UNIT_SIZE, UNIT_SIZE)

        # draw press count at center
        text_color = TEXT_PRESSED_COLOR if pressed else TEXT_COLOR
        qp.setPen(text_color)
        qp.drawText(
            QtCore.QRect(x, y, UNIT_SIZE, UNIT_SIZE),
            QtCore.Qt.AlignmentFlag.AlignCenter,
            str(bt_counts[num]),
        )

    def draw_fx(self, qp: QtGui.QPainter, num):
        # draw num-th FX
        pressed = fx_pressed[num]
        x = num * UNIT_SIZE * 3 + UNIT_SIZE * 5 // 4 - UNIT_SIZE // 2 + UNIT_SIZE
        y = UNIT_SIZE * 3 // 2 + UNIT_SIZE * 2
        color = FX_LED_COLOR if pressed else FX_BG_COLOR
        qp.setPen(color)
        qp.setBrush(color)
        qp.drawRect(x, y, UNIT_SIZE, UNIT_SIZE // 2)

        # draw press count at center
        text_color = TEXT_PRESSED_COLOR if pressed else TEXT_COLOR
        qp.setPen(text_color)
        qp.drawText(
            QtCore.QRect(x, y, UNIT_SIZE, UNIT_SIZE // 2),
            QtCore.Qt.AlignmentFlag.AlignCenter,
            str(fx_counts[num]),
        )


    def draw_tsumami(self, qp: QtGui.QPainter, right):
        global tsumami_l_angle, tsumami_r_angle, tsumami_l_turning, tsumami_r_turning, tsumami_l_clockwise, tsumami_r_clockwise
        tsumami_size = UNIT_SIZE * 3 // 4
        angle = tsumami_r_angle if right else tsumami_l_angle
        is_clockwise = tsumami_r_clockwise if right else tsumami_l_clockwise

        turning = tsumami_r_turning if right else tsumami_l_turning
        # blue for left, red for right
        indicator_opacity = TSUMAMI_INDICATOR_ON_OPACITY if turning else TSUMAMI_INDICATOR_OFF_OPACITY
        indicator_color = QtGui.QColor(255, 0, 0, indicator_opacity) if right else QtGui.QColor(0, 0, 255, indicator_opacity) 

        pos = [UNIT_SIZE * 6 + UNIT_SIZE // 2 + UNIT_SIZE // 4, 0] if right else [0, 0]
        # draw white at center
        qp.setPen(QtGui.QColor(255, 255, 255, BG_OPACITY))
        qp.setBrush(QtGui.QColor(255, 255, 255, BG_OPACITY))
        qp.drawEllipse(pos[0], pos[1], tsumami_size, tsumami_size)

        bg_color = QtGui.QColor(255, 0, 0) if right else QtGui.QColor(0, 0, 255)
        bg_color.setAlpha(TSUMAMI_LED_OPACITY) if turning else bg_color.setAlpha(0)
        qp.setPen(bg_color)
        qp.setBrush(bg_color)
        qp.drawEllipse(pos[0], pos[1], tsumami_size, tsumami_size)

        # draw red or right dots. calculate dots' position by angle
        dot_size = tsumami_size // 5
        inner_tsunami_size = tsumami_size - dot_size * 2
        qp.setPen(QtGui.QColor(indicator_color))
        qp.setBrush(QtGui.QColor(indicator_color))
        qp.drawEllipse(
            int(
                pos[0]
                + tsumami_size / 2
                - dot_size / 2
                + math.cos(math.radians(angle)) * inner_tsunami_size / 2
            ),
            int(
                pos[1]
                + tsumami_size / 2
                - dot_size / 2
                + math.sin(math.radians(angle)) * inner_tsunami_size / 2
            ),
            dot_size,
            dot_size,
        )

        # draw right arrow for clockwise, left arrow for counter-clockwise
        arrow_size = tsumami_size // 4
        arrow_pos = [
            pos[0] + tsumami_size // 2 - arrow_size // 2,
            pos[1] + tsumami_size // 2 - arrow_size // 2,
        ]
        arrow_color = indicator_color

        qp.setPen(arrow_color)
        qp.setBrush(arrow_color)
        if is_clockwise:
            qp.drawPolygon(
                
                    QtCore.QPoint(arrow_pos[0], arrow_pos[1]),
                    QtCore.QPoint(arrow_pos[0] + arrow_size, arrow_pos[1]+ arrow_size // 2),
                    QtCore.QPoint(arrow_pos[0], arrow_pos[1] + arrow_size),
                
            )
        else:
            qp.drawPolygon(
                
                    QtCore.QPoint(arrow_pos[0]+arrow_size, arrow_pos[1]),
                    QtCore.QPoint(arrow_pos[0], arrow_pos[1]+arrow_size//2),
                    QtCore.QPoint(arrow_pos[0] + arrow_size, arrow_pos[1] + arrow_size),
                
            )

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        global UNIT_SIZE
        UNIT_SIZE = int(self.width() / 7.5)
        font.setPixelSize(UNIT_SIZE//10*4)
        return super().resizeEvent(a0)

    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        if SCROLL_TO_RESIZE:
            if a0.angleDelta().y() > 0:
                new_width = self.width() + UNIT_SIZE
                self.resize(new_width, int(new_width / WINDOW_RATIO))
            else:
                if self.width() <= 200:
                    return
                new_width = self.width() - UNIT_SIZE
                self.resize(new_width, int(new_width / WINDOW_RATIO))
        return super().wheelEvent(a0)
    
    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        global fx_counts, bt_counts, running;
        # on delete, reset all counts
        if a0.key() == QtCore.Qt.Key.Key_Delete:
            fx_counts = [0, 0]
            bt_counts = [0, 0, 0, 0]
            self.update()
        # on esc, close window
        elif a0.key() == QtCore.Qt.Key.Key_Escape:
            running = False
            self.close()

        return super().keyPressEvent(a0)


main = MainWindow()




main.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
main.show()


bt_key_codes = [
    int(config["Keys"]["bt_a"]),
    int(config["Keys"]["bt_b"]),
    int(config["Keys"]["bt_c"]),
    int(config["Keys"]["bt_d"]),
]
fx_key_codes = [int(config["Keys"]["fx_l"]), int(config["Keys"]["fx_r"])]
start_key_code = int(config["Keys"]["start"])

os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
pg.init()
pg.joystick.init()


clock = pg.time.Clock()
joysticks = [pg.joystick.Joystick(x) for x in range(pg.joystick.get_count())]
running = True



bt_counts = [0 for _ in range(4)]
fx_counts = [0 for _ in range(2)]

start_pressed = False
bt_pressed = [False for _ in range(4)]
fx_pressed = [False for _ in range(2)]

tsumami_l_angle = float(-90)
tsumami_r_angle = float(-90)
tsumami_l_clockwise = True
tsumami_r_clockwise = True
tsumami_l_turning = False
tsumami_r_turning = False


def keydown(event):
    global start_pressed, bt_pressed, fx_pressed, bt_counts, fx_counts
    if event.button == start_key_code:
        start_pressed = True

    for i in range(4):
        if event.button == bt_key_codes[i]:
            bt_pressed[i] = True
            bt_counts[i] += 1
    for i in range(2):
        if event.button == fx_key_codes[i]:
            fx_pressed[i] = True
            fx_counts[i] += 1


def keyup(event):
    global start_pressed, bt_pressed, fx_pressed, bt_counts, fx_counts
    if event.button == start_key_code:
        start_pressed = False
        if RESET_COUNTS_ON_START:
            bt_counts = [0, 0, 0, 0]
            fx_counts = [0, 0]
    for i in range(4):
        if event.button == bt_key_codes[i]:
            bt_pressed[i] = False
    for i in range(2):
        if event.button == fx_key_codes[i]:
            fx_pressed[i] = False


def tsumami(event):
    global tsumami_l_angle, tsumami_r_angle, tsumami_l_turning, tsumami_r_turning, tsumami_l_clockwise, tsumami_r_clockwise
    angle = event.value * 180 + 180

    if event.axis == 0:
        tsumami_l_turning = True
        delta = angle - tsumami_l_angle
        is_clockwise = delta > 0
        if tsumami_l_angle == 360 and angle <= 0:
            is_clockwise = True
        if angle == 360 and tsumami_l_angle <= 0:
            is_clockwise = False
        tsumami_l_clockwise = is_clockwise
        tsumami_l_angle = angle
    if event.axis == 1:
        tsumami_r_turning = True
        delta = angle - tsumami_r_angle
        is_clockwise = delta > 0
        if tsumami_r_angle == 360 and angle <= 0:
            is_clockwise = True
        if angle == 360 and tsumami_r_angle <= 0:
            is_clockwise = False
        tsumami_r_clockwise = is_clockwise
        tsumami_r_angle = angle


while running:
    if pg.joystick.get_count() != len(joysticks):
        joysticks = [pg.joystick.Joystick(x) for x in range(pg.joystick.get_count())]
    tsumami_l_turning = False
    tsumami_r_turning = False
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.JOYBUTTONDOWN:
            keydown(event)
        if event.type == pg.JOYBUTTONUP:
            keyup(event)
        if event.type == pg.JOYAXISMOTION:
            tsumami(event)

    clock.tick(FPS)
    main.repaint()


pg.joystick.quit()
pg.quit()
