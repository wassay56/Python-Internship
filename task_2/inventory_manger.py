# %%
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import datetime
import os

# --- Theme Setup ---
try:
    from ttkthemes import ThemedTk
    def create_themed_root():
        return ThemedTk(theme="arc") # You can try other themes like 'plastik', 'breeze', 'scidgrey'
except ImportError:
    def create_themed_root():
        return tk.Tk()

DB_FILE = "inventory.db"
REMEMBER_ME_FILE = "rememberme.txt"
BILL_FOLDER = os.path.join(os.path.expanduser("~"), "Desktop", "Bills")

if not os.path.exists(BILL_FOLDER):
    os.makedirs(BILL_FOLDER)

# ---------------- Database ----------------
def init_db():
    """Initializes and populates the SQLite database for inventory."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS products (sku TEXT PRIMARY KEY, name TEXT NOT NULL, size TEXT, quantity INTEGER, price REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT NOT NULL)")

    products = [
        ("PS001", "Liquid Blue", "75 ml", 0, 0),
        ("PS002", "Liquid Blue", "150 ml", 0, 0),
        ("PS003", "Handwash", "250 ml", 0, 0),
        ("PS004", "Handwash", "500 ml", 0, 0),
        ("PS005", "Bleach", "550 ml", 0, 0),
        ("PS006", "Dishwash", "500 ml", 0, 0),
        ("PS007", "White Phenyl", "3 Liter", 0, 0),
        ("PS008", "Toilet Cleaner", "250 ml", 0, 0),
        ("PS009", "Toilet Cleaner", "550 ml", 0, 0),
        ("PS010", "Sweep", "300 ml", 0, 0),
        ("PS011", "Sweep", "600 ml", 0, 0),
        ("PS012", "Mustard Oil", "12 ml", 0, 0),
        ("PS013", "Mustard Oil", "50 ml", 0, 0),
        ("PS014", "Mustard Oil", "100 ml", 0, 0),
        ("PS015", "Mustard Oil", "200 ml", 0, 0),
    ]
    for p in products:
        cur.execute("INSERT OR IGNORE INTO products VALUES (?,?,?,?,?)", p)
    cur.execute("INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)", ("last_invoice_number", "0"))
    conn.commit()
    conn.close()

# ---------------- Login App ----------------
class LoginApp:
    def __init__(self, root, on_success_callback):
        self.root = root
        self.root.title("Login")
        self.root.geometry("300x200")
        self.on_success_callback = on_success_callback
        self.username = "perfectshine_admin"
        self.password = "shine123"
        self.remember_me_var = tk.IntVar()

        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10), foreground="black")
        style.configure("TLabel", font=("Arial", 10))

        if not self.check_remember_me():
            self.create_login_widgets()

    def check_remember_me(self):
        """Checks if a 'remember me' file exists and logs in automatically."""
        if os.path.exists(REMEMBER_ME_FILE):
            with open(REMEMBER_ME_FILE, 'r') as f:
                content = f.read().strip()
                if content == self.username:
                    self.on_success_callback()
                    return True
        return False

    def create_login_widgets(self):
        frame = ttk.Frame(self.root, padding=15)
        frame.pack(expand=True)

        ttk.Label(frame, text="Username").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.username_entry = ttk.Entry(frame)
        self.username_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Password").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Checkbutton(frame, text="Remember me", variable=self.remember_me_var).grid(row=2, columnspan=2, pady=5)
        ttk.Button(frame, text="Login", command=self.login).grid(row=3, columnspan=2, pady=10)

    def login(self):
        entered_username = self.username_entry.get()
        entered_password = self.password_entry.get()
        if entered_username == self.username and entered_password == self.password:
            if self.remember_me_var.get() == 1:
                with open(REMEMBER_ME_FILE, 'w') as f:
                    f.write(self.username)
            self.on_success_callback()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

# ---------------- Main App ----------------
class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory and Billing System")
        self.root.geometry("600x400")

        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12), foreground="black")
        style.configure("TLabel", font=("Arial", 10))
        
        ttk.Button(root, text="📝 New Bill", command=self.new_bill, width=20).pack(pady=10)
        ttk.Button(root, text="📦 Manage Inventory", command=self.manage_inventory, width=20).pack(pady=10)
        ttk.Button(root, text="⚙️ Admin Panel", command=self.admin_panel, width=20).pack(pady=10)
        ttk.Button(root, text="❌ Exit", command=root.quit, width=20).pack(pady=10)

    # -------- Bill Window --------
    def new_bill(self):
        win = tk.Toplevel(self.root)
        win.title("New Bill")
        win.geometry("600x650")

        # Customer Details Frame
        customer_frame = ttk.Frame(win, padding=10)
        customer_frame.pack(fill="x")
        ttk.Label(customer_frame, text="Customer Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.customer_name_entry = ttk.Entry(customer_frame)
        self.customer_name_entry.grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Label(customer_frame, text="Phone Number:").grid(row=1, column=0, sticky="w", pady=2)
        self.customer_phone_entry = ttk.Entry(customer_frame)
        self.customer_phone_entry.grid(row=1, column=1, sticky="ew", pady=2)
        ttk.Label(customer_frame, text="Address:").grid(row=2, column=0, sticky="w", pady=2)
        self.customer_address_entry = ttk.Entry(customer_frame)
        self.customer_address_entry.grid(row=2, column=1, sticky="ew", pady=2)

        # Product section
        item_frame = ttk.Frame(win, padding=10)
        item_frame.pack(fill="x")
        ttk.Label(item_frame, text="Product").grid(row=0, column=0, sticky="w")
        products = self.get_products()
        product_names = [f"{p[0]} - {p[1]} ({p[2]})" for p in products]
        self.product_var = tk.StringVar()
        self.product_menu = ttk.Combobox(item_frame, textvariable=self.product_var, values=product_names, state="readonly", width=35)
        self.product_menu.grid(row=0, column=1, sticky="ew")
        ttk.Label(item_frame, text="Quantity").grid(row=1, column=0, sticky="w")
        self.qty_entry = ttk.Entry(item_frame)
        self.qty_entry.grid(row=1, column=1, sticky="ew")
        ttk.Button(item_frame, text="Add Item", command=self.add_item).grid(row=2, column=1, sticky="e", pady=5)

        # Bill display
        bill_frame = ttk.Frame(win, padding=10)
        bill_frame.pack(fill="both", expand=True)
        self.bill_tree = ttk.Treeview(bill_frame, columns=("Product", "Quantity", "Price", "Total"), show="headings")
        self.bill_tree.heading("Product", text="Product")
        self.bill_tree.heading("Quantity", text="Qty")
        self.bill_tree.heading("Price", text="Price")
        self.bill_tree.heading("Total", text="Total")
        self.bill_tree.pack(fill="both", expand=True)
        self.bill_items = []
        ttk.Button(win, text="Finalize Bill", command=self.finalize_bill).pack(pady=10)

    def add_item(self):
        try:
            sku_name = self.product_var.get()
            if not sku_name:
                messagebox.showerror("Error", "Please select a product.")
                return
            sku = sku_name.split(" - ")[0]
            qty = int(self.qty_entry.get())
            if qty <= 0:
                messagebox.showerror("Error", "Quantity must be positive.")
                return
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Please enter a valid quantity.")
            return

        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT name, size, price, quantity FROM products WHERE sku=?", (sku,))
        row = cur.fetchone()
        conn.close()

        if row:
            name, size, price, stock_qty = row
            if qty > stock_qty:
                messagebox.showerror("Error", f"Not enough stock. Available: {stock_qty}")
                return

            total_price = price * qty
            for i, (item_sku, *_rest) in enumerate(self.bill_items):
                if item_sku == sku:
                    self.bill_items[i] = (sku, name, size, self.bill_items[i][3]+qty, price, price*(self.bill_items[i][3]+qty))
                    self.update_bill_treeview()
                    self.qty_entry.delete(0, tk.END)
                    return

            self.bill_items.append((sku, name, size, qty, price, total_price))
            self.update_bill_treeview()
            self.qty_entry.delete(0, tk.END)

    def update_bill_treeview(self):
        for item in self.bill_tree.get_children():
            self.bill_tree.delete(item)
        for item in self.bill_items:
            _, name, size, qty, price, total_price = item
            product_display_name = f"{name} ({size})"
            self.bill_tree.insert("", "end", values=(product_display_name, qty, f"Rs {price:.2f}", f"Rs {total_price:.2f}"))

    def finalize_bill(self):
        if not self.bill_items:
            messagebox.showerror("Error", "No items in the bill.")
            return
        customer_name = self.customer_name_entry.get()
        customer_phone = self.customer_phone_entry.get()
        customer_address = self.customer_address_entry.get()
        if not customer_name or not customer_phone:
            messagebox.showerror("Error", "Customer name and phone required.")
            return

        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        for item in self.bill_items:
            sku, _, _, qty, _, _ = item
            cur.execute("UPDATE products SET quantity = quantity - ? WHERE sku=?", (qty, sku))

        cur.execute("SELECT value FROM config WHERE key = 'last_invoice_number'")
        last_invoice_number = int(cur.fetchone()[0])
        new_invoice_number = last_invoice_number + 1
        cur.execute("UPDATE config SET value = ? WHERE key = 'last_invoice_number'", (str(new_invoice_number),))
        conn.commit()
        conn.close()

        # PDF creation
        pdf_file_name = os.path.join(BILL_FOLDER, f"Bill_{customer_name.replace(' ','_')}_{datetime.date.today().strftime('%Y%m%d')}.pdf")
        doc = SimpleDocTemplate(pdf_file_name, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        normal_style = styles['Normal']
        
        # Correctly style the company name to be centered
        company_style = ParagraphStyle('CompanyStyle', parent=styles['Heading1'], alignment=1, textColor=colors.blue)
        story.append(Paragraph("<b>Perfect Shine</b>", company_style))
        story.append(Spacer(1, 12))

        # Customer and Distributor side-by-side
        customer_data = [
            [Paragraph(f"<b>Customer Name:</b> {customer_name}", normal_style),
             Paragraph(f"<b>Distributor:</b> M.Hashir", normal_style)],
            [Paragraph(f"<b>Phone:</b> {customer_phone}", normal_style),
             Paragraph(f"<b>Contact:</b> 0328-6856755", normal_style)],
            [Paragraph(f"<b>Address:</b> {customer_address}", normal_style), '']
        ]
        
        # Apply table style for alignment
        customer_table_style = TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ])
        customer_table = Table(customer_data, colWidths=[250, 250])
        customer_table.setStyle(customer_table_style)
        story.append(customer_table)
        story.append(Spacer(1, 24))

        # Items table
        data = [["Sr.", "Name", "Qty", "Unit Price", "Total Price"]]
        total_bill = 0
        for i, item in enumerate(self.bill_items, 1):
            _, name, size, qty, price, total_price = item
            data.append([str(i), f"{name} ({size})", str(qty), f"Rs {price:.2f}", f"Rs {total_price:.2f}"])
            total_bill += total_price

        table_style = TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.Color(0.85,0.85,0.85)),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ALIGN', (1,1), (1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
        ])
        col_widths = [30, 200, 50, 80, 100]
        invoice_table = Table(data, colWidths=col_widths)
        invoice_table.setStyle(table_style)
        story.append(invoice_table)
        story.append(Spacer(1, 12))

        # Add grand total and signature
        total_table_data = [
            ['', '', Paragraph("<b>Grand Total</b>", normal_style), f"Rs {total_bill:.2f}"]
        ]
        total_table_style = TableStyle([
            ('GRID', (2,0), (-1,-1), 1, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ALIGN', (2,0), (2,0), 'RIGHT')
        ])
        total_table = Table(total_table_data, colWidths=[200, 100, 100, 100])
        total_table.setStyle(total_table_style)
        story.append(total_table)
        story.append(Spacer(1, 48))
        story.append(Paragraph("_____________________", normal_style))
        story.append(Paragraph("Signature", normal_style))
        
        doc.build(story)

        messagebox.showinfo("Success", f"Bill saved as {pdf_file_name}")
        self.bill_items = []
        self.update_bill_treeview()

    # -------- Inventory --------
    def manage_inventory(self):
        win = tk.Toplevel(self.root)
        win.title("Inventory")
        
        button_frame = ttk.Frame(win, padding=5)
        button_frame.pack(pady=5)
        
        # A new Treeview instance is created for this window and stored in a local variable
        tree = ttk.Treeview(win, columns=("SKU", "Name", "Size", "Quantity", "Price"), show="headings")
        for col in ("SKU", "Name", "Size", "Quantity", "Price"):
            tree.heading(col, text=col)
        tree.pack(fill=tk.BOTH, expand=True)

        # The delete button now calls the method and passes the local treeview instance
        ttk.Button(button_frame, text="Delete Selected", command=lambda: self.delete_product(tree)).pack(side=tk.LEFT, padx=5)

        # The load_products method is called with the specific Treeview instance for this window
        self.load_products(tree)

    # -------- Admin --------
    def admin_panel(self):
        win = tk.Toplevel(self.root)
        win.title("Admin Panel")
        
        button_frame = ttk.Frame(win, padding=5)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="Add Product", command=self.add_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Selected", command=self.update_product).pack(side=tk.LEFT, padx=5)
        
        # New delete button for Admin Panel
        style = ttk.Style()
        style.configure("TButton.Danger", foreground="red", font=("Arial", 12))
        ttk.Button(button_frame, text="Delete Selected", command=lambda: self.delete_product(self.tree), style="TButton.Danger").pack(side=tk.LEFT, padx=5)

        self.tree = ttk.Treeview(win, columns=("SKU", "Name", "Size", "Quantity", "Price"), show="headings")
        for col in ("SKU", "Name", "Size", "Quantity", "Price"):
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)
        # The load_products method is called with the specific Treeview instance for this window
        self.load_products(self.tree)

    def add_product(self):
        win = tk.Toplevel(self.root)
        win.title("Add New Product")
        
        labels = ["SKU", "Name", "Size", "Quantity", "Price"]
        entries = {}
        for i, text in enumerate(labels):
            ttk.Label(win, text=text).grid(row=i, column=0, padx=5, pady=2, sticky='w')
            entry = ttk.Entry(win)
            entry.grid(row=i, column=1, padx=5, pady=2, sticky='ew')
            entries[text.lower()] = entry
        
        def save_new_product():
            try:
                sku = entries['sku'].get().upper()
                name = entries['name'].get()
                size = entries['size'].get()
                qty = int(entries['quantity'].get())
                price = float(entries['price'].get())
                
                if not sku or not name or not size:
                    messagebox.showerror("Error", "SKU, Name, and Size cannot be empty.")
                    return
                
                conn = sqlite3.connect(DB_FILE)
                cur = conn.cursor()
                cur.execute("INSERT INTO products (sku, name, size, quantity, price) VALUES (?, ?, ?, ?, ?)", (sku, name, size, qty, price))
                conn.commit()
                conn.close()
                self.load_products(self.tree)
                win.destroy()
                messagebox.showinfo("Success", "New product added successfully!")
            except ValueError:
                messagebox.showerror("Error", "Quantity and Price must be valid numbers.")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "A product with this SKU already exists.")

        ttk.Button(win, text="Save Product", command=save_new_product).grid(row=len(labels), columnspan=2, pady=10)

    def delete_product(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "No product selected")
            return
        
        item = tree.item(selected[0])
        sku = item['values'][0]
        name = item['values'][1]
        
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {name} (SKU: {sku})? This action cannot be undone."):
            try:
                conn = sqlite3.connect(DB_FILE)
                cur = conn.cursor()
                cur.execute("DELETE FROM products WHERE sku=?", (sku,))
                conn.commit()
                conn.close()
                self.load_products(tree)
                messagebox.showinfo("Success", f"{name} has been deleted.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete product: {e}")

    def load_products(self, tree):
        for row in tree.get_children():
            tree.delete(row)
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT * FROM products")
        for row in cur.fetchall():
            tree.insert("", tk.END, values=row)
        conn.close()

    def update_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "No product selected")
            return
        item = self.tree.item(selected[0])["values"]
        sku, name, size, qty, price = item
        win = tk.Toplevel(self.root)
        win.title("Update Product")
        ttk.Label(win, text="Quantity").pack()
        qty_entry = ttk.Entry(win); qty_entry.insert(0, qty); qty_entry.pack()
        ttk.Label(win, text="Price").pack()
        price_entry = ttk.Entry(win); price_entry.insert(0, price); price_entry.pack()
        def save_changes():
            try:
                new_qty = int(qty_entry.get())
                new_price = float(price_entry.get())
                conn = sqlite3.connect(DB_FILE)
                cur = conn.cursor()
                cur.execute("UPDATE products SET quantity=?, price=? WHERE sku=?", (new_qty, new_price, sku))
                conn.commit()
                conn.close()
                self.load_products(self.tree)
                win.destroy()
                messagebox.showinfo("Success", "Product updated")
            except ValueError:
                messagebox.showerror("Error", "Quantity and Price must be valid numbers.")
        ttk.Button(win, text="Save", command=save_changes).pack(pady=5)

    def get_products(self):
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT * FROM products")
        rows = cur.fetchall()
        conn.close()
        return rows

# ---------------- Run ----------------
if __name__ == "__main__":
    init_db()
    login_root = create_themed_root()
    def on_login_success():
        login_root.destroy()
        main_root = create_themed_root()
        InventoryApp(main_root)
        main_root.mainloop()
    LoginApp(login_root, on_login_success)
    login_root.mainloop()


