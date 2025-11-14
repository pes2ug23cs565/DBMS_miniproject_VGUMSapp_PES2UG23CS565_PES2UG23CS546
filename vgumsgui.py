#!/usr/bin/env python3
"""
VGUMS Tkinter GUI - single-file app

Requirements:
    pip install mysql-connector-python

Edit get_db() to set your MySQL connection credentials if needed.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="23011032",      
        database="vgums_db",
        auth_plugin='mysql_native_password'
    )

class LoginWindow:
    def __init__(self, root):
        self.root = root
        root.title("VGUMS - Login")
        root.geometry("360x320")
        root.resizable(False, False)
        root.configure(bg="#1e1f26")

        title = tk.Label(root, text="VGUMS", fg="white", bg="#1e1f26",
                         font=("Segoe UI", 20, "bold"))
        title.pack(pady=(20, 10))

        frm = tk.Frame(root, bg="#1e1f26")
        frm.pack(pady=5)

        tk.Label(frm, text="Username", fg="white", bg="#1e1f26").grid(row=0, column=0, sticky="w")
        self.username_entry = tk.Entry(frm, width=30)
        self.username_entry.grid(row=1, column=0, pady=(0, 8))

        tk.Label(frm, text="Password", fg="white", bg="#1e1f26").grid(row=2, column=0, sticky="w")
        self.password_entry = tk.Entry(frm, show="*", width=30)
        self.password_entry.grid(row=3, column=0, pady=(0, 10))

        btn_frame = tk.Frame(root, bg="#1e1f26")
        btn_frame.pack(pady=5)

        login_btn = ttk.Button(btn_frame, text="Login", command=self.login, width=18)
        login_btn.grid(row=0, column=0, padx=5, pady=8)

        reg_btn = ttk.Button(btn_frame, text="Register", command=self.open_register, width=18)
        reg_btn.grid(row=1, column=0, padx=5, pady=2)

        root.bind('<Return>', lambda e: self.login())

    def open_register(self):
        RegisterWindow()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Login error", "Please provide username and password.")
            return

        try:
            db = get_db()
           
            auth_cursor = db.cursor(dictionary=True)
            auth_cursor.callproc("sp_AuthenticateUser", [username, password])

            user = None
            for result in auth_cursor.stored_results():
                rows = result.fetchall()
                if rows:
                    user = rows[0]
                    break
            auth_cursor.close()

            if not user:
                messagebox.showerror("Login failed", "Invalid username or password.")
                db.close()
                return

            # fetch role(s)
            role_cursor = db.cursor(dictionary=True)
            role_cursor.execute("""
                SELECT r.role_name
                FROM Users u
                JOIN User_Roles ur ON u.user_id = ur.user_id
                JOIN Roles r ON ur.role_id = r.role_id
                WHERE u.user_id = %s
            """, (user["user_id"],))
            roles = [r["role_name"] for r in role_cursor.fetchall()]
            role_cursor.close()
            db.close()

            self.root.destroy()
            if "Admin" in roles:
                AdminPanel(user)
            else:
                PlayerPanel(user)

        except Error as e:
            messagebox.showerror("Database error", str(e))
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

class RegisterWindow:
    def __init__(self):
        self.win = tk.Toplevel()
        self.win.title("Register - VGUMS")
        self.win.geometry("380x360")
        self.win.resizable(False, False)
        self.win.configure(bg="#1e1f26")

        tk.Label(self.win, text="Create Account", fg="white", bg="#1e1f26",
                 font=("Segoe UI", 16, "bold")).pack(pady=(14, 6))

        frame = tk.Frame(self.win, bg="#1e1f26")
        frame.pack(pady=6)

        tk.Label(frame, text="Username", fg="white", bg="#1e1f26").grid(row=0, column=0, sticky="w")
        self.username = tk.Entry(frame, width=36); self.username.grid(row=1, column=0, pady=(0,8))

        tk.Label(frame, text="Email", fg="white", bg="#1e1f26").grid(row=2, column=0, sticky="w")
        self.email = tk.Entry(frame, width=36); self.email.grid(row=3, column=0, pady=(0,8))

        tk.Label(frame, text="Password", fg="white", bg="#1e1f26").grid(row=4, column=0, sticky="w")
        self.password = tk.Entry(frame, show="*", width=36); self.password.grid(row=5, column=0, pady=(0,12))

        ttk.Button(self.win, text="Create Account", command=self.register, width=22).pack(pady=8)

    def register(self):
        username = self.username.get().strip()
        email = self.email.get().strip()
        password = self.password.get().strip()

        if not username or not email or not password:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            db = get_db()
            cur = db.cursor()
            cur.callproc("sp_RegisterUser", [username, email, password])
            db.commit()
            cur.close()
            db.close()
            messagebox.showinfo("Success", "Account created. You may login now.")
            self.win.destroy()
        except mysql.connector.IntegrityError as ie:
            # likely duplicate username/email
            messagebox.showerror("Registration error", f"Integrity error: {ie}")
        except Error as e:
            messagebox.showerror("Database error", str(e))
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

class AdminPanel:
    def __init__(self, user):
        self.user = user
        self.root = tk.Tk()
        self.root.title(f"VGUMS Admin - {user['username']}")
        self.root.geometry("760x520")
        self.root.configure(bg="#222831")
        self.root.resizable(False, False)

        header = tk.Label(self.root, text=f"Admin Console — {user['username']}", bg="#222831",
                          fg="white", font=("Segoe UI", 18, "bold"))
        header.pack(pady=(14, 8))

        btn_frame = tk.Frame(self.root, bg="#222831")
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Add Game", width=18, command=self.add_game_window).grid(row=0, column=0, padx=8, pady=6)
        ttk.Button(btn_frame, text="Delete Game", width=18, command=self.delete_game_window).grid(row=0, column=1, padx=8, pady=6)
        ttk.Button(btn_frame, text="View Users Report", width=18, command=self.user_report).grid(row=0, column=2, padx=8, pady=6)
        ttk.Button(btn_frame, text="View All Games", width=18, command=self.view_games).grid(row=0, column=3, padx=8, pady=6)

      
        self.output_frame = tk.Frame(self.root, bg="#222831")
        self.output_frame.pack(fill="both", expand=True, padx=12, pady=12)

        self.view_games()
        self.root.mainloop()

    def add_game_window(self):
        win = tk.Toplevel(self.root)
        win.title("Add New Game")
        win.geometry("420x320")
        win.resizable(False, False)

        frame = tk.Frame(win)
        frame.pack(pady=10, padx=12)

        tk.Label(frame, text="Title").grid(row=0, column=0, sticky="w")
        title = tk.Entry(frame, width=46); title.grid(row=1, column=0, pady=(0,8))

        tk.Label(frame, text="Description").grid(row=2, column=0, sticky="w")
        desc = tk.Entry(frame, width=46); desc.grid(row=3, column=0, pady=(0,8))

        tk.Label(frame, text="Genre").grid(row=4, column=0, sticky="w")
        genre = tk.Entry(frame, width=46); genre.grid(row=5, column=0, pady=(0,10))

        def submit():
            t = title.get().strip()
            d = desc.get().strip()
            g = genre.get().strip()
            if not t:
                messagebox.showerror("Input error", "Title is required.")
                return
            try:
                db = get_db()
                cur = db.cursor()
                cur.callproc("sp_AdminAddGame", [t, d, g])
                db.commit()
                cur.close()
                db.close()
                messagebox.showinfo("Success", "Game added.")
                win.destroy()
                self.view_games()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(win, text="Add Game", command=submit, width=20).pack(pady=12)

   
    def delete_game_window(self):
        win = tk.Toplevel(self.root)
        win.title("Delete Game")
        win.geometry("340x180")
        win.resizable(False, False)

        tk.Label(win, text="Game ID to delete").pack(pady=(12,6))
        gid_entry = tk.Entry(win, width=16); gid_entry.pack()

        def do_delete():
            gid = gid_entry.get().strip()
            if not gid.isdigit():
                messagebox.showerror("Input error", "Enter a valid numeric Game ID.")
                return
            try:
                db = get_db()
                cur = db.cursor()
                cur.callproc("sp_DeleteGame", [int(gid)])
                db.commit()
                cur.close()
                db.close()
                messagebox.showinfo("Deleted", f"Game id {gid} deleted (if existed).")
                win.destroy()
                self.view_games()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(win, text="Delete", command=do_delete, width=14).pack(pady=12)

   
    def user_report(self):
        # clear frame
        for w in self.output_frame.winfo_children():
            w.destroy()

        cols = ("ID", "Username", "Email", "Created At", "Role")
        tree = ttk.Treeview(self.output_frame, columns=cols, show="headings", height=18)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=140)
        tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(self.output_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")

        try:
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT user_id, username, email, created_at, role_name FROM v_Admin_UserReport")
            for row in cur.fetchall():
                tree.insert("", tk.END, values=row)
            cur.close(); db.close()
        except Exception as e:
            messagebox.showerror("DB error", str(e))

    def view_games(self):
        for w in self.output_frame.winfo_children():
            w.destroy()

        cols = ("Game ID", "Title", "Genre")
        tree = ttk.Treeview(self.output_frame, columns=cols, show="headings", height=18)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=220)
        tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(self.output_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")

        try:
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT game_id, title, genre FROM Games ORDER BY game_id")
            for row in cur.fetchall():
                tree.insert("", tk.END, values=row)
            cur.close(); db.close()
        except Exception as e:
            messagebox.showerror("DB error", str(e))

class PlayerPanel:
    def __init__(self, user):
        self.user = user
        self.root = tk.Tk()
        self.root.title(f"VGUMS - Player [{user['username']}]")
        self.root.geometry("720x520")
        self.root.configure(bg="#30475e")
        self.root.resizable(False, False)

        header = tk.Label(self.root, text=f"Welcome — {user['username']}", bg="#30475e",
                          fg="white", font=("Segoe UI", 18, "bold"))
        header.pack(pady=(14, 8))

        btn_frame = tk.Frame(self.root, bg="#30475e")
        btn_frame.pack(pady=8)

        ttk.Button(btn_frame, text="View All Games", width=18, command=self.view_games).grid(row=0, column=0, padx=6, pady=6)
        ttk.Button(btn_frame, text="Leaderboard (Cosmic Rift)", width=22, command=self.leaderboard).grid(row=0, column=1, padx=6, pady=6)
        ttk.Button(btn_frame, text="Update My Score", width=18, command=self.update_score_window).grid(row=0, column=2, padx=6, pady=6)

        self.output_frame = tk.Frame(self.root, bg="#30475e")
        self.output_frame.pack(fill="both", expand=True, padx=12, pady=12)

        self.view_games()
        self.root.mainloop()

    def view_games(self):
        for w in self.output_frame.winfo_children(): w.destroy()

        cols = ("Game ID", "Title", "Genre")
        tree = ttk.Treeview(self.output_frame, columns=cols, show="headings", height=18)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=220)
        tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(self.output_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")

        try:
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT game_id, title, genre FROM Games ORDER BY game_id")
            for row in cur.fetchall():
                tree.insert("", tk.END, values=row)
            cur.close(); db.close()
        except Exception as e:
            messagebox.showerror("DB error", str(e))

    def leaderboard(self):
        for w in self.output_frame.winfo_children(): w.destroy()

        cols = ("Username", "Score", "Level", "Last Played")
        tree = ttk.Treeview(self.output_frame, columns=cols, show="headings", height=18)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=160)
        tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(self.output_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")

        try:
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT username, score, level_achieved, last_played FROM v_Leaderboard_CosmicRift")
            for row in cur.fetchall():
                tree.insert("", tk.END, values=row)
            cur.close(); db.close()
        except Exception as e:
            messagebox.showerror("DB error", str(e))

    def update_score_window(self):
        win = tk.Toplevel(self.root)
        win.title("Update My Score")
        win.geometry("420x300")
        win.resizable(False, False)

        tk.Label(win, text="Select Game:").pack(pady=(12,4))
        game_combo = ttk.Combobox(win, width=46, state="readonly")
        game_combo.pack()

        try:
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT game_id, title FROM Games ORDER BY game_id")
            games = cur.fetchall()
            cur.close(); db.close()
            game_combo["values"] = [f"{gid} - {title}" for (gid, title) in games]
        except Exception as e:
            messagebox.showerror("DB error", str(e))
            win.destroy()
            return

        tk.Label(win, text="New Score:").pack(pady=(12,4))
        score_entry = tk.Entry(win, width=20); score_entry.pack()

        def submit_score():
            sel = game_combo.get().strip()
            new_score = score_entry.get().strip()
            if not sel or not new_score:
                messagebox.showerror("Error", "Select a game and enter a score.")
                return
            try:
                gid = int(sel.split(" - ", 1)[0])
                nscore = int(new_score)
            except ValueError:
                messagebox.showerror("Error", "Invalid values.")
                return

            try:
                db = get_db()
                cur = db.cursor()
                cur.callproc("sp_UpdatePlayerScore", [self.user["user_id"], gid, nscore])
                db.commit()
                cur.close(); db.close()
                messagebox.showinfo("Success", "Score updated.")
                win.destroy()
            except Exception as e:
                messagebox.showerror("DB error", str(e))

        ttk.Button(win, text="Submit", command=submit_score, width=16).pack(pady=14)

def main():
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
