#!/usr/bin/env python3
"""
Quick test to verify scrollbar functionality
This script creates a minimal window to test the scrollbar feature
"""

import tkinter as tk
from tkinter import ttk

def test_scrollbar():
    """Test scrollbar in a minimal window"""
    root = tk.Tk()
    root.title("Scrollbar Test")
    root.geometry("300x400")

    # Create outer frame
    outer_frame = ttk.LabelFrame(root, text="Scrollable Controls", padding=5)
    outer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Create canvas and scrollbar
    canvas = tk.Canvas(outer_frame, highlightthickness=0)
    scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Add many widgets to test scrolling
    for i in range(30):
        ttk.Label(scrollable_frame, text=f"Item {i+1}").pack(pady=5)
        ttk.Button(scrollable_frame, text=f"Button {i+1}").pack(pady=5)

    # Mousewheel binding
    def on_mousewheel(event):
        if event.num == 5 or event.delta < 0:
            canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            canvas.yview_scroll(-1, "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)
    canvas.bind_all("<Button-4>", on_mousewheel)
    canvas.bind_all("<Button-5>", on_mousewheel)

    # Adjust canvas window width
    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)

    canvas.bind('<Configure>', on_canvas_configure)

    print("✓ Scrollbar test window created successfully")
    print("✓ Try scrolling with mouse wheel or scrollbar")
    print("✓ Window should show 30 items with scrolling")

    root.mainloop()

if __name__ == "__main__":
    test_scrollbar()
