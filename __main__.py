import customtkinter as ctk
import tkinter.filedialog as tk
import tools

VERSION = "1.0.0"
FONT = "meiryo"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("640x360")

        self.title("SBANサポーター")

        self.setup_form()

    def setup_form(self):
        ctk.set_appearance_mode("dark")  # "System"(default) or "Light" or "dark"
        ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        frame_body = BodyFrame(self)
        frame_body.grid(row=0, column=0, columnspan=2, sticky="nsew")

        label_log = ctk.CTkLabel(
            master=self, text="あああ", font=(FONT, 15), anchor="w"
        )
        label_log.grid(row=1, column=0, padx=(10, 5), sticky="nsew")

        button_export = ctk.CTkButton(master=self, text="ログを出力", font=(FONT, 15))
        button_export.grid(row=1, column=1, padx=(5, 10))


class BodyFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master=master, corner_radius=0)

        self.current_tab = 0

        self.setup_form()

    def setup_form(self):
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.tab("数値からMIDI", 0).grid(row=0, column=0, sticky="nsew")
        self.tab("モールスからMIDI", 1).grid(row=0, column=1, sticky="nsew")
        self.tab("点字からMIDI", 2).grid(row=0, column=2, sticky="nsew")
        self.tab("MIDIから画像", 3).grid(row=0, column=3, sticky="nsew")

    def tab(self, text, index):
        return ctk.CTkButton(
            self,
            text=text,
            fg_color="gray20",
            hover_color="gray10",
            corner_radius=0,
            font=(FONT, 12),
            command=lambda: self.set_current_tab(index),
        )

    def set_current_tab(self, index):
        self.current_tab = index


if __name__ == "__main__":
    app = App()
    app.mainloop()
