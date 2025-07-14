from typing import Optional
from unittest.mock import ANY

import pytest
from llm_devtale.config import ParserConfig
from llm_devtale.node import Node, NodeType
from llm_devtale.parser import FileParser, FolderParser, ProjectParser


class TestParser:
    @pytest.mark.parametrize(
        "path, root_path, expected",
        [
            ("/path/to/project/src/file1.py", "/path/to/project", False),
            ("/path/to/project/src/file4.py", "/path/to/project", True),
        ],
    )
    def test_should_ignore(self, path, root_path, expected, test_repository):
        parser_config = ParserConfig()
        file_parser = FileParser(
            parser_config=parser_config,
            model=None,  # type: ignore
            valid_files=["src/file1.py"],
        )
        assert file_parser._should_ignore(path, root_path) == expected


class TestProjectParser:
    def test_parse_empty_project(self):
        parser_config = ParserConfig()
        project_parser = ProjectParser(parser_config=parser_config, model=None)  # type: ignore

        node: Node = project_parser.parse()
        assert node.children == []
        assert node.node_type == NodeType.REPOSITORY

    def test_parse_project_with_folders(self, mocker):
        parser_config = ParserConfig()
        mock_summary = "summary"
        mocker.patch("llm_devtale.parser.generate_summary", return_value=mock_summary)
        project_parser = ProjectParser(
            parser_config=parser_config,
            model=None,  # type: ignore
            valid_files=["src/file1.py"],
        )
        mocker.patch.object(
            FolderParser,
            "parse",
            return_value=Node(
                name="folder1", node_type=NodeType.FOLDER, description="folder1 summary"
            ),
            auto_espec=True,
        )

        node: Node = project_parser.parse()
        assert node.description == mock_summary
        assert len(node.children) == 1

    def test_parse_project_with_filter_folders(self, mocker):
        parser_config = ParserConfig(filter_folders=["src"])
        mock_summary = "summary"
        mocker.patch("llm_devtale.parser.generate_summary", return_value=mock_summary)
        project_parser = ProjectParser(
            parser_config=parser_config,
            model=None,  # type: ignore
            valid_files=["src/file1.py", "src2/file2.py"],
        )
        mocker.patch.object(
            FolderParser,
            "parse",
            return_value=Node(
                name="folder1", node_type=NodeType.FOLDER, description="folder1 summary"
            ),
            auto_espec=True,
        )

        node: Node = project_parser.parse()
        assert len(node.children) == 1

    def test_parse_project_with_folders_dry_run(self, mocker, test_repository):
        parser_config = ParserConfig(dry_run=True)
        project_parser = ProjectParser(
            parser_config=parser_config,
            model=None,  # type: ignore
            valid_files=["src/file1.py"],
        )
        mocker.patch.object(
            FolderParser,
            "parse",
            return_value=Node(
                name="folder1", node_type=NodeType.FOLDER, description="folder1 summary"
            ),
            autospec=True,
        )

        node: Node = project_parser.parse()
        assert node.description == ""
        assert len(node.children) == 1


class TestFolderParser:
    def test_parse_empty_folder(self, mocker):
        parser_config = ParserConfig()
        mock_summary = "summary"
        mocker.patch("llm_devtale.parser.generate_summary", return_value=mock_summary)
        folder_parser = FolderParser(
            parser_config=parser_config,
            model=None,  # type: ignore
            item_path="llm_devtale",
            folder_full_name="llm_devtale",
            valid_files=["llm_devtale/file1.py", "llm_devtale/file2.py"],
        )
        mocker.patch("llm_devtale.parser.os.listdir", return_value=[])
        node: Node = folder_parser.parse()
        assert node.children == []
        assert node.description == ""

    def test_parse_folder(self, mocker):
        parser_config = ParserConfig()
        folder_parser = FolderParser(
            parser_config=parser_config,
            model=None,  # type: ignore
            item_path="llm_devtale",
            folder_full_name="llm_devtale",
            valid_files=["llm_devtale/file1.py", "llm_devtale/file2.py"],
        )

        mock_summary = "summary"
        mocker.patch("llm_devtale.parser.generate_summary", return_value=mock_summary)
        mocker.patch(
            "llm_devtale.parser.os.listdir",
            return_value=["file1.py", "file2.py", "ignored.py"],
        )
        mocker.patch("llm_devtale.parser.os.path.isfile", return_value=True)
        mock_file_node = Node(
            name="file", node_type=NodeType.FILE, description="summary"
        )
        mocker.patch.object(
            FileParser,
            "parse",
            return_value=mock_file_node,
            autospec=True,
        )
        node_dir = folder_parser.parse()
        assert len(node_dir.children) == 2
        assert node_dir.description == mock_summary

    def test_parse_folder_dry_run(self, mocker):
        parser_config = ParserConfig(dry_run=True)
        folder_parser = FolderParser(
            parser_config=parser_config,
            model=None,  # type: ignore
            item_path="llm_devtale",
            folder_full_name="llm_devtale",
            valid_files=["llm_devtale/file1.py", "llm_devtale/file2.py"],
        )

        mocker.patch(
            "llm_devtale.parser.os.listdir", return_value=["file1.py", "file2.py"]
        )
        mocker.patch("llm_devtale.parser.os.path.isfile", return_value=True)
        mock_file_node = Node(
            name="file", node_type=NodeType.FILE, description="summary"
        )
        mocker.patch.object(
            FileParser,
            "parse",
            return_value=mock_file_node,
            autospec=True,
        )
        node_dir = folder_parser.parse()
        assert len(node_dir.children) == 2
        assert node_dir.description == ""


class TestFileParser:
    def test_parse_empty_file(self, mocker):
        parser_config = ParserConfig()
        file_parser = FileParser(
            parser_config=parser_config,
            model=None,  # type: ignore
            item_path="/path/to/project/src/file1.py",
        )
        mocker.patch("builtins.open", mocker.mock_open(read_data=""))
        node: Optional[Node | None] = file_parser.parse()
        assert node is None

    def test_parse_file(self, mocker):
        parser_config = ParserConfig(min_code_lenght=1)
        file_parser = FileParser(
            parser_config=parser_config,
            model=None,  # type: ignore
            item_path="/path/to/project/src/file1.py",
        )

        mock_summary = "summary"
        mocker.patch("llm_devtale.parser.generate_summary", return_value=mock_summary)
        mocker.patch("builtins.open", mocker.mock_open(read_data="def a(): pass"))
        node: Optional[Node | None] = file_parser.parse()

        assert isinstance(node, Node)
        assert node.description == mock_summary
        assert len(node.children) == 0

    def test_parse_file_drt_run(self, mocker):
        parser_config = ParserConfig(dry_run=True, min_code_lenght=1)
        file_parser = FileParser(
            parser_config=parser_config,
            model=None,  # type: ignore
            item_path="/path/to/project/src/file1.py",
        )

        mocker.patch("builtins.open", mocker.mock_open(read_data="def a(): pass"))
        node: Optional[Node | None] = file_parser.parse()

        assert isinstance(node, Node)
        assert node.description == ""
        assert len(node.children) == 0
