'''
Based on:
clevr-dataset-gen
https://github.com/facebookresearch/clevr-dataset-gen
'''

"""
Utilities for working with function program representations of questions.

Some of the metadata about what question node types are available etc are stored
in a JSON metadata file.
"""

# Handlers for answering questions. Each handler receives the scene structure
# that was output from Blender, the node, and a list of values that were output
# from each of the node's inputs; the handler should return the computed output
# value from this node.


def scene_handler(scene_struct, inputs, side_inputs):
    # Just return all objects in the scene
    return list(range(len(scene_struct['objects'])))


def make_filter_handler(attribute):
    def filter_handler(scene_struct, inputs, side_inputs):
        assert len(inputs) == 1
        assert len(side_inputs) == 1
        value = side_inputs[0]
        output = []
        for idx in inputs[0]:
            atr = scene_struct['objects'][idx][attribute]
            # print(value, atr)
            if attribute == 'attribute':
                if value in atr:
                    output.append(idx)
            else:
                if value == atr:
                    output.append(idx)
        return output
    return filter_handler


def unique_handler(scene_struct, inputs, side_inputs):
    assert len(inputs) == 1
    if len(inputs[0]) != 1:
        return '__INVALID__'
    return inputs[0][0]


def vg_relate_handler(scene_struct, inputs, side_inputs):
    assert len(inputs) == 1
    assert len(side_inputs) == 1
    output = set()
    for rel in scene_struct['relationships']:
        if rel['predicate'] == side_inputs[0] and rel['subject_idx'] == inputs[0]:
            output.add(rel['object_idx'])
    return sorted(list(output))


def relate_handler(scene_struct, inputs, side_inputs):
    assert len(inputs) == 1
    assert len(side_inputs) == 1
    relation = side_inputs[0]
    return scene_struct['relationships'][relation][inputs[0]]


def union_handler(scene_struct, inputs, side_inputs):
    assert len(inputs) == 2
    assert len(side_inputs) == 0
    return sorted(list(set(inputs[0]) | set(inputs[1])))


def intersect_handler(scene_struct, inputs, side_inputs):
    assert len(inputs) == 2
    assert len(side_inputs) == 0
    return sorted(list(set(inputs[0]) & set(inputs[1])))


def count_handler(scene_struct, inputs, side_inputs):
    assert len(inputs) == 1
    return len(inputs[0])


def make_same_attr_handler(attribute):
    def same_attr_handler(scene_struct, inputs, side_inputs):
        cache_key = '_same_%s' % attribute
        if cache_key not in scene_struct:
            cache = {}
            for i, obj1 in enumerate(scene_struct['objects']):
                same = []
                for j, obj2 in enumerate(scene_struct['objects']):
                    if i != j and obj1[attribute] == obj2[attribute]:
                        same.append(j)
                cache[i] = same
            scene_struct[cache_key] = cache

        cache = scene_struct[cache_key]
        assert len(inputs) == 1
        assert len(side_inputs) == 0
        return cache[inputs[0]]
    return same_attr_handler


def make_query_handler(attribute):
    def query_handler(scene_struct, inputs, side_inputs):
        assert len(inputs) == 1
        assert len(side_inputs) == 0
        idx = inputs[0]
        obj = scene_struct['objects'][idx]
        assert attribute in obj
        val = obj[attribute]
        if type(val) == list and len(val) != 1:
            if attribute == 'attribute':
                return val
            else:
                return '__INVALID__'
        elif type(val) == list and len(val) == 1:
            return val[0]
        else:
            return val
    return query_handler


def exist_handler(scene_struct, inputs, side_inputs):
    assert len(inputs) == 1
    assert len(side_inputs) == 0
    return len(inputs[0]) > 0


def equal_handler(scene_struct, inputs, side_inputs):
    assert len(inputs) == 2
    assert len(side_inputs) == 0
    return inputs[0] == inputs[1]


def less_than_handler(scene_struct, inputs, side_inputs):
    assert len(inputs) == 2
    assert len(side_inputs) == 0
    return inputs[0] < inputs[1]


def greater_than_handler(scene_struct, inputs, side_inputs):
    assert len(inputs) == 2
    assert len(side_inputs) == 0
    return inputs[0] > inputs[1]


# Register all of the answering handlers here.
# TODO maybe this would be cleaner with a function decorator that takes
# care of registration? Not sure. Also what if we want to reuse the same engine
# for different sets of node types?
execute_handlers = {
    'scene': scene_handler,
    'filter_color': make_filter_handler('color'),
    'filter_shape': make_filter_handler('shape'),
    'filter_material': make_filter_handler('material'),
    'filter_size': make_filter_handler('size'),
    'filter_objectcategory': make_filter_handler('objectcategory'),
    'filter_name': make_filter_handler('name'),
    'filter_weight': make_filter_handler('weight'),
    'filter_movability': make_filter_handler('movability'),
    'filter_stability': make_filter_handler('stability'),
    'filter_powering': make_filter_handler('powering'),
    'filter_disassembly': make_filter_handler('disassembly'),
    'filter_picking': make_filter_handler('picking'),
    'filter_attribute': make_filter_handler('attribute'),
    'unique': unique_handler,
    'relate': relate_handler,
    'union': union_handler,
    'intersect': intersect_handler,
    'count': count_handler,
    'query_color': make_query_handler('color'),
    'query_shape': make_query_handler('shape'),
    'query_material': make_query_handler('material'),
    'query_size': make_query_handler('size'),
    'query_name': make_query_handler('name'),
    'query_weight': make_query_handler('weight'),
    'query_movability': make_query_handler('movability'),
    'query_stability': make_query_handler('stability'),
    'query_powering': make_query_handler('powering'),
    'query_disassembly': make_query_handler('disassembly'),
    'query_picking': make_query_handler('picking'),
    'query_attribute': make_query_handler('attribute'),
    'exist': exist_handler,
    'equal_color': equal_handler,
    'equal_shape': equal_handler,
    'equal_integer': equal_handler,
    'equal_material': equal_handler,
    'equal_size': equal_handler,
    'equal_object': equal_handler,
    'equal_name': equal_handler,
    'equal_weight': equal_handler,
    'equal_movability': equal_handler,
    'equal_stability': equal_handler,
    'equal_disassembly': equal_handler,
    'equal_picking': equal_handler,
    'equal_powering': equal_handler,
    'equal_attribute': equal_handler,
    'less_than': less_than_handler,
    'greater_than': greater_than_handler,
    'same_color': make_same_attr_handler('color'),
    'same_shape': make_same_attr_handler('shape'),
    'same_size': make_same_attr_handler('size'),
    'same_material': make_same_attr_handler('material'),
    'same_name': make_same_attr_handler('name'),
    'same_weight': make_same_attr_handler('weight'),
    'same_movability': make_same_attr_handler('movability'),
    'same_stability': make_same_attr_handler('stability'),
    'same_powering': make_same_attr_handler('powering'),
    'same_disassembly': make_same_attr_handler('disassembly'),
    'same_picking': make_same_attr_handler('picking'),
    'same_attribute': make_same_attr_handler('attribute')
}


def answer_question(question, metadata, scene_struct, all_outputs=False,
                                        cache_outputs=True):
    """
    Use structured scene information to answer a structured question. Most of the
    heavy lifting is done by the execute handlers defined above.

    We cache node outputs in the node itself; this gives a nontrivial speedup
    when we want to answer many questions that share nodes on the same scene
    (such as during question-generation DFS). This will NOT work if the same
    nodes are executed on different scenes.
    """
    all_input_types, all_output_types = [], []
    node_outputs = []
    for node in question['nodes']:
        if cache_outputs and '_output' in node:
            node_output = node['_output']
        else:
            node_type = node['function']
            msg = 'Could not find handler for "%s"' % node_type
            assert node_type in execute_handlers, msg
            handler = execute_handlers[node_type]
            node_inputs = [node_outputs[idx] for idx in node['inputs']]
            side_inputs = node.get('value_inputs', [])
            node_output = handler(scene_struct, node_inputs, side_inputs)
            if cache_outputs:
                node['_output'] = node_output
        node_outputs.append(node_output)
        if node_output == '__INVALID__':
            break

    if all_outputs:
        return node_outputs
    else:
        return node_outputs[-1]


def insert_scene_node(nodes, idx):
    # First make a shallow-ish copy of the input
    new_nodes = []
    for node in nodes:
        new_node = {
            'function': node['function'],
            'inputs': node['inputs'],
        }
        if 'value_inputs' in node:
            new_node['value_inputs'] = node['value_inputs']
        new_nodes.append(new_node)

    # Replace the specified index with a scene node
    new_nodes[idx] = {'function': 'scene', 'inputs': []}

    # Search backwards from the last node to see which nodes are actually used
    output_used = [False] * len(new_nodes)
    idxs_to_check = [len(new_nodes) - 1]
    while idxs_to_check:
        cur_idx = idxs_to_check.pop()
        output_used[cur_idx] = True
        idxs_to_check.extend(new_nodes[cur_idx]['inputs'])

    # Iterate through nodes, keeping only those whose output is used;
    # at the same time build up a mapping from old idxs to new idxs
    old_idx_to_new_idx = {}
    new_nodes_trimmed = []
    for old_idx, node in enumerate(new_nodes):
        if output_used[old_idx]:
            new_idx = len(new_nodes_trimmed)
            new_nodes_trimmed.append(node)
            old_idx_to_new_idx[old_idx] = new_idx

    # Finally go through the list of trimmed nodes and change the inputs
    for node in new_nodes_trimmed:
        new_inputs = []
        for old_idx in node['inputs']:
            new_inputs.append(old_idx_to_new_idx[old_idx])
        node['inputs'] = new_inputs

    return new_nodes_trimmed


def is_degenerate(question, metadata, scene_struct, answer=None, verbose=False):
    """
    A question is degenerate if replacing any of its relate nodes with a scene
    node results in a question with the same answer.
    """
    if answer is None:
        answer = answer_question(question, metadata, scene_struct)

    for idx, node in enumerate(question['nodes']):
        if node['function'] == 'relate':
            new_question = {
                'nodes': insert_scene_node(question['nodes'], idx)
            }
            new_answer = answer_question(new_question, metadata, scene_struct)
            if verbose:
                print('here is truncated question:')
                for i, n in enumerate(new_question['nodes']):
                    name = n['function']
                    if 'value_inputs' in n:
                        name = '%s[%s]' % (name, n['value_inputs'][0])
                    print(i, name, n['_output'])
                print('new answer is: ', new_answer)

            if new_answer == answer:
                return True

    return False

