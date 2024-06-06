import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import sqlite3

class ProductDB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY,
                Nombre TEXT,
                Direccion1 TEXT,
                Direccion2 TEXT,
                Celular TEXT,
                Dinero INTEGER
            )
        """)
        self.conn.commit()

    def execute_query(self, query, *args):
        try:
            self.cursor.execute(query, args)
            self.conn.commit()
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Error de base de datos", str(e))

    def fetch_all_products(self):
        return self.execute_query("SELECT * FROM productos")




class ProductCRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Servicios")
        self.db= ProductDB("productos.db")
        self.create_widgets()


    def create_widgets(self):
        self.create_treeview()
        self.create_input_fields()
        self.create_buttons()
        self.load_products()

    def create_treeview(self):
        self.tree = ttk.Treeview(self.root, columns=("ID", "Nombre", "Direccion recogida", "Direccion entrega", "Celular", "Dinero a recaudar"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Direccion recogida", text="Direccion recogida")
        self.tree.heading("Direccion entrega", text="Direccion entrega")
        self.tree.heading("Celular", text="Celular")
        self.tree.heading("Dinero a recaudar", text="Dinero a recaudar")
        self.tree.pack(padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
    
    def create_input_fields(self):
        fields = [("Nombre:", 10), ("Direccion recogida:", 10), ("Direccion entrega:", 10), ("Celular:", 10),("Dinero a recaudar:", 10)]
        self.entries = {}
        for label_text, width in fields:
            label = ttk.Label(self.root, text=label_text)
            label.pack(pady=(0, 5), padx=10, anchor="w")

            entry = ttk.Entry(self.root, width=width)
            entry.pack(pady=(0, 10), padx=10, fill="x")
            self.entries[label_text] = entry
    
    def create_buttons(self):
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        buttons = [("Agregar", self.add_product), 
                   ("Eliminar", self.remove_product),
                   ("Actualizar", self.update_product), 
                   ("Buscar", self.search_product),
                   ("Mostrar Todo", self.show_all_products)]

        for text, command in buttons:
            button = ttk.Button(btn_frame, text=text, command=command)
            button.grid(row=0, column=buttons.index((text, command)), padx=5)

    def load_products(self):
        self.clear_table()
        for row in self.db.fetch_all_products():
            self.tree.insert("", "end", values=row)
    
    def add_product(self):
        values = [entry.get() for entry in self.entries.values()]
        if all(values):
            self.db.execute_query("INSERT INTO productos (Nombre, Direccion1, Direccion2, Celular, Dinero) VALUES (?, ?, ?, ?, ?)", *values)
            messagebox.showinfo("Éxito", "Servicio agregado con éxito")
            self.load_products()
            self.clear_input_fields()
        else:
            messagebox.showerror("Error", "Por favor, complete todos los campos")

    def remove_product(self):
        selected_item = self.tree.selection()
        if selected_item:
            product_id = self.tree.item(selected_item, "values")[0]
            self.db.execute_query("DELETE FROM productos WHERE id=?", product_id)
            messagebox.showinfo("Éxito", "Servicio eliminado con éxito")
            self.load_products()

    def update_product(self):
        selected_item = self.tree.selection()
        if selected_item:
            product_id = self.tree.item(selected_item, "values")[0]
            values = [entry.get() for entry in self.entries.values()]
            self.db.execute_query("UPDATE productos SET Nombre=?, Direccion1=?, Direccion2=?, Celular=?, Dinero=? WHERE id=?", *(values + [product_id]))
            messagebox.showinfo("Éxito", "Servicio actualizado con éxito")
            self.load_products()
            self.clear_input_fields()

    def search_product(self):
        search_term = self.entries["Nombre:"].get()
        if search_term:
            self.clear_table()
            for row in self.db.execute_query("SELECT * FROM productos WHERE Nombre LIKE ?", '%' + search_term + '%'):
                self.tree.insert("", "end", values=row)
        else:
            messagebox.showerror("Error", "Por favor, ingrese un término de búsqueda")

    def show_all_products(self):
        self.load_products()
    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            if values:
                for entry, value in zip(self.entries.values(), values[1:]):
                    entry.delete(0, tk.END)
                    entry.insert(0, value)

    def clear_input_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)



    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)


if __name__ == "__main__":
    root = tk.Tk()
    app = ProductCRUDApp(root)
    root.mainloop()