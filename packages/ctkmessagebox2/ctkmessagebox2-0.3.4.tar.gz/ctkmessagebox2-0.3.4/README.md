# CustomTkinter Messagebox 2

CustomTkinter Messagebox 2 is an implementation of the `tkinter.messagebox` functionalities using the `customtkinter` package. It replicates the same functions available in `tkinter.messagebox`, but with support for CustomTkinter's modernized interface.

Optimal widgets size proportion, better UX, easy to use and does not require configuration.

It allows the user to copy the message to the clipboard. 

## Features

This package offers the following functionalities, replicating the behavior of `tkinter.messagebox`:

There are 8 different message box types:

- **showinfo**: Displays a dialog with an informational message.
- **showwarning**: Displays a dialog with a warning message.
- **showerror**: Displays a dialog with an error message.
- **askquestion**: Displays a question and returns the user's response (`Yes/No`).
- **askokcancel**: Displays a question and returns `OK` or `Cancel`.
- **askyesno**: Displays a question and returns `Yes` or `No`.
- **askretrycancel**: Displays an error message and asks the user to choose `Retry` or `Cancel`.

The window size is self adjustable according to the number of lines in the message.
Messages will also be displayed with a scrollbar if they are bigger than the message box window. 

The main code will stop and wait for the message box to be closed and the function returns a value related to the button clicked:
- `showinfo(master, title:str, message:str)` 
- `showsuccess(master, title:str, message:str)`
- `showwarning(master, title:str, message:str)`
- `showerror(master, title:str, message:str)`
- `askokcancel(master, title:str, message:str)`
- `askyesno(master, title:str, message:str)` 
- `askyesnocancel(master, title:str, message:str)`
- `askretrycancel(master, title:str, message:str)`
- `showcustom(master, title:str, message:str, icon:str, *buttons:[str])` 

![ctkmb2.png](ctkmb2.png)

## Icons
There are 5 icons designed for this package and are free to use and redistribute. 
![IMG_0080.PNG](IMG_0080.PNG)
Icons variables:
```python
ERROR = "icons/error-icon.png"
INFO = "icons/info-icon.png"
QUESTION = "icons/ask-icon.png"
WARNING = "icons/alert-icon.png"
SUCCESS = "icons/ok-icon.png"
```

## Installation

Install the package via pip:

```bash
pip install ctkmessagebox2
```

## Project Structure
The project follows the same functional structure as tkinter.messagebox, allowing easy migration of code and adaptation to more modern interfaces with customtkinter.

Unlikely Tkinter messagebox, ctkmessagebox requires the master as the first argument for all messages.

## Usage

All functions share the same structure, with 3 arguments: `master: ctk.CTk`, `title: str` and `message: str`.
All the rest is done by the package.

Here’s a basic example of how to use the CustomTkinter Messagebox:

```python
import customtkinter as ctk
import ctkmessagebox2 as messagebox

app = ctk.CTk()
app.geometry("400x200")


def show_info():
    result = messagebox.showinfo(app, "Information", "This is an informational message.")
    print("Clicked Button: ", result)


button = ctk.CTkButton(app, text="Show Info", command=show_info)
button.pack(pady=20)

app.mainloop()
```

Complete example that allows you to test all message boxes available:
```python
import customtkinter as ctk
import ctkmessagebox2 as messagebox

class AppTest(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.minsize(400, 200)
        self.title("CTkMessageBox 2 Demo")

        buttons = ctk.CTkFrame(self)
        buttons.pack(side=ctk.LEFT)
        self.button_1 = ctk.CTkButton(buttons, text="showinfo", command=self.showinfo)
        self.button_2 = ctk.CTkButton(buttons, text="showsuccess", command=self.showsuccess)
        self.button_3 = ctk.CTkButton(buttons, text="showwarning", command=self.showwarning)
        self.button_4 = ctk.CTkButton(buttons, text="showerror", command=self.showerror)
        self.button_5 = ctk.CTkButton(buttons, text="askokcancel", command=self.askokcancel)
        self.button_6 = ctk.CTkButton(buttons, text="askyesno", command=self.askyesno)
        self.button_7 = ctk.CTkButton(buttons, text="askyesnocancel", command=self.askyesnocancel)
        self.button_8 = ctk.CTkButton(buttons, text="askretrycancel", command=self.askretrycancel)
        self.button_9 = ctk.CTkButton(buttons, text="askabortignore", command=self.askabortignore)
        self.button_10 = ctk.CTkButton(buttons, text="custom", command=self.custom)
        self.button_1.pack(side="top", padx=10, pady=10)
        self.button_2.pack(side="top", padx=10, pady=10)
        self.button_3.pack(side="top", padx=10, pady=10)
        self.button_4.pack(side="top", padx=10, pady=10)
        self.button_5.pack(side="top", padx=10, pady=10)
        self.button_6.pack(side="top", padx=10, pady=10)
        self.button_7.pack(side="top", padx=10, pady=10)
        self.button_8.pack(side="top", padx=10, pady=10)
        self.button_9.pack(side="top", padx=10, pady=10)
        self.button_10.pack(side="top", padx=10, pady=10)

        details = ctk.CTkFrame(self)
        details.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=5)

        self._result = ctk.StringVar(value='Clicked: ')
        self._title = ctk.StringVar(value='CTkMessageBox 2 Demo')

        ctk.CTkLabel(details, textvariable=self._result).pack()
        ctk.CTkLabel(details, text='Title').pack()
        ctk.CTkEntry(details, textvariable=self._title).pack(fill=ctk.X)
        ctk.CTkLabel(details, text='Message').pack()
        self._msg = ctk.CTkTextbox(details)
        self._msg.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

        self.toplevel_window = None

    def custom(self):
        msg = self._msg.get(0.0, ctk.END).strip('\n')
        if not msg:
            msg = "Lorem Ipsum is simply dummy text of the printing and typesetting industry."

        buttons = ['CTk', 'MessageBox 2', 'is', 'awesome!']
        icon = messagebox.SUCCESS
        self.toplevel_window = messagebox.showcustom(self, self._title.get(), msg, icon, *buttons)
        self._result.set(value=f"Clicked: {self.toplevel_window}")

    def showsuccess(self):
        msg = self._msg.get(0.0, ctk.END).strip('\n')
        if not msg:
            msg = "Lorem Ipsum is simply dummy text of the printing and typesetting industry."
        self.toplevel_window = messagebox.showsuccess(self, self._title.get(), msg)
        self._result.set(value=f"Clicked: {self.toplevel_window}")

    def askyesno(self):
        msg = self._msg.get(0.0, ctk.END).strip('\n')
        if not msg:
            msg = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."
        self.toplevel_window = messagebox.askyesno(self, self._title.get(), msg)
        self._result.set(value=f"Clicked: {self.toplevel_window}")

    def askyesnocancel(self):
        msg = self._msg.get(0.0, ctk.END).strip('\n')
        if not msg:
            msg = "Lorem Ipsum is simply dummy text of the printing and typesetting industry."  #
        self.toplevel_window = messagebox.askyesnocancel(self, self._title.get(), msg)
        self._result.set(value=f"Clicked: {self.toplevel_window}")

    def askretrycancel(self):
        msg = self._msg.get(0.0, ctk.END).strip('\n')
        if not msg:
            msg = "Lorem Ipsum is simply dummy text of the printing and typesetting industry."
        self.toplevel_window = messagebox.askretrycancel(self, self._title.get(), msg)
        self._result.set(value=f"Clicked: {self.toplevel_window}")

    def showinfo(self):
        msg = self._msg.get(0.0, ctk.END).strip('\n')
        if not msg:
            msg = "Lorem Ipsum is simply dummy text of the printing and typesetting industry."
        self.toplevel_window = messagebox.showinfo(self, self._title.get(), msg)
        self._result.set(value=f"Clicked: {self.toplevel_window}")

    def showwarning(self):
        msg = self._msg.get(0.0, ctk.END).strip('\n')
        if not msg:
            msg = "Lorem Ipsum is simply dummy text of the printing and typesetting industry."
        self.toplevel_window = messagebox.showwarning(self, self._title.get(), msg)
        self._result.set(value=f"Clicked: {self.toplevel_window}")

    def showerror(self):
        msg = self._msg.get(0.0, ctk.END).strip('\n')
        if not msg:
            msg = "Lorem Ipsum is simply dummy text of the printing and typesetting industry."
        self.toplevel_window = messagebox.showerror(self, self._title.get(), msg)
        self._result.set(value=f"Clicked: {self.toplevel_window}")

    def askokcancel(self):
        msg = self._msg.get(0.0, ctk.END).strip('\n')
        if not msg:
            msg = "Lorem Ipsum is simply dummy text of the printing and typesetting industry."  #
        self.toplevel_window = messagebox.askokcancel(self, self._title.get(), msg)
        self._result.set(value=f"Clicked: {self.toplevel_window}")

    def askabortignore(self):
        msg = self._msg.get(0.0, ctk.END).strip('\n')
        if not msg:
            msg = "Lorem Ipsum is simply dummy text of the printing and typesetting industry."  #
        self.toplevel_window = messagebox.askabortignore(self, self._title.get(), msg)
        self._result.set(value=f"Clicked: {self.toplevel_window}")


if __name__ == "__main__":
    app = AppTest()
    app.mainloop()
```
The example above is included in the package, and you can run it from the terminal using the command:

```bash
python -m ctkmessagebox2.demo
```

## Contributions
Contributions are welcome! If you want to improve the project, feel free to open an issue or submit a pull request.

Check the source code at [GitHub - ctkmessagebox](https://github.com/hoffmanlucas/ctkmessagebox.)

### Fork the repository
- Create a branch (git checkout -b feature/new-feature)
- Commit your changes (git commit -m 'Add new feature')
- Push to the branch (git push origin feature/new-feature)
- Open a Pull Request

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

