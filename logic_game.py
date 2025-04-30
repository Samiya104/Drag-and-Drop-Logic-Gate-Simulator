import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                            QTableWidget, QTableWidgetItem, QHeaderView, 
                            QGraphicsView, QGraphicsScene, QGraphicsItem, 
                            QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem,
                            QGraphicsRectItem, QGraphicsObject, QFrame, QMessageBox)
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath, QPolygonF, QPixmap, QTransform
from PyQt5.QtCore import Qt, QRectF, QPointF, QLineF, QSize

class ConnectionPoint(QGraphicsEllipseItem):
    """Connection point for wires with improved label positioning"""
    def __init__(self, x, y, parent=None, label=None):
        super().__init__(0, 0, 10, 10, parent)
        self.setPos(x, y)
        self.setBrush(QBrush(Qt.white))
        self.setPen(QPen(Qt.black, 1))
        self.connected_to = None
        self.line = None
        self.is_input = True  # Is this an input point or output point
        self.gate = None  # Reference to the parent gate
        self.port_index = -1  # Input/output port index
        self.label = label  # Label for this connection point
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setZValue(10)  # Ensure connection points are above other elements
        
    def mousePressEvent(self, event):
        """Start drag operation when a connection point is clicked"""
        if event.button() == Qt.LeftButton:
            # Start drawing a line from this point
            if self.scene():
                # Create temporary line
                self.line = WireLine(self.scenePos().x() + 5, self.scenePos().y() + 5, 
                                    event.scenePos().x(), event.scenePos().y())
                self.scene().addItem(self.line)
                self.scene().temporary_line = self.line
                self.scene().start_point = self
                super().mousePressEvent(event)
                
    def paint(self, painter, option, widget):
        """Override paint to draw the connection point and its label"""
        # Draw the connection point
        super().paint(painter, option, widget)
        
        # Draw the label if it exists
        if self.label:
            painter.setFont(QFont("Arial", 8))
            
            # Position the label above/below the connection point with improved spacing
            # Center it horizontally with the connection point
            if self.is_input:
                # Position label directly above the input connection point
                label_rect = QRectF(-20, -20, 50, 20)  # Increased width and offset
            else:
                # Position label directly below the output connection point
                label_rect = QRectF(-20, 15, 50, 20)  # Increased width and offset
                
            painter.drawText(label_rect, Qt.AlignCenter, self.label)

class WireLine(QGraphicsLineItem):
    """Line representing a wire connection"""
    def __init__(self, x1, y1, x2, y2, parent=None):
        super().__init__(x1, y1, x2, y2, parent)
        self.setPen(QPen(Qt.black, 2))
        self.start_point = None  # Connection point where the line starts
        self.end_point = None    # Connection point where the line ends
        self.setZValue(5)  # Ensure wires are below connection points but above other elements
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        
    def updateEndPoint(self, x, y):
        """Update the end point of the line"""
        line = self.line()
        self.setLine(line.x1(), line.y1(), x, y)
        
    def mousePressEvent(self, event):
        """Handle wire removal on click"""
        if event.button() == Qt.LeftButton:
            # Ask for confirmation
            if self.scene() and self.scene().parent() and self.start_point and self.end_point:
                # Get confirmation from user
                reply = QMessageBox.question(self.scene().parent().parent(), 
                                           'Remove Wire', 
                                           'Do you want to remove this wire?',
                                           QMessageBox.Yes | QMessageBox.No, 
                                           QMessageBox.No)
                
                if reply == QMessageBox.Yes:
                    # Check if LED is involved - turn off LED if its input is disconnected
                    if self.start_point.is_input and isinstance(self.start_point.gate, LED):
                        # Turn off LED since its input is being disconnected
                        self.start_point.gate.setState(False)
                        self.start_point.gate.has_connection = False
                    elif self.end_point.is_input and isinstance(self.end_point.gate, LED):
                        # Turn off LED since its input is being disconnected
                        self.end_point.gate.setState(False)
                        self.end_point.gate.has_connection = False
                    
                    # Disconnect the points
                    if self.start_point:
                        self.start_point.connected_to = None
                        self.start_point.line = None
                    
                    if self.end_point:
                        self.end_point.connected_to = None
                        self.end_point.line = None
                    
                    # Remove from connections list
                    if self in self.scene().connections:
                        self.scene().connections.remove(self)
                    
                    # Remove from scene
                    self.scene().removeItem(self)
                    
                    # Update truth table
                    if self.scene() and self.scene().parent():
                        self.scene().parent().updateTruthTable()
        
        super().mousePressEvent(event)
# Modified classes to create downward-facing gates

class SimpleAndGate(QGraphicsObject):
    """Simplified AND gate with exactly 2 inputs at top and 1 output at bottom"""
    def __init__(self, x, y, width=40, height=40, parent=None):
        super().__init__(parent)
        self.setPos(x, y)
        self.width = width
        self.height = height
        self.gate_type = "AND"
        self.image_path = os.path.join(os.getcwd(), ".venv", "Drag_and_Drop_Logic_Sim", "and_gate.png")
        self.pixmap = None
        self.inputs = []
        self.outputs = []
        self.input_values = [False, False]  # 2 input values
        self.output_values = [False]  # 1 output value
        
        # Force gate to be BEHIND other elements
        self.setZValue(0)
        
        # Set up the gate with rotated orientation
        self.setupConnectionPoints()
        
    def setupConnectionPoints(self):
        """Create exactly 2 inputs at top and 1 output at bottom, positioned at the gate edges"""
        # Position input points directly at the top edge with wider spacing
        in_spacing = self.width / 4  # More spacing between inputs
        
        # Create connection points on the SCENE directly, not as children
        in1 = ConnectionPoint(0, 0, None, "A")
        in1.setPos(self.mapToScene(in_spacing, 0))
        in1.is_input = True
        in1.gate = self
        in1.port_index = 0
        self.inputs.append(in1)
        
        in2 = ConnectionPoint(0, 0, None, "B")
        in2.setPos(self.mapToScene(3 * in_spacing, 0))
        in2.is_input = True
        in2.gate = self
        in2.port_index = 1
        self.inputs.append(in2)
        
        # Position output point directly at the bottom edge at center
        out = ConnectionPoint(0, 0, None, "Y")
        out.setPos(self.mapToScene(self.width / 2, self.height))
        out.is_input = False
        out.gate = self
        out.port_index = 0
        self.outputs.append(out)
    
    def boundingRect(self):
        """Define the bounding rectangle of the gate"""
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter, option, widget):
        """Draw the gate using its image if available, rotated to face downward"""
        if self.image_path and not self.pixmap:
            self.pixmap = QPixmap(self.image_path)
        
        if self.pixmap:
            # Create a rotated version of the pixmap (90 degrees clockwise)
            transform = QTransform()
            transform.rotate(90)
            rotated_pixmap = self.pixmap.transformed(transform)
            
            # Draw the rotated pixmap
            painter.drawPixmap(0, 0, self.width, self.height, rotated_pixmap)
        else:
            # Fallback if no image is available
            painter.setPen(QPen(Qt.black, 2))
            painter.setBrush(QBrush(Qt.lightGray))
            painter.drawRect(0, 0, self.width, self.height)
            painter.setFont(QFont("Arial", 10))
            painter.drawText(QRectF(0, 0, self.width, self.height), Qt.AlignCenter, self.gate_type)
    
    def evaluate(self):
        """Evaluate AND gate logic"""
        self.output_values[0] = self.input_values[0] and self.input_values[1]
    
    def updateConnections(self):
        """Update all downstream connections when this gate's output changes"""
        self.evaluate()
        for i, output in enumerate(self.outputs):
            if output.connected_to:
                connected_gate = output.connected_to.gate
                connected_index = output.connected_to.port_index
                
                if isinstance(connected_gate, LED):
                    connected_gate.setState(self.output_values[i])
                else:
                    connected_gate.input_values[connected_index] = self.output_values[i]
                    connected_gate.updateConnections()


class SimpleOrGate(QGraphicsObject):
    """Simplified OR gate with exactly 2 inputs at top and 1 output at bottom"""
    def __init__(self, x, y, width=40, height=40, parent=None):
        super().__init__(parent)
        self.setPos(x, y)
        self.width = width
        self.height = height
        self.gate_type = "OR"
        self.image_path = os.path.join(os.getcwd(), ".venv", "Drag_and_Drop_Logic_Sim", "or_gate.png")
        self.pixmap = None
        self.inputs = []
        self.outputs = []
        self.input_values = [False, False]  # 2 input values
        self.output_values = [False]  # 1 output value
        
        # Force gate to be BEHIND other elements
        self.setZValue(0)
        
        # Set up the gate with rotated orientation
        self.setupConnectionPoints()
        
    def setupConnectionPoints(self):
        """Create exactly 2 inputs at top and 1 output at bottom, positioned at the gate edges"""
        # Position input points directly at the top edge with wider spacing
        in_spacing = self.width / 4  # More spacing between inputs
        
        # Create connection points on the SCENE directly, not as children
        in1 = ConnectionPoint(0, 0, None, "A")
        in1.setPos(self.mapToScene(in_spacing, 0))
        in1.is_input = True
        in1.gate = self
        in1.port_index = 0
        self.inputs.append(in1)
        
        in2 = ConnectionPoint(0, 0, None, "B")
        in2.setPos(self.mapToScene(3 * in_spacing, 0))
        in2.is_input = True
        in2.gate = self
        in2.port_index = 1
        self.inputs.append(in2)
        
        # Position output point directly at the bottom edge at center
        out = ConnectionPoint(0, 0, None, "Y")
        out.setPos(self.mapToScene(self.width / 2, self.height))
        out.is_input = False
        out.gate = self
        out.port_index = 0
        self.outputs.append(out)
    
    def boundingRect(self):
        """Define the bounding rectangle of the gate"""
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter, option, widget):
        """Draw the gate using its image if available, rotated to face downward"""
        if self.image_path and not self.pixmap:
            self.pixmap = QPixmap(self.image_path)
        
        if self.pixmap:
            # Create a rotated version of the pixmap (90 degrees clockwise)
            transform = QTransform()
            transform.rotate(90)
            rotated_pixmap = self.pixmap.transformed(transform)
            
            # Draw the rotated pixmap
            painter.drawPixmap(0, 0, self.width, self.height, rotated_pixmap)
        else:
            # Fallback if no image is available
            painter.setPen(QPen(Qt.black, 2))
            painter.setBrush(QBrush(Qt.lightGray))
            painter.drawRect(0, 0, self.width, self.height)
            painter.setFont(QFont("Arial", 10))
            painter.drawText(QRectF(0, 0, self.width, self.height), Qt.AlignCenter, self.gate_type)
    
    def evaluate(self):
        """Evaluate OR gate logic"""
        self.output_values[0] = self.input_values[0] or self.input_values[1]
    
    def updateConnections(self):
        """Update all downstream connections when this gate's output changes"""
        self.evaluate()
        for i, output in enumerate(self.outputs):
            if output.connected_to:
                connected_gate = output.connected_to.gate
                connected_index = output.connected_to.port_index
                
                if isinstance(connected_gate, LED):
                    connected_gate.setState(self.output_values[i])
                else:
                    connected_gate.input_values[connected_index] = self.output_values[i]
                    connected_gate.updateConnections()


class SimpleNotGate(QGraphicsObject):
    """Simplified NOT gate with exactly 1 input at top and 1 output at bottom"""
    def __init__(self, x, y, width=40, height=40, parent=None):
        super().__init__(parent)
        self.setPos(x, y)
        self.width = width
        self.height = height
        self.gate_type = "NOT"
        self.image_path = os.path.join(os.getcwd(), ".venv", "Drag_and_Drop_Logic_Sim", "not_gate.png")
        self.pixmap = None
        self.inputs = []
        self.outputs = []
        self.input_values = [False]  # 1 input value
        self.output_values = [False]  # 1 output value
        
        # Force gate to be BEHIND other elements
        self.setZValue(0)
        
        # Set up the gate with rotated orientation
        self.setupConnectionPoints()
        
    def setupConnectionPoints(self):
        """Create exactly 1 input at top and 1 output at bottom, positioned at the gate edges"""
        # Create connection points on the SCENE directly, not as children
        in1 = ConnectionPoint(0, 0, None, "A")
        in1.setPos(self.mapToScene(self.width / 2, 0))
        in1.is_input = True
        in1.gate = self
        in1.port_index = 0
        self.inputs.append(in1)
        
        # Position output point directly at the bottom edge at center
        out = ConnectionPoint(0, 0, None, "Y")
        out.setPos(self.mapToScene(self.width / 2, self.height))
        out.is_input = False
        out.gate = self
        out.port_index = 0
        self.outputs.append(out)
    
    def boundingRect(self):
        """Define the bounding rectangle of the gate"""
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter, option, widget):
        """Draw the gate using its image if available, rotated to face downward"""
        if self.image_path and not self.pixmap:
            self.pixmap = QPixmap(self.image_path)
        
        if self.pixmap:
            # Create a rotated version of the pixmap (90 degrees clockwise)
            transform = QTransform()
            transform.rotate(90)
            rotated_pixmap = self.pixmap.transformed(transform)
            
            # Draw the rotated pixmap
            painter.drawPixmap(0, 0, self.width, self.height, rotated_pixmap)
        else:
            # Fallback if no image is available
            painter.setPen(QPen(Qt.black, 2))
            painter.setBrush(QBrush(Qt.lightGray))
            painter.drawRect(0, 0, self.width, self.height)
            painter.setFont(QFont("Arial", 10))
            painter.drawText(QRectF(0, 0, self.width, self.height), Qt.AlignCenter, self.gate_type)
    
    def evaluate(self):
        """Evaluate NOT gate logic"""
        self.output_values[0] = not self.input_values[0]
    
    def updateConnections(self):
        """Update all downstream connections when this gate's output changes"""
        self.evaluate()
        for i, output in enumerate(self.outputs):
            if output.connected_to:
                connected_gate = output.connected_to.gate
                connected_index = output.connected_to.port_index
                
                if isinstance(connected_gate, LED):
                    connected_gate.setState(self.output_values[i])
                else:
                    connected_gate.input_values[connected_index] = self.output_values[i]
                    connected_gate.updateConnections()

class LED(QGraphicsObject):
    """LED output indicator with input-only functionality"""
    def __init__(self, x, y, parent=None):
        super().__init__(parent)
        self.setPos(x, y)
        self.width = 20
        self.height = 40
        self.state = False
        self.has_connection = False  # Flag to check if it already has a connection
        
        # Force LED to be BEHIND other elements
        self.setZValue(0)
        
        # Create input connection with label on the SCENE directly, not as child
        self.input = ConnectionPoint(0, 0, None, "In")
        self.input.setPos(self.mapToScene(self.width/2, 0))
        self.input.is_input = True
        self.input.gate = self
        self.input.port_index = 0
    
    def boundingRect(self):
        """Define the bounding rectangle of the LED"""
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter, option, widget):
        """Draw the LED in its current state"""
        painter.setPen(QPen(Qt.black, 2))
        
        # Different color based on state
        if self.state:
            painter.setBrush(QBrush(Qt.green))  # LED is ON
        else:
            painter.setBrush(QBrush(Qt.darkGray))  # LED is OFF
            
        painter.drawEllipse(0, 0, self.width, self.height)
    
    def setState(self, state):
        """Set the state of the LED and update display"""
        self.state = state
        self.update()  # Trigger repaint

class InputButton(QGraphicsObject):
    """Input button for the circuit"""
    def __init__(self, x, y, label, parent=None):
        super().__init__(parent)
        self.setPos(x, y)
        self.width = 40
        self.height = 40
        self.label = label
        self.state = False
        self.setAcceptedMouseButtons(Qt.LeftButton)
        
        # Assign different colors based on the button label
        if label == "A":
            self.on_color = QColor(255, 255, 0)  # Yellow
        elif label == "B":
            self.on_color = QColor(0, 128, 255)  # Blue
        elif label == "C":
            self.on_color = QColor(128, 0, 128)  # Purple
        else:
            self.on_color = QColor(0, 255, 0)  # Default green

        # Force button to be BEHIND other elements
        self.setZValue(0)
        
        # Create output connection points directly, not as children
        spacing = 30  # Increased space between connection points
        
        # Left connection point
        self.output1 = ConnectionPoint(0, 0, None, f"{label}1")
        self.output1.setPos(self.mapToScene(self.width/2 - spacing/2, self.height))
        self.output1.is_input = False
        self.output1.gate = self
        self.output1.port_index = 0
        
        # Right connection point
        self.output2 = ConnectionPoint(0, 0, None, f"{label}2")
        self.output2.setPos(self.mapToScene(self.width/2 + spacing/2, self.height))
        self.output2.is_input = False
        self.output2.gate = self
        self.output2.port_index = 0
 
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.state = not self.state
            self.update()
            
            # Propagate changes
            for wire in self.scene().items():
                if isinstance(wire, ConnectionPoint) and wire.gate == self:
                    if wire.connected_to:
                        connected_gate = wire.connected_to.gate
                        connected_index = wire.connected_to.port_index
                        if isinstance(connected_gate, LED):
                            connected_gate.setState(self.state)
                        else:
                            connected_gate.input_values[connected_index] = self.state
                            connected_gate.updateConnections()
            
            # Update truth table
            if self.scene() and self.scene().parent():
                self.scene().parent().updateTruthTable()
            
        super().mousePressEvent(event)
        
    def paint(self, painter, option, widget):
        painter.setPen(QPen(Qt.black, 2))
        
        # Use custom on_color when button is active (state is True)
        if self.state:
            painter.setBrush(QBrush(self.on_color))
        else:
            painter.setBrush(QBrush(Qt.lightGray))
            
        painter.drawEllipse(0, 0, self.width, self.height)
        
        # Draw the label
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.drawText(QRectF(0, 0, self.width, self.height), Qt.AlignCenter, self.label)

class CircuitScene(QGraphicsScene):
    """Scene for the circuit simulation"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.temporary_line = None
        self.start_point = None
        self.connections = []  # List of connections (lines)
        self.gates = []        # List of all gates
        self.inputs = []       # List of input buttons
        self.outputs = []      # List of output LEDs
        self.used_inputs = set()  # Set of input buttons used in the circuit
        self.snap_radius = 20  # Radius for snapping in pixels
        
        # Set background color
        self.setBackgroundBrush(QBrush(Qt.white))

    def getWireColor(self, connection_point):
        """Determine wire color based on the source input button"""
        # Assign different colors based on which input button is the source
        if hasattr(connection_point, 'gate') and isinstance(connection_point.gate, InputButton):
            if connection_point.gate.label == "A":
                return QColor(255, 255, 0)  # Yellow for A
            elif connection_point.gate.label == "B":
                return QColor(0, 128, 255)  # Blue for B
            elif connection_point.gate.label == "C":
                return QColor(128, 0, 128)  # Purple for C
        
        # Try to trace back to a source button through connected points
        if connection_point.connected_to and hasattr(connection_point.connected_to, 'gate'):
            source_gate = connection_point.connected_to.gate
            if isinstance(source_gate, InputButton):
                if source_gate.label == "A":
                    return QColor(255, 255, 0)  # Yellow for A
                elif source_gate.label == "B":
                    return QColor(0, 128, 255)  # Blue for B
                elif source_gate.label == "C":
                    return QColor(128, 0, 128)  # Purple for C
        
        # Default color if no source button is found
        return Qt.black
        
    def mouseMoveEvent(self, event):
        """Update the temporary line during drag operation"""
        if self.temporary_line:
            # Find the nearest connection point for snapping
            nearest_point = self.findNearestConnectionPoint(event.scenePos())
            
            if nearest_point and self.isPointWithinSnapRadius(event.scenePos(), nearest_point.scenePos()):
                # Snap to the nearest connection point if within snap radius
                self.temporary_line.updateEndPoint(
                    nearest_point.scenePos().x() + 5,  # Center of connection point
                    nearest_point.scenePos().y() + 5
                )
                # Optional: Add visual feedback for snapping (e.g., highlight the connection point)
                nearest_point.setBrush(QBrush(Qt.yellow))
            else:
                # Reset brush color for all connection points
                for item in self.items():
                    if isinstance(item, ConnectionPoint) and item != self.start_point:
                        item.setBrush(QBrush(Qt.white))
                
                # Regular drag behavior - follow mouse cursor
                self.temporary_line.updateEndPoint(event.scenePos().x(), event.scenePos().y())
                
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        """Complete connection if releasing over a valid connection point"""
        if self.temporary_line and self.start_point:
            # Find if we're over a connection point
            nearest_point = self.findNearestConnectionPoint(event.scenePos())
            
            if nearest_point and self.isPointWithinSnapRadius(event.scenePos(), nearest_point.scenePos()):
                target = nearest_point
                
                # Reset brush color
                target.setBrush(QBrush(Qt.white))
                
                # Check compatibility (input to output or output to input)
                if self.start_point.is_input != target.is_input:
                    # Check if the LED already has a connection
                    if isinstance(target.gate, LED) and target.is_input:
                        if target.connected_to is not None:
                            # LED already has a connection, show error message
                            if self.parent():
                                QMessageBox.warning(self.parent().parent(), 
                                                  "Connection Error", 
                                                  "LED already has a connection. Remove the existing connection first.")
                            self.removeItem(self.temporary_line)
                            self.temporary_line = None
                            self.start_point = None
                            return

                    # Check if the target is already connected
                    if target.connected_to is not None:
                        # Target already has a connection
                        if self.parent():
                            QMessageBox.warning(self.parent().parent(), 
                                              "Connection Error", 
                                              "This connection point already has a connection. Remove the existing connection first.")
                        self.removeItem(self.temporary_line)
                        self.temporary_line = None
                        self.start_point = None
                        return

                    # Valid connection - finalize it
                    self.temporary_line.setLine(
                        self.start_point.scenePos().x() + 5, 
                        self.start_point.scenePos().y() + 5,
                        target.scenePos().x() + 5, 
                        target.scenePos().y() + 5
                    )
                    
                    # Set up connection references
                    self.temporary_line.start_point = self.start_point
                    self.temporary_line.end_point = target
                    
                    # Set wire color based on the source button - FIXED TERNARY OPERATOR
                    wire_color = self.getWireColor(target if self.start_point.is_input else self.start_point)
                    self.temporary_line.setPen(QPen(wire_color, 2))
                    
                    # Connect the points logically
                    if self.start_point.is_input:
                        # Wire goes from output to input
                        self.start_point.connected_to = target
                        target.connected_to = self.start_point
                        
                        # Propagate source button reference
                        if hasattr(target, 'source_button'):
                            self.start_point.source_button = target.source_button
                    else:
                        # Wire goes from input to output
                        target.connected_to = self.start_point
                        self.start_point.connected_to = target
                        
                        # Propagate source button reference
                        if hasattr(self.start_point, 'source_button'):
                            target.source_button = self.start_point.source_button
                    
                    # Store the connection
                    self.connections.append(self.temporary_line)
                    
                    # Update gate values
                    if not self.start_point.is_input:
                        # Output to input connection
                        self.updateConnectionLogic(self.start_point, target)
                    else:
                        # Input to output connection
                        self.updateConnectionLogic(target, self.start_point)
                    
                    # Update the truth table
                    if self.parent():
                        self.parent().updateTruthTable()
                else:
                    # Invalid connection (input to input or output to output)
                    if self.parent():
                        QMessageBox.warning(self.parent().parent(), 
                                          "Connection Error", 
                                          "Cannot connect input to input or output to output.")
                    self.removeItem(self.temporary_line)
            else:
                # No valid target - remove the temporary line
                self.removeItem(self.temporary_line)
            
            # Reset temporary variables
            self.temporary_line = None
            self.start_point = None
            
            # Reset all connection point colors
            for item in self.items():
                if isinstance(item, ConnectionPoint):
                    item.setBrush(QBrush(Qt.white))
            
        super().mouseReleaseEvent(event)
        
    def findNearestConnectionPoint(self, pos):
        """Find the nearest connection point to the given position"""
        nearest_point = None
        min_distance = float('inf')
        
        for item in self.items():
            if isinstance(item, ConnectionPoint) and item != self.start_point:
                distance = self.calculateDistance(pos, item.scenePos())
                if distance < min_distance:
                    min_distance = distance
                    nearest_point = item
        
        return nearest_point
    
    def isPointWithinSnapRadius(self, pos1, pos2):
        """Check if two points are within the snap radius"""
        return self.calculateDistance(pos1, pos2) <= self.snap_radius
    
    def calculateDistance(self, pos1, pos2):
        """Calculate Euclidean distance between two points"""
        dx = pos1.x() - pos2.x()
        dy = pos1.y() - pos2.y()
        return (dx * dx + dy * dy) ** 0.5
    
    def updateConnectionLogic(self, source_point, target_point):
        """Update the logic when a connection is made"""
        src_gate = source_point.gate
        tgt_gate = target_point.gate
        
        # Get port indices
        src_idx = source_point.port_index
        tgt_idx = target_point.port_index
        
        # Set the input value based on the output value
        if isinstance(src_gate, InputButton):
            if isinstance(tgt_gate, LED):
                tgt_gate.setState(src_gate.state)
                tgt_gate.has_connection = True
            else:
                tgt_gate.input_values[tgt_idx] = src_gate.state
                tgt_gate.updateConnections()
            
            # Add input to used inputs
            self.used_inputs.add(src_gate.label)
        else:
            # Handle case when source might be another gate
            if hasattr(src_gate, 'output_values'):
                value = src_gate.output_values[src_idx]
            elif hasattr(src_gate, 'state'):
                value = src_gate.state
            else:
                value = False
                
            if isinstance(tgt_gate, LED):
                tgt_gate.setState(value)
                tgt_gate.has_connection = True
            else:
                tgt_gate.input_values[tgt_idx] = value
                tgt_gate.updateConnections()

class CircuitView(QGraphicsView):
    """View for displaying the circuit"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = CircuitScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Set a fixed size for the scene
        self.scene.setSceneRect(0, 0, 800, 500)
        
        # Set up the initial circuit components
        self.setupCircuit()
        
    def resizeEvent(self, event):
        """Handle resize events to adjust component positions"""
        super().resizeEvent(event)
        
        # Update the scene rectangle to match the new view size
        self.scene.setSceneRect(0, 0, self.viewport().width(), self.viewport().height())
        
        # Only recreate if we're not in the constructor (avoid double initialization)
        if hasattr(self, 'led'):
            # Clear existing items first
            for item in self.scene.items():
                self.scene.removeItem(item)
                
            self.scene.connections = []
            self.scene.gates = []
            self.scene.inputs = []
            self.scene.outputs = []
            
            # Rebuild the circuit with proper positioning
            self.setupCircuit()
    
    def setupCircuit(self):
        """Set up the circuit with minimal connection points"""
        # Create input buttons (top row) - centered and higher up
        inputs_y = 20  # Changed from 50 to 20 to position buttons higher up
        
        # Get the actual view width from the viewport size
        scene_width = self.viewport().width()
        if scene_width == 0:
            scene_width = 800  # Fallback value if viewport width is not available
        
        # Number of input buttons
        num_buttons = 3
        
        # Button properties
        button_width = 40  # Width of the InputButton
        button_spacing = 100  # Space between buttons
        
        # Calculate total width needed for all buttons
        total_buttons_width = (num_buttons * button_width) + ((num_buttons - 1) * button_spacing)
        
        # Calculate the starting x position to center the buttons
        start_x = (scene_width - total_buttons_width) / 2
        
        # Create input buttons at calculated positions
        self.input_a = InputButton(start_x, inputs_y, "A")
        self.input_b = InputButton(start_x + button_width + button_spacing, inputs_y, "B")
        self.input_c = InputButton(start_x + 2 * (button_width + button_spacing), inputs_y, "C")
        
        self.scene.addItem(self.input_a)
        self.scene.addItem(self.input_b)
        self.scene.addItem(self.input_c)
        
        self.scene.inputs = [self.input_a, self.input_b, self.input_c]
        
        # Add the connection points to the scene AFTER adding the buttons
        for point in [
            self.input_a.output1, self.input_a.output2,
            self.input_b.output1, self.input_b.output2,
            self.input_c.output1, self.input_c.output2
        ]:
            self.scene.addItem(point)
            
        # ----- GATES SECTION -----
        # Create gates with specific spacing
        
        gate_width = 40   # Gate width
        gate_height = 40  # Gate height
        gate_spacing = 100  # Spacing between gates of the same type
        group_spacing = 150  # Spacing between different gate types
        
        gates_y = 150  # Position for the gates row - also reduced from 180 to 150
        
        # Calculate the starting x position to center all gates
        total_gates_width = (4 * gate_width + 3 * gate_spacing) + group_spacing + (4 * gate_width + 3 * gate_spacing) + group_spacing + (4 * gate_width + 3 * gate_spacing)
        left_margin = (scene_width - total_gates_width) / 2  # Center all gates horizontally
        
        self.scene.gates = []
        
        # Create 4 AND gates
        for i in range(4):
            x_pos = left_margin + i * gate_spacing
            
            # Create simplified AND gate with exact connection points
            gate = SimpleAndGate(x_pos, gates_y, gate_width, gate_height)
            
            # Update labels for this specific gate
            gate.inputs[0].label = f"{i+1}A"
            gate.inputs[1].label = f"{i+1}B"
            gate.outputs[0].label = f"{i+1}Y"
            
            self.scene.addItem(gate)
            self.scene.gates.append(gate)
            
            # Add connection points to scene AFTER adding the gate
            for point in gate.inputs + gate.outputs:
                self.scene.addItem(point)
        
        # Calculate starting position for OR gates (after AND gates + group spacing)
        or_start_x = left_margin + 4 * gate_spacing + group_spacing
        
        # Create 4 OR gates
        for i in range(4):
            x_pos = or_start_x + i * gate_spacing
            
            # Create simplified OR gate with exact connection points
            gate = SimpleOrGate(x_pos, gates_y, gate_width, gate_height)
            
            # Update labels for this specific gate
            gate.inputs[0].label = f"{i+1}A"
            gate.inputs[1].label = f"{i+1}B"
            gate.outputs[0].label = f"{i+1}Y"
            
            self.scene.addItem(gate)
            self.scene.gates.append(gate)
            
            # Add connection points to scene AFTER adding the gate
            for point in gate.inputs + gate.outputs:
                self.scene.addItem(point)
        
        # Calculate starting position for NOT gates (after OR gates + group spacing)
        not_start_x = or_start_x + 4 * gate_spacing + group_spacing
        
        # Create 4 NOT gates
        for i in range(4):
            x_pos = not_start_x + i * gate_spacing
            
            # Create simplified NOT gate with exact connection points
            gate = SimpleNotGate(x_pos, gates_y, gate_width, gate_height)
            
            # Update labels for this specific gate
            gate.inputs[0].label = f"{i+1}A"
            gate.outputs[0].label = f"{i+1}Y"
            
            self.scene.addItem(gate)
            self.scene.gates.append(gate)
            
            # Add connection points to scene AFTER adding the gate
            for point in gate.inputs + gate.outputs:
                self.scene.addItem(point)
        
        # Create LED at the bottom (centered)
        led_y = 320  # Also reduced from 350 to 320 to maintain proportions
        led_x = scene_width / 2 - 10  # Center the LED (width is 20)
        self.led = LED(led_x, led_y)
        self.scene.addItem(self.led)
        
        # Add LED input to scene AFTER adding the LED
        self.scene.addItem(self.led.input)
        
        self.scene.outputs = [self.led]
        
    def sizeHint(self):
        """Suggest a size for the view"""
        return self.minimumSizeHint()
        
    def minimumSizeHint(self):
        """Minimum size for the view"""
        return QSize(800, 400)
        
    def updateTruthTable(self):
        """Update the truth table based on the current circuit configuration"""
        if hasattr(self.parent(), 'updateTruthTable'):
            self.parent().updateTruthTable()

class SimpleTruthTableWidget(QTableWidget):
    """Widget for displaying a simplified dynamic truth table"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
    def updateTable(self, circuit_view):
        """Update the truth table based on circuit connections"""
        try:
            # Clear the table
            self.clear()
            
            # Collect connected inputs and build expressions
            scene = circuit_view.scene
            expressions = []
            input_labels = set()
            
            # Find all active connections
            for conn in scene.connections:
                if not conn.start_point or not conn.end_point:
                    continue
                    
                start_gate = conn.start_point.gate
                end_gate = conn.end_point.gate
                
                # Skip if any gate is None
                if not start_gate or not end_gate:
                    continue
                
                # Input connected to gates
                if isinstance(start_gate, InputButton):
                    input_labels.add(start_gate.label)
                    
                    # Input to gate
                    if not isinstance(end_gate, LED) and hasattr(end_gate, 'gate_type'):
                        gate_expression = {
                            'type': end_gate.gate_type,
                            'inputs': [start_gate.label],
                            'output': None,
                            'gate': end_gate
                        }
                        expressions.append(gate_expression)
                    
                    # Input direct to LED
                    if isinstance(end_gate, LED):
                        led_expression = {
                            'type': 'Direct',
                            'inputs': [start_gate.label],
                            'output': 'Output',
                            'gate': end_gate  
                        }
                        expressions.append(led_expression)
                
                # Gate to LED
                elif hasattr(start_gate, 'gate_type') and isinstance(end_gate, LED):
                    # Find existing gate expression
                    for expr in expressions:
                        if expr['gate'] == start_gate:
                            expr['output'] = 'Output'
            
            # Sort input labels
            sorted_inputs = sorted(list(input_labels))
            
            # Create column headers
            headers = sorted_inputs.copy()
            
            # Create expressions for the output column
            output_expressions = []
            
            for expr in expressions:
                if expr['output'] == 'Output':
                    if expr['type'] == 'AND':
                        e_label = '.'.join(expr['inputs'])
                        headers.append(e_label)
                        output_expressions.append(expr)
                    elif expr['type'] == 'OR':
                        e_label = '+'.join(expr['inputs'])
                        headers.append(e_label)
                        output_expressions.append(expr)
                    elif expr['type'] == 'NOT':
                        e_label = '¬' + expr['inputs'][0]
                        headers.append(e_label)
                        output_expressions.append(expr)
                    elif expr['type'] == 'Direct':
                        headers.append(expr['inputs'][0])
                        output_expressions.append(expr)
            
            if not sorted_inputs and not output_expressions:
                self.setRowCount(0)
                self.setColumnCount(0)
                return
                
            self.setColumnCount(len(headers))
            self.setHorizontalHeaderLabels(headers)
            
            # Calculate number of rows
            if sorted_inputs:
                num_rows = 2 ** len(sorted_inputs)
                self.setRowCount(num_rows)
                
                # Fill in truth table
                for row in range(num_rows):
                    # Calculate input values for this row
                    input_values = {}
                    for i, input_name in enumerate(sorted_inputs):
                        # Determine value for this input in this row
                        input_values[input_name] = (row & (1 << (len(sorted_inputs) - i - 1))) != 0
                        
                        # Add to table
                        item = QTableWidgetItem("1" if input_values[input_name] else "0")
                        item.setTextAlignment(Qt.AlignCenter)
                        self.setItem(row, i, item)
                    
                    # Calculate output expressions for this input combination
                    col_idx = len(sorted_inputs)
                    for expr in output_expressions:
                        result = False
                        
                        if expr['type'] == 'AND':
                            result = all(input_values.get(inp, False) for inp in expr['inputs'])
                        elif expr['type'] == 'OR':
                            result = any(input_values.get(inp, False) for inp in expr['inputs'])
                        elif expr['type'] == 'NOT':
                            result = not input_values.get(expr['inputs'][0], False)
                        elif expr['type'] == 'Direct':
                            result = input_values.get(expr['inputs'][0], False)
                        
                        item = QTableWidgetItem("1" if result else "0")
                        item.setTextAlignment(Qt.AlignCenter)
                        self.setItem(row, col_idx, item)
                        col_idx += 1

        except Exception as e:
            # Error handling
            print(f"Error updating truth table: {e}")
            self.clear()
            
            # Fallback table
            inputs = [inp.label for inp in circuit_view.scene.inputs]
            headers = inputs + ["Output"]
            self.setColumnCount(len(headers))
            self.setHorizontalHeaderLabels(headers)
            self.setRowCount(1)
            
            for i, input_btn in enumerate(circuit_view.scene.inputs):
                item = QTableWidgetItem("1" if input_btn.state else "0")
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(0, i, item)
                
            # Show LED state
            item = QTableWidgetItem("1" if circuit_view.led.state else "0")
            item.setTextAlignment(Qt.AlignCenter) 
            self.setItem(0, len(inputs), item)

class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logic Gate Simulator")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)  # Set minimum window size
        
        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Create the circuit view
        self.circuit_view = CircuitView(self)
        
        # Create the truth table
        self.truth_table = SimpleTruthTableWidget()
        
        # Add widgets to the layout
        main_layout.addWidget(QLabel("Logic Circuit Design"))
        main_layout.addWidget(self.circuit_view, 3)
        main_layout.addWidget(QLabel("Truth Table"))
        main_layout.addWidget(self.truth_table, 2)
        
        # Instructions
        instructions = QLabel(
            "Instructions: Click input buttons to toggle their state.\n"
            "Drag from connection points to create wires. Click on wires to remove them.\n"
            "The truth table updates automatically based on the circuit configuration."
        )
        instructions.setFrameShape(QFrame.Panel)
        instructions.setFrameShadow(QFrame.Sunken)
        instructions.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(instructions)
        
        # Initialize the truth table
        self.updateTruthTable()
        
    def updateTruthTable(self):
        """Update the truth table based on the current circuit"""
        self.truth_table.updateTable(self.circuit_view)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())