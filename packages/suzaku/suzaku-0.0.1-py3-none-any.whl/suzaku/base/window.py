from typing import Any

from .event import EventHanding



class Window(EventHanding):

    _instance_count = 0

    def __init__(self, parent=None, *, title: str = "suzaku", size: tuple[int, int] = (300, 300), id=None, fullscreen=False, opacity: float = 1.0, force_hardware_acceleration: bool = False):

        """
        初始化窗口

        :param parent: 父类 一般为"Application"
        :param title: 窗口标题
        :param size: 窗口大小
        :param id: 窗口ID，如果为None将自动设置ID
        :param fullscreen: 窗口是否全屏(有点问题，暂时不要使用)
        :param opacity: 窗口透明度
        """

        self.window_attr = {
            "name": "window",
            "parent": None,
            "glfw_window": None,
            "title": "",
            "width": 0,
            "height": 0,
            "x": 0,
            "y": 0,
            "visible": False,
            "id": "",
            "fullscreen": False,
            "opacity": 1.0,

            "mouse_x": 0,
            "mouse_y": 0,
            "mouse_rootx": 0,
            "mouse_rooty": 0,

            "default_cursor": "arrow",
            "cursor": "arrow",
            "focus": True,
            "force_hardware_acceleration": force_hardware_acceleration
        }

        self.evts = {
            "closed": [],
            "move": [],
            "update": [],

            "mouse_motion": [],
            "mouse_pressed": [],
            "mouse_released": [],
            "mouse_enter": [],
            "mouse_leave": [],

            "key_press": [],
            "key_release": [],
            "key_repeat": [],
            "char": [],

            "focus_in": [],
            "focus_out": [],

            "resize": [],
        }

        self.visuals = []

        Window._instance_count += 1

        ### 获取Application示例，并把自己添加进去。 ###
        from .application import Application
        parent = parent if parent is not None else Application.get_instance()
        self.window_attr["parent"] = parent
        if isinstance(parent, Application):
            parent.add_window(self)
        ##########################################

        ### 初始化窗口属性 ###
        self.window_attr["title"] = title

        if not id:
            id = self.window_attr["name"] + "." + str(self.get_instance_count())
        self.window_attr["id"] = id

        self.window_attr["width"] = size[0]
        self.window_attr["height"] = size[1]

        self.window_attr["fullscreen"] = fullscreen

        if self.window_attr["width"] <= 0 or self.window_attr["height"] <= 0:
            raise ValueError("窗口宽度和高度必须为正数")

        self.window_attr["opacity"] = opacity

        ####################

        self.is_mouse_pressed = False

        self.create()

    @classmethod
    def get_instance_count(cls):
        """
        获取窗口实例数量
        :return: 窗口实例数量
        """
        return cls._instance_count

    import contextlib

    # 修改窗口类的skia_surface方法
    @contextlib.contextmanager
    def skia_surface(self, window):
        import skia, glfw
        from OpenGL import GL

        # 添加窗口有效性检查
        if not glfw.get_current_context() or glfw.window_should_close(window):
            yield None
            return

        try:
            context = skia.GrDirectContext.MakeGL()
            (fb_width, fb_height) = glfw.get_framebuffer_size(window)
            backend_render_target = skia.GrBackendRenderTarget(
                fb_width, fb_height, 0, 0, skia.GrGLFramebufferInfo(0, GL.GL_RGBA8))
            surface = skia.Surface.MakeFromBackendRenderTarget(
                context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
                skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB())
            # 将断言改为更友好的错误处理
            if surface is None:
                raise RuntimeError("Failed to create Skia surface")
            yield surface
        finally:
            if 'context' in locals():
                context.releaseResourcesAndAbandonContext()

    def _on_char(self, window, char) -> None:
        """
        触发字符事件

        Args:
            window: GLFW窗口
            char: 字符

        Returns:
            None
        """
        from .event import Event
        evt = Event(char=chr(char))
        self.event_generate("char", evt)

    def _on_key(self, window, key, scancode, action, mods) -> None:
        """
        触发键盘事件

        Args:
            window: GLFW窗口
            key: 按键
            scancode: 扫描码
            action: 动作
            mods: 修饰键

        Returns:

        """
        from glfw import PRESS, RELEASE, REPEAT, MOD_CONTROL, MOD_ALT, MOD_SHIFT, MOD_SUPER, MOD_NUM_LOCK, MOD_CAPS_LOCK
        from .event import Event
        from glfw import get_key_name

        keyname: str = get_key_name(key, scancode)  # 获取对应的键名，不同平台scancode不同，因此需要输入scancode来正确转换。有些按键不具备键名
        mods_dict = {
            MOD_CONTROL: "control",
            MOD_ALT: "alt",
            MOD_SHIFT: "shift",
            MOD_SUPER: "super",
            MOD_NUM_LOCK: "num_lock",
            MOD_CAPS_LOCK: "caps_lock",
        }

        if mods:
            m = mods_dict[mods]
        else:
            m = "none"

        evt = Event(key=key, keyname=keyname, mods=m)

        # 我真尼玛服了啊，改了半天，发现delete键获取不到键名，卡了我半天啊

        if action == PRESS:
            self.event_generate("key_press", evt)
        elif action == RELEASE:
            self.event_generate("key_release", evt)
        elif action == REPEAT:
            self.event_generate("key_repeat", evt)

    def _on_focus(self, window, focused) -> None:
        from .event import Event
        evt = Event()
        if focused:
            self.window_attr["focus"] = True
            self.event_generate("focus_in", evt)
        else:
            self.window_attr["focus"] = False
            self.event_generate("focus_out", evt)

    def _on_framebuffer_size(self, window, width, height, ) -> None:
        if self.draw_func:
            # 确保设置当前窗口上下文
            import glfw
            glfw.make_context_current(window)
            with self.skia_surface(window) as surface:
                with surface as canvas:
                    self.draw_func(canvas)
                surface.flushAndSubmit()
                self.update()

    def _on_resizing(self, window, width, height) -> None:
        """
        触发resize事件(窗口大小改变时触发)

        :param window: GLFW窗口
        :param width: 宽度
        :param height: 高度
        :return: None
        """
        from OpenGL import GL
        GL.glViewport(0, 0, width, height)
        self._on_framebuffer_size(window, width, height)
        self.window_attr["width"] = width
        self.window_attr["height"] = height
        self.event_generate("resize", width, height)
        #self.update()

    def _on_window_pos(self, window, x, y) -> None:
        """
        触发move事件(窗口位置改变时触发)

        :param window:
        :param x: 传遍鼠标相对窗口的Y坐标
        :param y: 传递鼠标相对窗口的X坐标
        :return: None
        """
        self.window_attr["x"] = x
        self.window_attr["y"] = y
        from .event import Event
        self.event_generate("move", Event(x=x, y=y))

    def _on_closed(self, window) -> None:
        """
        触发closed事件(窗口关闭后触发)

        :param window: GLFW窗口
        :return: None
        """
        #from glfw import terminate
        from .event import Event
        self.event_generate("closed", Event())
        #terminate()

    def _on_mouse_button(self, window, arg1, is_pressed: bool, arg2) -> None:
        """
        触发mouse_pressed事件(鼠标按下时触发)或mouser_released事件(鼠标松开时触发)

        is_pressed:
          True  -> 鼠标按键按下时触发`window_mouse_pressed`事件
          False -> 鼠标按键松开时触发`window_mouse_released`事件

        :param window: GLFW窗口
        :param arg1: 按键
        :param is_pressed: 是否按下
        :param arg2: 修饰键
        :return: None
        """
        #print(arg1, arg2)

        from .event import Event
        from glfw import get_cursor_pos
        pos = get_cursor_pos(window)

        if is_pressed:
            self.event_generate("mouse_pressed", Event(x=pos[0], y=pos[1]))
        else:
            self.event_generate("mouse_released", Event(x=pos[0], y=pos[1]))

    def _on_cursor_enter(self, window, is_enter: bool) -> None:
        """
        触发mouse_enter事件(鼠标进入窗口时触发)或mouser_leave事件(鼠标离开窗口时触发)

        is_enter:
          True  -> 鼠标进入窗口时触发`window_mouse_enter`事件
          False -> 鼠标离开窗口时触发`window_mouse_leave`事件
        :param window: GLFW窗口
        :param is_enter: 是否进入窗口
        :return: None
        """

        from .event import Event
        from glfw import get_cursor_pos
        pos = get_cursor_pos(window)

        if is_enter:
            self.event_generate("mouse_enter", Event(x=pos[0], y=pos[1]))
        else:
            self.event_generate("mouse_leave", Event(x=pos[0], y=pos[1]))

    def _on_cursor_pos(self, window, x, y) -> None:
        """
        触发mouse_motion事件(鼠标进入窗口并移动时触发)

        :param window: GLFW窗口
        :param x: 鼠标x坐标
        :param y: 鼠标y坐标
        :return: None
        """

        from .event import Event

        self.event_generate("mouse_motion", Event(x=x, y=y))

    def update(self) -> None:
        """
        更新窗口
        :return: None
        """
        if self.window_attr["visible"]:
            self.event_generate("update")
            from glfw import swap_buffers
            swap_buffers(self.winfo_glfw_window())

    def __str__(self):
        """
        获取窗口字符串表示
        :return: 窗口字符串表示
        """
        return self.winfo_id()

    def configure(self, **kwargs) -> "Window":
        """
        配置window_attr中的属性

        :param kwargs: 需要设置的属性
        :return: self
        """
        self.window_attr.update(kwargs)
        return self

    config = configure  # 别名

    def cget(self, name: str) -> any:
        """
        获取window_attr中的属性

        :param name: 需要获取属性的名称
        :return: any
        """
        return self.windowattr[name]

    def cursor(self, cursorname: str = None) -> str | type:

        """
        设置窗口当前的鼠标指针样式

        cursorname:
          None -> 获取当前光标样式名
          其他 -> 设置当前光标样式

        :param cursorname: 光标样式名
        :return: 光标样式名 或者 self
        """

        from glfw import (set_cursor, create_standard_cursor, ARROW_CURSOR, HAND_CURSOR, VRESIZE_CURSOR,
                          RESIZE_NWSE_CURSOR, RESIZE_NS_CURSOR, RESIZE_NESW_CURSOR, RESIZE_EW_CURSOR, RESIZE_ALL_CURSOR,
                          POINTING_HAND_CURSOR, NOT_ALLOWED_CURSOR, NO_CURRENT_CONTEXT, IBEAM_CURSOR, HRESIZE_CURSOR,
                          CROSSHAIR_CURSOR, CENTER_CURSOR)
        if cursorname is None:
            return self.window_attr["cursor"]

        name = cursorname.lower()

        cursorget = vars()[f"{name.upper()}_CURSOR"] # e.g. crosschair -> CROSSHAIR_CURSOR
        if cursorget:
            c = create_standard_cursor(cursorget)
        else:
            return self.window_attr["cursor"]

        self.window_attr["cursor"] = name
        set_cursor(self.winfo_glfw_window(), c)
        return self

    def default_cursor(self, cursorname: str = None) -> str | type:
        """
        设置窗口的默认光标样式

        cursorname:
          None -> 获取窗口默认光标样式
          其他 -> 设置窗口默认光标样式

        :param cursorname: 光标样式名
        :return: 光标吗
        """
        if cursorname is None:
            return self.window_attr["default_cursor"]
        self.window_attr["default_cursor"] = cursorname
        return self

    def opacity(self, value: float = None) -> float | type:
        """
        获取或设置窗口透明度

        value:
          None -> 获取窗口透明度
          其他 -> 设置窗口透明度

        :param value: 透明度
        :return: self
        """
        if value is None:
            return self.window_attr["opacity"]
        else:
            self.window_attr["opacity"] = value
            from glfw import set_window_opacity
            set_window_opacity(self.winfo_glfw_window(), value)
        return self

    def visible(self, is_visible: bool = None) -> bool | type:
        """
        获取或设置窗口可见性

        is_visible:
          None -> 获取窗口可见性
          True -> 显示窗口
          False -> 隐藏窗口

        :param is_visible:
        :return: self
        """
        if is_visible is None:
            return self.window_attr["visible"]
        elif is_visible:
            self.show()
        else:
            self.hide()
        return self

    def show(self) -> "Window":
        """
        显示窗口
        :return: self
        """
        from glfw import show_window
        show_window(self.winfo_glfw_window())
        self.window_attr["visible"] = True
        return self

    def hide(self) -> "Window":
        """
        隐藏窗口
        :return: self
        """
        from glfw import hide_window
        hide_window(self.winfo_glfw_window())
        self.window_attr["visible"] = False
        return self

    def maximize(self) -> "Window":
        """
        最大化窗口
        :return: self
        """
        from glfw import maximize_window
        maximize_window(self.winfo_glfw_window())
        return self

    def restore(self) -> "Window":
        """
        恢复窗口(取消窗口最大化)
        :return: self
        """
        from glfw import restore_window
        restore_window(self.winfo_glfw_window())
        return self

    def add(self, visual) -> "Window":
        """
        添加子元素
        :param visual: 子元素
        :return: self
        """
        self.visuals.append(visual)
        return self

    def destroy(self) -> None:
        """Proper window destruction"""
        if self.window_attr["glfw_window"]:
            import glfw
            glfw.destroy_window(self.window_attr["glfw_window"])
            self.window_attr["glfw_window"] = None  # Clear the reference

    def title(self, text: str = None) -> str | type:
        """
        获取或设置窗口标题

        text:
        None -> 获取窗口标题
        其他 -> 设置窗口标题

        :param text: 标题
        :return: self
        """
        if text is None:
            return self.window_attr["title"]
        else:
            self.window_attr["title"] = text
            from glfw import set_window_title
            set_window_title(self.winfo_glfw_window(), text)
            return self

    def resize(self, width: int = None, height: int = None) -> "Window":
        """
        调整窗口大小
        :param width: 宽度
        :param height: 高度
        :param animation_s: 动画持续时间(秒)，0表示无动画
        :return: self
        """
        if width is None:
            width = self.width
        if height is None:
            height = self.height

        self.window_attr["width"] = width
        self.window_attr["height"] = height

        from glfw import set_window_size
        set_window_size(self.winfo_glfw_window(), width, height)
        self.event_generate("resize", width, height)

        return self

    def move(self, x: int = None, y: int = None) -> "Window":
        """
        移动窗口
        :param x: x坐标
        :param y: y坐标
        :return: self
        """
        if x is None:
            x = self.x
        if y is None:
            y = self.y
        self.window_attr["x"] = x
        self.window_attr["y"] = y
        from glfw import set_window_pos
        set_window_pos(self.winfo_glfw_window(), x, y)
        self.event_generate("move")

        return self

    def configure(self, **kw) -> "Window":
        """
        配置窗口属性

        :param kw: 属性名-属性值对
        :return: self
        """
        pass
        return self

    config = configure

    def cget(self, key: str) -> any:
        """
        获取窗口属性

        :param key: 属性名
        :return: 属性值
        """
        return self.window_attr[key]

    def winfo(self) -> dict:
        """
        获取窗口的全部属性
        :return: 窗口属性
        """
        return self.window_attr

    def winfo_parent(self) -> "Application":
        """
        获取父Application
        :return: Application
        """
        return self.window_attr["parent"]

    def winfo_glfw_window(self) -> any:
        """
        获取GLFW窗口
        :return: GLFW窗口
        """
        return self.window_attr["glfw_window"]

    def winfo_id(self) -> str:
        """
        获取窗口的ID(与GLFW窗口ID不同，仅供Application记录作为标识符)
        :return: ID
        """
        return self.window_attr["id"]

    def winfo_width(self) -> int:
        """
        获取窗口的宽度
        :return: 宽度
        """
        return self.window_attr["width"]

    def winfo_height(self) -> int:
        """
        获取窗口的高度
        :return: 高度
        """
        return self.window_attr["height"]

    def winfo_x(self) -> int:
        """
        获取窗口的x坐标
        return: x坐标
        """
        return self.window_attr["x"]

    def winfo_y(self) -> int:
        """
        获取窗口的y坐标
        return: y坐标
        """
        return self.window_attr["y"]

    def winfo_rootx(self) -> int:
        """
        获取窗口的根窗口x坐标
        return: x坐标
        """
        return self.window_attr["rootx"]

    def winfo_rooty(self) -> int:
        """
        获取窗口的根窗口y坐标
        return: y坐标
        """
        return self.window_attr["rooty"]

    def winfo_master_window(self) -> "Window":
        return self

    def set_draw_func(self, func: callable) -> "Window":
        """
        处理Skia绘制事件
        param func: 绘制函数
        return: self
        """
        self.draw_func = func
        return self

    def set_application(self, app) -> "Window":
        """
        供Application调用，一般来说无需使用该方法
        param app: Application实例
        return: self
        """
        self.application = app
        return self

    def create(self) -> any:
        """
        创建GLFW窗口

        Returns:
            any: GLFW窗口
        """

        import glfw

        if hasattr(self, 'application') and self.application:
            if self.window_attr["fullscreen"]:
                monitor = glfw.get_primary_monitor()
            else:
                monitor = None

            import sys
            glfw.window_hint(glfw.STENCIL_BITS, 8)
            # see https://www.glfw.org/faq#macos
            if sys.platform.startswith("darwin"):
                glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
                glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
                glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
                glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

            # 使用应用程序的GLFW配置
            window = glfw.create_window(
                self.winfo_width(),
                self.winfo_height(),
                self.title(),
                monitor, None
            )
            if not window:
                raise RuntimeError("无法创建GLFW窗口")

            self.window_attr["visible"] = True

            self.window_attr["glfw_window"] = window

            pos = glfw.get_window_pos(window)

            self.window_attr["x"] = pos[0]
            self.window_attr["y"] = pos[1]

            self.cursor(self.default_cursor())

            if self.window_attr["force_hardware_acceleration"]:
                glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
                glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_API)
                glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
                glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
                glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

            return window
        else:
            raise RuntimeError("窗口必须先添加到Application实例")

    def create_bind(self) -> None:
        """
        绑定GLFW窗口事件

        Returns:
            None
        """
        window =  self.winfo_glfw_window()
        import glfw
        glfw.make_context_current(window)
        glfw.set_window_size_callback(window, self._on_resizing)
        glfw.set_framebuffer_size_callback(window, self._on_framebuffer_size)
        glfw.set_window_close_callback(window, self._on_closed)
        glfw.set_window_opacity(window, self.window_attr["opacity"])
        glfw.set_mouse_button_callback(window, self._on_mouse_button)
        glfw.set_cursor_enter_callback(window, self._on_cursor_enter)
        glfw.set_cursor_pos_callback(window, self._on_cursor_pos)
        glfw.set_window_pos_callback(window, self._on_window_pos)
        glfw.set_window_focus_callback(window, self._on_focus)
        glfw.set_key_callback(window, self._on_key)
        glfw.set_char_callback(window, self._on_char)


