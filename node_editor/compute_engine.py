# Compute the value of the pin based on the current state of the graph
def get_pin_data(pin):
    pass

    # if pin isn't connected, return it current data

    # get the evalutation order of the owning node of the pin

    # loop over each node and process it

    # retur the pin's data


# Get a list of nodes in the order to be computed. Forward evaluation by default.
def get_node_compute_order(node, forward=False):
    # Create a set to keep track of visited nodes
    visited = set()
    # Create a stack to keep track of nodes to visit
    stack = [node]
    # Create a list to store the evaluation order
    order = []


# Get the next nodes that this node is dependent on
def get_next_input_node(node):
    pass


# Get the next nodes that is affected by the input node.
def get_next_output_node(node):
    pass
