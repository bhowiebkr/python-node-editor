from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

from node_editor.gui.port import Pin
from enum import Enum


class Node_Status(Enum):
    CLEAN = 1
    DIRTY = 2
    ERROR = 3


class Node(QtWidgets.QGraphicsItem):
    """
    A QGraphicsPathItem representing a node in the node editor.

    Attributes
    ----------
    node_color : QtGui.QColor
        The color of the node.
    _title_text : str
        The text of the node's title.
    _type_text : str
        The text of the node's type.
    _width : int
        The width of the node.
    _height : int
        The height of the node.
    _pins : list
        A list of pins connected to this node.
    title_path : QtGui.QPainterPath
        The path for the title of the node.
    type_path : QtGui.QPainterPath
        The path for the type of the node.
    misc_path : QtGui.QPainterPath
        The path for miscellaneous items.
    horizontal_margin : int
        The horizontal margin of the node.
    vertical_margin : int
        The vertical margin of the node.

    """

    def __init__(self):
        super().__init__()

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)

        self._title_text = "Title"
        self._title_color = QtGui.QColor(123, 33, 177)
        self.size = QtCore.QRectF()  # Size of
        self.status = Node_Status.DIRTY

        self.widget = QtWidgets.QWidget()
        self.widget.resize(0, 0)

        self._type_text = "base"

        self._width = 20  # The Width of the node
        self._height = 20  # the height of the node
        self._pins = []  # A list of pins
        self.uuid = None  # An identifier to used when saving and loading the scene

        self.node_color = QtGui.QColor(20, 20, 20, 200)

        self.title_path = QtGui.QPainterPath()  # The path for the title
        self.type_path = QtGui.QPainterPath()  # The path for the type
        self.misc_path = QtGui.QPainterPath()  # a bunch of other stuff
        self.status_path = QtGui.QPainterPath()  # A path showing the status of the node

        self.horizontal_margin = 15  # horizontal margin
        self.vertical_margin = 15  # vertical margin

    def get_status_color(self):
        if self.status == Node_Status.CLEAN:
            return QtGui.QColor(0, 255, 0)
        elif self.status == Node_Status.DIRTY:
            return QtGui.QColor(255, 165, 0)
        elif self.status == Node_Status.ERROR:
            return QtGui.QColor(255, 0, 0)

    def boundingRect(self):
        return self.size

    def set_color(self, title_color=(123, 33, 177), background_color=(20, 20, 20, 200)):
        self._title_color = QtGui.QColor(title_color[0], title_color[1], title_color[2])
        self.node_color = QtGui.QColor(background_color[0], background_color[1], background_color[2])

    @property
    def title(self):
        return self._title_text

    @title.setter
    def title(self, title):
        self._title_text = title

    @property
    def type_text(self):
        return self._type_text

    @type_text.setter
    def type_text(self, type_text):
        self._type_text = type_text

    def paint(self, painter, option=None, widget=None):
        """
        Paints the node on the given painter.

        Args:
            painter (QtGui.QPainter): The painter to use for drawing the node.
            option (QStyleOptionGraphicsItem): The style options to use for drawing the node (optional).
            widget (QWidget): The widget to use for drawing the node (optional).
        """

        painter.setPen(self.node_color.lighter())
        painter.setBrush(self.node_color)
        painter.drawPath(self.path)

        gradient = QtGui.QLinearGradient()
        gradient.setStart(0, -90)
        gradient.setFinalStop(0, 0)
        gradient.setColorAt(0, self._title_color)  # Start color (white)
        gradient.setColorAt(1, self._title_color.darker())  # End color (blue)

        painter.setBrush(QtGui.QBrush(gradient))
        painter.setPen(self._title_color)
        painter.drawPath(self.title_bg_path.simplified())

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.white)

        painter.drawPath(self.title_path)
        painter.drawPath(self.type_path)
        painter.drawPath(self.misc_path)

        # Status path
        painter.setBrush(self.get_status_color())
        painter.setPen(self.get_status_color().darker())
        painter.drawPath(self.status_path.simplified())

        # Draw the highlight
        if self.isSelected():
            painter.setPen(QtGui.QPen(self._title_color.lighter(), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(self.path)

    def get_pin(self, name):
        for pin in self._pins:
            if pin.name() == name:
                return pin

    def add_pin(self, name, is_output=False, execution=False):
        """
        Adds a new pin to the node.

        Args:
            name (str): The name of the new pin.
            is_output (bool, optional): True if the new pin is an output pin, False if it's an input pin. Default is False.
            flags (int, optional): A set of flags to apply to the new pin. Default is 0.
            ptr (Any, optional): A pointer to associate with the new pin. Default is None.

        Returns:
            None: This method doesn't return anything.

        """
        pin = Pin(self, self.scene())
        pin.set_is_output(is_output)
        pin.set_name(name)
        pin.set_node(node=self)
        pin.set_execution(execution)

        self._pins.append(pin)

    def build(self):
        """
        Builds the node by constructing its graphical representation.

        This method calculates the dimensions of the node, sets the fonts for various elements, and adds the necessary
        graphical components to the node, such as the title, type, and pins. Once the graphical representation of the node
        is constructed, the `setPath` method is called to set the path for the node.

        Returns:
            None.
        """

        self.init_widget()  # configure the widget side of things. We need to get the size of the widget before building the rest of the node
        self.widget.setStyleSheet("background-color: " + self.node_color.name() + ";")
        self.title_path = QtGui.QPainterPath()  # reset
        self.type_path = QtGui.QPainterPath()  # The path for the type
        self.misc_path = QtGui.QPainterPath()  # a bunch of other stuff

        bg_height = 35  # background title height

        total_width = self.widget.size().width()
        self.path = QtGui.QPainterPath()  # The main path
        # The fonts what will be used
        title_font = QtGui.QFont("Lucida Sans Unicode", pointSize=12)
        title_type_font = QtGui.QFont("Lucida Sans Unicode", pointSize=8)
        pin_font = QtGui.QFont("Lucida Sans Unicode")

        # Get the dimentions of the title and type
        title_dim = {
            "w": QtGui.QFontMetrics(title_font).horizontalAdvance(self._title_text),
            "h": QtGui.QFontMetrics(title_font).height(),
        }

        title_type_dim = {
            "w": QtGui.QFontMetrics(title_type_font).horizontalAdvance(f"{self._type_text}"),
            "h": QtGui.QFontMetrics(title_type_font).height(),
        }

        # Get the max width
        for dim in [title_dim["w"], title_type_dim["w"]]:
            if dim > total_width:
                total_width = dim

        # Add both the title and type height together for the total height
        # total_height = sum([title_dim["h"], title_type_dim["h"]]) + self.widget.size().height()
        total_height = bg_height + self.widget.size().height()

        pin_dim = None
        # Add the heigth for each of the pins
        exec_height_added = False
        for pin in self._pins:
            pin_dim = {
                "w": QtGui.QFontMetrics(pin_font).horizontalAdvance(pin.name()),
                "h": QtGui.QFontMetrics(pin_font).height(),
            }

            if pin_dim["w"] > total_width:
                total_width = pin_dim["w"]

            if pin.is_execution() and not exec_height_added or not pin.is_execution():
                total_height += pin_dim["h"]
                exec_height_added = True

        # Add the margin to the total_width
        total_width += self.horizontal_margin
        # total_height += self.vertical_margin

        # Draw the background rectangle
        self.size = QtCore.QRectF(-total_width / 2, -total_height / 2, total_width, total_height)
        self.path.addRoundedRect(-total_width / 2, -total_height / 2, total_width, total_height + 10, 5, 5)

        # Draw the status rectangle
        self.status_path.setFillRule(Qt.WindingFill)
        self.status_path.addRoundedRect(total_width / 2 - 12, -total_height / 2 + 2, 10, 10, 2, 2)
        # self.status_path.addRect(total_width / 2 - 10, -total_height / 2, 5, 5)
        # self.status_path.addRect(total_width / 2 - 10, -total_height / 2 + 15, 5, 5)
        # self.status_path.addRect(total_width / 2 - 5, -total_height / 2 + 15, 5, 5)

        # The color on the title
        self.title_bg_path = QtGui.QPainterPath()  # The title background path
        self.title_bg_path.setFillRule(Qt.WindingFill)
        self.title_bg_path.addRoundedRect(-total_width / 2, -total_height / 2, total_width, bg_height, 5, 5)
        self.title_bg_path.addRect(-total_width / 2, -total_height / 2 + bg_height - 10, 10, 10)  # bottom left corner
        self.title_bg_path.addRect(total_width / 2 - 10, -total_height / 2 + bg_height - 10, 10, 10)  # bottom right corner

        # Draw the title
        self.title_path.addText(
            -total_width / 2 + 5,
            (-total_height / 2) + title_dim["h"] / 2 + 5,
            title_font,
            self._title_text,
        )

        # Draw the type
        self.type_path.addText(
            -total_width / 2 + 5,
            (-total_height / 2) + title_dim["h"] + 5,
            title_type_font,
            f"{self._type_text}",
        )

        # Position the pins. Execution pins stay on the same row
        if pin_dim:
            # y = (-total_height / 2) + title_dim["h"] + title_type_dim["h"] + 5
            y = bg_height - total_height / 2 - 10

            # Do the execution pins
            exe_shifted = False
            for pin in self._pins:
                if not pin.is_execution():
                    continue
                if not exe_shifted:
                    y += pin_dim["h"]
                    exe_shifted = True
                if pin.is_output():
                    pin.setPos(total_width / 2 - 10, y)
                else:
                    pin.setPos(-total_width / 2 + 10, y)

            # Do the rest of the pins
            for pin in self._pins:
                if pin.is_execution():
                    continue
                y += pin_dim["h"]

                if pin.is_output():
                    pin.setPos(total_width / 2 - 10, y)
                else:
                    pin.setPos(-total_width / 2 + 10, y)

        self._width = total_width
        self._height = total_height

        # move the widget to the bottom
        self.widget.move(-self.widget.size().width() / 2, total_height / 2 - self.widget.size().height() + 5)

    def select_connections(self, value):
        """
        Sets the highlighting of all connected pins to the specified value.

        This method takes a boolean value `value` as input and sets the `_do_highlight` attribute of all connected pins to
        this value. If a pin is not connected, this method does nothing for that pin. After setting the `_do_highlight`
        attribute for all connected pins, the `update_path` method is called for each connection.

        Args:
            value: A boolean value indicating whether to highlight the connected pins or not.

        Returns:
            None.
        """

        for pin in self._pins:
            if pin.connection:
                pin.connection._do_highlight = value
                pin.connection.update_path()

    def contextMenuEvent(self, event):
        """Open a context menu when the node is right-clicked.

        Args:
            event (QtGui.QContextMenuEvent): The context menu event.

        Returns:
            None
        """
        menu = QtWidgets.QMenu(self)
        pos = event.pos()

        # actions
        delete_node = QtWidgets.QAction("Delete Node")
        edit_node = QtWidgets.QAction("Edit Node")
        menu.addAction(delete_node)

        action = menu.exec_(self.mapToGlobal(pos))

        if action == delete_node:
            item_name = self.selectedItems()[0].text()

            if item_name not in ["And", "Not", "Input", "Output"]:
                print(f"delete node: {item_name}")
            else:
                print("Cannot delete default nodes")

        elif action == edit_node:
            print("editing node")

            # confirm to open in the editor replacing what is existing

    def delete(self):
        """Deletes the connection.

        This function removes any connected pins by calling :any:`Port.remove_connection` for each pin
        connected to this connection. After all connections have been removed, the stored :any:`Port`
        references are set to None. Finally, :any:`QGraphicsScene.removeItem` is called on the scene to
        remove this widget.

        Returns:
            None
        """

        to_delete = [pin.connection for pin in self._pins if pin.connection]
        for connection in to_delete:
            connection.delete()

        self.scene().removeItem(self)

    # Override me
    def init_widget(self):
        pass

    def execute(self):
        # Get the values from the input pins
        self.execute_inputs()

        # Compute the value
        pass

        # execute nodes connected to output
        self.execute_outputs()

    def execute_inputs(self):
        pass

    def execute_outputs(self):
        pass
