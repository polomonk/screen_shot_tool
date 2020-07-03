from tkinter import *
from tkinter import filedialog, ttk
import os
from PIL import ImageGrab, Image, ImageTk
import configparser
import ctypes
ctypes.windll.user32.SetProcessDPIAware()
config_raw = configparser.RawConfigParser()
config_raw.read('config.cfg')
img_father_dir = os.path.dirname(config_raw.get('setting', 'img2open'))
imglist = os.listdir(img_father_dir)
imglist.sort(key=lambda x: int(x[:-4]))
imglist = iter(imglist)


class Window(Tk):
    def __init__(self):
        super().__init__()
        self.title('要测试的图片或视频:')
        self.geometry('1000x800')
        self.configure(background='gray')
        self.img_path = StringVar()
        self.img_path.set(config_raw.get('setting', 'img2open'))
        self.cnt = 0
        self.canvas = None
        self.show_photo = None
        self.next_img = imglist.__next__
        Label(self, text='打开', fg='blue', bg='gray', font=('Fixdsys', 12))\
            .grid(row=0, column=0, ipady=10, sticky=E)
        Entry(self, textvariable=self.img_path, width=50).grid(row=0, column=1, columnspan=3)
        self.open_btn = Button(self, text='...', width=3, height=1, command=self.btn_open)\
            .grid(row=0, column=4, sticky=W)
        # self.open_btn.config('disabled')
        Button(self, text='查看', width=6, height=1, command=self.btn_show)\
            .grid(row=0, column=5, padx=10)
        Button(self, text='下一个', width=6, height=1, command=self.btn_next)\
            .grid(row=0, column=6, padx=10)
        self.auto_next = IntVar()
        self.auto_next.set(0)
        Radiobutton(self, text='一图一换', variable=self.auto_next).grid(row=0, column=7)

        self.dir = StringVar()
        self.dir.set(config_raw.get('setting', 'dir2open'))
        self.win_bgn_x = IntVar()
        self.win_bgn_y = IntVar()
        self.selecting = False
        self.lastDraw = None
        Label(self, text='保存目录', bg='gray', fg='blue', font=('Fixdsys', 12))\
            .grid(row=1, column=0, sticky=E)
        self.cbb = ttk.Combobox(self, textvariable=self.dir, width=48, state='readonly')
        dir_father_dir = os.path.dirname(self.dir.get())
        dirs = []
        for sub_dir in os.listdir(dir_father_dir):
            dirs.append(dir_father_dir + os.sep + sub_dir)
        self.cbb['values'] = dirs
        self.cbb.grid(row=1, column=1, columnspan=3)
        Button(self, text='...', width=3, height=1, command=self.btn_dir_open)\
            .grid(row=1, column=4, sticky=W)
        self.str = StringVar()
        tmp = 'winx:' + str(self.winfo_x()) + '\twiny:' + str(self.winfo_y())
        self.str.set(tmp)
        self.test = Entry(self, textvariable=self.str).grid(row=1, column=5, columnspan=3)

        self.meg = StringVar()
        self.meg.set('快捷键还没搞好')
        Label(self, text='提示', bg='gray', fg='blue', font=('Fixdsys', 12))\
            .grid(row=2, column=0, ipady=10, sticky=SE)
        Label(self, textvariable=self.meg, bg='gray', fg='red', font=('Fixdsys', 12))\
            .grid(row=2, column=1, ipady=10, sticky=SE)


    def btn_open(self):
        img2open = filedialog.askopenfilename()
        self.img_path.set(img2open)
        if os.path.exists(self.img_path.get()):
            self.meg.set('')

    def btn_show(self):
        img2open = self.img_path.get()
        if img2open is '':
            self.meg.set('请选择要打开的文件')
        elif not os.path.exists(img2open):
            self.meg.set('不存在该文件')
        elif img2open.endswith(('.bmp', '.dib', '.png', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.tif', '.tiff')):
            # print(img2open)
            img = Image.open(img2open)
            self.show_photo = ImageTk.PhotoImage(img)
            # photo = PhotoImage(img2open)
            self.canvas = Canvas(self, bg='gray', width=self.winfo_screenwidth()//2, height=self.winfo_screenheight()//2)
            self.canvas.create_image(0, 0, anchor=CENTER, image=self.show_photo)
            self.canvas.bind('<B1-Motion>', self.onLeftButtonMove)
            self.canvas.bind('<ButtonRelease-1>', self.onLeftButtonUp)
            self.canvas.bind('<Button-1>', self.onLeftButtonDown)
            # self.canvas.bind_all('<KeyPress-q>', self.onKeyDown)
            # self.canvas.bind_all('<KeyPress-n>', self.onKeyDown)
            self.canvas.grid(row=3, column=1, columnspan=15)
            config_raw.set('setting', 'img2open', img2open)

        elif img2open.endswith(('avi', 'mp4', 'rmvb', 'flv')):
            config_raw.set('setting', 'img2open', img2open)
        else:
            self.meg.set('文件类型错误')

    def btn_next(self):
        old_path = self.img_path.get()
        new_path = self.next_img()
        while os.path.samefile(img_father_dir+os.sep+new_path, old_path):
            new_path = self.next_img()
        self.img_path.set(img_father_dir + os.sep + new_path)

    def btn_dir_open(self):
        dir2open = filedialog.askdirectory()
        self.dir.set(dir2open)
        config_raw.set('setting', 'dir2open', dir2open)
        if os.path.exists(dir2open):
            self.meg.set('')

    def onLeftButtonDown(self, event):
        self.win_bgn_x.set(event.x)
        self.win_bgn_y.set(event.y)
        # 开始截图
        self.selecting = True

    def onLeftButtonMove(self, event):
        # 鼠标左键移动，显示选取的区域
        if not self.selecting:
            return
        try:  # 删除刚画完的图形，要不然鼠标移动的时候是黑乎乎的一片矩形
            self.canvas.delete(self.lastDraw)
        except:
            pass
        self.lastDraw = self.canvas.create_rectangle(self.win_bgn_x.get(), self.win_bgn_y.get(), event.x, event.y, outline='green')

    def onLeftButtonUp(self, event):
        # 获取鼠标左键抬起的位置，保存区域截图
        self.selecting = False
        try:
            self.canvas.delete(self.lastDraw)
        except:
            pass

        # 考虑鼠标左键从右下方按下而从左上方抬起的截图
        left, right = sorted([self.win_bgn_x.get(), event.x])
        top, bottom = sorted([self.win_bgn_y.get(), event.y])
        # pic = ImageGrab.grab((left+1, top+1, right, bottom))
        pic = ImageGrab.grab((self.winfo_x()+left+1, self.winfo_y()+top+1, self.winfo_x()+right, self.winfo_y()+bottom))
        self.str.set('winx:' + str(self.winfo_x()) + '  winy:' + str(self.winfo_y()) + '  dx:' + str(event.x) + '  dy:' + str(event.y))
        # print(self.winfo_x(), left+1, self.winfo_y(), top+1, self.winfo_x(), right, self.winfo_y(), bottom)
        while os.path.exists(self.dir.get() + os.sep + str(self.cnt) + '.jpg'):
            self.cnt += 1
        pic.save(self.dir.get() + os.sep + str(self.cnt) + '.jpg')
        self.cnt += 1
        self.meg.set(self.dir.get() + os.sep + str(self.cnt) + '.jpg已保存')
        # print(self.auto_next.get())
        # if self.auto_next.get():
        #     self.btn_next()
        #     self.show_photo = PhotoImage(self.img_path.get())
        #     self.canvas.create_image(0, 0, image=self.show_photo)



window = Window()

window.mainloop()
