from __future__ import annotations
from copy import deepcopy
from typing import Optional, Tuple
import skia
from ..models import Style, Shadow, PositionMode, RenderProps, CropMode
from ..painters import Painter
from ..utils import create_composite_shadow_filter, clone_skia_rect, to_int_skia_rect
from ..layout import SizeResolver

class Node:

    def __init__(self, style: Style):
        self._raw_style = style
        self._parent: Optional[Node] = None
        self._children: list[Node] = []
        self._computed_styles: Optional[Style] = None
        self._size: Optional[Tuple[int, int]] = None
        self._content_bounds: Optional[skia.Rect] = None
        self._padding_bounds: Optional[skia.Rect] = None
        self._border_bounds: Optional[skia.Rect] = None
        self._margin_bounds: Optional[skia.Rect] = None
        self._paint_bounds: Optional[skia.Rect] = None
        self._render_props: Optional[RenderProps] = None
        self._absolute_position: Optional[Tuple[float, float]] = None

    @property
    def parent(self) -> Node:
        return self._parent

    @property
    def children(self) -> list[Node]:
        return self._children

    @property
    def computed_styles(self) -> Style:
        if self._computed_styles is None:
            self._computed_styles = self._compute_styles()
        return self._computed_styles

    @property
    def size(self) -> Tuple[int, int]:
        if self._size is None:
            self._size = (self.border_bounds.width(), self.border_bounds.height())
        return self._size

    @property
    def absolute_position(self) -> Optional[Tuple[float, float]]:
        if self._absolute_position:
            return self._absolute_position

        position = self.computed_styles.position.get()
        if not position or not self._parent:
            return None

        self_width, self_height = self.size
        if position.mode == PositionMode.RELATIVE:
            parent_content_bounds = self._parent.content_bounds
            parent_position = self._parent.absolute_position
            self_position = position.get_relative_position(self_width, self_height, parent_content_bounds.width(), parent_content_bounds.height())
            self._absolute_position = (
                parent_position[0] + parent_content_bounds.left() + self_position[0],
                parent_position[1] + parent_content_bounds.top() + self_position[1]
            )
            return self._absolute_position

        root = self._get_root()
        root_width, root_height = root.size
        self._absolute_position = position.get_relative_position(self_width, self_height, root_width, root_height)
        return self._absolute_position

    @property
    def padding_bounds(self):
        if self._padding_bounds is None:
            self._padding_bounds = to_int_skia_rect(self._compute_padding_bounds())
        return self._padding_bounds

    @property
    def border_bounds(self):
        if self._border_bounds is None:
            self._border_bounds = to_int_skia_rect(self._compute_border_bounds())
        return self._border_bounds

    @property
    def margin_bounds(self):
        if self._margin_bounds is None:
            self._margin_bounds = to_int_skia_rect(self._compute_margin_bounds())
        return self._margin_bounds

    @property
    def content_bounds(self) -> skia.Rect:
        if self._content_bounds is None:
            self._content_bounds = to_int_skia_rect(self._compute_content_bounds())
        return self._content_bounds

    @property
    def paint_bounds(self) -> skia.Rect:
        if self._paint_bounds is None:
            self._paint_bounds = to_int_skia_rect(self._compute_paint_bounds())
        return self._paint_bounds

    def _compute_padding_bounds(self) -> skia.Rect:
        """
        Compute the box bounds, relative to the node box size, (0, 0).
        """
        content_bounds = self.content_bounds
        padding = self.computed_styles.padding.get()
        return skia.Rect.MakeLTRB(
            content_bounds.left() - padding.left,
            content_bounds.top() - padding.top,
            content_bounds.right() + padding.right,
            content_bounds.bottom() + padding.bottom
        )

    def _compute_border_bounds(self) -> skia.Rect:
        """
        Compute the box bounds, relative to the node box size, (0, 0).
        """
        padding_bounds = self.padding_bounds
        border = self.computed_styles.border.get()
        if not border:
            return clone_skia_rect(padding_bounds)

        return skia.Rect.MakeLTRB(
            padding_bounds.left() - border.width,
            padding_bounds.top() - border.width,
            padding_bounds.right() + border.width,
            padding_bounds.bottom() + border.width
        )

    def _compute_margin_bounds(self) -> skia.Rect:
        """
        Compute the layout bounds (box + margin), relative to the node box size, (0, 0).
        """
        border_bounds = self.border_bounds
        margin = self.computed_styles.margin.get()
        return skia.Rect.MakeLTRB(
            border_bounds.left() - margin.left,
            border_bounds.top() - margin.top,
            border_bounds.right() + margin.right,
            border_bounds.bottom() + margin.bottom
        )

    def _compute_content_bounds(self) -> skia.Rect:
        """
        Compute the inner content bounds (implicit), relative to the node box size, (0, 0).
        Implicit means that it ignores the explicit size set from the styles for the node.
        """
        return SizeResolver(self).resolve()

    def _compute_intrinsic_content_bounds(self) -> skia.Rect:
        """
        Compute the intrinsic content bounds. That is, ignoring any size strategy set.
        It measures the actual content (if the strategy is 'fit-content', then it's the same that _compute_content_bounds())
        """
        raise NotImplementedError("_compute_implicit_content_bounds() is not implemented")

    def _compute_paint_bounds(self) -> skia.Rect:
        """
        Compute the paint bounds, including anything that will be painted for this node, even outside the box (like shadows).
        The final result is relative to the node box size, (0, 0).
        """
        raise NotImplementedError("_compute_paint_bounds() is not implemented")

    def _get_painters(self) -> list[Painter]:
        raise NotImplementedError("_get_painters() is not implemented")

    def prepare_tree_for_rendering(self, render_props: RenderProps) -> None:
        """
        Prepares the node and its children to be rendered.
        It's meant to be called in the root node.
        """
        self.clear()
        self._init_render_dependencies(render_props)
        self._calculate_bounds()
        self._set_absolute_position(0, 0)

    def _init_render_dependencies(self, render_props: RenderProps) -> None:
        self._render_props = render_props
        for child in self._children:
            child._init_render_dependencies(render_props)

    def _calculate_bounds(self) -> None:
        for child in self._children:
            child._calculate_bounds()

        bounds = self._get_all_bounds()
        offset_x, offset_y = -self.margin_bounds.left(), -self.margin_bounds.top()
        for bound in bounds:
            bound.offset(offset_x, offset_y)

    def _get_all_bounds(self) -> list[skia.Rect]:
        return [
            self.content_bounds,
            self.padding_bounds,
            self.border_bounds,
            self.margin_bounds,
            self.paint_bounds,
        ]

    def _set_absolute_position(self, x: float, y: float) -> None:
        has_position = self.computed_styles.position.get() is not None
        has_parent = self._parent is not None
        if not has_position or not has_parent:
            self._absolute_position = (x, y)

    def paint(self, canvas: skia.Canvas) -> None:
        canvas.save()
        x, y = self.absolute_position
        canvas.translate(x, y)
        for painter in self._get_painters():
            painter.paint(canvas)

        canvas.restore()

        for child in self._children:
            child.paint(canvas)

    def clear(self):
        for child in self._children:
            child.clear()

        self._computed_styles = None
        self._size = None
        self._content_bounds = None
        self._padding_bounds = None
        self._border_bounds = None
        self._margin_bounds = None
        self._paint_bounds = None
        self._render_props = None
        self._absolute_position = None

    def _compute_styles(self) -> Style:
        parent_computed_styles = self._parent.computed_styles if self._parent else None
        computed_styles = deepcopy(self._raw_style)
        if not parent_computed_styles:
            return computed_styles

        field_names = computed_styles.get_field_names()
        for field_name in field_names:
            if not computed_styles.is_inheritable(field_name):
                continue
            if computed_styles.is_explicit(field_name):
                continue

            parent_field_value = deepcopy(getattr(parent_computed_styles, field_name))
            setattr(computed_styles, field_name, parent_field_value)

        return computed_styles

    def _compute_shadow_bounds(self, source_bounds: skia.Rect, shadows: list[Shadow]) -> skia.Rect:
        # I don't like this. It only makes sense because it is only being used by paint bounds calculation
        #  However, that responsibility is not clear by the method name.
        #  I mean, if you want to get the shadow bounds in another scenario, this "if" statement don't make any sense.
        if self._render_props.crop_mode == CropMode.CONTENT_BOX:
            return source_bounds
        filter = create_composite_shadow_filter(shadows)
        if filter:
            return filter.computeFastBounds(source_bounds)
        return source_bounds

    def _set_children(self, nodes: list[Node]):
        for node in nodes:
            node._parent = self
        self._children = nodes

    def _get_root(self) -> Optional[Node]:
        root = self
        while root._parent:
            root = root._parent
        return root

    def _get_positionable_children(self) -> list[Node]:
        return [child for child in self.children if child.computed_styles.position.get() is None]
