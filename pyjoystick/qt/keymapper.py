"""
    bt_controller.keymapper
    SeaLandAire Technologies
    @author: jengel
"""
import os
import threading
from qtpy import QtCore, QtGui, QtWidgets

from pyjoystick.interface import Joystick
from pyjoystick.qt.widgets import AxisWidget, ButtonWidget, HatWidget, SpinSlider, LED
from pyjoystick.resources import JOYSTICK_ACTIVE_IMG, JOYSTICK_INACTIVE_IMG


__all__ = ["JOYSTICK_ACTIVE_IMG", "JOYSTICK_INACTIVE_IMG",
           'JoystickKeyMapperMixin', 'JoystickKeyMapper', 'JoystickKeyMapperDialog']


class JoystickKeyMapperMixin(object):
    """Help the user map the keys."""

    Joystick = Joystick

    JOYSTICK_ACTIVE_IMG = JOYSTICK_ACTIVE_IMG
    JOYSTICK_INACTIVE_IMG = JOYSTICK_INACTIVE_IMG

    def __init__(self, joystick=None, event_mngr=None, **kwargs):
        super().__init__()

        self._event_mngr = None
        self._joystick = None
        self._joysticks = []
        self.btns_per_row = 5
        self._lock = None

        # Qt variables
        self.main_layout = None
        self.name_lay = None
        self.name_lbl = None
        self.deadband_layout = None
        self.deadband_input = None
        self.axis_layout = None
        self.button_layout = None
        self.hat_layout = None
        self.ball_layout = None
        self.sel_btn = None
        self._dialog = None

        self.init(joystick=joystick, event_mngr=event_mngr)

    def init(self, joystick=None, event_mngr=None):
        self._event_mngr = None
        self._joystick = None
        self._joysticks = []
        self.btns_per_row = 5

        self.init_layout()

        # Items
        self._lock = threading.Lock()
        if joystick is not None:
            self.sel_btn.hide()
            self.set_joystick(joystick)

        if event_mngr is not None:
            self.set_event_mngr(event_mngr)

    def init_layout(self):
        # Layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        # Joystick name
        self.name_lbl = QtWidgets.QLabel("Joystick Name")
        self.name_lbl.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        font = self.name_lbl.font()
        font.setPointSize(12)
#         font.setWeight(QtWidgets.QFont.Bold)
        self.name_lbl.setFont(font)
        self.name_lay = QtWidgets.QHBoxLayout()
        self.name_lay.addWidget(self.name_lbl, alignment=QtCore.Qt.AlignLeft)
        self.main_layout.addLayout(self.name_lay)

        self.deadband_input = QtWidgets.QDoubleSpinBox()
        self.deadband_input.setToolTip('Give the joystick some dead space for the analog sticks.\n'
                                       'This helps analog sticks rest at 0.')
        self.deadband_input.setMinimum(0)
        self.deadband_input.setMaximum(1)
        self.deadband_input.setDecimals(4)
        self.deadband_input.valueChanged.connect(self.set_deadband)
        self.deadband_layout = QtWidgets.QFormLayout()
        self.deadband_layout.addRow(QtWidgets.QLabel('Deadband: '), self.deadband_input)
        self.main_layout.addLayout(self.deadband_layout)

        
        # Button layouts
        lbl = QtWidgets.QLabel("Axes (Analog sticks or triggers):")
        lbl.setToolTip("Values are scaled -100.0 to 100.0 for the slider display.\n"
                       "real values are -1.0 to 1.0")
        self.main_layout.addWidget(lbl)
        self.axis_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.axis_layout)

        self.main_layout.addWidget(QtWidgets.QLabel("Buttons:"))
        self.button_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.button_layout)

        self.main_layout.addWidget(QtWidgets.QLabel("Hats (D-pads):"))
        self.hat_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.hat_layout)

        self.main_layout.addWidget(QtWidgets.QLabel("Track Balls:"))
        self.ball_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.ball_layout)

        # Select joystick button
        self.sel_btn = QtWidgets.QPushButton("Select Joystick")
        self.sel_btn.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.sel_btn.clicked.connect(self.select_joystick)
        self.name_lay.addWidget(self.sel_btn, alignment=QtCore.Qt.AlignLeft)
        self._dialog = None

    def get_event_mngr(self):
        """Return the event manager."""
        return self._event_mngr

    def set_event_mngr(self, value):
        """Set the event manager."""
        self._event_mngr = value
        try:
            self._event_mngr.add_joystick = self.add_joystick
            self._event_mngr.remove_joystick = self.remove_joystick
            self._event_mngr.handle_key_event = self.handle_key_event
            self._event_mngr.start()
        except:
            pass

    event_mngr = property(get_event_mngr, set_event_mngr)

    def add_joystick(self, joy):
        """Add the joystick that was found."""
        self._joysticks.append(joy)

    def remove_joystick(self, joy):
        """Remove teh joystick that was removed."""
        try:
            self._joysticks.remove(joy)
        except:
            pass

    def handle_key_event(self, key):
        """Handle the given key that an event occurred on."""
        if self.joystick != key.joystick:
            return

        if key.keytype == key.AXIS:
            self.set_axes_values(key)
        elif key.keytype == key.BUTTON:
            self.set_button_values(key)
        elif key.keytype == key.HAT:
            self.set_hat_values(key)
        elif key.keytype == key.BALL:
            self.set_ball_values(key)

    def get_joysticks(self):
        """Return a list of joysticks."""
        return self._joysticks

    def select_joystick(self):
        """Select a gamepad if there is no joystick selected."""
        try: self._dialog.close()
        except AttributeError: pass

        self._dialog = QtWidgets.QDialog()
        layout = QtWidgets.QVBoxLayout()
        self._dialog.setLayout(layout)
        
        # Joysticks
        btngroup = QtWidgets.QButtonGroup()
        btngroup.setExclusive(True)
        for item in self.get_joysticks():
            btn = QtWidgets.QRadioButton(item.get_name())
            layout.addWidget(btn)
            btngroup.addButton(btn)

        # Accept method        
        def select():
            btn = btngroup.checkedButton()
            joystick = None
            if btn is not None:
                name = btn.text()
                for joy in self.get_joysticks():
                    if joy.get_name() == name:
                        joystick = joy
                        break
            self.set_joystick(joystick)
            self._dialog.close()

        # Buttons
        accept = QtWidgets.QPushButton("Select")
        accept.clicked.connect(select)
        cancel = QtWidgets.QPushButton("Cancel")
        cancel.clicked.connect(self._dialog.close)

        # Button layout
        hlay = QtWidgets.QHBoxLayout()
        hlay.addWidget(accept, alignment=QtCore.Qt.AlignRight)
        hlay.addWidget(cancel, alignment=QtCore.Qt.AlignRight)
        layout.addLayout(hlay)
        self._dialog.show()

    def _clear_layout(self, layout):
        """Clear a layout."""
        while layout.itemAt(0) is not None:
            item = layout.takeAt(0)
            try:
                obj = item.widget()
                if obj is None:
                    obj = item.layout()
                    self._clear_layout(obj)
                    obj.setParent(None)
                    obj.deleteLater()
                else:
                    obj.close()
                    obj.setParent(None)
                    obj.deleteLater()
            except AttributeError:
                pass
            del item

    def removeWidgets(self):
        """Remove all of the testing widgets."""
        self._clear_layout(self.axis_layout)
        self._clear_layout(self.button_layout)
        self._clear_layout(self.hat_layout)
        self._clear_layout(self.ball_layout)

    def createWidgets(self, joystick=None):
        """Initialize the widgets."""
        self.removeWidgets()

        self.deadband_input.setValue(joystick.deadband)

        for i in range(joystick.get_numaxes()):
            widg = AxisWidget("Axis "+str(i))
            self.axis_layout.addWidget(widg)

        btn_lay = []
        for i in range(joystick.get_numbuttons()):
            if (i % self.btns_per_row) == 0:
                btn_lay.append(QtWidgets.QHBoxLayout())
                self.button_layout.addLayout(btn_lay[-1])
            widg = ButtonWidget("Button "+str(i)+":")
            btn_lay[-1].addWidget(widg)

        for i in range(joystick.get_numhats()):
            widg = HatWidget("Hat "+str(i)+":")
            self.hat_layout.addWidget(widg)

        for i in range(joystick.get_numballs()):
            widg = HatWidget("Ball "+str(i)+":")
            self.ball_layout.addWidget(widg)

    def get_joystick(self):
        """Return the active joystick."""
        return self._joystick

    def set_joystick(self, joystick):
        """Set the active joystick."""
        if joystick is None:
            self.removeWidgets()
            return

        # Try to get the proper joystick for this event loop
        try:
            event_mngr = self.get_event_mngr()
            if joystick not in event_mngr.joysticks:
                event_mngr.save_joystick(joystick)
            joystick = event_mngr.joysticks[joystick]
        except (AttributeError, IndexError, KeyError, Exception):
            pass

        self._joystick = joystick
        self.createWidgets(self._joystick)
        try:
            self.name_lbl.setText(self._joystick.get_name())
        except:
            pass

    joystick = property(get_joystick, set_joystick)

    def set_deadband(self, value):
        try:
            self.joystick.set_deadband(value)
        except:
            pass

    def set_axes_values(self, key):
        try:
            self.axis_layout.itemAt(key.number).widget().setValue(key.get_value())
        except AttributeError:
            pass

    def set_button_values(self, key):
        try:
            btn_lay = self.button_layout.itemAt(int(key.number // self.btns_per_row)).layout()
            btn_lay.itemAt(key.number % self.btns_per_row).widget().setValue(key.get_value())
        except AttributeError:
            pass

    def set_hat_values(self, key):
        try:
            self.hat_layout.itemAt(key.number).widget().setValue(key.get_value())
        except AttributeError:
            pass

    def set_ball_values(self, key):
        try:
            self.ball_layout.itemAt(key.number).widget().setValue(key.get_value())
        except AttributeError:
            pass

    def closeEvent(self, *args, **kwargs):
        try:
            self._event_mngr.stop()
        except:
            pass
        return QtWidgets.QWidget.closeEvent(self, *args, **kwargs)


class JoystickKeyMapper(QtWidgets.QWidget, JoystickKeyMapperMixin):
    """Help the user map the keys."""
    def __init__(self, joystick=None, event_mngr=None, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.init(joystick=joystick, event_mngr=event_mngr)


class JoystickKeyMapperDialog(QtWidgets.QDialog, JoystickKeyMapperMixin):
    """Help the user map the keys."""
    def __init__(self, joystick=None, event_mngr=None, parent=None):
        QtWidgets.QDialog.__init__(self, parent=parent)
        self.init(joystick=joystick, event_mngr=event_mngr)


if __name__ == "__main__":
    import sys
    from pyjoystick import ThreadEventManager, ButtonHatRepeater
    from pyjoystick.run_process import MultiprocessingEventManager
    from pyjoystick.sdl2 import Joystick, run_event_loop
    # from pyjoystick.pygame import Joystick, run_event_loop

    app = QtWidgets.QApplication([])

    w = JoystickKeyMapperDialog(event_mngr=ThreadEventManager(run_event_loop, button_repeater=ButtonHatRepeater()))  # , activity_timeout=0.02))
    # w = JoystickKeyMapper(event_mngr=MultiprocessingEventManager(run_event_loop, button_repeater=ButtonHatRepeater()))  # , activity_timeout=0.02))
    w.show()

    sys.exit(app.exec_())
