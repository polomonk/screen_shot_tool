from tkinter import *
from tkinter import filedialog, ttk
import os
from PIL import ImageGrab, Image, ImageTk
import configparser
# 去除屏幕分辨率的影响。遇坑立牌
import ctypes
ctypes.windll.user32.SetProcessDPIAware()


class Window(Tk):
    def __init__(self):
        super().__init__()
        self.config_raw = configparser.RawConfigParser()     # 定义配置文件的类
        self.config_raw.read('config.cfg')       # 读取配置文件
        # 如果配置文件中的路径存在，则读取同级的全部文件，文件类型筛选放在img_next()
        if os.path.exists(self.config_raw.get('setting', 'img2open')):
            self.img_father_dir = os.path.dirname(self.config_raw.get('setting', 'img2open'))
            self.imglist = os.listdir(self.img_father_dir)
            try:        # 尝试文件按数字排序
                self.imglist.sort(key=lambda x: int(x.split('.')[0]))
            except:
                pass
            self.imglist = iter(self.imglist)     # 将文件列表转换成可迭代形式

        self.title('要测试的图片或视频:')
        # self.wm_overrideredirect(True)
        self.geometry('900x600+400+300')       # 默认窗口的大小和离屏幕左上角的距离
        self.configure(background='gray')       # 窗口背景设置成灰色
        self.img_path = StringVar()     # 创建图像路径的绑定字符变量
        self.img_path.set(self.config_raw.get('setting', 'img2open'))        # 读取配置文件并赋值
        self.cnt = 0        # 对已保存的图片进行计数
        self.canvas = None      # 图片画板
        self.show_photo = None  # 要在画板上显示的图片
        Label(self, text='打开', fg='blue', bg='gray', font=('Fixdsys', 12))\
            .grid(row=0, column=0, ipady=10, sticky=E)      # 放置静态文字：打开
        Entry(self, textvariable=self.img_path, width=50)\
            .grid(row=0, column=1, columnspan=3)        # 能手动改写的文本框，用来存放要打开图片的路径
        self.open_btn = Button(self, text='...', width=3, height=1, command=self.btn_img_chg)\
            .grid(row=0, column=4, sticky=W)        # 切换图像路径按键，绑定btn_img_chg函数
        # self.open_btn.config('disabled')
        Button(self, text='查看', width=6, height=1, command=self.btn_show)\
            .grid(row=0, column=5, padx=10)     # 放置静态文本查看
        Button(self, text='下一张图', width=6, height=1, command=self.btn_next)\
            .grid(row=0, column=6, padx=10)     # 下一张图按键，绑定btn_next函数。点击手动切换到下一张图的路径
        self.auto_next = IntVar()       # 创建整型变量，截图完成后是否直接自动换到下一张图
        self.auto_next.set(0)       # 默认不自动切换
        Radiobutton(self, text='一图一换', variable=self.auto_next)\
            .grid(row=0, column=7)       # 截一张图自动切换到下一张

        self.dir = StringVar()      # 创建存放文件夹路径的字符变量
        self.dir.set(self.config_raw.get('setting', 'dir2open'))     # 读取配置文件的设置并赋值
        self.cbb = ttk.Combobox(self, textvariable=self.dir, width=48, state='readonly')        # 创建可以下拉的组合框方便快速切换保存路径
        self.cbb.grid(row=1, column=1, columnspan=3)
        if os.path.exists(self.dir.get()):      # 如果保存图像的路径存在
            dir_father_dir = os.path.dirname(self.dir.get())        # 读取其上一级文件夹名
            dirs = []       # 用来存放同级目录文件
            for sub_dir in os.listdir(dir_father_dir):      # 遍历上一级目录中的子文件夹并保存在dirs变量中
                dirs.append(dir_father_dir + os.sep + sub_dir)
            self.cbb['values'] = dirs       # 创建下拉框的可选列表

        self.canvas_bgn_x = IntVar()        # 创建画板的坐标整型变量
        self.canvas_bgn_y = IntVar()
        self.selecting = False      # 状态位，是否正在选择要截图的区域
        self.lastDraw = None        # 保存上一次拖到鼠标留下的矩形框，以便之后清除
        Label(self, text='保存目录', bg='gray', fg='blue', font=('Fixdsys', 12))\
            .grid(row=1, column=0, sticky=E)        # 放置静态文本：保存目录
        Button(self, text='...', width=3, height=1, command=self.btn_dir_chg)\
            .grid(row=1, column=4, sticky=W)        # 切换保存目录按键

        self.meg = StringVar()      # 创建提示信息的字符变量
        self.meg.set('快捷键还没弄好')
        Label(self, text='提示', bg='gray', fg='blue', font=('Fixdsys', 12))\
            .grid(row=2, column=0, ipady=10, sticky=SE)     # 放置静态文本：提示
        Label(self, textvariable=self.meg, bg='gray', fg='yellow', font=('Fixdsys', 12))\
            .grid(row=2, column=1, ipady=10, sticky=SE)     # 放置绑定提示变量的文本，提示修改时文本也会随之改变
        Button(self, text='quit', command=self.quit)\
            .grid(row=1, column=5)      # 推出程序按键

    def next_img(self):     # 切换到迭代图像路径列表的下一个图片路径
        file = imglist.__next__()
        while not file.endswith(('.bmp', '.dib', '.png', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.tif', '.tiff')):
            file = imglist.__next__()
        return file

    def btn_img_chg(self):      # 改变图片路径
        global imglist      # 声明图像列表为全局变量
        img2open = filedialog.askopenfilename()     # 打开文件
        if img2open is '':      # 如果中途退出则会返回空字符
            return -1

        img_file = open('config.cfg', 'w')      # 修改配置文件与新的图像路径同步
        self.config_raw.set("setting", "img2open", img2open)
        self.config_raw.write(img_file)
        img_file.close()

        self.img_path.set(img2open)     # 修改要显示的图像路径
        if os.path.exists(self.img_path.get()):     # 如果路径没错，清除提示信息
            self.meg.set('')
        if not os.path.exists(self.dir.get()) or self.dir.get() is '':      # 保存目录不存在则修改提示信息
            self.meg.set('保存目录没有完成设置')
        # 重新得到同级的全部文件并将图像列表转换为可迭代对象
        self.img_father_dir = os.path.dirname(self.config_raw.get('setting', 'img2open'))
        self.imglist = os.listdir(self.img_father_dir)
        try:
            self.imglist.sort(key=lambda x: int(x.split('.')[0]))
        except:
            pass
        self.imglist = iter(self.imglist)

    def btn_show(self):     # 显示图像
        img2open = self.img_path.get()      # 要显示图像的路径
        if img2open is '':      # 图像路径存在判断
            self.meg.set('请选择要打开的文件')
        elif not os.path.exists(img2open):
            self.meg.set('不存在该文件')
        elif img2open.endswith(('.bmp', '.dib', '.png', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.tif', '.tiff')):
            img = Image.open(img2open)      # 读取图像
            self.show_photo = ImageTk.PhotoImage(img)       # 转换成画板能使用的格式
            self.canvas = Canvas(self, bg='gray', width=self.winfo_screenwidth()//2, height=self.winfo_screenheight()//2)       # 创建画板
            self.canvas.create_image(0, 0, anchor=NW, image=self.show_photo)        # 画板左上角对齐格式显示图像
            self.canvas.bind('<B1-Motion>', self.onLeftButtonMove)      # 画板绑定鼠标左键移动事件
            self.canvas.bind('<ButtonRelease-1>', self.onLeftButtonUp)      # 绑定松开鼠标左键事件
            self.canvas.bind('<Button-1>', self.onLeftButtonDown)       # 绑定按下鼠标左键事件
            # self.canvas.bind_all('<KeyPress-q>', self.onKeyDown)      # 绑定快捷键
            # self.canvas.bind_all('<KeyPress-n>', self.onKeyDown)
            self.canvas.grid(row=3, column=1, columnspan=15)        # 给画板安排足够大的空间

        elif img2open.endswith(('avi', 'mp4', 'rmvb', 'flv')):
            # config_raw.set('setting', 'img2open', img2open)
            self.meg.set('暂不支持视频格式')
        else:
            self.meg.set('文件类型错误')

    def btn_next(self):     # 切换到下一张图并显示
        old_path = self.img_path.get()
        new_path = self.next_img()
        try:      # 如果文件名是纯数字排序的
            old_path_num = int(old_path.split('.')[0])
            new_path_num = int(new_path.split('.')[0])
            while old_path_num >= new_path_num:
                new_path = self.next_img()
                new_path_num = int(new_path.split('.')[0])
        except ValueError:     # 如果文件名不是数字排序的
            while os.path.samefile(old_path, new_path):
                new_path = self.next_img()
            new_path = self.next_img()     

        real_path = self.img_father_dir + os.sep + new_path     # 保存当前图像路径
        img_file = open('config.cfg')
        self.config_raw.set("setting", "img2open", real_path)
        self.config_raw.write(img_file)
        img_file.close()

        self.img_path.set(real_path)        # 更改图像路径变量
        self.btn_show()     # 显示更改后的图像

    def btn_dir_chg(self):      # 更改保存目录
        dir2open = filedialog.askdirectory()
        if dir2open is '':
            return
        self.dir.set(dir2open)
        self.config_raw.set('setting', 'dir2open', dir2open)
        if os.path.exists(dir2open):
            self.meg.set('')
        dir_father_dir = os.path.dirname(self.dir.get())
        dirs = []
        for sub_dir in os.listdir(dir_father_dir):
            dirs.append(dir_father_dir + os.sep + sub_dir)
        self.cbb['values'] = dirs
        directory = open('config.cfg')
        self.config_raw.set('setting', 'dir2open', dir2open)
        self.config_raw.write(directory)
        directory.close()

    def onLeftButtonDown(self, event):      # 按下鼠标左键事件
        self.canvas_bgn_x.set(event.x)
        self.canvas_bgn_y.set(event.y)
        # 开始截图
        self.selecting = True

    def onLeftButtonMove(self, event):      # 鼠标移动事件
        # 鼠标左键移动，显示选取的区域
        if not self.selecting:
            return
        try:  # 删除刚画完的图形，要不然鼠标移动的时候是黑乎乎的一片矩形
            self.canvas.delete(self.lastDraw)
        except:
            pass
        self.lastDraw = self.canvas.create_rectangle(self.canvas_bgn_x.get(), self.canvas_bgn_y.get(), event.x, event.y, outline='green')

    def onLeftButtonUp(self, event):        # 鼠标左键松开事件
        # 获取鼠标左键抬起的位置，保存区域截图
        self.selecting = False
        try:
            self.canvas.delete(self.lastDraw)
        except:
            pass
        # 考虑鼠标左键从右下方按下而从左上方抬起的截图
        left, right = sorted([self.canvas_bgn_x.get(), event.x])
        top, bottom = sorted([self.canvas_bgn_y.get(), event.y])

        self.canvas.update()        # 更新画板参数
        # 在屏幕上要截图的区域
        pic = ImageGrab.grab((self.winfo_x()+self.canvas.winfo_x()+left+10, self.winfo_y()+38+self.canvas.winfo_y()+top,
                              self.winfo_x()+self.canvas.winfo_x()+right+10, self.winfo_y()+38+self.canvas.winfo_y()+bottom))
        # 保存图像文件
        while os.path.exists(self.dir.get() + os.sep + str(self.cnt) + '.jpg'):
            self.cnt += 1
        pic.save(self.dir.get() + os.sep + str(self.cnt) + '.jpg')
        self.cnt += 1
        self.meg.set(self.dir.get() + os.sep + str(self.cnt-1) + '.jpg已保存')     # 修改提升信息
        print(self.auto_next.get())
        if self.auto_next.get():
            self.btn_next()
            # self.show_photo = PhotoImage(self.img_path.get())
            # self.canvas.create_image(0, 0, image=self.show_photo)



window = Window()

window.mainloop()
