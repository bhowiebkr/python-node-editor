# Python Node Editor

This is a node based Python tool used for visual scripting that is designed to be used for composing high level Python code into reusable blocks. Nodes look and function similar to Unreal Engine blueprints. Each node consists of connection pins and a widget section enabling the developer to write a full custom PySide GUI for each node type.

The tool is designed to allow you to write Python code in individual files per class/node. This means that your code is self-contained, easily modifiable, and reusable across multiple projects. Additionally, the GUI is designed to be familiar to those who have used Unreal Engine's blueprinting system, making it easy to learn and use.

My goal with this project is to provide a new and innovative way of organizing and working with Python code. While the tool is still in the development phase, I am constantly working to improve its functionality and features.

Visual scripting using nodes does have some benefits and drawbacks and it’s up to the end developer to decide when such a system is beneficial or not. 

![nodes](https://github.com/bhowiebkr/simple-node-editor/blob/master/images/node_editor2.jpg)

Use it for:
- high level composing/configurable code.  If a given system consists of many similar components but have a unique set of steps or requirements on similar tasks. Example a VFX or game pipeline.
- readability for non programmers as a dependency graph with built-in functionality
- enabling non-programmers a simple system to assemble blocks of logic
- networks that require a high level of feedback throughout that network and not just the end result. Example shader building, sound synthesizing, machine learning, robotics and sensors. Each node can have a custom visual feedback such as images, graphs, sound timelines, spreadsheets etc.
- prototyping logic.
- Generator scripts. Taking an input or building up a result that gets saved for other uses. Example textures, images, sound, ML training data. 

Don’t use it for
- Anything complex. 40 nodes or less. This is because the user not only needs to think of how nodes are logically connected, but also the visual composure of nodes in the graph. It’s always best to refactor code when a graph gets too complex to make sense of.
- code that needs to run fast. The overhead of node based tools will increase processing in almost all cases.
- Code that doesn’t need a GUI/human interface to use.

For minimal GUI code for creating a node network see [GUI-nodes-only](https://github.com/bhowiebkr/simple-node-editor/tree/GUI-nodes-only) branch.


[![Video](http://img.youtube.com/vi/DOsFJ8lm9dU/0.jpg)](http://www.youtube.com/watch?v=DOsFJ8lm9dU)

