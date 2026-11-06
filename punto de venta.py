import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import os

PALETA_NOCHE = {
    "fondo":        "#1E1E1E",
    "fondo_caja":   "#2D2D2D",
    "texto":        "#E0E0E0",
    "acento":       "#4CAF50",  # verde para total y destacados
    "encabezado":   "#3A3A3A",
    "presionado":     "#1A1A1A",
}

PALETA_DIA = {
    "fondo":        "#F0F0F0",
    "fondo_caja":   "#FFFFFF",
    "texto":        "#202020",
    "acento":       "#2E7D32",  # verde más oscuro para que se lea sobre claro
    "encabezado":   "#DCDCDC",
    "presionado":     "#D0D0D0",
}

#obtener ruta correcta de la BD
ruta_proyecto = os.path.dirname(os.path.abspath(__file__))
ruta_bd = os.path.join(ruta_proyecto, "punto_de_venta.db")

#==========================
#1 Base de Datos ( Creacion de tablas)
#==========================
def inicializar_bd():
    conexion = sqlite3.connect(ruta_bd)
    cursor = conexion.cursor()

    #Tabla de productos
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS productos (
        codigo TEXT PRIMARY KEY,
        NOMBRE TEXT NOT NULL,
        precio REAL NOT NULL,
        stock INTEGER NOT NULL
)
"""
    )

    #tabla de ventas 

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total REAL NOT NULL
        )
        """
        )

    conexion.commit()
    conexion.close()


    #Inicializamos la base de datos al arrancar
inicializar_bd()

    #==========================
    #2. Interfaz grafica (Ventana principal)
    #==========================



class AppPOS:

    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Sistema punto de venta (POS)")
        self.ventana.geometry("850x550")
        self.ventana.configure(bg=PALETA_NOCHE["fondo"])
    #Lista interna para almacenar los articulos del carrito actual
        self.carrito = []

    #Panel de pestañas (ventas / inventario)
        self.pestana = ttk.Notebook(self.ventana)
        self.ventana_ventas = ttk.Frame(self.pestana)
        self.pestana_inventario = ttk.Frame(self.pestana)
        self.pestana_dashboard = ttk.Frame(self.pestana)

        self.pestana.add(self.ventana_ventas, text="🛒 Caja / Ventas")
        self.pestana.add(self.pestana_inventario, text="📦 Inventario")
        self.pestana.add(self.pestana_dashboard, text="📊 Dashboard")
        self.pestana.pack(expand=True, fill="both")

    #Construir la interfaz de cada pestaña
        self.crear_pestana_inventario()
        self.crear_pestana_ventas()
        self.crear_pestana_dashboard()
        self.modo_actual = "dia"
        self.aplicar_tema("dia")

    #============================
    #dEFINIR TEMA OSCURO O CLARO 
    #============================
    
    def aplicar_tema(self, modo):
        paleta = PALETA_NOCHE if modo == "noche" else PALETA_DIA
        estilo = ttk.Style()
        estilo.theme_use("clam")

        self.ventana.configure(bg=paleta["fondo"])
        estilo.configure("TFrame", background=paleta["fondo"])
        estilo.configure("TLabel", background=paleta["fondo"], foreground=paleta["texto"])
        estilo.configure("TButton", background=paleta["fondo_caja"], foreground=paleta["texto"])
        estilo.map("TButton", background=[("active", paleta["encabezado"]), ("pressed", paleta["presionado"])])
        estilo.configure("TEntry", fieldbackground=paleta["fondo_caja"], foreground=paleta["texto"])
        estilo.configure("TNotebook", background=paleta["fondo"])
        estilo.configure("TNotebook.Tab", background=paleta["fondo_caja"], foreground=paleta["texto"])
        estilo.map("TNotebook.Tab", background=[("selected", paleta["fondo"])], foreground=[("selected", paleta["acento"])])
        estilo.configure("Treeview", background=paleta["fondo_caja"], fieldbackground=paleta["fondo_caja"], foreground=paleta["texto"])
        estilo.configure("Treeview.Heading", background=paleta["encabezado"], foreground=paleta["texto"])
        estilo.map("Treeview.Heading", background=[("active", paleta["encabezado"])])
    #==========================
    #aplicar tema oscuro o claro
    #==========================
    def  alternar_tema(self):
        if self.modo_actual == "noche":
            self.modo_actual = "dia"
        else :
            self.modo_actual = "noche"
        self.aplicar_tema(self.modo_actual)

    
    #==========================
    #Pestaña Inventario (Registrar Productos,)
    #==========================
    def crear_pestana_inventario(self):
        frame = ttk.LabelFrame(
            self.pestana_inventario, text="Registrar Nuevo Prodcuto "       
        )
        frame.pack(padx=20, pady=20, fill="x")


        #ENTRADA DE TEXTO
        ttk.Label(frame, text="Codigo de Barras:").grid(
                row=0, column=0, padx=10, pady=5, sticky="w"
            )
        self.ent_codigo = ttk.Entry(frame)
        self.ent_codigo.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Nombre del Producto:").grid(
                row=1, column=0, padx=10, pady=5, sticky="W"
            )
        self.ent_nombre = ttk.Entry(frame)
        self.ent_nombre.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Precio ($):").grid(
                row=2, column=0, padx=10, pady=5, sticky="w"
            )
        self.ent_precio =ttk.Entry(frame)
        self.ent_precio.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Stock Inicial:").grid(
                row=3, column=0, padx=10, pady=5, sticky="w"
            )
        self.ent_stock =ttk.Entry(frame)
        self.ent_stock.grid(row=3, column=1, padx=10, pady=5)

        btn_guardar = ttk.Button(
                frame, text="Guardar Producto", command=self.guardar_producto
            )
        btn_guardar.grid(row=4, column=0, columnspan=2, pady=15)

        self.tabla_inventario = ttk.Treeview(
            self.pestana_inventario,
            columns=("Código", "Nombre", "Precio", "Stock"),
            show="headings",
            height=10
        )
        self.tabla_inventario.heading("Código", text="Código")
        self.tabla_inventario.heading("Nombre", text="Nombre")
        self.tabla_inventario.heading("Precio", text="Precio")
        self.tabla_inventario.heading("Stock", text="Stock")

        self.tabla_inventario.column("Código", width=120, anchor="center")
        self.tabla_inventario.column("Nombre", width=250)
        self.tabla_inventario.column("Precio", width=100, anchor="e")
        self.tabla_inventario.column("Stock", width=80, anchor="center")

        self.tabla_inventario.pack(padx=20, pady=10, fill="both", expand=True)

        self.actualizar_tabla_inventario()

    def actualizar_tabla_inventario(self):
        #Limpiar tabla visual
        for item in self.tabla_inventario.get_children():
            self.tabla_inventario.delete(item)

        #Volver a cargar los productos desde la base de datos
        for codigo, nombre, precio, stock in self.obtener_productos():
            self.tabla_inventario.insert(
                "",
                "end",
                values=(codigo, nombre, f"${precio:.2f}", stock),
            )

    def guardar_producto(self):
        codigo = self.ent_codigo.get().strip()
        nombre = self.ent_nombre.get().strip()
        precio = self.ent_precio.get().strip()
        stock = self.ent_stock.get().strip()

        if not (codigo and nombre and precio and stock):
            messagebox.showwarning("Error", "Todos los campos son obligatorios.")
            return

        try:
            conexion = sqlite3.connect(ruta_bd)
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO productos VALUES (?, ?, ?, ?)", (codigo, nombre, float(precio), int(stock))
            )
            conexion.commit()
            conexion.close()

            self.actualizar_tabla_inventario()
            self.ent_codigo.delete(0, tk.END)
            self.ent_nombre.delete(0, tk.END)
            self.ent_precio.delete(0, tk.END)
            self.ent_stock.delete(0, tk.END)

            messagebox.showinfo("Éxito", "Producto guardado correctamente.")
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Error", "Ya existe un producto registrado con ese Código."
            )
        except ValueError:
            messagebox.showerror(
                "Error", "Precio debe ser Número y Stock un número entero."
            )

    def obtener_productos(self):
        conexion = sqlite3.connect(ruta_bd)
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM productos")

        productos = cursor.fetchall()
        conexion.close()
        return productos


    def obtener_ventas_por_periodo(self, periodo):
        conexion = sqlite3.connect(ruta_bd)
        cursor = conexion.cursor()

        if periodo == "hoy":
            cursor.execute(
                "SELECT SUM(total) FROM ventas WHERE date(fecha) = date('now')"
            )
        elif periodo == "semana":
            cursor.execute("SELECT SUM(total) FROM ventas WHERE strftime('%W', fecha) = strftime('%W', 'now')")

        elif periodo == "mes":
            cursor.execute("SELECT SUM(total) FROM ventas WHERE strftime('%m', fecha) = strftime('%m', 'now')")

        resultado = cursor.fetchone()
        conexion.close()

        if resultado [0] is None:
            return 0
        else:
            return resultado[0]

    def crear_pestana_dashboard(self):
        titulo = ttk.Label(
            self.pestana_dashboard,
            text="DASHBOARD DE VENTAS",
            font=("Arial", 20, "bold")
        )
        titulo.pack(pady=20)

        frame_stats = ttk.Frame(self.pestana_dashboard)
        frame_stats.pack(padx=20, pady=20, fill="both", expand=True)
        #cuadro 1:Ventas del dia
        self.crear_cuadro_estadistica(frame_stats, "Ventas HOY", "hoy", 0)
        #Cuadro 2: Ventas de la semana
        self.crear_cuadro_estadistica(frame_stats, "Ventas SEMANA", "semana", 1)
        #Cuadro 3: Ventas del mes
        self.crear_cuadro_estadistica(frame_stats, "Ventas MES", "mes", 2)

        #Botón para refrescar
        btn_refrescar = ttk.Button(
            self.pestana_dashboard,
            text="Refrescar Dashboard",
            command=self.refrescar_dashboard
            )
        btn_refrescar.pack(pady=10)

    def crear_cuadro_estadistica(self, padre, titulo, periodo, columna):
        frame = ttk.LabelFrame(padre, text=titulo, padding=20)
        frame.grid(row=0, column=columna, padx=10, pady=10, sticky="nsew")

        total = self.obtener_ventas_por_periodo(periodo)

        lbl_total = ttk.Label(
            frame, 
            text=f"${total:.2f}",
            font=("Arial", 24, "bold"),
            foreground="green"
        )
        lbl_total.pack()

        #Guardar referencia para actualizar después
        if periodo == "hoy":
            self.lbl_hoy = lbl_total
        elif periodo == "semana":
            self.lbl_semana = lbl_total
        elif periodo == "mes":
            self.lbl_mes = lbl_total

    def refrescar_dashboard(self):
        #Actualizar los numeros cuando presiona el boton
        self.lbl_hoy.config(text=f"${self.obtener_ventas_por_periodo('hoy'):.2f}")
        self.lbl_semana.config(text=f"${self.obtener_ventas_por_periodo('semana'):.2f}")
        self.lbl_mes.config(text=f"${self.obtener_ventas_por_periodo('mes'):.2f}")

    

#--------------------------
#PESTAÑA VENTAS (Caja de cobro)
#--------------------------

    def crear_pestana_ventas(self):
        #Entrada de codigo de barras
        frame_top = ttk.Frame(self.ventana_ventas)
        frame_top.pack(padx=20, pady=10, fill="x")

        ttk.Label(
            frame_top, text="Código de Barras:", font=("Arial", 11, "bold")
        ).pack(side="left", padx=5)
        self.ent_buscar_codigo = ttk.Entry(frame_top, font=("Arial", 11))
        self.ent_buscar_codigo.pack(side="left", padx=5)
        # Al presionar ENTER en este campo, busca el producto automaticamente
        self.ent_buscar_codigo.bind("<Return>", lambda event: self.agregar_al_carrito())

        btn_agregar = ttk.Button (
            frame_top, text= "Agregar", command=self.agregar_al_carrito
        )
        btn_agregar.pack(side="left", padx=5)

        self.btn_tema = ttk.Button(frame_top, text="Cambiar tema", command=self.alternar_tema)
        self.btn_tema.pack(side="right", padx=5)

        #Tabla del Carrito de Ventas
        self.tabla_cart = ttk.Treeview(
            self.ventana_ventas,
            columns=("Código", "Nombre", "Precio", "Cant", "Subtotal"),
            show="headings",
        )
        self.tabla_cart.heading("Código", text="Código")
        self.tabla_cart.heading("Nombre", text="Nombre")
        self.tabla_cart.heading("Precio", text="Precio Unitario")
        self.tabla_cart.heading("Cant", text="Cant")
        self.tabla_cart.heading("Subtotal", text="Subtotal")
        self.tabla_cart.pack(padx=20, pady=10, fill="both", expand=True)

        #Panel inferior (Total y Cobrar)
        frame_bottom = ttk.Frame(self.ventana_ventas)
        frame_bottom.pack(padx=20, pady=10, fill="x")

        self.lbl_total = ttk.Label(
            frame_bottom,
            text="Total: $0.00",
            font=("Arial", 16, "bold"),
            foreground="green",
        )
        self.lbl_total.pack(side="left", padx=10)

        btn_cobrar = ttk.Button(
            frame_bottom, text="Cobrar", command=self.procesar_venta
        )
        btn_cobrar.pack(side="right", padx=10)

    def agregar_al_carrito(self):
        codigo = self.ent_buscar_codigo.get().strip()
        if not codigo:
            return

        conexion = sqlite3.connect(ruta_bd)
        cursor = conexion.cursor()
        cursor.execute("SELECT codigo, nombre, precio, stock FROM productos WHERE codigo = ?", (codigo,))
        prod = cursor.fetchone()
        conexion.close()


        if prod:
            cod, nombre, precio, stock = prod
            if stock <= 0:
                messagebox.showwarning(
                    "Sin Stock", f"El producto ´{nombre}´ no tiene existencias."
                )
                return

            #Si ya esta en el carrito, aumentamos cantidad
            encontrado = False
            for item in self.carrito:
                if item["codigo"] == cod:
                   if item["cantidad"] + 1 > stock:
                       messagebox.showwarning(
                           "Stock Insuficiente",
                           "No hay mas unidades en inventario.",
                       )
                       return
                   item["cantidad"] += 1
                   item["subtotal"] =item["cantidad"] * precio
                   encontrado = True
                   break

            if not encontrado:
                self.carrito.append(
                    {
                        "codigo": cod,
                        "nombre": nombre,
                        "precio": precio,
                        "cantidad": 1,
                        "subtotal": precio,
                    }
                )

            self.actualizar_tabla_carrito()
            self.ent_buscar_codigo.delete(0, tk.END)
        else:
            messagebox.showerror("No encontrado", "Producto no registrado.")

    def actualizar_tabla_carrito(self):
        #Limpiar tabla visual
        for item in self.tabla_cart.get_children():
            self.tabla_cart.delete(item)

        total = 0.0
        for item in self.carrito:
            self.tabla_cart.insert(
                "",
                "end",
                values=(
                    item["codigo"],
                    item["nombre"],
                    f"${item['precio']:.2f}",
                    item["cantidad"],
                    f"${item['subtotal']:.2f}"
                ),
            )
            total += item["subtotal"]

        self.lbl_total.config(text=f"TOTAL: ${total:.2f}")

    def procesar_venta(self):
        if not self.carrito:
            messagebox.showwarning(
                "Carrito Vacío", "No hay productos agregados a la venta."
            )
            return

        total_venta = sum(item["subtotal"] for item in self.carrito)

        conexion = sqlite3.connect(ruta_bd)
        cursor = conexion.cursor()

        #Registrar la venta en la base de datos
        cursor.execute("INSERT INTO ventas (total) VALUES (?)", (total_venta,))

        #Descontar el stock de cada producto vendido
        for item in self.carrito:
            cursor.execute(
                "UPDATE productos SET stock = stock - ? WHERE codigo = ?",
                (item["cantidad"], item["codigo"]),
            )

        conexion.commit()
        conexion.close()

        messagebox.showinfo(
            "Venta Exitosa", f"Venta registrada con exito. \nTotal: ${total_venta:.2f}"
        )

        # Vaciar carrito
        self.carrito = []
        self.actualizar_tabla_carrito()
        self.actualizar_tabla_inventario()


#===========================
# 3. EJECUCIÓN
#===========================
if __name__ == "__main__":
    raiz = tk.Tk()
    app = AppPOS(raiz)
    raiz.mainloop()
                    



