import os
from pathlib import Path
from typing import List, Optional


from .utils import generate_summary, get_llm_model
from .node import NodeType, Node
from .config import ParserConfig


class Parser:
    def __init__(
        self,
        parser_config: ParserConfig,
        item_path: str = "./",
        folder_full_name: str = "",
        valid_files: list = [],
    ):
        self.parser_config: ParserConfig = parser_config
        self.root_path: str = str(parser_config.directory)
        self.item_path: str = item_path
        self.folder_full_name: str = folder_full_name
        self.valid_files = valid_files

    def _should_ignore(self, path, root_path) -> bool:
        path = Path(path)

        if os.path.isabs(path):
            item_relative_path: str = str(Path(path).relative_to(root_path))
        else:
            item_relative_path: str = str(path)

        # If hot_files is not empty, only include the files that are in the hot_files list
        if self.valid_files and item_relative_path not in self.valid_files:
            return True

        return False


class ProjectParser(Parser):
    def get_readme(self) -> str:
        original_readme_content: str = ""
        for readme in self.parser_config.readme_valid_files:
            readme_path = os.path.join(self.root_path, readme)
            if os.path.exists(readme_path):
                with open(readme_path, "r") as file:
                    original_readme_content = " ".join(file.readlines())
                    break

        return original_readme_content

    def parse(
        self,
    ) -> Node:
        """It creates a dev tale for each file in the repository, and it
        generates a README for the whole repository.
        """

        repository_name: str = os.path.basename(os.path.abspath(self.root_path))
        project_node = Node(
            name=repository_name,
            description="",
            node_type=NodeType.REPOSITORY,
        )
        folder_tales = {
            "repository_name": repository_name,
            "folders": [],
        }

        # Get the project tree before modify it along with the complete list of files
        # that the repository has.
        file_paths = list(
            map(lambda x: os.path.join(self.root_path, x), self.valid_files)
        )

        # Extract the folder paths from files list. This allows to avoid processing
        # folders that should be ignored, and to use the process_folder logic.
        folders = list(set([os.path.dirname(file_path) for file_path in file_paths]))

        # sort to always have the root folder at the beggining of the list.
        folders: List[str] = sorted(folders, key=lambda path: path.count("/"))

        # Get the folder's README section of each folder while it create a dev tale
        # for each file.
        for folder_path in folders:
            folder_full_name: str = ""
            try:
                # Fix folder path to avoid issues with file system.
                if not folder_path.endswith("/"):
                    folder_path += "/"

                folder_full_name = os.path.relpath(folder_path, self.root_path)

                # folder's summary
                folder_parser = FolderParser(
                    parser_config=self.parser_config,
                    item_path=folder_path,
                    folder_full_name=folder_full_name,
                    valid_files=self.valid_files,
                )

                folder_tale = folder_parser.parse()
            except Exception:
                folder_tale = None

            # Create a dictionary with the folder's info that serves as context for
            # generating the main repository summary
            if folder_tale:
                folder_tales["folders"].append(
                    {folder_tale.name: folder_tale.description}
                )
                project_node.add_children(folder_tale)

        project_summary = ""
        if project_node.children and not self.parser_config.skip_folder_readme:
            original_readme = self.get_readme()
            project_data: dict = {
                "project_name": repository_name,
                "project_content": folder_tales,
                "project_readme": original_readme,
            }
            model = get_llm_model(self.parser_config.model_name)
            project_summary = generate_summary(
                model, project_data, summary_type=NodeType.REPOSITORY
            )
            project_node.description = project_summary

        return project_node


class FolderParser(Parser):
    def parse(self) -> Node:
        """It creates a dev tale for each file in the directory without exploring
        subdirectories, and it generates a summary section for the folder.
        """
        folder_path: str = self.item_path
        tales: list = []
        node_dir = Node(
            name=self.folder_full_name, description="", node_type=NodeType.FOLDER
        )

        # Iterate through each file in the folder
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)

            # Check it if is a file that we need to process
            if os.path.isfile(file_path) and not self._should_ignore(
                file_path, self.root_path
            ):
                # Create dev tale for the file

                try:
                    file_parser = FileParser(
                        parser_config=self.parser_config,
                        item_path=file_path,
                        valid_files=self.valid_files,
                    )
                    file_tale = file_parser.parse()
                except Exception:
                    file_tale = None

                # Create a dictionary with the tale's file_docstrings values to use them
                # as context for the folder's README section
                if file_tale is not None:
                    tales.append(file_tale.description)
                    node_dir.add_children(file_tale)

        if node_dir.children and not self.parser_config.skip_folder_readme:
            # Generate a folder one-line description using the folder's readme as context.
            folder_data: dict = {
                "folder_name": self.folder_full_name,
                "folder_content": tales,
            }

            model = get_llm_model(self.parser_config.model_name)
            folder_summary = generate_summary(
                model, folder_data, summary_type=NodeType.FOLDER
            )
            node_dir.description = folder_summary

        return node_dir


class FileParser(Parser):
    def parse(self) -> Optional[Node | None]:
        file_path: str = self.item_path
        file_name: str = os.path.basename(file_path)
        file_ext: str = os.path.splitext(file_name)[-1]

        with open(file_path, "r") as file:
            code: str = file.read()

        # # Return empty devtale if the input file is empty.
        if not code or len(code) < self.parser_config.min_code_lenght:
            return None

        code_text = code
        # For config/bash files we do not aim to document the file itself. We
        # care about understanding what the file does.
        if not file_ext:
            # a small single chunk is enough
            code_text: str = code

        file_data: dict[str, str] = {
            "file_name": file_name,
            "file_content": code_text,
        }

        model = get_llm_model(self.parser_config.model_name)
        file_summary = generate_summary(model, file_data, summary_type=NodeType.FILE)

        return Node(name=file_name, description=file_summary, node_type=NodeType.FILE)
