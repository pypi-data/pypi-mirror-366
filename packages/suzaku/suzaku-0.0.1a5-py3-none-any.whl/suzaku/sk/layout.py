import warnings
from typing import Union, Any

class Boxes:

    from .window import SkWindow

    def __init__(self, parent: Union[SkWindow, "SkVisual"], direction: str="h") -> None:

        """

        Box layout manager.

        Box布局管理器。

        Args:
            parent (SkWindow | SkVisual): 
                Container that accepts the layout.

                接受布局的容器。
        
            direction (str): 
                Direction of the layout, either `v` for vertical or `h` for horizontal.

                布局的方向（`h`为水平方向布局，`v`为垂直方向布局）。
        """

        self.parent = parent
        self.children = []
        self.direction = direction

    def add_child(self, child: "SkVisual", padx: int=5, pady: int=5, expand: bool=False) -> None:
        """
        Add a component to the layout.

        添加组件至该布局。

        Args:
            child (SkVisual): 
                Conponent.

                组件。

            padx (int): 
                Paddings on x direction.

                左右的外边距。

            pady (int): 
                Paddings on y direction.
                
                上下的外边距。

            expand (int): 
                Whether should the children expand to fill empty space.
                
                是否占满剩余空间。

        Returns:
            None
        """
        self.children.append(
            {
                "child": child,
                "padx": padx,
                "pady": pady,
                "expand": expand,
            }
        )

        self.parent.bind("resize", self.update)

    def change_direction(self, direction: str) -> None:
        """
        Change layout direction.

        改变布局方向。

        Args
            direction (str): 
                Direction of the layout, either `v` or `h`

                布局方向，`v`代表纵向或`h`代表横向。

        Returns:
            None
        """
        direction = direction.lower()
        if direction not in ["v", "h"]:
            warnings.warn(f"Invalid direction '{direction}', ingnored and kept old layout direction.")
            return
        self.direction = direction
        self.update(self.parent.winfo_width(), self.parent.winfo_height())
        self.update(self.parent.winfo_width(), self.parent.winfo_height())
        # Don't ask why to update twice here, idk how but it gets the layout finally correct.
        # 别问我为什么要放两个update，我也不知道为什么，这样做布局意外的正常改变了

    def update(self, width: int, height: int) -> None:
        """
        Update layout.

        更新布局。

        Args:
            width (int): 
                Container width.

                容器宽度。

            height (int): 
                Container height.
            
                容器高度。

        Returns: 
            None
        """
        if self.direction == "h":
            # Horizontal Layout

            width -= self.children[-1]["padx"]

            fixed_width = 0
            expand_count = 0
            total_padx = 0

            # Calculate total width of fixed elements, and number of available extended elements.
            for child in self.children:
                total_padx += child["padx"]
                if child["expand"]:
                    expand_count += 1
                else:
                    fixed_width += child["child"].visual_attr["width"]

            # Calculate available width (minus all padx)
            remaining_width = max(0, width - fixed_width - total_padx)
            expand_width = remaining_width // expand_count if expand_count > 0 else 0

            current_x = 0
            for child in self.children:
                c = child["child"]
                current_x += child["padx"]  # Add padx of current element

                if child["expand"]:
                    c.visual_attr["x"] = current_x
                    c.visual_attr["y"] = child["pady"]
                    c.visual_attr["width"] = expand_width
                    c.visual_attr["height"] = height - child["pady"] * 2
                else:
                    c.visual_attr["x"] = current_x
                    c.visual_attr["y"] = child["pady"]
                    c.visual_attr["width"] = c.visual_attr["d_height"]
                    c.visual_attr["height"] = height - child["pady"] * 2

                current_x += c.visual_attr["width"]  # Move to next element
        else:
            # Vertival Layout

            height -= self.children[-1]["pady"]

            fixed_height = 0
            expand_count = 0
            total_pady = 0

            for child in self.children:
                total_pady += child["pady"]
                if child["expand"]:
                    expand_count += 1
                else:
                    fixed_height += child["child"].visual_attr["height"]

            remaining_height = max(0, height - fixed_height - total_pady)
            expand_height = remaining_height // expand_count if expand_count > 0 else 0

            current_y = 0
            for child in self.children:
                c = child["child"]
                current_y += child["pady"]

                if child["expand"]:
                    c.visual_attr["x"] = child["padx"]
                    c.visual_attr["y"] = current_y
                    c.visual_attr["width"] = width - child["padx"] * 2
                    c.visual_attr["height"] = expand_height
                else:
                    c.visual_attr["x"] = child["padx"]
                    c.visual_attr["y"] = current_y
                    c.visual_attr["width"] = width - child["padx"] * 2
                    c.visual_attr["height"] = c.visual_attr["d_height"]

                current_y += c.visual_attr["height"]

class Box:
    def box_configure(self, padx: int=5, pady: int=5, expand: bool=False, direction=None) -> "Box":
        """
        Set components layout.

        配置组件布局。

        Args:
            padx (int):
                Paddings on x direction.
                
                左右的外边距。

            pady (int): 
                Paddings on y direction
                
                上下的外边距。

            expand (bool): 
                Whether should the component expand to fill empty space.
                
                是否占满剩余空间。

            direction (str): 
                Layout direction, either `v` for vertical or `h` for horizontal.

                布局的方向(`h`为水平方向布局，`v`为垂直方向布局)。

        Returns:
            Box: The box itself.
        """
        parent = self.winfo_parent()
        layout = parent.winfo_layout()
        if not layout:
            if direction is None:
                direction = "h"
            l = Boxes(parent, direction)
            parent.set_layout(l)
        else:
            l = layout
        if not self in l.children:
            l.add_child(self, padx=padx, pady=pady, expand=expand)
            l.update(parent.winfo_width(), parent.winfo_height())
            self._show()
        return self

    box = box_configure

    def hbox_configure(self, *args, **kwargs) -> "Box":
        """
        Horizontal layout

        水平布局

        Args:
            *args: 
                Will be sent to `box_configure()`.

                `box_configure()`参数。

            **kwargs: 
                Will be sent to `box_configure()`.

                `box_configure()`参数。
        
        Returns:
            Box: The box itself.
        """
        return self.box_configure(*args, **kwargs, direction="h")

    hbox = hbox_configure

    def vbox_configure(self, *args, **kwargs) -> "Box":
        """
        Vertical layout.

        垂直布局。

        Args:
            *args: 
                Will be sent to `box_configure()`.

                `box_configure()`参数。

            **kwargs: 
                Will be sent to `box_configure()`.

                `box_configure()`参数。
        
        Returns:
            Box: The box itself.
        """
        return self.box_configure(*args, **kwargs, direction="v")

    vbox = vbox_configure

    def box_forget(self) ->  "Box":
        """
        Remove box layout.

        移除组件布局。

        Returns:
            None
        """
        layout = self.winfo_parent().winfo_layout()
        if layout:
            for child in layout.children:
                if self is child["child"]:
                    layout.children.remove(child)
                    self._hide()
                    layout.update(layout.parent.winfo_width(), layout.parent.winfo_height())
        return self



class Place:
    def place_configure(self, x: int, y: int, width: int = None, height: int = None):
        """
        Absolute positioning layout.

        绝对位置布局。

        Args:
            x:
                x position of the component.

                组件的x坐标。

            y:
                y position of the component.

                组件的y坐标。

            width:
                Width of the component, `dwidth` by default.

                组件的宽度（不填则为`dwidth`）。

            height:
                Height of the component, `dheight` by default.

                组件的高度（不填则为`dheight`）。
        
        Returns:
            None
        """
        self.winfo_parent().set_layout("place")

        self.visual_attr["x"] = x
        self.visual_attr["y"] = y
        if width is not None:
            self.visual_attr["width"] = width
        if height is not None:
            self.visual_attr["height"] = height

        self._show()

    place = place_configure

    def place_forget(self) -> None:
        """
        Remove layout.
        移除组件布局。

        Returns:
            None
        """
        self._hide()


class Puts:

    from .window import SkWindow

    def __init__(self, parent: Union[SkWindow, "SkVisual"]) -> None:
        """
        Rerlative layout manager.

        相对位置布局管理器。

        Args:
            parent (SkWindow | SkVisual): 
                Parent component
                父组件
        
        Returns:
            None
        """

        self.parent = parent
        self.children = []

    def add_child(self, child: "SkVisual", margin: tuple[int, int, int, int] = (5, 5, 5, 5)):
        """
        Add child component.

        添加组件。

        Args:
            child (SkVisual): 
                The child component.

                组件。

            margin (tuple[int, int, int, int]): 
                Distance from the components to the container.

                组件与容器的间距。
        
        Returns:
            None
        """
        self.children.append(
            {
                "child": child,
                "margin": margin,
            }
        )

        self.parent.bind("resize", self.update)

    def update(self, width, height):
        """
        Update layout.

        更新布局。

        Args:
            width: 
                Container width.

                容器宽度。

            height:
                Container height.
                
                容器高度。

        Returns: 
            None
        """
        for child in self.children:
            c = child["child"]
            c.visual_attr["x"] = child["margin"][0]
            c.visual_attr["y"] = child["margin"][1]
            c.visual_attr["width"] = width - child["margin"][2] - child["margin"][3]
            c.visual_attr["height"] = height - child["margin"][1] - child["margin"][3]


class Put:

    """
    Relative layout.

    相对位置布局。
    """

    def put_configure(self, margin: tuple[int, int, int, int] = (0, 0, 0, 0)) -> None:
        """
        Relative layout. ()
        相对组件所在容器布局。（未来将会制作anchor来对齐位置）。

        Args:
            margin:
                Distance from the components to the container.

                组件与容器的间距。

        Returns:
            None
        """
        parent = self.winfo_parent()
        layout = parent.winfo_layout()
        if not layout:
            l = Puts(parent)
            parent.set_layout(l)
        else:
            l = layout
        if not self in l.children:
            l.add_child(self, margin=margin)
            l.update(parent.winfo_dwidth(), parent.winfo_dheight())
            self._show()
        return None

    put = put_configure

    def put_forget(self) -> None:
        """
        Remove component layuout.

        移除组件布局。

        Returns:
            None
        """
        parent = self.winfo_parent()
        layout = parent.winfo_layout()
        if layout:
            l = layout
            if self in l.children:
                l.children.remove(self)
                l.update(parent.winfo_dwidth(), parent.winfo_dheight())
                self._hide()


class Layout(Box, Place, Put):
    pass
