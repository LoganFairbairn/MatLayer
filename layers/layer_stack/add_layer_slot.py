from os import name
import bpy
import random

def add_layer_slot(context):
    '''Creates a layer node.'''
    layers = context.scene.coater_layers
    layer_stack = context.scene.coater_layer_stack
    selected_layer_index = context.scene.coater_layer_stack.layer_index

    # Add a new layer slot.
    layers.add()
    
    # Assign the layer a unique name.
    new_layer_name = "Layer"
    layers[len(layers) - 1].name = new_layer_name

    # If there is no layer selected, move the layer to the top of the stack.
    if selected_layer_index < 0:
        move_index = len(layers) - 1
        move_to_index = 0
        layers.move(move_index, move_to_index)
        layer_stack.layer_index = move_to_index

        #
        selected_layer_index = len(layers) - 1

    # Moves the new layer above the currently selected layer and selects it.
    else: 
        move_index = len(layers) - 1
        move_to_index = max(0, min(selected_layer_index + 1, len(layers) - 1))
        layers.move(move_index, move_to_index)
        layer_stack.layer_index = move_to_index

        selected_layer_index = selected_layer_index + 1

    # Assign the layer a unique random ID number.
    number_of_layers = len(layers)
    new_id = random.randint(100000, 999999)
    id_exists = True

    while (id_exists):
        for i in range(number_of_layers):
            if layers[i].id == new_id:
                new_id += 1
                break

            if i == len(layers) - 1:
                id_exists = False
                layers[selected_layer_index].id = new_id