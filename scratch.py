import tkinter as tk

class PageController(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Multi-page App")
        self.geometry("400x300")

        # Container to hold pages
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.pages = {}

        # List of page classes
        for PageClass in (HomePage, PageOne, PageTwo):
            page = PageClass(container, self)
            self.pages[PageClass.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("HomePage")

    def show_page(self, page_name):
        page = self.pages[page_name]
        page.tkraise()

# ------------------------
# Modular Page Definitions
# ------------------------

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="Home Page", font=("Arial", 18))
        label.pack(pady=20)

        btn1 = tk.Button(self, text="Go to Page One",
                         command=lambda: self.controller.show_page("PageOne"))
        btn1.pack(pady=10)

        btn2 = tk.Button(self, text="Go to Page Two",
                         command=lambda: self.controller.show_page("PageTwo"))
        btn2.pack(pady=10)

class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="Page One", font=("Arial", 18))
        label.pack(pady=20)

        btn = tk.Button(self, text="Back to Home",
                        command=lambda: self.controller.show_page("HomePage"))
        btn.pack()

class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="Page Two", font=("Arial", 18))
        label.pack(pady=20)

        btn = tk.Button(self, text="Back to Home",
                        command=lambda: self.controller.show_page("HomePage"))
        btn.pack()

# ------------------------

if __name__ == "__main__":
    app = PageController()
    app.mainloop()
