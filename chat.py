import tkinter as tk
from PIL import Image, ImageTk
import os

class ExamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Dek Jung")
        self.root.geometry("600x500")
        
        # Define background image path
        self.image_path = "image/bg.jpg"
        
        # Create a container to hold all pages
        self.container = tk.Frame(self.root)
        self.container.pack(side="top", fill="both", expand=True)
        
        # Create a dictionary to hold all the pages
        self.pages = {}

        # Initialize the pages
        for page in (HomePage, ClientPage, ServerPage):
            page_instance = page(self.container, self)
            self.pages[page.__name__] = page_instance
            page_instance.grid(row=0, column=0, sticky="nsew")
        
        # Show the home page initially
        self.show_page("HomePage")

    def load_image(self, image_path, size):
        """Helper function to load and resize images."""
        try:
            if os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize(size)
                return ImageTk.PhotoImage(image)
            else:
                raise FileNotFoundError(f"Image file '{image_path}' not found.")
        except Exception as e:
            print(f"Error loading image: {e}")
            # Return a blank image if the image fails to load
            return ImageTk.PhotoImage(Image.new('RGB', size, color='gray'))

    def show_page(self, page_name):
        """Method to raise the selected page."""
        page = self.pages[page_name]
        page.tkraise()


class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="Welcome", font=("Arial", 24), bg="white", fg="black")
        label.pack(pady=20)

        client_button = tk.Button(self, text="Go to Client Page", font=("Arial", 14),
                                  command=lambda: controller.show_page("ClientPage"))
        client_button.pack(pady=10)

        server_button = tk.Button(self, text="Go to Server Page", font=("Arial", 14),
                                  command=lambda: controller.show_page("ServerPage"))
        server_button.pack(pady=10)

        quit_button = tk.Button(self, text="Quit", font=("Arial", 14), command=controller.root.quit)
        quit_button.pack(pady=10)


class ClientPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="Client Page", font=("Arial", 24), bg="white", fg="black")
        label.pack(pady=20)

        back_button = tk.Button(self, text="Back to Home", font=("Arial", 14),
                                command=lambda: controller.show_page("HomePage"))
        back_button.pack(pady=10)


class ServerPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="Server Page", font=("Arial", 24), bg="white", fg="black")
        label.pack(pady=20)

        back_button = tk.Button(self, text="Back to Home", font=("Arial", 14),
                                command=lambda: controller.show_page("HomePage"))
        back_button.pack(pady=10)


# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = ExamApp(root)
    root.mainloop()
