import socket
import tkinter as tk
from tkinter import Scrollbar, messagebox, Listbox
from PIL import Image, ImageTk
from tkinter import font
import os
import threading
import sys

# คลาสหลักของแอปพลิเคชัน ใช้สำหรับสร้างหน้าต่างหลักและจัดการเฟรมต่างๆ
class ExamApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chat Dek Jung")  # ตั้งชื่อหน้าต่างหลัก
        self.geometry("600x500")     # กำหนดขนาดหน้าต่างหลัก

        # สร้างคอนเทนเนอร์เพื่อถือเฟรมต่างๆ
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # พจนานุกรมสำหรับเก็บเฟรมต่างๆ
        self.frames = {}

        # เลือกฟอนต์ที่รองรับอิโมจิ ตามระบบปฏิบัติการ
        self.emoji_font = self.get_emoji_font()

        # แสดงหน้าเริ่มต้น (StartPage)
        self.show_frame(StartPage)

    def get_emoji_font(self):
        """เลือกฟอนต์ที่รองรับอิโมจิ ตามระบบปฏิบัติการ"""
        if self.tk.call("tk", "windowingsystem") == "win32":
            return "Segoe UI Emoji"
        elif self.tk.call("tk", "windowingsystem") == "aqua":
            return "Apple Color Emoji"
        else:
            # สำหรับ Linux อาจต้องติดตั้ง "Noto Color Emoji" ก่อน
            return "Noto Color Emoji"

    def show_frame(self, page_class, user_data=None):
        """สลับไปยังเฟรมใหม่ (page)"""
        # หากเฟรมนั้นยังไม่ได้ถูกสร้าง ให้สร้างขึ้นมา
        if page_class not in self.frames:
            frame = page_class(self.container, self, user_data, self.emoji_font)
            self.frames[page_class] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # นำเฟรมนั้นขึ้นมาด้านหน้า
        frame = self.frames[page_class]
        frame.tkraise()

    def load_image(self, image_path, size):
        """ฟังก์ชันช่วยในการโหลดและปรับขนาดรูปภาพ"""
        try:
            if os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize(size, Image.LANCZOS)
                return ImageTk.PhotoImage(image)
            else:
                raise FileNotFoundError(f"Image file '{image_path}' not found.")
        except Exception as e:
            print(f"Error loading image: {e}".encode('utf-8', errors='ignore').decode('utf-8'))
            # หากโหลดรูปไม่สำเร็จ ให้สร้างรูปสีเทาแทน
            return ImageTk.PhotoImage(Image.new('RGB', size, color='gray'))


# หน้าจอเริ่มต้นของแอปพลิเคชัน
class StartPage(tk.Frame):
    def __init__(self, parent, controller, user_data=None, emoji_font="Segoe UI Emoji"):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # ตั้งค่าภาพพื้นหลัง
        image_path = "image/bg.jpg"
        self.photo_image = controller.load_image(image_path, (600, 500))

        # สร้าง Canvas สำหรับแสดงภาพพื้นหลัง
        self.canvas = tk.Canvas(self, width=600, height=500)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.create_image(0, 0, image=self.photo_image, anchor="nw")
        self.canvas.create_rectangle(100, 100, 500, 400, fill="#87CEEB", width=0)

        # สร้างวิดเจ็ตบน Canvas
        label = tk.Label(self.canvas, text="แชทททท", font=("Arial", 24), bg="white", fg="black")
        self.ip_textfield = tk.Entry(self.canvas, width=30, bg='gray', font=(emoji_font, 12))
        client_button = tk.Button(self.canvas, text="เข้าห้องแชท", font=("Arial", 14), command=self.open_secondary_page)
        server_button = tk.Button(self.canvas, text="สร้างห้องแชท", font=("Arial", 14), command=self.open_server_page)
        quit_button = tk.Button(self.canvas, text="ออก", font=("Arial", 14), command=self.controller.quit)

        # วางวิดเจ็ตบน Canvas
        self.canvas.create_window(300, 100, window=label)
        self.canvas.create_window(300, 150, window=self.ip_textfield)
        self.canvas.create_window(300, 200, window=client_button)
        self.canvas.create_window(300, 300, window=server_button)
        self.canvas.create_window(300, 350, window=quit_button)

    def open_secondary_page(self):
        """เปิดหน้าต่าง ClientWindow และส่งข้อมูลที่ผู้ใช้กรอกมา"""
        user_input = self.ip_textfield.get()  # รับค่าจาก Entry widget
        if user_input:
            self.controller.show_frame(ClientWindow, user_input)
        else:
            messagebox.showwarning("เข้าไม่ได้", "กรอกเลขIPห้องก่อน")

    def open_server_page(self):
        """เปิดหน้าต่าง ServerWindow"""
        self.controller.show_frame(ServerWindow)


# หน้าจอสำหรับ Client ที่เชื่อมต่อกับ Server
class ClientWindow(tk.Frame):
    def __init__(self, parent, controller, user_data, emoji_font="Segoe UI Emoji"):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.PORT = 7500
        self.BUFSIZE = 4096
        self.hostname = socket.gethostname()
        self.SERVERIP = f"{user_data}"  # IP ของ Server ที่ได้รับจาก StartPage

        self.clist = []  # รายการ client (ไม่ได้ใช้ในที่นี้)
        self.cdict = {}  # พจนานุกรมเก็บข้อมูล client

        # แสดงข้อมูลที่ได้รับจาก StartPage
        label = tk.Label(self, text=f"ห้องแชท : {user_data}", font=("Arial", 18))
        label.pack(pady=20)

        # ตั้งค่า Scrollbar
        self.scroll_bar = Scrollbar(self)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        # สร้าง Listbox เพื่อแสดงข้อความ (มี Scrollbar)
        self.my_listbox = Listbox(self, yscrollcommand=self.scroll_bar.set, height=10, width=50, font=(emoji_font, 12))
        self.my_listbox.pack(pady=20)
        self.scroll_bar.config(command=self.my_listbox.yview)

        # สร้างเฟรมสำหรับ Entry และปุ่มส่งข้อความ
        self.entry_frame = tk.Frame(self)
        self.entry_frame.pack(pady=10)

        # สร้าง Entry สำหรับกรอกข้อความ
        self.entry = tk.Entry(self.entry_frame, width=40, font=(emoji_font, 12))
        self.entry.grid(row=0, column=0, padx=5)

        # สร้างปุ่มส่งข้อความ
        self.send_button = tk.Button(self.entry_frame, text="ส่ง", command=self.send_message)
        self.send_button.grid(row=0, column=1, padx=5)

        # สร้างปุ่มกลับไปหน้าหลัก
        self.close_button = tk.Button(self, text="กลับไปหน้าหลัก", command=lambda: controller.show_frame(StartPage))
        self.close_button.pack(pady=20)

        # เริ่มการเชื่อมต่อเป็น Client
        self.start_client()

    def start_client(self):
        """ตั้งค่าเชื่อมต่อ Socket และเริ่มรับข้อมูลจาก Server"""
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.client.connect((self.SERVERIP, self.PORT))
        except Exception as e:
            print(f'ERROR: {e}')
            self.client.close()
            self.controller.show_frame(StartPage)            

        # เริ่ม Thread สำหรับจัดการการรับข้อมูลจาก Server
        task = threading.Thread(target=self.server_handler, args=(self.client,))
        task.daemon = True  # ทำให้ Thread ปิดอัตโนมัติเมื่อโปรแกรมหลักปิด
        task.start()

    def server_handler(self, client):
        """จัดการการรับข้อความจาก Server"""
        while True:
            try:
                data = client.recv(self.BUFSIZE)
            except Exception as e:
                print(f"Error receiving data: {e}")
                break

            if not data or data.decode('utf-8') == 'q':
                print("Disconnected from server.")
                break

            # แสดงข้อความที่ได้รับจาก Server ใน Listbox
            self.receive_message(f"User: {data.decode('utf-8')}")

        client.close()

    def send_message(self):
        """จัดการการคลิกปุ่มส่งข้อความและส่งข้อความไปยัง Server"""
        message = self.entry.get()  # รับข้อความจาก Entry
        if message:
            self.client.sendall(message.encode('utf-8'))  # ส่งข้อความไปยัง Server
            self.receive_message(f"You: {message}")
            self.entry.delete(0, tk.END)  # ล้างข้อความใน Entry หลังส่ง

            # ถ้าข้อความคือ 'q' ก็ปิดการเชื่อมต่อ
            if message == 'q':
                self.client.close()
        else:
            print("Entry is empty")

    def receive_message(self, message):
        """เพิ่มข้อความลงใน Listbox"""
        self.my_listbox.insert(tk.END, message)


# หน้าจอสำหรับ Server ที่รอรับการเชื่อมต่อจาก Client
class ServerWindow(tk.Frame):
    def __init__(self, parent, controller, user_data=None, emoji_font="Segoe UI Emoji"):
        tk.Frame.__init__(self, parent,bg='Brown')
        self.controller = controller

        # พารามิเตอร์ของ Server
        self.PORT = 7500
        self.BUFSIZE = 4096
        self.hostname = socket.gethostname()
        self.SERVERIP = socket.gethostbyname(self.hostname)  # IP ของ Server
        self.clist = []  # รายการ Client ที่เชื่อมต่อ
        self.cdict = {}  # พจนานุกรมเก็บข้อมูล Client

        # แสดง IP ของ Server
        label = tk.Label(self, text=f"ห้องแชท : {self.SERVERIP}", font=("Arial", 18))
        label.pack(pady=20)

        # ตั้งค่า Scrollbar
        self.scroll_bar = Scrollbar(self)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        # สร้าง Listbox เพื่อแสดงข้อความ (มี Scrollbar)
        self.my_listbox = Listbox(self, yscrollcommand=self.scroll_bar.set, height=10, width=50, font=(emoji_font, 12))
        self.my_listbox.pack(pady=20)
        self.scroll_bar.config(command=self.my_listbox.yview)

        # สร้างเฟรมสำหรับ Entry และปุ่มส่งข้อความ
        self.entry_frame = tk.Frame(self)
        self.entry_frame.pack(pady=10)

        # สร้าง Entry สำหรับกรอกข้อความ
        self.entry = tk.Entry(self.entry_frame, width=40, font=(emoji_font, 12))
        self.entry.grid(row=0, column=0, padx=5)

        # สร้างปุ่มส่งข้อความ
        self.send_button = tk.Button(self.entry_frame, text="ส่ง", command=self.send_message)
        self.send_button.grid(row=0, column=1, padx=5)

        # สร้างปุ่มกลับไปหน้าหลัก
        self.close_button = tk.Button(self, text="กลับไปหน้าหลัก", command=lambda: controller.show_frame(StartPage))
        self.close_button.pack(pady=20)

        # เริ่ม Server ใน Thread แยก
        self.start_server_thread()

    def client_handler(self, client, addr):
        """จัดการการรับและส่งข้อความกับ Client"""
        try:
            while True:
                data = client.recv(self.BUFSIZE)
                if not data:
                    break

                # แปลงข้อมูลที่ได้รับเป็นข้อความ
                decoded_data = data.decode('utf-8')
                check = decoded_data.split('|')

                # ตรวจสอบการตั้งชื่อผู้ใช้
                if check[0] == 'NAME':
                    self.cdict[str(addr)] = check[1]
                    continue

                # สร้างข้อความที่จะแพร่กระจายไปยังทุก Client
                username = self.cdict.get(str(addr), str(addr))
                msg = f'{username} >>> {decoded_data}'
                self.receive_message(f"USER: {msg}")
                print("USER: ", msg)
                self.broadcast(msg, client)
        finally:
            self.remove_client(client)
            client.close()

    def broadcast(self, message, sender_client):
        """ส่งข้อความไปยังทุก Client ยกเว้นผู้ส่ง"""
        for client in self.clist:
            if client != sender_client:
                try:
                    client.sendall(message.encode('utf-8'))
                except:
                    self.remove_client(client)

    def remove_client(self, client):
        """ลบ Client ออกจากรายการที่เชื่อมต่อ"""
        if client in self.clist:
            self.clist.remove(client)
            self.receive_message(f"Client {client} removed")
            print(f"Client {client} removed")

    def start_server(self):
        """ตั้งค่า Server และรอรับการเชื่อมต่อจาก Client"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.SERVERIP, self.PORT))
        server.listen(5)
        self.receive_message(f"Server started at {self.SERVERIP}:{self.PORT}")
        print(f"Server started at {self.SERVERIP}:{self.PORT}")

        while True:
            client, addr = server.accept()
            self.receive_message(f"New connection from {addr}")
            self.clist.append(client)

            # สร้าง Thread ใหม่สำหรับการเชื่อมต่อแต่ละ Client
            threading.Thread(target=self.client_handler, args=(client, addr), daemon=True).start()

    def start_server_thread(self):
        """เริ่ม Server ใน Thread ใหม่เพื่อไม่ให้บล็อก Tkinter main loop"""
        server_thread = threading.Thread(target=self.start_server, daemon=True)
        server_thread.start()

    def send_message(self):
        """จัดการการคลิกปุ่มส่งข้อความและแสดงข้อความใน Listbox"""
        message = self.entry.get()  # รับข้อความจาก Entry
        if message:
            self.receive_message(f"You: {message}")
            self.broadcast(message, self.clist)  # ส่งข้อความไปยังทุก Client
            self.entry.delete(0, tk.END)  # ล้างข้อความใน Entry หลังส่ง
        else:
            messagebox.showwarning("Input Error", "Please enter some text.")
            print("Entry is empty")

    def receive_message(self, message):
        """เพิ่มข้อความลงใน Listbox"""
        self.my_listbox.insert(tk.END, message)


# โค้ดหลักสำหรับรันแอปพลิเคชัน
if __name__ == "__main__":
    app = ExamApp()
    app.mainloop()
