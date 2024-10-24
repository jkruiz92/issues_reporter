import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv

# Crear la conexión a la base de datos SQLite
conn = sqlite3.connect('error_tracking.db')
c = conn.cursor()

# Crear la tabla si no existe
c.execute('''CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature TEXT,
                test TEXT,
                sw TEXT,
                requirement TEXT,
                conditions TEXT,
                expected TEXT,
                result TEXT,
                status TEXT
            )''')
conn.commit()

# Función para añadir un error a la base de datos
def add_error():
    feature = feature_entry.get()
    test = test_entry.get()
    sw = sw_entry.get()
    requirement = requirement_entry.get()
    conditions = conditions_text.get("1.0", tk.END).strip()
    expected = expected_text.get("1.0", tk.END).strip()
    result = result_text.get("1.0", tk.END).strip()
    status = status_combobox.get()

    if feature and test and sw and requirement and conditions and expected and result and status:
        c.execute('''INSERT INTO errors (feature, test, sw, requirement, conditions, expected, result, status)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                     (feature, test, sw, requirement, conditions, expected, result, status))
        conn.commit()
        messagebox.showinfo("Success", "Error registrado correctamente")
        clear_fields()
        display_errors()  # Actualizar la tabla
    else:
        messagebox.showwarning("Input Error", "Todos los campos son obligatorios")

# Función para limpiar los campos de entrada
def clear_fields():
    feature_entry.delete(0, tk.END)
    test_entry.delete(0, tk.END)
    sw_entry.delete(0, tk.END)
    requirement_entry.delete(0, tk.END)
    conditions_text.delete("1.0", tk.END)
    expected_text.delete("1.0", tk.END)
    result_text.delete("1.0", tk.END)
    status_combobox.set("")
    update_button.config(state=tk.DISABLED)  # Deshabilitar el botón de actualización
    add_button.config(state=tk.NORMAL)  # Habilitar el botón de añadir

# Función para mostrar los errores en la pestaña de visualización
def display_errors(status_filter=None):
    for row in tree.get_children():
        tree.delete(row)
    
    query = 'SELECT * FROM errors'
    if status_filter:
        query += f" WHERE status='{status_filter}'"
    c.execute(query)
    rows = c.fetchall()
    for row in rows:
        tree.insert("", tk.END, values=row)

# Función para exportar a CSV
def export_to_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                             filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if not file_path:
        return

    c.execute('SELECT * FROM errors')
    rows = c.fetchall()

    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Feature", "Test", "SW", "Requirement", "Conditions", "Expected", "Result", "Status"])  # Escribir encabezados
            writer.writerows(rows)
        messagebox.showinfo("Éxito", f"Los errores han sido exportados a {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar el archivo. Error: {str(e)}")

# Función para cargar un error seleccionado para su edición
def load_selected_error(event):
    selected_item = tree.selection()
    if selected_item:
        item_data = tree.item(selected_item, 'values')
        error_id = item_data[0]

        # Cargar los datos del error en los campos de entrada
        feature_entry.delete(0, tk.END)
        feature_entry.insert(0, item_data[1])

        test_entry.delete(0, tk.END)
        test_entry.insert(0, item_data[2])

        sw_entry.delete(0, tk.END)
        sw_entry.insert(0, item_data[3])

        requirement_entry.delete(0, tk.END)
        requirement_entry.insert(0, item_data[4])

        conditions_text.delete("1.0", tk.END)
        conditions_text.insert(tk.END, item_data[5])

        expected_text.delete("1.0", tk.END)
        expected_text.insert(tk.END, item_data[6])

        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, item_data[7])

        status_combobox.set(item_data[8])

        # Habilitar botón de actualizar y deshabilitar el de añadir
        add_button.config(state=tk.DISABLED)
        update_button.config(state=tk.NORMAL)
        update_button.error_id = error_id  # Guardar el ID del error para actualizarlo

# Función para actualizar un error existente
def update_error():
    error_id = update_button.error_id  # Obtener el ID del error a actualizar

    feature = feature_entry.get()
    test = test_entry.get()
    sw = sw_entry.get()
    requirement = requirement_entry.get()
    conditions = conditions_text.get("1.0", tk.END).strip()
    expected = expected_text.get("1.0", tk.END).strip()
    result = result_text.get("1.0", tk.END).strip()
    status = status_combobox.get()

    if feature and test and sw and requirement and conditions and expected and result and status:
        c.execute('''UPDATE errors SET feature=?, test=?, sw=?, requirement=?, conditions=?, expected=?, result=?, status=?
                     WHERE id=?''', (feature, test, sw, requirement, conditions, expected, result, status, error_id))
        conn.commit()
        messagebox.showinfo("Success", "Error actualizado correctamente")
        clear_fields()
        display_errors()  # Actualizar la tabla
    else:
        messagebox.showwarning("Input Error", "Todos los campos son obligatorios")

# Crear la ventana principal
root = tk.Tk()
root.title("Seguimiento de Errores")

# Crear el control de pestañas
tab_control = ttk.Notebook(root)

# Pestaña 1: Entrada de errores
tab1 = ttk.Frame(tab_control)
tab_control.add(tab1, text="Registrar Error")

# Campos de entrada para la pestaña 1
tk.Label(tab1, text="Feature").grid(row=0, column=0, padx=10, pady=5)
feature_entry = tk.Entry(tab1)
feature_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(tab1, text="Test").grid(row=1, column=0, padx=10, pady=5)
test_entry = tk.Entry(tab1)
test_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(tab1, text="SW").grid(row=2, column=0, padx=10, pady=5)
sw_entry = tk.Entry(tab1)
sw_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(tab1, text="Requirement").grid(row=3, column=0, padx=10, pady=5)
requirement_entry = tk.Entry(tab1)
requirement_entry.grid(row=3, column=1, padx=10, pady=5)

tk.Label(tab1, text="Conditions").grid(row=4, column=0, padx=10, pady=5)
conditions_text = tk.Text(tab1, height=4, width=30)
conditions_text.grid(row=4, column=1, padx=10, pady=5)

tk.Label(tab1, text="Expected").grid(row=5, column=0, padx=10, pady=5)
expected_text = tk.Text(tab1, height=4, width=30)
expected_text.grid(row=5, column=1, padx=10, pady=5)

tk.Label(tab1, text="Result").grid(row=6, column=0, padx=10, pady=5)
result_text = tk.Text(tab1, height=4, width=30)
result_text.grid(row=6, column=1, padx=10, pady=5)

tk.Label(tab1, text="Status").grid(row=7, column=0, padx=10, pady=5)
status_combobox = ttk.Combobox(tab1, values=["Open", "Review", "Checked", "Reported", "Obsolete"])
status_combobox.grid(row=7, column=1, padx=10, pady=5)

# Botones para añadir y actualizar errores
add_button = tk.Button(tab1, text="Registrar Error", command=add_error)
add_button.grid(row=8, column=0, pady=10)

update_button = tk.Button(tab1, text="Actualizar Error", command=update_error)
update_button.grid(row=8, column=1, pady=10)
update_button.config(state=tk.DISABLED)  # Deshabilitado por defecto

# Pestaña 2: Visualización de errores
tab2 = ttk.Frame(tab_control)
tab_control.add(tab2, text="Visualizar Errores")

# Filtros de status
tk.Label(tab2, text="Filtrar por Status").grid(row=0, column=0, padx=10, pady=5)
filter_combobox = ttk.Combobox(tab2, values=["All", "Open", "Review", "Checked", "Reported"])
filter_combobox.grid(row=0, column=1, padx=10, pady=5)
filter_combobox.set("All")

# Botón para aplicar el filtro
filter_button = tk.Button(tab2, text="Aplicar Filtro", command=lambda: display_errors(None if filter_combobox.get() == "All" else filter_combobox.get()))
filter_button.grid(row=0, column=2, padx=10, pady=5)

# Tabla para mostrar los errores
columns = ("ID", "Feature", "Test", "SW", "Requirement", "Conditions", "Expected", "Result", "Status")
tree = ttk.Treeview(tab2, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)

tree.grid(row=1, column=0, columnspan=3, padx=10, pady=5)
tree.bind("<Double-1>", load_selected_error)  # Vincular evento de doble clic para cargar error

# Botón para exportar a CSV
export_button = tk.Button(tab2, text="Exportar a CSV", command=export_to_csv)
export_button.grid(row=2, column=0, columnspan=3, pady=10)

# Añadir control de pestañas a la ventana principal
tab_control.pack(expand=1, fill="both")

# Inicializar mostrando todos los errores
display_errors()

# Iniciar la aplicación
root.mainloop()

# Cerrar la conexión con la base de datos al cerrar la aplicación
conn.close()
