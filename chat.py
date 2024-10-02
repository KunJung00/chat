import socket
import tkinter as tk
from tkinter import Scrollbar, messagebox, Listbox
from PIL import Image, ImageTk
from tkinter import font
import os
import socket
import threading
import sys


class ExamApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chat Dek Jung")
        self.geometry("600x500")
        
        # Container to hold the frames
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Dictionary to keep track of pages
        self.frames = {}

        # Add pages to the app
        self.show_frame(StartPage)

    def show_frame(self, page_class, user_data=None):
        """Switches to a new frame (page)."""
        # If the frame is not yet created, create it
        if page_class not in self.frames:
            frame = page_class(self.container, self, user_data)
            self.frames[page_class] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Bring the frame to the front
        frame = self.frames[page_class]
        frame.tkraise()

    def load_image(self, image_path, size):
        """ฟังก์ชันช่วยเหลือในการโหลดและปรับขนาดรูปภาพ"""
        try:
            if os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize(size, Image.LANCZOS)
                return ImageTk.PhotoImage(image)
            else:
                raise FileNotFoundError(f"Image file '{image_path}' not found.")
        except Exception as e:
            print(f"Error loading image: {e}".encode('utf-8', errors='ignore').decode('utf-8'))
            return ImageTk.PhotoImage(Image.new('RGB', size, color='gray'))

class StartPage(tk.Frame):
    def __init__(self, parent, controller, user_data=None):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Background image setup
        image_path = "image/bg.jpg"
        self.photo_image = controller.load_image(image_path, (600, 500))

        # Canvas for the background
        self.canvas = tk.Canvas(self, width=600, height=500)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.create_image(0, 0, image=self.photo_image, anchor="nw")
        self.canvas.create_rectangle(100, 100, 500, 400, fill='white', width=0)

        # Widgets on the canvas
        label = tk.Label(self.canvas, text="Welcome", font=("Arial", 24), bg="white", fg="black")
        self.ip_textfield = tk.Entry(self.canvas, width=30, bg='gray')
        client_button = tk.Button(self.canvas, text="Go to Client Page", font=("Arial", 14), command=self.open_secondary_page)
        server_button = tk.Button(self.canvas, text="Go to Server Page", font=("Arial", 14), command=self.open_server_page)
        quit_button = tk.Button(self.canvas, text="Quit", font=("Arial", 14), command=self.controller.quit)

        # Place widgets on the canvas
        self.canvas.create_window(300, 100, window=label)
        self.canvas.create_window(300, 150, window=self.ip_textfield)
        self.canvas.create_window(300, 200, window=client_button)
        self.canvas.create_window(300, 300, window=server_button)
        self.canvas.create_window(300, 400, window=quit_button)

    def open_secondary_page(self):
        user_input = self.ip_textfield.get()  # Get the input from the Entry widget
        if user_input:
            self.controller.show_frame(ClientWindow, user_input)
        else:
            messagebox.showwarning("Input Error", "Please enter some text.")
    def open_server_page(self):
        self.controller.show_frame(ServerWindow)

class ClientWindow(tk.Frame):
    def __init__(self, parent, controller, user_data):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.PORT = 7500
        self.BUFSIZE = 4096
        self.hostname = socket.gethostname()
        # self.SERVERIP = socket.gethostbyname(self.hostname)
        self.SERVERIP = f"{user_data}"
        
        self.clist = []
        self.cdict = {}
        
        

        # Display the data received from StartPage
        label = tk.Label(self, text=f"Received Data: {user_data}", font=("Arial", 18))
        label.pack(pady=20)

        # Scrollbar setup
        self.scroll_bar = Scrollbar(self)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox to show entries (with scrollbar)
        self.my_listbox = Listbox(self, yscrollcommand=self.scroll_bar.set, height=10, width=50)
        self.my_listbox.pack(pady=20)
        self.scroll_bar.config(command=self.my_listbox.yview)

        # Frame to hold the entry and button
        self.entry_frame = tk.Frame(self)
        self.entry_frame.pack(pady=10)

        # Entry widget for input
        self.entry = tk.Entry(self.entry_frame, width=40)
        self.entry.grid(row=0, column=0, padx=5)

        # Button to send the text
        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=0, column=1, padx=5)

        # Close button to go back to the main page
        self.close_button = tk.Button(self, text="Back to Main Page", command=lambda: controller.show_frame(StartPage))
        self.close_button.pack(pady=20)

        # Start client connection
        self.start_client()

    def start_client(self):
        """Initialize the socket connection and start the server handler."""
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.client.connect((self.SERVERIP, self.PORT))
        except Exception as e:
            print(f'ERROR: {e}')
            self.client.close()
            self.show_frame(StartPage)            

        # Start server handler in a separate thread
        task = threading.Thread(target=self.server_handler, args=(self.client,))
        task.daemon = True  # Ensure the thread will close when the main program closes
        task.start()

    def server_handler(self, client):
        """Handle receiving messages from the server."""
        while True:
            try:
                data = client.recv(self.BUFSIZE)
            except Exception as e:
                print(f"Error receiving data: {e}")
                break

            if not data or data.decode('utf-8') == 'q':
                print("Disconnected from server.")
                break

            # Display the message received from the server in the listbox
            self.receive_message(f"User: {data.decode('utf-8')}")
        
        client.close()

    def send_message(self):
        """Handle the send button click and send the message to the server."""
        message = self.entry.get()  # Get the text from the entry
        if message:
            self.client.sendall(message.encode('utf-8'))  # Send the message to the server
            self.receive_message(f"You: {message}")
            self.entry.delete(0, tk.END)  # Clear the entry after sending the message

            # Disconnect if the message is 'q'
            if message == 'q':
                self.client.close()
        else:
            print("Entry is empty")
    def receive_message(self,message):
        self.my_listbox.insert(tk.END, message)




class ServerWindow(tk.Frame):
    def __init__(self, parent, controller, user_data=None):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Server parameters
        self.PORT = 7500
        self.BUFSIZE = 4096
        self.hostname = socket.gethostname()
        self.SERVERIP = socket.gethostbyname(self.hostname)
        self.clist = []
        self.cdict = {}
        
        # Display the server IP
        label = tk.Label(self, text=f"Server IP: {self.SERVERIP}", font=("Arial", 18))
        label.pack(pady=20)

        # Scrollbar setup
        self.scroll_bar = Scrollbar(self)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox to show entries (with scrollbar)
        self.my_listbox = Listbox(self, yscrollcommand=self.scroll_bar.set, height=10, width=50)
        self.my_listbox.pack(pady=20)
        self.scroll_bar.config(command=self.my_listbox.yview)

        # Frame to hold the entry and button
        self.entry_frame = tk.Frame(self)
        self.entry_frame.pack(pady=10)

        # Entry widget for input
        self.entry = tk.Entry(self.entry_frame, width=40)
        self.entry.grid(row=0, column=0, padx=5)

        # Button to send the text
        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=0, column=1, padx=5)

        # Close button to go back to the main page
        self.close_button = tk.Button(self, text="Back to Main Page", command=lambda: controller.show_frame(StartPage))
        self.close_button.pack(pady=20)

        # Start the server in a separate thread
        self.start_server_thread()

    def client_handler(self, client, addr):
        try:
            while True:
                data = client.recv(self.BUFSIZE)
                if not data:
                    break
                
                # Decode the received data
                decoded_data = data.decode('utf-8')
                check = decoded_data.split('|')

                # Handle client name setup
                if check[0] == 'NAME':
                    self.cdict[str(addr)] = check[1]
                    continue
                
                # Broadcast the message to all clients
                username = self.cdict.get(str(addr), str(addr))
                msg = f'{username} >>> {decoded_data}'
                self.receive_message(f"USER: {msg}")
                print("USER: ", msg)
                self.broadcast(msg, client)
        finally:
            self.remove_client(client)
            client.close()

    def broadcast(self, message, sender_client):
        """Send message to all clients except the sender."""
        for client in self.clist:
            if client != sender_client:
                try:
                    client.sendall(message.encode('utf-8'))
                except:
                    self.remove_client(client)

    def remove_client(self, client):
        """Remove the client from the list of connected clients."""
        if client in self.clist:
            self.clist.remove(client)
            self.receive_message(f"Client {client} removed")
            print(f"Client {client} removed")

    def start_server(self):
        """Sets up the server and listens for incoming connections."""
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

            # Start a new thread for each client connection
            threading.Thread(target=self.client_handler, args=(client, addr)).start()

    def start_server_thread(self):
        """Starts the server in a new thread to avoid blocking the Tkinter main loop."""
        server_thread = threading.Thread(target=self.start_server)
        server_thread.daemon = True  # This ensures the thread will close when the main program exits
        server_thread.start()

    def send_message(self):
        """Handle the send button click and display the message in the listbox."""
        message = self.entry.get()  # Get the text from the entry
        if message:
            self.receive_message(f"You: {message}")
            self.broadcast(message,self.clist)
            self.entry.delete(0, tk.END)  # Clear the entry after sending the message
        else:
            messagebox.showwarning("Input Error", "Please enter some text.")
            print("Entry is empty")
    def receive_message(self,message):
        self.my_listbox.insert(tk.END, message)
        


# Main code to run the application
if __name__ == "__main__":
    app = ExamApp()
    app.mainloop()
