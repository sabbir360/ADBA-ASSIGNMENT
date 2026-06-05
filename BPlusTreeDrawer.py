from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from b_plus_tree import Node

class BPlusTreeDrawer:
    def draw(self, root: Node, order: int) -> None:
        ascii_lines: list[str] = self.__build_tree_diagram(root, order)[0]

        for line in ascii_lines:
            print(line.rstrip())

    def __build_tree_diagram(self, node: Node, order: int) -> tuple[list[str], int, int]:
        node_box: list[str] = self.__build_node_box(node, order)
        box_width: int = len(node_box[0])
        box_center: int = box_width // 2
        parent_pointer_centers: list[int] = self.__get_pointer_centers(node, order)

        if node.is_leaf or not node.child_pointers:
            return node_box, box_width, box_center

        child_blocks: list[tuple[list[str], int, int]] = [
            self.__build_tree_diagram(child_node, order) for child_node in node.child_pointers
        ]
        gap_between_children: int = 4
        child_height: int = max(len(child_lines) for child_lines, _, _ in child_blocks)

        combined_child_lines: list[str] = ["" for _ in range(child_height)]
        child_centers: list[int] = []
        child_area_width: int = 0

        for child_index, (child_lines, child_width, child_center) in enumerate(child_blocks):
            padded_child_lines: list[str] = child_lines + [" " * child_width] * (child_height - len(child_lines))

            if child_index > 0:
                for line_index in range(child_height):
                    combined_child_lines[line_index] += " " * gap_between_children
                child_area_width += gap_between_children

            for line_index in range(child_height):
                combined_child_lines[line_index] += padded_child_lines[line_index]

            child_centers.append(child_area_width + child_center)
            child_area_width += child_width

        diagram_width: int = max(box_width, child_area_width)
        box_start: int = (diagram_width - box_width) // 2
        children_start: int = (diagram_width - child_area_width) // 2
        parent_center: int = box_start + box_center
        shifted_parent_pointer_centers: list[int] = [
            box_start + pointer_center for pointer_center in parent_pointer_centers
        ]
        shifted_child_centers: list[int] = [children_start + child_center for child_center in child_centers]

        top_lines: list[str] = [(" " * box_start) + line for line in node_box]
        top_lines = [line.ljust(diagram_width) for line in top_lines]

        connector_pairs: list[tuple[int, int]] = []
        for child_index, child_center in enumerate(shifted_child_centers):
            start_x: int = parent_center
            if child_index < len(shifted_parent_pointer_centers):
                start_x = shifted_parent_pointer_centers[child_index]

            connector_pairs.append((start_x, child_center))

        connector_height: int = 4
        connector_grid: list[list[str]] = [[" " for _ in range(diagram_width)] for _ in range(connector_height)]

        for start_x, child_center in connector_pairs:
            self.__draw_connector(connector_grid, start_x, 0, child_center, connector_height - 1)

        connector_lines: list[str] = ["".join(row) for row in connector_grid]
        shifted_child_lines: list[str] = [
            ((" " * children_start) + line).ljust(diagram_width) for line in combined_child_lines
        ]

        return top_lines + connector_lines + shifted_child_lines, diagram_width, parent_center

    def __build_node_box(self, node: Node, order: int) -> list[str]:
        slot_count: int = order
        widest_key: int = max((len(str(key)) for key in node.keys), default=1)
        cell_width: int = max(3, widest_key + 1)
        border: str = "+" + "+".join("-" * cell_width for _ in range(slot_count)) + "+"

        key_cells: list[str] = [str(key).center(cell_width) for key in node.keys]
        key_cells.extend([" " * cell_width] * (slot_count - len(key_cells)))

        if node.is_leaf:
            marker_count: int = len(node.record_values)
        else:
            marker_count = len(node.child_pointers)

        lower_cells: list[str] = ["o".center(cell_width) for _ in range(marker_count)]

        lower_cells.extend([" " * cell_width] * (slot_count - len(lower_cells)))

        return [
            border,
            "|" + "|".join(key_cells) + "|",
            "+" + "+".join("-" * cell_width for _ in range(slot_count)) + "+",
            "|" + "|".join(lower_cells) + "|",
            border,
        ]

    def __get_pointer_centers(self, node: Node, order: int) -> list[int]:
        slot_count: int = order
        widest_key: int = max((len(str(key)) for key in node.keys), default=1)
        cell_width: int = max(3, widest_key + 1)

        if node.is_leaf:
            pointer_count: int = len(node.record_values)
        else:
            pointer_count = len(node.child_pointers)

        pointer_centers: list[int] = []
        for pointer_index in range(min(pointer_count, slot_count)):
            cell_start: int = 1 + pointer_index * (cell_width + 1)
            pointer_centers.append(cell_start + cell_width // 2)

        return pointer_centers

    def __draw_connector(
        self,
        connector_grid: list[list[str]],
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
    ) -> None:
        if not connector_grid or not connector_grid[0]:
            return

        grid_height: int = len(connector_grid)
        grid_width: int = len(connector_grid[0])

        if not (0 <= start_x < grid_width and 0 <= start_y < grid_height):
            return
        if not (0 <= end_x < grid_width and 0 <= end_y < grid_height):
            return

        def place(row: int, column: int, character: str) -> None:
            existing_character: str = connector_grid[row][column]
            if existing_character not in (" ", character):
                connector_grid[row][column] = "+"
            else:
                connector_grid[row][column] = character

        place(start_y, start_x, "|")

        if start_y == end_y:
            return

        turn_y: int = min(start_y + 1, end_y)
        place(turn_y, start_x, "|")

        if start_x == end_x:
            for row in range(turn_y + 1, end_y + 1):
                place(row, start_x, "|")
            return

        step_x: int = 1 if end_x > start_x else -1
        branch_character: str = "\\" if step_x > 0 else "/"

        for column in range(start_x + step_x, end_x, step_x):
            place(turn_y, column, "-")

        for row in range(turn_y + 1, end_y):
            place(row, end_x, branch_character)

        place(end_y, end_x, "|")
