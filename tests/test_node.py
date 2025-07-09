import pytest
from llm_devtale.node import (  # Assuming Node and NodeType are in 'your_module.py'
    Node, NodeType)


def test_add_children_multiple_nodes():
    """Test adding multiple children one by one."""
    parent = Node(name="Parent", description="Parent node", node_type=NodeType.FOLDER)
    child1 = Node(name="Child1", description="First child", node_type=NodeType.FILE)
    child2 = Node(name="Child2", description="Second child", node_type=NodeType.FILE)

    parent.add_children(child1)
    parent.add_children(child2)

    assert len(parent.children) == 2
    assert parent.children[0].name == "Child1"
    assert parent.children[1].name == "Child2"


def test_to_dict_with_nested_children():
    """Test to_dict for a node with multiple levels of nesting."""
    grandchild = Node(
        name="Grandchild.txt", description="Deep file", node_type=NodeType.FILE
    )
    child = Node(
        name="Subfolder",
        description="A subfolder",
        node_type=NodeType.FOLDER,
        children=[grandchild],
    )
    parent = Node(
        name="RootFolder",
        description="Top level",
        node_type=NodeType.REPOSITORY,
        children=[child],
    )

    expected_dict = {
        "name": "RootFolder",
        "description": "Top level",
        "node_type": NodeType.REPOSITORY,
        "children": [
            {
                "name": "Subfolder",
                "description": "A subfolder",
                "node_type": NodeType.FOLDER,
                "children": [
                    {
                        "name": "Grandchild.txt",
                        "description": "Deep file",
                        "node_type": NodeType.FILE,
                        "children": [],
                    }
                ],
            }
        ],
    }
    assert parent.to_dict() == expected_dict


def test_to_string_with_nested_children():
    """Test to_string for a node with multiple levels of nesting."""
    grandchild = Node(
        name="data.json", description="Config data", node_type=NodeType.FILE
    )
    child_folder = Node(
        name="config",
        description="Configuration files",
        node_type=NodeType.FOLDER,
        children=[grandchild],
    )
    child_file = Node(
        name="main.py", description="Main script", node_type=NodeType.FILE
    )
    root = Node(
        name="my_project",
        description="Root project",
        node_type=NodeType.REPOSITORY,
        children=[child_folder, child_file],
    )

    expected_string = (
        "my_project (project): Root project\n"
        "    config (folder): Configuration files\n"
        "        data.json (file): Config data\n"
        "    main.py (file): Main script"
    )
    assert root.to_string() == expected_string
