==========
pyjoystick
==========

Python joystick event handler.


Simple Example
==============

.. code-block:: python

    from pyjoystick.sdl2 import Key, Joystick, run_event_loop

    def print_add(joy):
        print('Added', joy)

    def print_remove(joy):
        print('Removed', joy)

    def key_received(key):
        print('Key:', key)
        if key.keytype == Key.BUTTON and key.number == 0:
            if key.value == 1:
                # Button 0 pressed
                print("Do action!")
            else:
                # Button 0 released
                pass

    run_event_loop(print_add, print_remove, key_received)


Qt Integration
==============

The code below displays a label with the most recent key's value.
A green ball will move around as you press the HAT button on the controller.

.. code-block:: python

    # App with a green ball in the center that moves when you press the HAT buttons
    import pyjoystick
    from pyjoystick.sdl2 import Key, Joystick, run_event_loop
    # from pyjoystick.pygame import Key, Joystick, run_event_loop
    from qt_thread_updater import ThreadUpdater

    from qtpy import QtWidgets, QtGui, QtCore


    app = QtWidgets.QApplication()

    updater = ThreadUpdater()

    main = QtWidgets.QWidget()
    main.setLayout(QtWidgets.QHBoxLayout())
    main.resize(800, 600)
    main.show()

    lbl = QtWidgets.QLabel()  # Absolute positioning
    main.layout().addWidget(lbl, alignment=QtCore.Qt.AlignTop)

    mover = QtWidgets.QLabel(parent=main)  # Absolute positioning
    mover.resize(50, 50)
    mover.point = main.rect().center()
    mover.move(mover.point)
    mover.show()

    def svg_paint_event(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(painter.Antialiasing, True)

        # Get Black Background
        rect = self.rect()
        center = rect.center()
        radius = 20

        # Colors
        painter.setBrush(QtGui.QColor('green'))  # Fill color
        painter.setPen(QtGui.QColor('black'))  # Line Color

        # Draw
        painter.drawEllipse(center, radius, radius)

        painter.end()

    mover.paintEvent = svg_paint_event.__get__(mover, mover.__class__)

    def handle_key_event(key):
        updater.now_call_latest(lbl.setText, '{}: {} = {}'.format(key.joystick, key, key.value))

        # print(key, '-', key.keytype, '-', key.number, '-', key.value)

        if key.keytype != Key.HAT:
            return

        if key.value == Key.HAT_UP:
            mover.point.setY(mover.point.y() - 10)
        elif key.value == Key.HAT_DOWN:
            mover.point.setY(mover.point.y() + 10)
        if key.value == Key.HAT_LEFT:
            mover.point.setX(mover.point.x() - 10)
        elif key.value == Key.HAT_UPLEFT:
            mover.point.setX(mover.point.x() - 5)
            mover.point.setY(mover.point.y() - 5)
        elif key.value == Key.HAT_DOWNLEFT:
            mover.point.setX(mover.point.x() - 5)
            mover.point.setY(mover.point.y() + 5)
        elif key.value == Key.HAT_RIGHT:
            mover.point.setX(mover.point.x() + 10)
        elif key.value == Key.HAT_UPRIGHT:
            mover.point.setX(mover.point.x() + 5)
            mover.point.setY(mover.point.y() - 5)
        elif key.value == Key.HAT_DOWNRIGHT:
            mover.point.setX(mover.point.x() + 5)
            mover.point.setY(mover.point.y() + 5)
        updater.now_call_latest(mover.move, mover.point)

    # If it button is held down it should be repeated
    repeater = pyjoystick.HatRepeater(first_repeat_timeout=0.5, repeat_timeout=0.03, check_timeout=0.01)

    mngr = pyjoystick.ThreadEventManager(event_loop=run_event_loop,
                                         handle_key_event=handle_key_event,
                                         button_repeater=repeater)
    mngr.start()

    # Find key functionality
    btn = QtWidgets.QPushButton('Find Key:')

    def find_key():
        key = mngr.find_key(timeout=float('inf'))
        if key is None:
            btn.setText('Find Key:')
        else:
            btn.setText('Find Key: {} = {}'.format(key, key.value))

    btn.clicked.connect(find_key)
    main.layout().addWidget(btn, alignment=QtCore.Qt.AlignTop)

    app.exec_()
