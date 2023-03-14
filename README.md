# Logic Node Editor

A very basic minimal code for implementing a node graph or editor using PySide6. All nodes are built using QGraphics items.

## Note
I’ve thought about extending some functionality to this that would be useful for most people wanting to use this to bootstrap projects.

Save and load. Not sure what file format. Was thinking it’d be cool to save as a compatible graphviz gv file. Other options would be a very basic node at the top, connections on the bottom file format. Keep the logic of node types as python classes.
Implement some compute logic on a node. Maybe as a python class/object with standard input/output with type checking. 
Run python code for each node into its own thread when calculating a DAG graph. This would speed processing up on multithreaded systems. And would be nice as a core feature. 


Let me know what your thoughts are and open an issue to discuss it. I’d like to keep features as open, generalized, and simple as possible.

Example video: https://www.youtube.com/watch?v=DOsFJ8lm9dU

![nodes](https://github.com/bhowiebkr/simple-node-editor/blob/master/images/node_editor.jpg)
