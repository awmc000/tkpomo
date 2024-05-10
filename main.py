'''
Pomodoro Timer App

Apr 23 - 24th, 2024

Alex McColm
'''
from datetime import timedelta
import tkinter as tk
from tkinter import ttk
import os.path
from pygame import mixer

class PomodoroTimerApp(tk.Frame):
    '''
    The pomodoro timer application class extends tk.Frame.
    '''
    # Whether or not the timer is started.
    started = False

    # True if user is in work period, False if on break.
    active = True

    # False if the break is short, True if it is long. 
    long_break = False

    pomodoro_minutes = 35
    break_minutes = 10

    # Timer starts on "work" period.
    time_remaining = timedelta(minutes=pomodoro_minutes)

    # Colour to set widgets to for the respective modes.
    colours = {"pomodoro": "#f05b56", "break": "#57f15c"}

    def valid_time(self, p):
        '''
        Function used to validate input to timer length
        fields. Checks if the input is empty or digits.
        '''
        return str.isdigit(p) or p == ""

    def toggle_settings(self, event):
        '''
        Hides or unhides settings widgets.
        '''
        if self.pomodoro_time_label.winfo_ismapped():
            self.pomodoro_time_label.pack_forget()
            self.pomodoro_time_entry.pack_forget()
            self.short_break_label.pack_forget()
            self.short_break_entry.pack_forget()
            self.confirm_button.pack_forget()
        else:
            self.pomodoro_time_label.pack()
            self.pomodoro_time_entry.pack()
            self.short_break_label.pack()
            self.short_break_entry.pack()
            self.confirm_button.pack()

    def toggle_timer(self, event):
        '''
        Toggle whether the timer is running or stopped.
        '''
        self.started = not self.started
        self.start_sound.play()
        if self.timer_button['text'] == "Start":
            self.timer_button.config(text="Stop")
        else:
            self.timer_button.config(text="Start")

    def reset_timer(self, event):
        '''
        Rolls back the timer to start the work or break period again.
        '''
        if self.active:
            self.time_remaining = timedelta(minutes=self.pomodoro_minutes)
        else:
            if not self.long_break:
                self.time_remaining = timedelta(minutes=self.break_minutes)
                self.long_break = True
            else:
                self.time_remaining = timedelta(minutes=2*self.break_minutes)
                self.long_break = False
                
        self.time_label.config(text=self.get_time_remaining())
        self.started = False
        self.timer_button.config(text="Start")

    def skip_state(self, event):
        '''
        Skip from either work to break or break to work state.
        '''
        self.started = False
        self.active = not self.active
        if self.active:
            self.parent.configure(background=self.colours['pomodoro'])
            self.style.configure(style="BW.TLabel", background=self.colours['pomodoro'])
            self.parent.title('[POMODORO] Timer')
        else:
            self.parent.configure(background=self.colours['break'])
            self.style.configure(style="BW.TLabel", background=self.colours['break'])
            self.parent.title('[BREAK] Timer')
        self.reset_timer(event)

    def update(self):
        '''
        Called every second to update the timer text.
        '''
        if self.started:
            self.time_remaining = self.time_remaining - timedelta(seconds=1)
            self.time_label.config(text=self.get_time_remaining())
            if self.time_remaining <= timedelta(seconds=0):
                self.done_sound.play()
                self.skip_state(None)
        window.after(1000, self.update)

    def confirm_settings(self, event):
        '''
        Save study/break period times to the .conf file.
        '''
        pomodoro_input = self.pomodoro_time_entry.get()
        break_input = self.short_break_entry.get()

        if pomodoro_input.isdigit():
            self.pomodoro_minutes = int(pomodoro_input)
        if break_input.isdigit():
            self.break_minutes = int(break_input)

        with open('pomodoro.conf', 'w', encoding="utf-8") as file:
            file.write(f'pomodoro\t{self.pomodoro_minutes}'
                f'\nbreak\t{self.break_minutes}')

    def get_time_remaining(self):
        '''
        Return the time left in the form MM:SS.
        '''
        return str(self.time_remaining)[2:]

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # Check if a config file exists saving the user's times
        if os.path.isfile('pomodoro.conf'):
            with open('pomodoro.conf', 'r', encoding="utf-8") as file:
                print(file.read())
        else:
            with open('pomodoro.conf', 'w', encoding="utf-8") as file:
                file.write(f'pomodoro\t{self.pomodoro_minutes}'
                    f'\nbreak\t{self.break_minutes}')

        # Use Pygame mixer to play sound effects
        mixer.init()
        self.start_sound = mixer.Sound("start.mp3")
        self.done_sound = mixer.Sound("done.mp3")

        # Style to use for large text
        self.style = ttk.Style()
        self.style.configure("BW.TLabel",
            foreground="black",
            background="#f05b56",
            font=("sans-serif", 28))

        vtcb = self.register(self.valid_time)
        # self.state_label = ttk.Label(text="POMODORO", style="BW.TLabel")
        self.time_label = ttk.Label(text=self.get_time_remaining(), style="BW.TLabel")

        self.pomodoro_time_label = ttk.Label(text='Pomodoro time:')
        self.pomodoro_time_entry = ttk.Entry(validate="all", validatecommand=(vtcb, '%P'))

        self.short_break_label = ttk.Label(text='Short break time\n(long break will be double):')
        self.short_break_entry = ttk.Entry(validate="all", validatecommand=(vtcb, '%P'))

        self.timer_button = ttk.Button(self.parent, text='Start')
        self.timer_button.bind('<Button-1>', self.toggle_timer)

        self.reset_button = ttk.Button(self.parent, text="Reset")
        self.reset_button.bind("<Button-1>", self.reset_timer)

        self.skip_button = ttk.Button(self.parent, text="Skip")
        self.skip_button.bind("<Button-1>", self.skip_state)

        self.settings_button = ttk.Button(self.parent, text='Settings')
        self.settings_button.bind('<Button-1>', self.toggle_settings)

        self.confirm_button = ttk.Button(self.parent, text="Confirm")
        self.confirm_button.bind('<Button-1>', self.confirm_settings)

        self.time_label.pack()
        self.timer_button.pack(side=tk.LEFT)
        self.reset_button.pack(side=tk.LEFT)
        self.skip_button.pack(side=tk.LEFT)
        self.settings_button.pack(side=tk.LEFT)

        parent.configure(background=self.colours['pomodoro'])
        parent.title('[POMODORO] Timer')

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    window = PomodoroTimerApp(root)

    window.after(1000, window.update)
    window.mainloop()
