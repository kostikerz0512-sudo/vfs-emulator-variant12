"""Виртуальная файловая система. Загрузка из XML."""
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field


@dataclass
class Node:
    name: str
    is_dir: bool = True
    content: str = ""
    children: dict = field(default_factory=dict)
    parent: "Node | None" = None


class VFS:
    def __init__(self, name: str = "vfs"):
        self.name = name
        self.root = Node("/")
        self.cwd = self.root

    def load_from_xml(self, filepath: str):
        """Загружает VFS из XML-файла в память."""
        try:
            tree = ET.parse(filepath)
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл VFS не найден: {filepath}")
        except ET.ParseError as e:
            raise ValueError(f"Неверный формат XML: {e}")

        root_elem = tree.getroot()
        self.root = Node("/")
        self.cwd = self.root

        def build(node, elem):
            for child in elem:
                name = child.get("name", "")
                is_dir = child.tag == "dir"
                content = child.text.strip() if child.text else ""

                new_node = Node(name=name, is_dir=is_dir, content=content)
                new_node.parent = node
                node.children[name] = new_node

                if is_dir:
                    build(new_node, child)

        build(self.root, root_elem)

    def resolve_path(self, path: str) -> Node | None:
        """Возвращает узел по пути (абсолютному или относительному)."""
        if not path or path == "/":
            return self.root

        if path.startswith("/"):
            current = self.root
            parts = [p for p in path.split("/") if p]
        else:
            current = self.cwd
            parts = [p for p in path.split("/") if p]

        for part in parts:
            if part == "..":
                if current.parent:
                    current = current.parent
            elif part == ".":
                continue
            elif part in current.children:
                current = current.children[part]
            else:
                return None
        return current