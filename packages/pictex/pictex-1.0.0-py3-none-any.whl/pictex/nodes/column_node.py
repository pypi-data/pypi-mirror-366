from typing import Tuple, Callable
from .node import Node
from .container_node import ContainerNode
from ..models import HorizontalAlignment, VerticalDistribution
import skia

class ColumnNode(ContainerNode):

    def _compute_intrinsic_content_bounds(self) -> skia.Rect:
        children = self._get_positionable_children()
        if not children:
            return skia.Rect.MakeEmpty()

        gap = self.computed_styles.gap.get()
        total_gap = gap * (len(children) - 1)
        total_children_height = sum(child.margin_bounds.height() for child in children)
        total_intrinsic_height = total_children_height + total_gap
        max_child_width = max(child.margin_bounds.width() for child in children)
        return skia.Rect.MakeWH(max_child_width, total_intrinsic_height)

    def _calculate_children_relative_positions(self, children: list[Node], get_child_bounds: Callable[[Node], skia.Rect]) -> list[Tuple[float, float]]:
        positions = []
        user_gap = self.computed_styles.gap.get()
        alignment = self.computed_styles.horizontal_alignment.get()
        start_y, distribution_gap = self._distribute_vertically(user_gap, children)

        final_gap = user_gap + distribution_gap
        current_y = start_y
        for child in children:
            child_bounds = get_child_bounds(child)
            child_width = child_bounds.width()
            container_width = self.content_bounds.width()
            child_x = self.content_bounds.left()

            if alignment == HorizontalAlignment.CENTER:
                child_x += (container_width - child_width) / 2
            elif alignment == HorizontalAlignment.RIGHT:
                child_x += container_width - child_width

            positions.append((child_x, current_y))
            current_y += child_bounds.height() + final_gap

        return positions

    def _distribute_vertically(self, user_gap: float, children: list[Node]) -> Tuple[float, float]:
        distribution = self.computed_styles.vertical_distribution.get()
        container_height = self.content_bounds.height()
        children_total_height = sum(child.margin_bounds.height() for child in children)
        total_gap_space = user_gap * (len(children) - 1)
        extra_space = container_height - children_total_height - total_gap_space

        start_y = self.content_bounds.top()
        distribution_gap = 0
        if distribution == VerticalDistribution.BOTTOM:
            start_y += extra_space
        elif distribution == VerticalDistribution.CENTER:
            start_y += extra_space / 2
        elif distribution == VerticalDistribution.SPACE_BETWEEN and len(children) > 1:
            distribution_gap = extra_space / (len(children) - 1)
        elif distribution == VerticalDistribution.SPACE_AROUND:
            distribution_gap = extra_space / len(children)
            start_y += distribution_gap / 2
        elif distribution == VerticalDistribution.SPACE_EVENLY:
            distribution_gap = extra_space / (len(children) + 1)
            start_y += distribution_gap

        return start_y, distribution_gap
