from .visual import SkVisual

from typing import Union

class SkButton(SkVisual):

    def __init__(self, *args, text: str = "SkButton", size: tuple[int, int] = (105, 35),
                 cursor: Union[str, None] = "hand", style="SkButton",
                 command: Union[callable, None] = None, id: Union[str, None] = None, **kwargs) -> None:

        """
        Button Component.

        按钮组件。

        **Will be re-written in future. 将被重写。**

        Args:
            *args:
                Passed to `SkVisual`.

                `SkVisual`参数。

            text (str):
                Button text.

                标签文本。

            size (tuple[int, int]):
                Default size.

                默认大小。

            cursor (str | None):
                Cursor style when floating.

                鼠标放上去的光标样式。

            command (function | None):
                Function to run when clicked

                触发点击按钮时，执行的函数（无回调）。

            id (str | None):
                Identification code (Optional).

                可选ID标识码

            **kwargs:
                Passed to `SkVisual`

                `SkVisual`参数。

        Returns:
            None
        """

        super().__init__(*args, size=size, style=style, name="sk_button", **kwargs)

        self.evts["click"] = []
        self.visual_attr["text"] = text

        self.visual_attr["cursor"] = cursor

        self.command = command

        if command:
            self.bind("click", lambda evt: command())

        """self.bind("mouse_enter", lambda evt: print("enter"))
        self.bind("mouse_leave", lambda evt: print("leave"))
        self.bind("mouse_motion", lambda evt: print("motion"))"""

        #self.bind("mouse_pressed", lambda evt: print("pressed"))
        self.bind("mouse_released", self._click)

    def _click(self, evt) -> None:
        """
        Check click event (not pressed).

        判断点击事件，而非按下事件。

        :return: None
        """
        if self.is_mouse_enter:
            self.event_generate("click", evt)

    def draw(self, canvas, rect) -> None:
        """
        绘制按钮方法。

        :param canvas: 传入的skia.Surface
        :param rect: 给出的矩形
        :return:
        """

        from ..style.color import color

        if self.is_mouse_enter:
            if self.is_mouse_pressed:
                sheets = self.theme.get_theme()[self.winfo_style()]["pressed"]
            else:
                sheets = self.theme.get_theme()[self.winfo_style()]["hover"]
        else:
            if self.focus_get() is self and "focus" in self.theme.get_theme()[self.winfo_style()]:
                sheets = self.theme.get_theme()[self.winfo_style()]["focus"]
            else:
                sheets = self.theme.get_theme()[self.winfo_style()]["rest"]

        radius = self.theme.get_theme()[self.winfo_style()]["radius"]

        # 绘制背景
        import skia
        rect_paint = skia.Paint(
            AntiAlias=True,
            Style=skia.Paint.kStrokeAndFill_Style,
        )

        rect_paint.setColor(color(sheets["bg"]))
        rect_paint.setStrokeWidth(sheets["width"])

        canvas.drawRoundRect(rect, radius, radius, rect_paint)

        # 绘制边框
        rect_paint.setStyle(skia.Paint.kStroke_Style)

        # 绘制阴影
        if "bd_shadow" in sheets:
            if "bd_shadw":
                from .packs import set_drop_shadow
                set_drop_shadow(rect_paint, color(sheets["bd"]))

        # Rainbow Border Effect
        if "bd_shader" in sheets:
            if sheets["bd_shader"] == "rainbow":
                from .packs import set_rainbow_shader
                set_rainbow_shader(rect_paint, rect)

        rect_paint.setColor(color(sheets["bd"]))

        canvas.drawRoundRect(rect, radius, radius, rect_paint)

        # 绘制文本
        from .packs import central_text

        central_text(canvas, self.cget("text"), color(sheets["fg"]), self.winfo_x(), self.winfo_y(), self.winfo_width(), self.winfo_height())

