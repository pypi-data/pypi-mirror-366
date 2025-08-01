from .event import EventHanding



class Window(EventHanding):

    _instance_count = 0

    def __init__(self, parent=None, *, title: str = "suzaku", size: tuple = (300, 300), id=None, fullscreen=False, opacity: float = 1.0):

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
            "cursor": "arrow"
        }

        self.evts = {
            "close": [],
            "move": [],
            "update": [],
            "mouse_motion": [],
            "mouse_pressed": [],
            "mouse_released": [],
            "mouse_enter": [],
            "mouse_leave": [],
            "key_pressed": [],
            "key_released": [],
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

    @contextlib.contextmanager
    def skia_surface(self, window):

        """
        处理窗口内显示内容

        :param window:
        :return:
        """

        import skia, glfw
        from OpenGL import GL
        context = skia.GrDirectContext.MakeGL()
        (fb_width, fb_height) = glfw.get_framebuffer_size(window)
        backend_render_target = skia.GrBackendRenderTarget(
            fb_width, fb_height, 0, 0, skia.GrGLFramebufferInfo(0, GL.GL_RGBA8))
        surface = skia.Surface.MakeFromBackendRenderTarget(
            context, backend_render_target, skia.kBottomLeft_GrSurfaceOrigin,
            skia.kRGBA_8888_ColorType, skia.ColorSpace.MakeSRGB())
        assert surface is not None
        yield surface
        #context.abandonContext()  <-- 危险方法！容易造成内存泄露
        context.releaseResourcesAndAbandonContext()

    def _on_framebuffer_size(self, window, width, height, ) -> None:
        if self.draw_func:
            with self.skia_surface(window) as surface:
                with surface as canvas:
                    self.draw_func(canvas)
                surface.flushAndSubmit()
                self.update()

    def _on_resizing(self, window, width, height) -> None:
        """
        GLFW窗口事件 -> 窗口大小改变时触发

        :param window: GLFW窗口
        :param width: 宽度
        :param height: 高度
        :return:
        """
        from OpenGL import GL
        GL.glViewport(0, 0, width, height)
        self._on_framebuffer_size(window, width, height)
        self.update()
        self.event_generate("resize", width, height)

    def _on_window_pos(self, window, x, y):
        self.window_attr["x"] = x
        self.window_attr["y"] = y
        self.event_generate("move", x, y)

    def _on_closed(self, window) -> None:
        """
        GLFW窗口事件 -> 窗口关闭时触发

        :param window: GLFW窗口
        :return: None
        """
        #from glfw import terminate
        self.event_generate("close")
        #terminate()

    def _on_mouse_button(self, window, arg1, is_pressed: bool, arg2) -> None:
        """
        GLFW窗口事件 -> 鼠标按键事件触发

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
        if is_pressed:
            self.event_generate("mouse_pressed")
        else:
            self.event_generate("mouse_released")

    def _on_cursor_enter(self, window, is_enter: bool) -> None:
        """
        GLFW窗口事件 -> 鼠标进入、离开窗口时触发

        is_enter:
        True  -> 鼠标进入窗口时触发`window_mouse_enter`事件
        False -> 鼠标离开窗口时触发`window_mouse_leave`事件
        :param window: GLFW窗口
        :param is_enter: 是否进入窗口
        :return: None
        """
        if is_enter:
            self.event_generate("mouse_enter")
        else:
            self.event_generate("mouse_leave")

    def _on_cursor_pos(self, window, x, y) -> None:
        """
        GLFW窗口事件 -> 鼠标在窗口内移动时触发

        :param window: GLFW窗口
        :param x: 鼠标x坐标
        :param y: 鼠标y坐标
        :return: None
        """
        self.event_generate("mouse_motion", x, y)

    def update(self):
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
        return f"Window(title={self.title}, width={self.width}, height={self.height})"

    def cursor(self, cursorname: str = None):
        from glfw import (set_cursor, create_standard_cursor, ARROW_CURSOR, HAND_CURSOR, VRESIZE_CURSOR,
                          RESIZE_NWSE_CURSOR, RESIZE_NS_CURSOR, RESIZE_NESW_CURSOR, RESIZE_EW_CURSOR, RESIZE_ALL_CURSOR,
                          POINTING_HAND_CURSOR, NOT_ALLOWED_CURSOR, NO_CURRENT_CONTEXT, IBEAM_CURSOR, HRESIZE_CURSOR,
                          CROSSHAIR_CURSOR, CENTER_CURSOR)
        if cursorname is None:
            return self.window_attr["cursor"]
        name = cursorname.lower()
        if name == "arrow":
            c = create_standard_cursor(ARROW_CURSOR)
        elif name == "hand":
            c = create_standard_cursor(HAND_CURSOR)
        elif name == "vresize":
            c = create_standard_cursor(VRESIZE_CURSOR)
        elif name == "resize_nwse":
            c = create_standard_cursor(RESIZE_NWSE_CURSOR)
        elif name == "resize_ns":
            c = create_standard_cursor(RESIZE_NS_CURSOR)
        elif name == "resize_nesw":
            c = create_standard_cursor(RESIZE_NESW_CURSOR)
        elif name == "resize_ew":
            c = create_standard_cursor(RESIZE_EW_CURSOR)
        elif name == "resize_all":
            c = create_standard_cursor(RESIZE_ALL_CURSOR)
        elif name == "pointing_hand":
            c = create_standard_cursor(POINTING_HAND_CURSOR)
        elif name == "not_allowed":
            c = create_standard_cursor(NOT_ALLOWED_CURSOR)
        elif name == "no_current":
            c = create_standard_cursor(NO_CURRENT_CONTEXT)
        elif name == "ibeam":
            c = create_standard_cursor(IBEAM_CURSOR)
        elif name == "hresize":
            c = create_standard_cursor(HRESIZE_CURSOR)
        elif name == "crosshair":
            c = create_standard_cursor(CROSSHAIR_CURSOR)
        elif name == "center":
            c = create_standard_cursor(CENTER_CURSOR)
        else:
            return self.window_attr["cursor"]
        self.window_attr["cursor"] = name
        set_cursor(self.winfo_glfw_window(), c)
        return self

    def default_cursor(self, cursorname: str = None):
        if cursorname is None:
            return self.window_attr["default_cursor"]
        self.window_attr["default_cursor"] = cursorname

    def opacity(self, value: float = None):
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

    def visible(self, is_visible: bool = None):
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

    def show(self):
        """
        显示窗口
        :return: self
        """
        from glfw import show_window
        show_window(self.winfo_glfw_window())
        self.window_attr["visible"] = True
        return self

    def hide(self):
        """
        隐藏窗口
        :return: self
        """
        from glfw import hide_window
        hide_window(self.winfo_glfw_window())
        self.window_attr["visible"] = False
        return self

    def maximize(self):
        """
        最大化窗口
        :return: self
        """
        from glfw import maximize_window
        maximize_window(self.winfo_glfw_window())
        return self

    def restore(self):
        """
        恢复窗口（取消窗口最大化）
        :return: self
        """
        from glfw import restore_window
        restore_window(self.winfo_glfw_window())
        return self

    def add(self, visual):
        """
        添加子元素
        :param visual: 子元素
        :return: self
        """
        self.visuals.append(visual)
        self.winfo_parent().add(visual)
        return self

    def destory(self):
        """
        销毁窗口
        :return: None
        """
        from glfw import destroy_window
        destroy_window(self.winfo_glfw_window())

    def title(self, text: str = None):
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

    def resize(self, width: int = None, height: int = None):
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

    def after(self, ms, func):
        """延迟执行函数"""
        import threading
        timer = threading.Timer(ms / 1000, func)
        timer.start()

    def move(self, x: int = None, y: int = None):
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

    def configure(self, **kw):
        """
        配置窗口属性

        :param kw: 属性名-属性值对
        :return: self
        """
        pass
        return self

    config = configure

    def cget(self, key):
        """
        获取窗口属性

        :param key: 属性名
        :return: 属性值
        """
        return self.window_attr[key]

    def winfo(self):
        """
        获取窗口的全部属性
        :return: 窗口属性
        """
        return self.window_attr

    def winfo_parent(self):
        """
        获取父Application
        :return: Application
        """
        return self.window_attr["parent"]

    def winfo_glfw_window(self):
        """
        获取GLFW窗口
        :return: GLFW窗口
        """
        return self.window_attr["glfw_window"]

    def winfo_id(self):
        """
        获取窗口的ID（与GLFW窗口ID不同，仅供Application记录作为标识符）
        :return: ID
        """
        return self.window_attr["id"]

    def winfo_width(self):
        """
        获取窗口的宽度
        :return: 宽度
        """
        return self.window_attr["width"]

    def winfo_height(self):
        """
        获取窗口的高度
        :return: 高度
        """
        return self.window_attr["height"]

    def winfo_x(self):
        """
        获取窗口的x坐标
        :return: x坐标
        """
        return self.window_attr["x"]

    def winfo_y(self):
        """
        获取窗口的y坐标
        :return: y坐标
        """
        return self.window_attr["y"]

    def winfo_rootx(self):
        """
        获取窗口的根窗口x坐标
        :return: x坐标
        """
        return self.window_attr["rootx"]

    def winfo_rooty(self):
        """
        获取窗口的根窗口y坐标
        :return: y坐标
        """
        return self.window_attr["rooty"]

    def set_draw_func(self, func):
        """
        处理Skia绘制事件
        :param func: 绘制函数
        :return: self
        """
        self.draw_func = func
        return self

    def set_application(self, app):
        """
        供Application调用，一般来说无需使用该方法
        :param app: Application实例
        :return: self
        """
        self.application = app
        return self

    def create(self):
        """
        创建GLFW窗口
        :return: GLFW窗口
        """

        import glfw

        if hasattr(self, 'application') and self.application:
            if self.window_attr["fullscreen"]:
                monitor = glfw.get_primary_monitor()
            else:
                monitor = None
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

            return window
        else:
            raise RuntimeError("窗口必须先添加到Application实例")

    def create_bind(self) -> None:
        """
        绑定GLFW窗口事件
        :return: None
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


