import tkinter as tk

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Multi-Page GUI Example")
        self.geometry("400x300")
        
        # Create a container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        
        # Create a dictionary to hold the pages
        self.pages = {}
        
        # Initialize the pages
        for page in (HomePage, PageOne, PageTwo):
            page_instance = page(container, self)
            self.pages[page.__name__] = page_instance
            page_instance.grid(row=0, column=0, sticky="nsew")
        
        # Show the home page
        self.show_page("HomePage")

    def show_page(self, page_name):
        page = self.pages[page_name]
        page.tkraise()

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="Home Page", font=("Arial", 18))
        label.pack(pady=10, padx=10)
        
        button1 = tk.Button(self, text="Go to Page One",
                            command=lambda: controller.show_page("PageOne"))
        button1.pack()

        button2 = tk.Button(self, text="Go to Page Two",
                            command=lambda: controller.show_page("PageTwo"))
        button2.pack()

class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="Page One", font=("Arial", 18))
        label.pack(pady=10, padx=10)
        
        button = tk.Button(self, text="Back to Home",
                           command=lambda: controller.show_page("HomePage"))
        button.pack()

class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="Page Two", font=("Arial", 18))
        label.pack(pady=10, padx=10)
        
        button = tk.Button(self, text="Back to Home",
                           command=lambda: controller.show_page("HomePage"))
        button.pack()

# Run the application
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
