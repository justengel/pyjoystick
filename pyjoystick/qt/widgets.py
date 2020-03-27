import threading
from qtpy import QtWidgets, QtGui, QtCore

from pyjoystick.qt.widget_updater import get_updater


__all__ = ['AxisWidget', 'ButtonWidget', 'HatWidget', 'SpinSlider', 'LED']


class AxisWidget(QtWidgets.QWidget):
    def __init__(self, title=""):
        super().__init__()

        # Layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self._value = 0
        self.title = QtWidgets.QLabel(title)
        self.slider = SpinSlider(-100.0, 100.0, decimals=2)
        self.slider.setReadOnly(True)
        self.slider.setTickInterval(10)
        self.slider.setMinimumHeight(200)
        self.slider.setOrientation(QtCore.Qt.Vertical)
        self.slider.setValue(0)

        self.main_layout.addWidget(self.slider)
        self.main_layout.addWidget(self.title)
    # end Constructor

    def value(self):
        return self._value

    def setValue(self, value):
        self._value = value * 100
        get_updater().now_call_latest(self.slider.setValue, self._value)  # Only need latest value displayed


class ButtonWidget(QtWidgets.QWidget):
    def __init__(self, title=""):
        super().__init__()

        # Layout
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)

        self._value = 0
        self.title = QtWidgets.QLabel(title)
        self.led = LED()
        self.led.setValue(0)

        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.led)

        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)

    def value(self):
        return self._value

    def setValue(self, value):
        self._value = value
        get_updater().now_call_in_main(self.led.setValue, self._value)  # Show every value change


class HatWidget(QtWidgets.QWidget):
    def __init__(self, title=""):
        super().__init__()

        # Layout
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)

        self._value = ""
        self.title = QtWidgets.QLabel(title)
        self.edit = QtWidgets.QLineEdit()
        self.edit.setMaximumWidth(100)
        self.edit.setReadOnly(True)

        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.edit)

        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)

    def value(self):
        return self._value

    def setValue(self, value):
        self._value = str(value)
        get_updater().now_call_in_main(self.edit.setText, self._value)  # Show every value change


class SpinSlider(QtWidgets.QWidget):
    """Custom slider that displays the minimum, maximum, and spinbox next to the slider to aid in
    usability.

    Args:
        minimum (int)[None]: Minimum value
        maximum (int)[None]: Maximum value
        decimals (int)[0]: Number of decimals to display and control.
    """
    # Signals
    actionTriggered = QtCore.Signal(object)
    rangeChanged = QtCore.Signal(object, object)
    sliderMoved = QtCore.Signal(object)
    sliderPressed = QtCore.Signal()
    sliderReleased = QtCore.Signal()
    valueChanged = QtCore.Signal(object)

    # Slider class attributes
    TickPosition = QtWidgets.QSlider.TickPosition
    NoTicks = QtWidgets.QSlider.NoTicks
    TicksAbove = QtWidgets.QSlider.TicksAbove
    TicksBelow = QtWidgets.QSlider.TicksBelow
    TicksBothSides = QtWidgets.QSlider.TicksBothSides
    TicksLeft = QtWidgets.QSlider.TicksLeft
    TicksRight = QtWidgets.QSlider.TicksRight

    SliderAction = QtWidgets.QSlider.SliderAction
    SliderMove = QtWidgets.QSlider.SliderMove
    SliderNoAction = QtWidgets.QSlider.SliderNoAction
    SliderPageStepAdd = QtWidgets.QSlider.SliderPageStepAdd
    SliderPageStepSub = QtWidgets.QSlider.SliderPageStepSub
    SliderSingleStepAdd = QtWidgets.QSlider.SliderSingleStepAdd
    SliderSingleStepSub = QtWidgets.QSlider.SliderSingleStepSub
    SliderToMaximum = QtWidgets.QSlider.SliderToMaximum
    SliderToMinimum = QtWidgets.QSlider.SliderToMinimum

    SliderChange = QtWidgets.QSlider.SliderChange
    SliderOrientationChange = QtWidgets.QSlider.SliderOrientationChange
    SliderRangeChange = QtWidgets.QSlider.SliderRangeChange
    SliderStepsChange = QtWidgets.QSlider.SliderStepsChange
    SliderValueChange = QtWidgets.QSlider.SliderValueChange

    # SpinBox class attributes
    ButtonSymbols = QtWidgets.QDoubleSpinBox.ButtonSymbols
    NoButtons = QtWidgets.QDoubleSpinBox.NoButtons
    PlusMinus = QtWidgets.QDoubleSpinBox.PlusMinus
    UpDownArrows = QtWidgets.QDoubleSpinBox.UpDownArrows

    CorrectionMode = QtWidgets.QDoubleSpinBox.CorrectionMode
    CorrectToNearestValue = QtWidgets.QDoubleSpinBox.CorrectToNearestValue
    CorrectToPreviousValue = QtWidgets.QDoubleSpinBox.CorrectToPreviousValue

    StepEnabledFlag = QtWidgets.QDoubleSpinBox.StepEnabledFlag
    StepDownEnabled = QtWidgets.QDoubleSpinBox.StepDownEnabled
    StepNone = QtWidgets.QDoubleSpinBox.StepNone
    StepUPEnabled = QtWidgets.QDoubleSpinBox.StepUpEnabled

    def __init__(self, minimum=0, maximum=99, decimals=0, parent=None):
        super().__init__(parent)

        # Widgets
        self.spinbox = QtWidgets.QDoubleSpinBox()
        self.slider = QtWidgets.QSlider()
        self._min = QtWidgets.QLabel("0")
        self._max = QtWidgets.QLabel("99")
        self._value = 0

        # Check Inputs
        self.setDecimals(decimals)
        self.setRange(minimum, maximum)
        self.setValue(minimum)

        # Create the layout
        self.main_layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight)
        self.setLayout(self.main_layout)
        self.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.main_layout.addWidget(self.spinbox)
        self.main_layout.addWidget(self._min)
        self.main_layout.addWidget(self.slider)
        self.main_layout.addWidget(self._max)

        # Style
        self.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setFocusPolicy(QtCore.Qt.NoFocus)  # Keyboard up and down -> spinbox

        # Signals
        self.slider.actionTriggered.connect(self.actionTriggered.emit)
        self.slider.rangeChanged.connect(self.rangeChanged.emit)
        self.slider.sliderMoved.connect(self.sliderMoved.emit)
        self.slider.sliderPressed.connect(self.sliderPressed.emit)
        self.slider.sliderReleased.connect(self.sliderReleased.emit)
        self.slider.valueChanged.connect(self._value_changed)
        self.spinbox.valueChanged.connect(self._value_changed)

    def _value_changed(self, value):
        """Sync the spinbox and slider values."""
        if self.spinbox.value() != value:
            self.spinbox.blockSignals(True)
            self.spinbox.setValue(value)
            self.spinbox.blockSignals(False)
        if self.slider.value() != value:
            self.slider.blockSignals(True)
            self.slider.setValue(value)
            self.slider.blockSignals(False)
        self.valueChanged.emit(self.spinbox.value())

    def isReadOnly(self):
        return self.spinbox.isReadOnly()

    def setReadOnly(self, value):
        self.slider.setEnabled(not value)
        self.spinbox.setReadOnly(value)
        if value:
            self.spinbox.setButtonSymbols(QtWidgets.QDoubleSpinBox.NoButtons)
        else:
            self.spinbox.setButtonSymbols(QtWidgets.QDoubleSpinBox.UpDownArrows)

    def decimals(self):
        """Return the decimals.

        Returns:
            decimals (int): Number of decimals that are available. 0 Means a regular spin box is used.
        """
        return self.spinbox.decimals()

    def setDecimals(self, decimals):
        """Set the number of decimals.

        Args:
            decimals (int): Number of decimals to display.
        """
        self.spinbox.setDecimals(decimals)
        if decimals > 0:
            single_step = float("0."+str(1).zfill(decimals))
            self.spinbox.setSingleStep(single_step)
            self.slider.setSingleStep(single_step)
        elif self.spinbox.singleStep() < 1:
            self.spinbox.setSingleStep(1)
            self.slider.setSingleStep(1)

    def minimum(self):
        """Return the minimum range value."""
        return self.slider.minimum()

    def setMinimum(self, minimum):
        """Set the minimum range value.

         Note:
             The default value is 0.

        Args:
            minimum (int/flaot): Minimum value.
        """
        self.slider.setMinimum(minimum)
        self.spinbox.setMinimum(minimum)
        self._min.setText(str(self.minimum()))

    def maximum(self):
        """Return the maximum range value."""
        return self.slider.maximum()

    def setMaximum(self, maximum):
        """Set the maximum range value.

        Note:
             The default value is 99.

        Args:
            maximum (int/flaot): Maximum value.
        """
        self.slider.setMaximum(maximum)
        self.spinbox.setMaximum(maximum)
        self._max.setText(str(self.maximum()))

    def setRange(self, minimum, maximum):
        """Set the min and max range.

        Args:
            minimum (int/flaot): Minimum value.
            maximum (int/flaot): Maximum value.
        """
        # flip
        if minimum > maximum:
            temp = minimum
            minimum = maximum
            maximum = temp

        self.slider.setRange(minimum, maximum)
        self.spinbox.setRange(minimum, maximum)

        self._min.setText(str(self.minimum()))
        self._max.setText(str(self.maximum()))

    def singleStep(self):
        return self.spinbox.singleStep()

    def setSingleStep(self, value):
        self.spinbox.setSingleStep(value)
        self.slider.setSingleStep(value)

    def hasTracking(self):
        return self.slider.hasTracking()

    def setTracking(self, value):
        """Set if the valueChanged signal should be activated whenever the slider is moved."""
        self.slider.setTracking(value)
        self.spinbox.setKeyboardTracking(value)

    def specialValueText(self):
        """This property holds the special-value text.

        If set, the spin box will display this text instead of a numeric value whenever the
        current value is equal to minimum(). Typical use is to indicate that this choice has
        a special (default) meaning.

        See Also:
            QAbstractSpinBox.specialValueText
        """
        return self.spinbox.specialValueText()

    def setSpecialValueText(self, text):
        self.spinbox.setSpecialValueText(text)

    # ========== Slider Override ==========
    def tickInterval(self):
        return self.slider.tickInterval()

    def setTickInterval(self, ti):
        if self.tickPosition() == QtWidgets.QSlider.NoTicks:
            self.slider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.slider.setTickInterval(ti)

    def tickPosition(self):
        return self.slider.tickPosition()

    def setTickPosition(self, position):
        self.slider.setTickPosition(position)

    def invertedAppearance(self):
        """Return if the appearance is inverted."""
        return self.slider.invertedAppearance()

    def setInvertedAppearance(self, value):
        """Set the slider inverted appearance.

        Args:
            value (bool): Is the appearance backwards?
        """
        self.slider.setInvertedAppearance(value)
        self.setOrientation(self.orientation())

    def invertedControls(self):
        return self.slider.invertedControls()

    def setInvertedControls(self, value):
        """Set if the keyboard controls for the slider should be inverted."""
        self.slider.setInvertedControls(value)

    def isSliderDown(self):
        """Return if the slider is pressed down."""
        return self.slider.isSliderDown()

    def setSliderDown(self, value):
        self.slider.setSliderDown(value)

    def orientation(self):
        """Return the slider orientation."""
        return self.slider.orientation()

    def setOrientation(self, orientation):
        """Set the orientation."""
        self.slider.setOrientation(orientation)
        if orientation == QtCore.Qt.Horizontal:
            self.main_layout.insertWidget(1, self._min)
            self.main_layout.insertWidget(3, self._max)
            if self.invertedAppearance():
                self.main_layout.setDirection(QtWidgets.QBoxLayout.RightToLeft)
            else:
                self.main_layout.setDirection(QtWidgets.QBoxLayout.LeftToRight)
        else:
            self.main_layout.insertWidget(3, self._min)
            self.main_layout.insertWidget(1, self._max)
            if self.invertedAppearance():
                self.main_layout.setDirection(QtWidgets.QBoxLayout.BottomToTop)
            else:
                self.main_layout.setDirection(QtWidgets.QBoxLayout.TopToBottom)

    def pageStep(self):
        return self.slider.pageStep()

    def setPageStep(self, value):
        self.slider.setPageStep(value)

    def repeatAction(self):
        return self.slider.repeatAction()

    def setRepeatAction(self, action, thresholdTime=5000, repeatTime=50):
        self.slider.setRepeatAction(action, thresholdTime, repeatTime)

    def sliderPosition(self):
        return self.slider.sliderPosition()

    def setSliderPosition(self, value):
        self.slider.setSliderPosition(value)

    def triggerAction(self, action):
        self.slider.triggerAction(action)

    def value(self):
        """Return the value."""
        return self._value

    def setValue(self, value):
        self._value = value
        get_updater().now_call_latest(self.slider.setValue, self._value)   # Only need latest value displayed
        get_updater().now_call_latest(self.spinbox.setValue, self._value)  # Only need latest value displayed

    def sliderChange(self, change):
        self.slider.sliderChange(change)

    # ========== SpinBox Override ==========
    def setCleanText(self, value):
        try:
            value = float(value)
        except: pass
        self.setValue(value)

    def cleanText(self):
        return self.spinbox.cleanText()

    def prefix(self):
        return self.spinbox.prefix()

    def setPrefix(self, prefix):
        self.spinbox.setPrefix(prefix)

    def suffix(self):
        return self.spinbox.suffix()

    def setSuffix(self, suffix):
        self.spinbox.setSuffix(suffix)

    def textFromValue(self, val):
        return self.spinbox.textFromValue(val)

    def valueFromText(self, text):
        return self.spinbox.valueFromText(text)


class LED(QtWidgets.QWidget):
    """Display for showing an LED light color.

    This class can be used to show a Text Label and LED light or just an LED light. This class is
    also capable of making the LED a clickable button.
    """

    clicked = QtCore.Signal()

    def __init__(self, state=None):
        super().__init__()
        self.setObjectName("LED")
        self.setMinimumSize(14, 14)

        # Properties
        self._state = None
        self._colors = {}
        self._value = QtGui.QColor(255, 0, 0)
        self.alert_time = 1000
        self._timer_arg = "blank"
        self._alert_timer = QtCore.QTimer()
        self._alert_timer.setSingleShot(True)
        self._alert_timer.timeout.connect(self.alert_timeout)

        # Button Properties
        self._seq_iter = None
        self._btn_seq = None

        # Add Default Colors
        self.addColor("red", QtGui.QColor(255, 0, 0))
        self.addColor(0, QtGui.QColor(255, 0, 0))
        self.addColor("off", QtGui.QColor(255, 0, 0))
        self.addColor("no", QtGui.QColor(255, 0, 0))

        self.addColor("green", QtGui.QColor(0, 255, 0))
        self.addColor(1, QtGui.QColor(0, 255, 0))
        self.addColor("on", QtGui.QColor(0, 255, 0))
        self.addColor("yes", QtGui.QColor(0, 255, 0))

        self.addColor("yellow", QtGui.QColor(255, 255, 0))
        self.addColor(2, QtGui.QColor(255, 255, 0))

        self.addColor("blank", QtGui.QColor(225, 225, 225))
        self.addColor("gray", QtGui.QColor(225, 225, 225))
        self.addColor("grey", QtGui.QColor(225, 225, 225))
        self.addColor("colorless", QtGui.QColor(225, 225, 225))
        self.addColor(3, QtGui.QColor(225, 225, 225))

        self.addColor("blue", QtGui.QColor(65, 65, 255))
        self.addColor(4, QtGui.QColor(65, 65, 255))

        self.addColor("orange", QtGui.QColor(255, 153, 0))
        self.addColor(5, QtGui.QColor(255, 153, 0))

        # self.setButtonSequence([0, 1])
        self.setState(state)

    def state(self):
        """Return the current state identifier of the LED."""
        return self._state

    def activeColor(self):
        """Return the active QColor of the LED."""
        return self._value

    def buttonSequence(self):
        """Return the button sequence list of states to change to on button click."""
        return self._btn_seq

    def value(self):
        """Gets the state. This method was made to be an interchangeable
        method with TextIndicator.
        """
        return self.state()

    def setValue(self, value):
        """Sets the LED State. This method was made to be an interchangeable
        method with TextIndicator.

        Args:
            value(key): Color key state to set the LED color.
        """
        self.setState(value)

    def setColor(self, value):
        self.setState(value)

    def setColors(self, colors):
        """A dictionary or list of colors.

        Args:
            colors(list):list of strings (rgb, rgba, or hex) or a list of QtGui.QColor's.
        """
        for color in colors:
            color = self.checkColor(color)
        self._colors = colors

        self.setState(self._state)

    def addColor(self, state, color):
        """Add a color to the color changing dictionary."""
        color = self.checkColor(color)
        self._colors[state] = color

    def setState(self, state):
        """Set the state of the LED and show the color for that state."""
        self._state = state
        try:
            color = self._colors[state]
        except KeyError:
            try:
                state = int(state)
            except(ValueError, TypeError):
                state = str(state)
            try:
                color = self._colors[state]
            except KeyError:
                color = self._colors["blank"]

        self._value = color
        self.update()

    @staticmethod
    def checkColor(color):
        """Check the given color and return a valid color."""
        valid_color = None
        if isinstance(color, str) and "," in color:
            valid_color = QtGui.QColor(color)

        elif isinstance(color, list):
            if len(color) == 4:
                valid_color = QtGui.QColor(color[0], color[1], color[2], color[3])
            else:
                valid_color = QtGui.QColor(color[0], color[1], color[2])

        elif isinstance(color, QtGui.QColor):
            valid_color = color

        return valid_color

    def setButtonSequence(self, sequence):
        """States for the color of the sequence. Allows button presses to cycle through a sequence.

        Args:
            sequence(iterable): Sequence of states when pressing the button.
        """
        self._btn_seq = sequence
        self._seq_iter = iter(self._btn_seq)

        self.clicked.connect(self.cycle_colors)

    def alert(self, timeout=None, color="red", timeout_color="blank"):
        """Change the color for a given time then change back to the timeout_color.

        Args:
            timeout (int)[None]: Time in seconds. If None use alert_time property
            color (str)["red"]: Color to immediately change to.
            timeout_color (str)["blank"]: Color to reset the LED to after the timeout.
        """
        if timeout is None:
            timeout = self.alert_time
        self.setColor(color)
        self._timer_arg = timeout_color

        self._alert_timer.stop()
        self._alert_timer.start(timeout)

    def alert_timeout(self):
        """Method to run after the alert time to clear the alert LED."""
        self.setState(self._timer_arg)

    def cycle_colors(self):
        """Cycle Colors."""
        try:
            next_state = next(self._seq_iter)
        except StopIteration:
            self._seq_iter = iter(self._btn_seq)
            next_state = next(self._seq_iter)
        # end

        self.setState(next_state)

    def mousePressEvent(self, event):
        """Override to activate button click and change to the next state."""
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit()

    def paintEvent(self, event):
        """Overrides the default paintEvent method to create the widget's
        display.

        Args:
            event: needed for paintEvent super class method override
        """
        painter = QtGui.QPainter(self)
        painter.setRenderHint(painter.Antialiasing, True)

        # Get Black Background
        rect_back = self.getBackgroundRect()
        center = rect_back.center()
        radius = rect_back.width() + 0.0

        # Draw Black Background
        grad = QtGui.QRadialGradient(center, radius)
        grad.setColorAt(0.0, QtGui.QColor(255, 255, 255, 10))
        grad.setColorAt(0.90, QtGui.QColor(0, 0, 0, 255))
        grad.setColorAt(0.98, QtGui.QColor(0, 0, 0, 100))
        grad.setColorAt(1.0, QtGui.QColor(0, 0, 0, 255))
        painter.setPen(QtGui.QColor(0, 0, 0))
        painter.setBrush(grad)
        painter.drawEllipse(center, radius, radius)

        # Get LED
        rect_val = self.getValueRect()
        center = rect_val.center()
        radius = rect_val.width() + 0.0

        # Draw LED
        red = self._value.red()
        green = self._value.green()
        blue = self._value.blue()
        grad = QtGui.QRadialGradient(center, radius)
        grad.setColorAt(0.0, QtGui.QColor(red, green, blue, 100))
        grad.setColorAt(0.95, QtGui.QColor(red, green, blue, 255))
        grad.setColorAt(1.0, QtGui.QColor(red, green, blue, 100))
        painter.setPen(self._value)
        painter.setBrush(grad)
        painter.drawEllipse(center, radius, radius)

        painter.end()

    def getValueRect(self):
        """Return the value rectangel container."""
        width = self.width()
        height = self.height()

        radius = min(width/2, height/2)
        center = QtCore.QPoint(width/2, height/2)
        back_r = radius - radius/50
        led_r = back_r - back_r/10
        rect_val = self.rect()

        # Set the LED
        rect_val.setWidth(led_r)
        rect_val.setHeight(led_r)
        rect_val.moveCenter(center)

        return rect_val

    def getBackgroundRect(self):
        """Return the background rectangel container."""
        width = self.width()
        height = self.height()

        radius = min(width/2, height/2)
        center = QtCore.QPoint(width/2, height/2)
        back_r = radius - radius/50
        rect_back = self.rect()

        # Set the LED
        rect_back.setWidth(back_r)
        rect_back.setHeight(back_r)
        rect_back.moveCenter(center)

        return rect_back
