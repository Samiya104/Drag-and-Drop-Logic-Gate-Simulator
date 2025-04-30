# Logic Gate Simulator

## Overview

The Logic Gate Simulator is an interactive PyQt5-based application that allows users to design, simulate, and analyze digital logic circuits. This educational tool provides a drag-and-drop interface for creating circuits with various logic gates, input buttons, and LED outputs.

## Features

- Interactive Circuit Design
  - Drag and drop logic gates
  - Connect components with wires
  - Real-time circuit simulation
- Supported Logic Gates
  - AND Gate
  - OR Gate
  - NOT Gate
- Dynamic Truth Table Generation
- Visual Circuit Representation
- Easy-to-use Interface

## Prerequisites

- Python 3.7+
- PyQt5
- Required Python packages:
  ```
  pip install PyQt5
  ```

## Installation

1. Clone the repository
2. Create a virtual environment (optional but recommended)
3. Install dependencies
4. Run the application

```bash
git clone https://github.com/Samiya104/Drag-and-Drop-Logic-Gate-Simulator
cd logic-gate-simulator
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
pip install PyQt5
python logic_simulator.py
```

## Usage Instructions

### Circuit Creation
- Click on input buttons (A, B, C) to toggle their state
- Drag from connection points to create wires
- Click on existing wires to remove them
- Observe how the truth table updates automatically

### Components

#### Input Buttons
- Represented as colored circular buttons
- Toggle between 0 (off) and 1 (on)
- Labeled A, B, and C
- Each button has two output connection points

#### Logic Gates
- AND Gate: Outputs 1 only when all inputs are 1
- OR Gate: Outputs 1 if at least one input is 1
- NOT Gate: Inverts the input (0 becomes 1, 1 becomes 0)

#### LED Output
- Located at the bottom of the circuit
- Displays the final circuit output
- Illuminates based on the circuit's logic

### Truth Table
- Automatically generated based on circuit configuration
- Shows all possible input combinations
- Displays output for each input state

## Code Structure

### Main Classes
- `MainWindow`: Primary application window
- `CircuitView`: Graphical view of the circuit
- `CircuitScene`: Manages circuit components and interactions
- `ConnectionPoint`: Represents connection points for wires
- `InputButton`: Toggleable input buttons
- `SimpleAndGate`, `SimpleOrGate`, `SimpleNotGate`: Logic gate implementations
- `LED`: Output indicator
- `SimpleTruthTableWidget`: Generates and displays truth table

### Key Modules
- `sys`: System-specific parameters and functions
- `os`: Interacting with operating system
- `PyQt5.QtWidgets`: GUI components
- `PyQt5.QtGui`: Graphics rendering
- `PyQt5.QtCore`: Core non-GUI functionality

## Customization

### Extending the Simulator
- Add more gate types by subclassing `QGraphicsObject`
- Modify `setupCircuit()` method to change default circuit layout
- Customize connection and wire drawing logic in `CircuitScene`

## Limitations
- Currently supports a fixed number of gates
- Limited to 3 input buttons
- Simplified circuit design for educational purposes

## Future Improvements
- Dynamically add/remove gates
- More complex gate types
- Save and load circuit configurations
- Enhanced visual design

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Contact
Your Name - qasms01@pfw.edu

Project Link:[https://github.com/Samiya104/Drag-and-Drop-Logic-Gate-Simulator](https://github.com/Samiya104/Drag-and-Drop-Logic-Gate-Simulator)
