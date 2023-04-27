import requests
import sqlite3
import tkinter as tk
from tkinter import messagebox


def retrieve_data():
    url = "https://data.brreg.no/enhetsregisteret/api/enheter"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Connect to SQLite DB
        conn = sqlite3.connect("organizations.db")
        c = conn.cursor()

        # Create table if doesnt exists already
        c.execute('''CREATE TABLE IF NOT EXISTS organizations
                    (org_number INT PRIMARY KEY, name TEXT, type TEXT)''')

        # Insert data into organizations table
        for org in data["_embedded"]["enheter"]:
            org_number = org["organisasjonsnummer"]
            name = org["navn"]
            org_type = org["organisasjonsform"]["beskrivelse"]
            c.execute("INSERT OR IGNORE INTO organizations (org_number, name, type) VALUES (?, ?, ?)",
                      (org_number, name, org_type))

            conn.commit()
        conn.close()
        # messagebox.showinfo("Success", "Data retrieved and saved to database successfully!")
        return True
    except requests.exceptions.HTTPError as err:
        messagebox.showerror("Error", f"Failed to retrieve data: {err}")
        return False
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return False


def display_data():
    # Create listbox
    listbox = tk.Listbox(window)
    listbox.pack(fill=tk.BOTH, expand=True)

    # Add data to listbox
    conn = sqlite3.connect("organizations.db")
    c = conn.cursor()
    c.execute("SELECT * FROM organizations")
    data = c.fetchall()
    for item in data:
        listbox.insert(tk.END, f"{item[0]} - {item[1]} - {item[2]}")
    conn.close()


def display_gui():
    # Create main window
    global window
    window = tk.Tk()
    window.title("Organization Data")

    # Create load button
    load_button = tk.Button(window, text="Load Data", command=lambda: load_data())
    load_button.pack(padx=10, pady=10)

    # Flag variable to keep track of data load status
    global data_loaded
    data_loaded = False

    window.mainloop()


def load_data():
    global data_loaded
    if not data_loaded:
        data_loaded = retrieve_data()
        if data_loaded:
            display_data()
    else:
        messagebox.showinfo("Info", "Data has already been loaded!")


if __name__ == "__main__":
    display_gui()
