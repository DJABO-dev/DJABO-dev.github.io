
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
from pathlib import Path
import shutil
import threading
import subprocess
import re
import filecmp
#----------------------------- UNIDADES EN WINDOWS ----------------------------

# UNIDADES EXTRAIBLES

#import os
#import ctypes

#def obtener_unidades_usb():
    # Obtener todas las unidades del sistema
#    unidades = []
#    for letra in range(65, 91):  # Letras de la A a la Z
#        unidad = f"{chr(letra)}:\\"
#        if os.path.exists(unidad):
#            # Verificar si la unidad es extraíble (USB)
#            if ctypes.windll.kernel32.GetDriveTypeW(unidad) == 2:  # 2 indica que es una unidad extraíble
#                unidades.append(unidad)
#    return unidades

# Ejemplo de uso
#unidades_usb = obtener_unidades_usb()
#print("Unidades USB encontradas:", unidades_usb)

# RESTO DE UNIDADES

#import os
#import ctypes

#def obtener_unidades():
#    unidades = []
#    for letra in range(65, 91):  # Letras de la A a la Z
#        unidad = f"{chr(letra)}:\\"
#        if os.path.exists(unidad):
#            # Agregar la unidad a la lista
#            unidades.append(unidad)
#    return unidades


#----------------------------- FUNCIÓN PARA OBTENER LAS UNIDADES USB (SOLO LINUX) ----------------------------
# Obtenere las unidades USB montadas en el sistema
def obtener_unidades_usb():
    # Usar un conjunto para evitar duplicados
    unidades_usb = set()
    # Listar los dispositivos en /dev/disk/by-id
    for dispositivo in os.listdir('/dev/disk/by-id'):
        if 'usb' in dispositivo.lower():
            # Obtener el punto de montaje
            ruta = os.path.realpath(f'/dev/disk/by-id/{dispositivo}')
            # Obtener el punto de montaje usando lsblk
            with os.popen(f'lsblk -o MOUNTPOINT {ruta}') as p:
                lineas = p.readlines()  # Leer todas las líneas de la salida
                if len(lineas) > 1:
                    punto_montaje = lineas[1].strip()  # Capturar solo la segunda línea
                    if punto_montaje:
                        unidades_usb.add(punto_montaje)  # Agregar al conjunto
    return list(unidades_usb)  # Convertir el conjunto a lista
#-------------------------------------------------------------------------------------------------------

#------------------FUNCION PARA OBTENER LA CARPETA MÚSICA DEL USUARIO --------------)

# ---------------------------------------WINDOWS
#def obtener_ruta_carpeta_musica():
#    if platform.system() == "Windows":
#        # En Windows, se puede acceder a la ruta de la carpeta de música a través del registro
#        import winreg

#        try:
#            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
#            ruta_musica = winreg.QueryValueEx(key, "Personal")[0]
#            return Path(ruta_musica) / "Music"
#        except FileNotFoundError:
#            return None
#    elif platform.system() == "Darwin":  # macOS
#        return Path.home() / "Music"
#    else:  # Asumimos que es Linux
#        return Path.home() / "Music"

#ruta_musica = obtener_ruta_carpeta_musica()
#print("Ruta a la carpeta de música:", ruta_musica)

#___________________________________________________________________ LINUX
def obtener_ruta_carpeta_musica():
    home = Path.home()
    # Opción 1
    posibles_rutas = [
        home / "Music",
        home / "Música",
        home / "musica",
        home / "Muzyka",  # Polaco
        home / "Musik",    # Alemán
        home / "Musique",  # Francés
    ]
    for ruta in posibles_rutas:
        if ruta.exists() and ruta.is_dir():
            return ruta
    # Opción 2: 
    user_dirs_file = home / ".config/user-dirs.dirs"
    if user_dirs_file.exists():
        with open(user_dirs_file, 'r') as f:
            for line in f:
                if "XDG_MUSIC_DIR" in line:
                    # Extraer la ruta
                    ruta_musica = line.split('=')[1].strip().strip('"')
                    return Path(ruta_musica)

    return None
#-------------------------------------------------------------------------------------------------------

#--------------------------- EJECUCION INICIAL SE OBTIENEN LAS UNIDADES USB Y LA RUTA DEL USUARIO--------
# Obtener las unidades USB montadas y la ruta a la carpeta del usuario
unidades_usb = obtener_unidades_usb()
ruta_usuario = obtener_ruta_carpeta_musica()
unidades_usb.append(ruta_usuario)

#---------------------------------------------------------------------------------------------------------

# ----------------------------FUNCION PARA EL BOTON DE RECARGA DE UNIDADES USB -----------------
def recargar_unidades():
    unidades_usb = obtener_unidades_usb()
    ruta_usuario = obtener_ruta_carpeta_musica()
    unidades_usb.append(ruta_usuario)
    combo1['values'] = unidades_usb
    combo2['values'] = unidades_usb
#--------------------------------------------------------------------------------------------------------

# ------------------------ FUNCION PARA ALTERNAR EL ESTADO DE LOS NODOS ------------------------------
def toggle_nodos(tree, item, item_text):
    if item_text[:3] == '[✅]':
         new_text = item_text.replace('[✅]', '[➖]', 1)
         tree.item(item, text=new_text)
         tree.selection_remove(item)    # SI EL NODO CLIC ESTA MARCADO SE DESMARCA
         hijos = tree.get_children(item) # SE OBIENEN LOS NODOS HIJOS DE CLIC
         for nene in hijos:
             texto_hijo = tree.item(nene, 'text')
             if texto_hijo[:3] == '[✅]':
                 nuevo_texto_hijo = texto_hijo.replace('[✅]', '[➖]', 1)
                 tree.item(nene, text=nuevo_texto_hijo)   # SE DESMARCAN LOS HIJOS DE CLIC
                 tree.selection_remove(nene)
                 toggle_nodos(tree, nene, texto_hijo) # SE PASA NENE COMO CLIC PARA DESMARCARLO
         nodo_papa = tree.parent(item)
         nodos_nenes = tree.get_children(nodo_papa)
         for marcados in nodos_nenes:
              desmarcar = 1
              marcados_texto = tree.item(marcados, 'text')
              if marcados_texto.startswith('[✅]'):
                  texto_papa = tree.item(nodo_papa, 'text')
                  nuevo_texto_papa = texto_papa.replace('[➖]', '[✅]', 1)
                  tree.item(nodo_papa, text = nuevo_texto_papa)
                  tree.selection_add(nodo_papa)
                  desmarcar = 0
                  break
              if desmarcar == 1:
                  nodo_papa_texto = tree.item(nodo_papa, 'text')
                  nuevo_nodo_papa_texto = nodo_papa_texto.replace('[✅]', '[➖]', 1)
                  tree.item(nodo_papa, text=nuevo_nodo_papa_texto)
                  desmarcar_padres(tree, item)
    if item_text[:3] == '[➖]':
         new_text = item_text.replace('[➖]', '[✅]', 1)
         tree.item(item, text=new_text)
         tree.selection_add(item)         # SI EL NODO CLIC ESTA DESMARCADO SE MARCA
         hijos = tree.get_children(item)

         for nene in hijos:
             texto_hijo = tree.item(nene, 'text')
             if texto_hijo[:3] == '[➖]':
                 nuevo_texto_hijo = texto_hijo.replace('[➖]', '[✅]', 1)
                 tree.item(nene, text=nuevo_texto_hijo)
                 tree.selection_add(nene)
                 toggle_nodos(tree, nene, texto_hijo)
         nodo_padre = tree.parent(item)
         texto_padre = tree.item(nodo_padre, 'text')
         marcar_padres(tree, nodo_padre)
         if texto_padre[:3] == '[➖]':  # Si el padre no está marcado
            texto_sin_cambiar = texto_padre
            nuevo_texto_padre = texto_padre.replace('[➖]', '[✅]', 1)
            tree.item(nodo_padre, text=nuevo_texto_padre)
            tree.selection_add(nodo_padre)

# ----------------------------------------------------------------------------------------

# ---------------FUNCIONES DE MARCADO Y DESMARCADO DE NODOS PADRE ------------------------
def marcar_padres(tree, item):
    nodo_superior = tree.parent(item)
    tiene_padre_marcado = 0
    if nodo_superior: # SI EXISTE UN NODO SUPERIOR
        texto_comprobacion = tree.item(nodo_superior, 'text')
        if texto_comprobacion.startswith('[✅]'):
            tiene_padre_marcado = 1
            tree.selection_add(nodo_superior)
        if tiene_padre_marcado == 0:
            texto_superior = tree.item(nodo_superior, 'text')
            nuevo_texto_superior = texto_superior.replace('[➖]', '[✅]', 1)
            tree.item(nodo_superior, text = nuevo_texto_superior)
            tree.selection_add(nodo_superior)
            nodo_padre2 = tree.parent(nodo_superior)
            texto_nodo_padre2 = tree.item(nodo_padre2, 'text')
            marcar_padres(tree, nodo_padre2)
    if not nodo_superior:  # SI NO EXISTE NODO SUPERIOR
        texto_raiz = tree.item(item, 'text')
        nuevo_texto_raiz = texto_raiz.replace('[➖]', '[✅]', 1)
        tree.item(item, text = nuevo_texto_raiz)
        tree.selection_add(item)
#-------------------------------------------------------------------------------------
def desmarcar_padres(tree, item):
    nodo_superior = tree.parent(item)
    tiene_hijos_marcados = 0
    if nodo_superior: # SI EXISTE UN NODO SUPERIOR
        # COMPROBAR SI ESTE NODO SUPERIOR TIENE HIJOS MARCADOS
        hijos_de_nodo_superior = tree.get_children(nodo_superior)
        for comprobacion in hijos_de_nodo_superior:
            texto_comprobacion = tree.item(comprobacion, 'text')
            if texto_comprobacion.startswith('[✅]'):
                tiene_hijos_marcados = 1
                break
        if tiene_hijos_marcados == 0:
            texto_superior = tree.item(nodo_superior, 'text')
            nuevo_texto_superior = texto_superior.replace('[✅]', '[➖]', 1)
            tree.item(nodo_superior, text = nuevo_texto_superior)
            tree.selection_remove(nodo_superior)
            nodo_padre2 = tree.parent(nodo_superior)
            texto_nodo_padre2 = tree.item(nodo_padre2, 'text')
            desmarcar_padres(tree, nodo_superior)
    if not nodo_superior:  # SI NO EXISTE NODO SUPERIOR, RECORRER HIJOS
        hijos_de_raiz = tree.get_children(item)
        for comprobacion2 in hijos_de_raiz:
            texto_comprobacion2 = tree.item(comprobacion2, 'text')
            if texto_comprobacion2.startswith('[✅]'):
                tiene_hijos_marcados = 1
                break
        if tiene_hijos_marcados == 0:
            texto_raiz = tree.item(item, 'text')
            nuevo_texto_raiz = texto_raiz.replace('[✅]', '[➖]', 1)
            tree.item(item, text = nuevo_texto_raiz)
            tree.selection_remove(item)
# ---------------------------------------------------------------------------------------------------------------

# ------------------- FUNCIONES QUE RECOJEN EL CLIC SOBRE UN NODO --- GESTION CLIC EN ZONA VACÍA -------

def seleccionar_nodos_left(event):
    items_marcados = []
    item_seleccionado = tree_left.selection()
    items_marcados = item_seleccionado
    if item_seleccionado:
    # SE OBTIENE EL NODO SOBRE EL QUE SE HA HECHO CLIC
        item = tree_left.selection()[0]
    # Y SU TEXTO
        item_text = tree_left.item(item, 'text')
    # Y SE ENVÍAN LOS NODOS PARA SU CAMBIO
        toggle_nodos(tree_left, item, item_text)
        button2.config(state='normal')
        button4.config(state='disabled')
        button10.config(state='normal')
    
    # -------------------------------------------
def seleccionar_nodos_right(event):
    items_marcados = []
    item_seleccionado = tree_right.selection()
    if item_seleccionado:
    # SE OBTIENE EL NODO SOBRE EL QUE SE HA HECHO CLIC
        item = tree_right.selection()[0]
    # Y SU TEXTO
        item_text = tree_right.item(item, 'text')
        toggle_nodos(tree_right, item, item_text)
        button3.config(state='normal')
        #button5.config(state='disabled')
# ----------------------------------------------------------------------------------------

#------------ FUNCIÓN PARA COPIAR UNA BASE DE DATOS VACÍA A UNA UNIDAD QUE NO TIENE
def copiar_base_de_datos(unidad):
    carpeta_origen = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Engine Library')
    carpeta_destino = unidad+"/Engine Library"
    try:
    # Asegúrate de que la carpeta de destino existe
        os.makedirs(carpeta_destino, exist_ok=True)
    # Copiar todos los archivos y subcarpetas
        for item in os.listdir(carpeta_origen):
            origen_item = os.path.join(carpeta_origen, item)
            destino_item = os.path.join(carpeta_destino, item)
        if os.path.isdir(origen_item):
            shutil.copytree(origen_item, destino_item)  # Copia subcarpetas
        else:
            shutil.copy2(origen_item, destino_item)  # Copia archivos
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    messagebox.showinfo("Éxito", "Se ha creado una base de datos vacía en la unidad.")

# --------------------------------------------------------------------------------------------------

# --------------- FUNCIÓN QUE LLENA LOS TREEVIEW CON LOS DATOS DE LA BASE DE DATOS SELECCIONADA --
def on_combobox_selected(event):
    # Borrar el contenido del Treeview
    for item in tree_left.get_children():
        tree_left.delete(item)
    # Obtener el texto del combobox
    valor=combo1.get()
    # Formatear la ruta hasta la base de datos
    frase=valor+"/Engine Library/Database2/m.db"
    frase2=valor+" ERROR"
## ASEGURARSE DE QUE LA BASE DE DATOS EXISTE EN LA UNIDAD
    if os.path.isfile(frase):
        # Actualizar la etiqueta que muestra la base de datos
        etiqueta_izquierda.config(text=frase)
        # Conexion a la base de datos y extraccion de los datos
        conexion = sqlite3.connect(frase)
        cursor1 = conexion.cursor()
        cursor1.execute("SELECT id, title, parentListId FROM Playlist WHERE isPersisted = 1 ORDER BY parentListId")
        global resultados1
        global resultados2
        resultados1 = []
        resultados2 = []
        resultados1 = cursor1.fetchall()
        conexion.close()
        # COMPROBAR QUE LA BASE NO ESTÁ VACÍA
        if resultados1:
            # Insertar los resultados en el control treeview
            nodos = {}
            for id, title, parentListId in resultados1:
                nodos[id] = (title, parentListId)
                # Si no tiene padre, es un nodo raíz
                if parentListId == 0:
                    tree_left.insert('', 'end', id, text='[➖] '+title, tags=('checkbox',))
                else:
                    # Si tiene padre, insertarlo como hijo
                    tree_left.insert(parentListId, 'end', id, text='[➖] '+title, tags=('checkbox',))

        # SI LA BASE ESTÁ VACÍA
        else:
            mensaje="La base de datos está vacía"
            tree_left.insert('', 'end', text=mensaje)
            button2.config(state='disabled')
            button10.config(state='disabled')
            button4.config(state='disabled')
            # RECARGAR SOLO EL OTRO COMBOBOX SI NO HAY TAMBIEN BASE VACÍA
            resultados2 = []
            if resultados2:
                on_combobox2_selected(event)
    # SI NO EXISTE LA BASE DE DATOS
    else:
        button2.config(state='disabled')
        button10.config(state='disabled')
        button4.config(state='disabled')
        etiqueta_izquierda.config(text=frase2)
        mensaje="Esta unidad no tiene librería Engine DJ"
        tree_left.insert('', 'end', text=mensaje)
        respuesta = messagebox.askyesno("¿Continuar?", "¿Copiar una base de datos vacía a la unidad?")
        if respuesta:
            copiar_base_de_datos(valor)
            recargar_unidades()
            on_combobox_selected(event)

# ------------------------------------------------------------------------------
def on_combobox2_selected(event):
    # Borrar el contenido del Treeview
    for item in tree_right.get_children():
        tree_right.delete(item)
    # Obtener el texto del combobox
    valor=combo2.get()
    # Formatear la ruta hasta la base de datos
    frase2=valor+"/Engine Library/Database2/m.db"
    frase3=valor+" ERROR"
## ASEGURARSE DE QUE LA BASE DE DATOS EXISTE EN LA UNIDAD
    if os.path.isfile(frase2):
        # Actualizar la etiqueta que muestra la base de datos
        etiqueta_derecha.config(text=frase2)
        # Conexion a la base de datos y extraccion de los datos
        conexion2 = sqlite3.connect(frase2)
        cursor2 = conexion2.cursor()
        cursor2.execute("SELECT id, title, parentListId FROM Playlist WHERE isPersisted = 1 ORDER BY parentListId")
        global resultados1
        global resultados2
        resultados1 = []
        resultados2 = []
        resultados2 = cursor2.fetchall()
        conexion2.close()
        # COMPROBAR QUE LA BASE NO ESTÁ VACÍA
        if resultados2:
            # Insertar los resultados en el control treeview
            nodos2 = {}
            for id, title, parentListId in resultados2:
                nodos2[id] = (title, parentListId)
                # Si no tiene padre, es un nodo raíz
                if parentListId == 0:
                    tree_right.insert('', 'end', id, text='[➖] '+title, tags=('checkbox',))
                else:
                    # Si tiene padre, insertarlo como hijo
                    tree_right.insert(parentListId, 'end', id, text='[➖] '+title, tags=('checkbox',))

        # SI LA BASE ESTÁ VACÍA
        else:
            mensaje2="La base de datos está vacía"
            tree_right.insert('', 'end', text=mensaje2)
            button3.config(state='disabled')
            # RECARGAR SOLO EL OTRO COMBOBOX SI NO HAY TAMBIEN BASE VACÍA
            if resultados1:
                on_combobox_selected(event)
    # SI NO EXISTE LA BASE DE DATOS
    else:
        button3.config(state='disabled')
        button4.config(state='disabled')
        etiqueta_derecha.config(text=frase3)
        mensaje="Esta unidad no tiene librería Engine DJ"
        tree_right.insert('', 'end', text=mensaje)
        respuesta = messagebox.askyesno("¿Continuar?", "¿Copiar una base de datos vacía a la unidad?")
        if respuesta:
            copiar_base_de_datos(valor)
            recargar_unidades()
            on_combobox2_selected(event)

# -----------------------------------------------------------------------------------------------


# ----------------------- FUNCIÓN DE APOYO A GUARDAR_SELECCION -------------------------------
def guardar_nodos_recursivamente(tree, nodo, lista_seleccionada):
    # Obtiene el texto del nodo
    tex = tree.item(nodo, 'text')
    # Verifica si el nodo está marcado
    if tex.startswith('[✅]'):
        lista_seleccionada.append(nodo)  # Agrega el código del nodo a la lista
        print(f'{nodo}')
        # Obtiene los hijos del nodo actual
        hijos = tree.get_children(nodo)
        for hijo in hijos:
            # Llama recursivamente a la función para cada hijo
            print(f'{hijo}')
            guardar_nodos_recursivamente(tree, hijo, lista_seleccionada)
# -------------------------------------------------------------------------------------------------

# -------------------------FUNCION PARA GUARDAR EN UNA VARIABLE TODOS LOS NODOS SELECCIONADOS-
def guardar_seleccion_left():
    nodos = tree_left.get_children()
    lista_nodos_seleccionados_left = []  # Inicializa la lista para almacenar los nodos seleccionados
    control = 0
    if nodos:
        for todo in nodos:
            # Llama a la función recursiva para cada nodo padre
            guardar_nodos_recursivamente(tree_left, todo, lista_nodos_seleccionados_left)
            control = 1
    if control == 1:
        # Aquí puedes acceder a la lista de nodos seleccionados
        print(lista_nodos_seleccionados_left)  # Imprime la lista para verificar
        
    # COMPROBAR LA EXISTENCIA DE UNA BASE DE DATOS EN EL TREEVIEW DE LA DERECHA
        valor = combo2.get()
        frase = valor+"/Engine Library/Database2/m.db"
        frase_error = "Para sincronizar debe seleccionar una base de datos en el otro lado"
        if os.path.isfile(frase):
            button4.config(state='normal')
            
        else:
            button4.config(state='disabled')
            messagebox.showwarning("Advertencia", frase_error)
        if len(lista_nodos_seleccionados_left) == 0:
            messagebox.showwarning("ERROR", "No hay nodos seleccionados.")
            button2.config(state='disabled')
            button10.config(state='disabled')
            button4.config(state='disabled')
        return lista_nodos_seleccionados_left
    else:
        messagebox.showwarning("Advertencia", "No hay nodos seleccionados.")
        button10.config(state='disabled')
        button2.config(state='disabled')
        button4.config(state='disabled')

#------------------------------------------------------------------------------
def guardar_seleccion_right():
    nodos = tree_right.get_children()
    lista_nodos_seleccionados_right = []  # Inicializa la lista para almacenar los nodos seleccionados
    control = 0
    if nodos:
        for todo in nodos:
            # Llama a la función recursiva para cada nodo padre
            guardar_nodos_recursivamente(tree_right, todo, lista_nodos_seleccionados_right)
            control = 1
    if control == 1:
        # Aquí puedes acceder a la lista de nodos seleccionados
        print(lista_nodos_seleccionados_right)  # Imprime la lista para verificar

    # COMPROBAR LA EXISTENCIA DE UNA BASE DE DATOS EN EL TREEVIEW DE LA IZQUIERDA
        valor = combo1.get()
        frase = valor+"/Engine Library/Database2/m.db"
        frase_error = "Debe seleccionar una base de datos en el otro lado"
        if os.path.isfile(frase):
            button3.config(state='normal')
        else:
            button3.config(state='disabled')
            messagebox.showwarning("Advertencia", frase_error)
        if len(lista_nodos_seleccionados_right) == 0:
            messagebox.showwarning("ERROR", "No hay nodos seleccionados.")
            button3.config(state='disabled')
        return lista_nodos_seleccionados_right
    else:
        messagebox.showwarning("Advertencia", "No hay nodos seleccionados.")
        button3.config(state='disabled')
#------------------------------------------------------------------------------

# FUNCIÓN PARA MOSTRAR LAS TRACKS DE LOS NODOS SELECCIONADOS

def mostrar_ventana_tracks_left():
	nodos_listar = guardar_seleccion_left()
	if nodos_listar:
		ventana_tracks = tk.Toplevel()
		ventana_tracks.title("Lista de archivos de música en nodos seleccionados")
		ventana_tracks.geometry("800x980")
		frame_para_botonera = tk.Frame(ventana_tracks)
		frame_para_botonera.pack(fill=tk.BOTH, expand=False)
		button_Salir = tk.Button(frame_para_botonera, text="SALIR", state='active', command=ventana_tracks.destroy)
		button_Salir.pack(side=tk.BOTTOM, padx=10, pady=10, anchor="w")
		frame_para_lista = tk.Frame(ventana_tracks)
		frame_para_lista.pack(fill=tk.BOTH, expand=True)
		tree_tracks = ttk.Treeview(frame_para_lista, height=10, selectmode='extended')
		tree_tracks.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
		scrollbar = ttk.Scrollbar(frame_para_lista, orient="vertical", command=tree_tracks.yview)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		tree_tracks.configure(yscroll=scrollbar.set)
		valor=combo1.get()
		frase=valor+"/Engine Library/Database2/m.db"
		conexion = sqlite3.connect(frase)
		cursor1 = conexion.cursor()
		cursor2 = conexion.cursor()
		cursor3 = conexion.cursor()
		resultados1 = []
		resultados2 = []
		for nds in nodos_listar:
			cursor1.execute("SELECT trackId FROM PlaylistEntity WHERE listId = "  + nds)
			cursor2.execute("SELECT id, title, parentListId FROM Playlist WHERE id = " + nds)
			cursor3.execute("SELECT id FROM PlaylistAllParent WHERE parentListId = " + nds)
			resultados1 = cursor1.fetchall() # LISTA DE CANCIONES DE LA PLAYLIST
			resultados2 = cursor2.fetchone() # ID, TITULO Y LISTA PADRE DE nds
			resultados3 = cursor3.fetchall() # ID de la lista, SI EXISTE ES PADRE DE OTRA LISTA, SINO RELLENAR CANCIONES
			es_padre = resultados3
			if resultados2:
				id, title, parentListId = resultados2
				if parentListId == 0:
					tree_tracks.insert("", 'end', id, text='[📀] ' + title)
				else:
					tree_tracks.insert(parentListId, 'end', id, text='[📀]' + title)
					print(f'PLAYLIST BUSCADA: {nds}')
					if resultados1 and not es_padre: # SI HAY TRACKS EN LA LISTA nds y nds NO TIENE HIJOS
						for playlists in resultados1:
							trackId = playlists
							cursor1.execute("SELECT title, artist, filename FROM Track WHERE id = ?", trackId)
							cancion = cursor1.fetchone()
							#title, artist = cancion
							if cancion:
								title, artist, filename = cancion
								if not artist and title:
									cancion_texto = "".join(str(num) for num in title)
									tree_tracks.insert(nds, 'end', text='🎝 '+ cancion_texto + " 👷  SIN AUTOR")
								if artist and title:
									cancion_texto = "".join(str(num) for num in title)
									tree_tracks.insert(nds, 'end', text='🎝 '+ cancion_texto + " 👷 " + artist)
		cursor1.close()
		cursor2.close()
		cursor3.close()
		conexion.close()

def mostrar_ventana_tracks_right():
	nodos_listar = guardar_seleccion_right()
	if nodos_listar:
		print(f'VENTANA TRACKS: {nodos_listar}')
		ventana_tracks = tk.Toplevel()
		ventana_tracks.title("Lista de archivos de música en nodos seleccionados")
		ventana_tracks.geometry("800x980")
		frame_para_botonera = tk.Frame(ventana_tracks)
		frame_para_botonera.pack(fill=tk.BOTH, expand=False)
		button_Salir = tk.Button(frame_para_botonera, text="SALIR", state='active', command=ventana_tracks.destroy)
		button_Salir.pack(side=tk.BOTTOM, padx=10, pady=10, anchor="w")
		frame_para_lista = tk.Frame(ventana_tracks)
		frame_para_lista.pack(fill=tk.BOTH, expand=True)
		tree_tracks = ttk.Treeview(frame_para_lista, height=10, selectmode='extended')
		tree_tracks.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
		scrollbar = ttk.Scrollbar(frame_para_lista, orient="vertical", command=tree_tracks.yview)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		tree_tracks.configure(yscroll=scrollbar.set)
		valor=combo2.get()
		frase=valor+"/Engine Library/Database2/m.db"
		conexion = sqlite3.connect(frase)
		cursor1 = conexion.cursor()
		cursor2 = conexion.cursor()
		cursor3 = conexion.cursor()
		resultados1 = []
		resultados2 = []
		tracks = {}
		for nds in nodos_listar:
			cursor1.execute("SELECT trackId FROM PlaylistEntity WHERE listId = "  + nds)
			cursor2.execute("SELECT id, title, parentListId FROM Playlist WHERE id = " + nds)
			cursor3.execute("SELECT id FROM PlaylistAllParent WHERE parentListId = " + nds)
			resultados1 = cursor1.fetchall() # LISTA DE CANCIONES DE LA PLAYLIST
			resultados2 = cursor2.fetchone() # ID, TITULO Y LISTA PADRE DE nds
			resultados3 = cursor3.fetchall() # ID de la lista, SI EXISTE ES PADRE DE OTRA LISTA, SINO RELLENAR CANCIONES
			es_padre = resultados3
			if resultados2:
				id, title, parentListId = resultados2
				if parentListId == 0:
					tree_tracks.insert("", 'end', id, text='[📀] ' + title)
				else:
					tree_tracks.insert(parentListId, 'end', id, text='[📀]' + title)
					print(f'PLAYLIST BUSCADA: {nds}')
					if resultados1 and not es_padre: # SI HAY TRACKS EN LA LISTA nds y nds NO TIENE HIJOS
						for playlists in resultados1:
							trackId = playlists
							cursor1.execute("SELECT title, artist, filename FROM Track WHERE id = ?", trackId)
							cancion = cursor1.fetchone()
							if cancion:
								title, artist, filename = cancion
								if not artist and title:
									cancion_texto = "".join(str(num) for num in title)
									tree_tracks.insert(nds, 'end', text='🎝 '+ cancion_texto + " 👷  SIN AUTOR")
								if artist and title:
									cancion_texto = "".join(str(num) for num in title)
									tree_tracks.insert(nds, 'end', text='🎝 '+ cancion_texto + " 👷 " + artist)
		cursor1.close()
		cursor2.close()
		cursor3.close()
		conexion.close()

#------------------------------------------------------ FUNCIONES DE SINCRONIZACIÓN -------------
def iniciar_sincronizacion_left_to_right(progress_bar):
    # Crear y comenzar el hilo
    progress_bar['value'] = 0
    thread = threading.Thread(target=sync_left_to_right, args=(progress_bar,))
    thread.start()

def iniciar_sincronizacion_right_to_left(progress_bar):
    # Crear y comenzar el hilo
    progress_bar['value'] = 0
    thread = threading.Thread(target=sync_right_to_left, args=(progress_bar,))
    thread.start()


# ----------------- FUNCION SINCRONIZAR LEFT TO RIGHT --------------------------------
def sync_left_to_right(progress_bar):

    # CONFIGURACION GENERAL

    tree_left.bind('<ButtonRelease-1>', lambda e: "break")
    tree_right.bind('<ButtonRelease-1>', lambda e: "break")
    etiqueta_barra.pack(padx=10, pady=10)
    etiqueta_barra2.pack(padx=10, pady=10)
    progress_bar.pack(pady=20)
    lista_para_sync = []
    lista_para_sync = guardar_seleccion_left()
    if lista_para_sync:
        button1.config(state='disabled')
        button2.config(state='disabled')
        #button10.config(state='disabled')
        button4.config(state='disabled')
        #button3.config(state='disabled')
        button4.config(state='disabled')
        print(f'DESDE SINC: {lista_para_sync}')  # Imprime la lista para verificar
        valor=combo1.get()
        valor2=combo2.get()
        # Formatear la ruta hasta la base de datos
        frase_origen=valor+"/Engine Library/Database2/m.db"
        frase_destino=valor2+"/Engine Library/Database2/m.db"
        conexion = sqlite3.connect(frase_origen)
        cursor1 = conexion.cursor()
        conexion2 = sqlite3.connect(frase_destino)
        cursor2 = conexion2.cursor()
        i = len(lista_para_sync)
        i = i*25000
        m = 300/i
        cursor2.execute('''INSERT INTO sqlite_sequence (name, seq) VALUES (?, ?)''', ('Track', 0))
        cursor2.execute('''INSERT INTO sqlite_sequence (name, seq) VALUES (?, ?)''', ('Playlist', 0))
        cursor2.execute('''INSERT INTO sqlite_sequence (name, seq) VALUES (?, ?)''', ('PlaylistEntity', 0))
        cursor2.execute('''INSERT INTO sqlite_sequence (name, seq) VALUES (?, ?)''', ('AlbumArt', 0))
        conexion2.commit()
#-----------------------------------------------------------------------------------------------------------------------------------------------

    # PLAYLIST
        rowid = 0
        for codigo in reversed(lista_para_sync):
            progress_bar['value'] = m
            progress_bar.update_idletasks()
            cursor1.execute('SELECT * FROM Playlist WHERE id = '+ codigo)
            cursor2.execute('SELECT * FROM Playlist WHERE id = '+ codigo)
            valores_destino = cursor2.fetchone()
            if valores_destino:
                id, title, parentListId, isPersisted, nextListId, lastEditTime, isExplicitlyExported = valores_destino
                tree_left.selection_remove(codigo)
                print(f"CODIGO ELIMINADO PORQUE YA EXISTE: {codigo}")
                update_left_to_right(progress_bar, codigo, lista_para_sync)
                print(f'LISTA lista_para_sync DESPUES DE UPDATE: {lista_para_sync}')
                break

#            # AÑADO LA PLAYLIST SI NO EXISTE EN DESTINO
            else:
                valores_origen = cursor1.fetchone()
                if valores_origen and rowid == 0:
                    cursor2.execute('''UPDATE sqlite_sequence SET seq = ? WHERE name = 'Playlist' ''', ('0',))
                    conexion2.commit()
                    id, title, parentListId, isPersisted, nextListId, lastEditTime, isExplicitlyExported = valores_origen
                    cursor2.execute('''INSERT OR IGNORE INTO Playlist (id, title, parentListId, isPersisted, nextListId, lastEditTime, isExplicitlyExported) VALUES (?,?,?,?,?,?,?)''', (id, title, parentListId, isPersisted, "0", lastEditTime, isExplicitlyExported))
                    rowid = cursor2.lastrowid
                    conexion2.commit()
                else:
                    cursor2.execute('''UPDATE sqlite_sequence SET seq = ? WHERE name = 'Playlist' ''', ('0',))
                    conexion2.commit()
                    id, title, parentListId, isPersisted, nextListId, lastEditTime, isExplicitlyExported = valores_origen
                    cursor2.execute('''INSERT OR IGNORE INTO Playlist (id, title, parentListId, isPersisted, nextListId, lastEditTime, isExplicitlyExported) VALUES (?,?,?,?,?,?,?)''', (id, title, parentListId, isPersisted, rowid, lastEditTime, isExplicitlyExported))
                    rowid = cursor2.lastrowid
                    conexion2.commit()
            conexion2.commit()
            progress_bar['value'] = m
            etiqueta_barra2.config(text="SINCRONIZANDO...")
            etiqueta_barra.config(text=("CREANDO PLAYLIST...", title))
            progress_bar.update_idletasks()
            m = m + 300/i
#------------------------------------------------------------------------------------------------------------------------------------

    # PLAYLISTENTITY

        for codigo_lista in lista_para_sync:
            codigo_lista_texto = "".join(str(num) for num in codigo_lista)
            cursor1.execute('SELECT id FROM PlaylistAllChildren WHERE id = '+ codigo_lista_texto)
            es_padre = cursor1.fetchall()
            if not es_padre:
                cursor1.execute('SELECT * FROM PlaylistEntity WHERE listId = '+ codigo_lista_texto)
                todas_playlistentity = cursor1.fetchall()
                for entrada in todas_playlistentity:
                    progress_bar['value'] = m
                    progress_bar.update_idletasks()
                    m = m + 300/i
                    id, listId, trackId, databaseUuid, nextEntityId, membershipReference = entrada
                    cursor2.execute('''INSERT OR IGNORE INTO PlaylistEntity (listId, trackId, databaseUuid, nextEntityId, membershipReference) VALUES (?, ?, ?, ?, ?)''', (listId, trackId, databaseUuid, '0', membershipReference))
                etiqueta_barra2.config(text="SINCRONIZANDO...")
                etiqueta_barra.config(text="INSERTANDO PLAYLIST INFO...")
                conexion2.commit()
#-----------------------------------------------------------------------------------------------------------

    # TRACKS
                cursor2.execute('SELECT trackId FROM PlaylistEntity WHERE listId ='+ codigo_lista_texto)
                mytracks = cursor2.fetchall()
                for codigo_trackId in mytracks:
                    cursor2.execute('''UPDATE sqlite_sequence SET seq = ? WHERE name = 'Track' ''', ('0',)) # INICIALIZO A 0 EL CONTADOR DE CANCIONES PARA QUE NO PRODUZCA ERROR DE ID RECICLADO
                    conexion2.commit()
                    codigo_texto = "".join(str(cod) for cod in codigo_trackId)
                    cursor1.execute('SELECT * FROM Track WHERE id = '+ codigo_texto)
                    todas_las_tracks = cursor1.fetchall()
                    for tracks_to_copy in todas_las_tracks:
                        id, playOrder, length, bpm, year, path, filename, bitrate, bpmAnalyzed, albumArtId, fileBytes, title, artist, album, genre, comment, label, composer, remixer, key, rating, albumArt, timeLastPlayed, isPlayed, fileType, isAnalyzed, dateCreated, dateAdded, isAvailable, isMetadataOfPackedTrackChanged, isPerfomanceDataOfPackedTrackChanged, playedIndicator, isMetadataImported, pdbImportKey, streamingSource, uri, isBeatGridLocked, originDAtabaseUuid, originTrackId, streamingFlags, explicitLyrics, lastEditTime = tracks_to_copy
                        cursor2.execute('''INSERT OR IGNORE INTO Track (id, playOrder, length, bpm, year, path, filename, bitrate, bpmAnalyzed, albumArtId, fileBytes, title, artist, album, genre, comment, label, composer, remixer, key, rating, albumArt, timeLastPlayed, isPlayed, fileType, isAnalyzed, dateCreated, dateAdded, isAvailable, isMetadataOfPackedTrackChanged, isPerfomanceDataOfPackedTrackChanged, playedIndicator, isMetadataImported, pdbImportKey, streamingSource, uri, isBeatGridLocked, originDAtabaseUuid, originTrackId, streamingFlags, explicitLyrics, lastEditTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (id, playOrder, length, bpm, year, path, filename, bitrate, bpmAnalyzed, albumArtId, fileBytes, title, artist, album, genre, comment, label, composer, remixer, key, rating, albumArt, timeLastPlayed, isPlayed, fileType, isAnalyzed, dateCreated, dateAdded, isAvailable, isMetadataOfPackedTrackChanged, isPerfomanceDataOfPackedTrackChanged, playedIndicator, isMetadataImported, pdbImportKey, streamingSource, uri, isBeatGridLocked, originDAtabaseUuid, originTrackId, streamingFlags, explicitLyrics, lastEditTime))
                        #messagebox.showinfo("Información", "MIRA LA DB")
                        etiqueta_barra2.config(text="SINCRONIZANDO...")
                        etiqueta_barra.config(text="INSERTANDO TRACKS...")
                        progress_bar['value'] = m
                        progress_bar.update_idletasks()
                        m = m + 300/i

#----------------------------------------------------------------------------------------------------------------------------------------------------

    # PLAYLISTENTITY ADITIONAL INFO

                        cursor1.execute('SELECT * FROM PlaylistEntity WHERE trackId = ?', (id,))
                        inserts = cursor1.fetchall()
                        for lines in inserts:
                            id2, listId2, trackId2, databaseUuid2, nextEntityId2, membershipReference2 = lines
                            if listId2 != listId:
                                cursor2.execute('''INSERT OR IGNORE INTO PlaylistEntity (listId, trackId, databaseUuid, nextEntityId, membershipReference) VALUES (?, ?, ?, ?, ?)''', (listId2, trackId2, databaseUuid2, '0', membershipReference2))
                                progress_bar['value'] = m
                                progress_bar.update_idletasks()
                                m = m + 300/i
                                etiqueta_barra2.config(text="SINCRONIZANDO...")
                                etiqueta_barra.config(text=('Playlist info '+filename))
                conexion2.commit()
                progress_bar['value'] = m
                progress_bar.update_idletasks()
                m = m + 300/i

#-------------------------------------------------------------------------------------------------------------

    # PERFORMANCEDATA

                for codigo_trackId in mytracks:
                    codigo_texto = "".join(str(codi) for codi in codigo_trackId)
                    cursor1.execute('SELECT * FROM PerformanceData WHERE trackId = '+ codigo_texto)
                    todas_las_tracks = cursor1.fetchall()
                    for data_to_copy in todas_las_tracks:
                        trackId, trackData, overviewWaveFormData, beatData, quickCues, loops, thirdPartySourceId, activeOnLoadLoops = data_to_copy
                        cursor2.execute('''UPDATE PerformanceData SET trackData = ?, overviewWaveFormData = ?, beatData = ?, quickCues = ?, loops = ?, thirdPartySourceId = ?, activeOnLoadLoops = ? WHERE trackId = ?''', (trackData, overviewWaveFormData, beatData, quickCues, loops, thirdPartySourceId, activeOnLoadLoops, trackId))
                        etiqueta_barra2.config(text="SINCRONIZANDO...")
                        etiqueta_barra.config(text="INSERTANDO PERFORMANCE DATA...")
                conexion2.commit()
                progress_bar['value'] = m
                progress_bar.update_idletasks()
                m = m + 300/i
#-----------------------------------------------------------------------------------------------------------

    # ALBUMART

                for codigo_trackId in mytracks:
                    codigo_texto = "".join(str(cod) for cod in codigo_trackId)
                    cursor1.execute('SELECT albumArtId FROM Track WHERE id = '+ codigo_texto)
                    codigo_Art = cursor1.fetchone()
                    if codigo_Art:
                        codigo_Art_texto = "".join(str(go) for go in codigo_Art)
                        cursor1.execute('SELECT * FROM AlbumArt WHERE id = '+ codigo_Art_texto)
                        album_data = cursor1.fetchall()
                        for data_to_copy in album_data:
                            id, hash, albumArt = data_to_copy
                            cursor2.execute('''INSERT OR REPLACE INTO AlbumArt (id, hash, albumArt) VALUES (?, ?, ?)''', (id, hash, albumArt))
                            etiqueta_barra2.config(text="SINCRONIZANDO...")
                            etiqueta_barra.config(text="INSERTANDO ALBUMART...")
                conexion2.commit()
                progress_bar['value'] = m
                progress_bar.update_idletasks()
                m = m + 300/i
#--------------------------------------------------------------------------------------------------------------

    # COPIAR LOS ARCHIVOS DE MUSICA EN LA RUTA DE DESTINO

                for codigo_trackId in mytracks:
                    cursor1.execute('SELECT path FROM Track WHERE id = ?',codigo_trackId)
                    ruta_archivo_origen = cursor1.fetchone()
                    print(f'CODIGO_TRACKID:    {codigo_trackId}')
                    if ruta_archivo_origen:
                        ruta_archivo_origen_texto = ''.join(ruta_archivo_origen)
						
						# COMPROBACIÓN DE LA REFERENCIA DE LA RUTA
                        if ruta_archivo_origen_texto.startswith('..'):
                            ruta_archivo_origen_modificada = ruta_archivo_origen_texto[2:]
                        else:
                            ruta_archivo_origen_modificada = "/Engine Library/" + ruta_archivo_origen_texto # ¿ES CORRECTO PARA CUALQUIER RUTA A ARCHIVO??

                        ruta_origen_definitiva = valor + ruta_archivo_origen_modificada
                        ruta_destino_definitiva = valor2 + ruta_archivo_origen_modificada
                        etiqueta_barra2.config(text=ruta_archivo_origen_modificada)
                        etiqueta_barra.config(text="COPIANDO ARCHIVOS DE MÚSICA...")
                        os.makedirs(os.path.dirname(ruta_destino_definitiva), exist_ok=True)
                        try:
                            if os.path.exists(ruta_destino_definitiva):
                                if filecmp.cmp(ruta_origen_definitiva, ruta_destino_definitiva, shallow=False):
                                    print(f'Omitiendo TRACK, ya existe')
                                else:
                                    shutil.copy(ruta_origen_definitiva, ruta_destino_definitiva)
                                    progress_bar['value'] = m
                                    progress_bar.update_idletasks()
                                    m = m + 30/i
                            else:
                                shutil.copy(ruta_origen_definitiva, ruta_destino_definitiva)
                                progress_bar['value'] = m
                                progress_bar.update_idletasks()
                                m = m + 30/i
                        except FileNotFoundError:
                            messagebox.showwarning("Advertencia", "No se han encontrado los archivos de música en origen.")
                            break
                        except PermissionError:
                            messagebox.showwarning("Advertencia", "No tiene permisos para escribir en destino.")
                            break
                        except Exception as e:
                            messagebox.showwarning("Advertencia", "Error inesperado.")
                            break
# ------------------------------------------------------------------------------------------------------------------------

    # SINCRONIZAR STEMS

                ruta_carpeta_stems = valor + "/Engine Library/Stems/"
                ruta_carpeta_destino_stems = valor2 + "/Engine Library/Stems/"
                if os.path.exists(ruta_carpeta_stems) and os.path.isdir(ruta_carpeta_stems):
                    for codigo_trackId in mytracks:
                        cursor1.execute('SELECT id FROM Track WHERE id = ?', codigo_trackId)
                        codigos_para_stems = cursor1.fetchall()
                        archivos = [f for f in os.listdir(ruta_carpeta_stems) if os.path.isfile(os.path.join(ruta_carpeta_stems, f))]
                        for nombre in archivos:
                            nombre_hasta_espacio = nombre.split(' ')[0]
                            codigo_stm = "".join(str(stm) for stm in codigo_trackId)
                            if nombre_hasta_espacio == codigo_stm:
                                os.makedirs(os.path.dirname(ruta_carpeta_destino_stems), exist_ok=True)
                                try:
                                    if os.path.exists(ruta_carpeta_destino_stems + nombre):
                                        if filecmp.cmp(ruta_carpeta_stems + nombre, ruta_carpeta_destino_stems + nombre, shallow=False):
                                            print(f'STEM ya existe')
                                        else:
                                            shutil.copy(ruta_carpeta_stems + nombre, ruta_carpeta_destino_stems + nombre)
                                    else:
                                        shutil.copy(ruta_carpeta_stems + nombre, ruta_carpeta_destino_stems + nombre)
                                except FileNotFoundError:
                                    messagebox.showwarning("Advertencia", "No se han encontrado el archivo STEM en origen.")
                                    break
                                except PermissionError:
                                    messagebox.showwarning("Advertencia", "No tiene permisos para escribir en destino.")
                                    break
                                except Exception as e:
                                    if e.errno == 28:
                                        messagebox.showwarning("ERROR", "Error DISCO LLENO.")
                                        break
                                    messagebox.showwarning("Advertencia", "Error inesperado.")
                                    break
                            etiqueta_barra2.config(text="STEM FILE "+ nombre)
                            etiqueta_barra.config(text="COPIANDO STEMS...")
                            progress_bar['value'] = m
                            progress_bar.update_idletasks()
                            m = m + 300/i
                else:
                    messagebox.showwarning("Advertencia", "No hay carpeta STEMS para sincronizar.")
#-----------------------------------------------------------------------------------------------------------------------------------------------

    # SINCRONIZAR SOUNDSWITCH

                ruta_carpeta_origen_soundswitch = valor + "/SoundSwitch/" # CARPETA ORIGEN
                ruta_carpeta_destino_soundswitch = valor2 + "/SoundSwitch/" # CARPETA DESTINO
                if os.path.exists(ruta_carpeta_origen_soundswitch) and os.path.isdir(ruta_carpeta_origen_soundswitch): # SI LA CARPETA ORIGEN EXISTE
                    proyects = os.listdir(ruta_carpeta_origen_soundswitch)
                    proyects_folders = [elem for elem in proyects if os.path.isdir(os.path.join(ruta_carpeta_origen_soundswitch))]
                    ruta_musicfile_origen_definitiva = ""
                    for folder in proyects_folders: # PARA CADA CARPETA DE PROYECTO SI HAY MÁS DE UNA CARPETA DE PROYECTO
                        ruta_proyecto = ruta_carpeta_origen_soundswitch + folder
                        carpetas = os.listdir(ruta_proyecto)
                        print(f'{ruta_proyecto}') 
                        archivos2 = [f for f in os.listdir(ruta_proyecto) if os.path.isfile(os.path.join(ruta_proyecto, f))] # ALMACEN DE LOS ARCHIVOS DE PROYECTO
                        for codigo_trackId in mytracks:
                            cursor1.execute('SELECT path FROM Track WHERE id = ?', codigo_trackId)
                            basic_path = cursor1.fetchone()
                            if basic_path:
                                ruta_musicfile_origen_texto = ''.join(basic_path)
                                if ruta_musicfile_origen_texto.startswith(".."):
                                    ruta_musicfile_origen_modificada = ruta_musicfile_origen_texto[2:]
                                else:
                                    ruta_musicfile_origen_modificada = "/Engine Library/" + ruta_musicfile_origen_texto
                                ruta_musicfile_origen_definitiva = valor + ruta_musicfile_origen_modificada # TENGO LA RUTA AL ARCHIVO DE AUDIO
                                ruta_soundswitch_destino_definitiva = valor2 + ruta_proyecto
                            proceso = subprocess.run(['mediainfo', ruta_musicfile_origen_definitiva], capture_output=True, text=True)
                            tag = 'SOUNDSWITCH_ID'
                            salida = proceso.stdout
                            patron = rf"{tag} *: *(.*)"
                            coincidencias = re.findall(patron, salida)
                            if coincidencias:
                                valor_tag = coincidencias[0].strip()
                                directorio_destino = (ruta_carpeta_destino_soundswitch + folder)
                                directorio_origen_automation_presets = (ruta_proyecto + '/automation_presets')
                                directorio_destino_automation_presets = (directorio_destino + '/automation_presets')
                                directorio_origen_recordable = (ruta_proyecto + '/recordable')
                                directorio_destino_recordable = (directorio_destino + '/recordable')
                                os.makedirs(directorio_destino, exist_ok=True)
                                try:
                                    shutil.copytree(directorio_origen_automation_presets, directorio_destino_automation_presets)
                                    shutil.copytree(directorio_origen_recordable, directorio_destino_recordable)
                                except FileExistsError:
                                    print(f"Procesando {folder} SoundSwitch file " + valor_tag)
                                except Exception as e:
                                    print(f"Ocurrió un error: {e}")
                                for proyect_files in os.listdir(ruta_proyecto):
                                    if proyect_files.startswith('SSAutoLoop'):
                                        ssautoloop_file_origen = os.path.join(ruta_proyecto, proyect_files)
                                        ssautoloop_file_destino = os.path.join(directorio_destino, proyect_files)
                                        shutil.copy(ssautoloop_file_origen, ssautoloop_file_destino)
                                    if proyect_files.endswith('.bin'):
                                        bin_file_origen = os.path.join(ruta_proyecto, proyect_files)
                                        bin_file_destino = os.path.join(directorio_destino, proyect_files)
                                        shutil.copy(bin_file_origen, bin_file_destino)
                                    if proyect_files.endswith('.backup'):
                                        backup_file_origen = os.path.join(ruta_proyecto, proyect_files)
                                        backup_file_destino = os.path.join(directorio_destino, proyect_files)
                                        shutil.copy(backup_file_origen, backup_file_destino)
                                    if proyect_files.startswith('.ssproj'):  # ARCHIVO OCULTO COPIAR PARA QUE FUNCIONE EN SOUNDSWITCH ENGINE STANDALONE MODE
                                        backup_file_origen = os.path.join(ruta_proyecto, proyect_files)
                                        backup_file_destino = os.path.join(directorio_destino, proyect_files)
                                        shutil.copy(backup_file_origen, backup_file_destino)
                                    if proyect_files.startswith(valor_tag):
                                        ss_file_origen = os.path.join(ruta_proyecto, proyect_files)
                                        ss_file_destino = os.path.join(directorio_destino, proyect_files)
                                        if os.path.exists(ss_file_destino):
                                            if filecmp.cmp(ss_file_origen, ss_file_destino, shallow=False):
                                                print(f'SoundSwitch file omited')
                                            else:
                                                shutil.copy(ss_file_origen, ss_file_destino)
                                        else:
                                            shutil.copy(ss_file_origen, ss_file_destino)
                                    etiqueta_barra2.config(text="SoundSwitch file " + valor_tag)
                                    etiqueta_barra.config(text="SOUNDSWITCH FILES...")
                                    progress_bar['value'] = m
                                    progress_bar.update_idletasks()
                                    m = m + 300/i
                else:
                    messagebox.showwarning("Advertencia", "No hay carpeta SoundSwitch para sincronizar.")

    # FIN DE LA EJECUCIÓN

        cursor1.close()
        cursor2.close()
        conexion.close()
        conexion2.close()
        progress_bar['value'] = 300
        button1.config(state='normal')
        etiqueta_barra2.config(text="Sincronización terminada")
        etiqueta_barra.config(text="¡CORRECTO!")
        messagebox.showinfo("Información", "Ejecución completada!")
        tree_left.bind('<ButtonRelease-1>', seleccionar_nodos_left)
        tree_right.bind('<ButtonRelease-1>', seleccionar_nodos_right)
        button1.config(state='normal')
        button2.config(state='disabled')
        button10.config(state='disabled')
        button4.config(state='disabled')
        button3.config(state='disabled')
        ruta = combo1.get()
        combo1.set(ruta)
        combo1.event_generate("<<ComboboxSelected>>")
        ruta2 = combo2.get()
        combo2.set(ruta2)
        combo2.event_generate("<<ComboboxSelected>>")
        progress_bar['value'] = 0
        etiqueta_barra.pack_forget()
        etiqueta_barra2.pack_forget()
        progress_bar.pack_forget()


# FUNCION ACTUALIZAR DATOS SI LA PLAYLIST EXISTE

################################################################################# NUEVO

def update_left_to_right(progress_bar, codigo, lista_para_sync):

    # CONFIGURACION GENERAL
    tree_left.bind('<ButtonRelease-1>', lambda e: "break")
    tree_right.bind('<ButtonRelease-1>', lambda e: "break")
    etiqueta_barra.pack(padx=10, pady=10)
    etiqueta_barra2.pack(padx=10, pady=10)
    progress_bar.pack(pady=20)
    if codigo:
        button1.config(state='disabled')
        button2.config(state='disabled')
        #button10.config(state='disabled')
        button4.config(state='disabled')
        #button3.config(state='disabled')
        button4.config(state='disabled')
        print(f'ACTUALIZANDO: {codigo}')  # Imprime la lista para verificar
        valor=combo1.get()
        valor2=combo2.get()
        # Formatear la ruta hasta la base de datos
        frase_origen=valor+"/Engine Library/Database2/m.db"
        frase_destino=valor2+"/Engine Library/Database2/m.db"
        conexion = sqlite3.connect(frase_origen)
        cursor1 = conexion.cursor()
        conexion2 = sqlite3.connect(frase_destino)
        cursor2 = conexion2.cursor()
        i = len(lista_para_sync)
        i = i*25000
        m = 300/i
        cursor2.execute('''INSERT INTO sqlite_sequence (name, seq) VALUES (?, ?)''', ('Track', 0))
        cursor2.execute('''INSERT INTO sqlite_sequence (name, seq) VALUES (?, ?)''', ('Playlist', 0))
        cursor2.execute('''INSERT INTO sqlite_sequence (name, seq) VALUES (?, ?)''', ('PlaylistEntity', 0))
        cursor2.execute('''INSERT INTO sqlite_sequence (name, seq) VALUES (?, ?)''', ('AlbumArt', 0))
        conexion2.commit()
#-----------------------------------------------------------------------------------------------------------------------------------------------

    # UPDATE PLAYLIST

        if codigo:
            print(f"PROGRESBAR 1 m: {m}")
            progress_bar['value'] = m
            progress_bar.update_idletasks()
            cursor1.execute('SELECT * FROM Playlist WHERE id = '+ codigo)
            cursor2.execute('SELECT * FROM Playlist WHERE id = '+ codigo)
            valores_origen = cursor1.fetchone()
            valores_destino = cursor2.fetchone()
            if valores_origen != valores_destino:
                id, title, parentListId, isPersisted, nextListId, lastEditTime, isExplicitlyExported = valores_origen
                cursor2.execute('''UPDATE sqlite_sequence SET seq = ? WHERE name = 'Playlist' ''', ('0',))
                conexion2.commit()
                id, title, parentListId, isPersisted, nextListId, lastEditTime, isExplicitlyExported = valores_origen
# TO DO
# CAMBIAR EL VALOR isPersisted a 1 PARA BASE DE DATOS DE LA CARPETA DE USUARIO. NO SE MUESTRAN LAS QUE VALEN 0

                cursor2.execute('''UPDATE Playlist SET title = ?, isPersisted = ?, lastEditTime = ?, isExplicitlyExported = ? WHERE id = ?''', (title, isPersisted, lastEditTime, isExplicitlyExported, id))
                conexion2.commit()
                progress_bar['value'] = m
                etiqueta_barra2.config(text="SINCRONIZANDO...")
                etiqueta_barra.config(text=("UPDATING PLAYLIST...", title))
                progress_bar.update_idletasks()
                m = m + 300/i
#------------------------------------------------------------------------------------------------------------------------------------

    # UPDATE PLAYLISTENTITY

        if codigo:
            codigo_lista_texto = "".join(str(num) for num in codigo)
            cursor1.execute('SELECT id FROM PlaylistAllChildren WHERE id = '+ codigo_lista_texto)
            es_padre = cursor1.fetchall()
            if not es_padre:
                cursor1.execute('SELECT * FROM PlaylistEntity WHERE listId = '+ codigo_lista_texto)
                todas_playlistentity = cursor1.fetchall()
                for entrada in todas_playlistentity:
                    progress_bar['value'] = m
                    progress_bar.update_idletasks()
                    m = m + 300/i
                    id, listId, trackId, databaseUuid, nextEntityId, membershipReference = entrada
                    cursor2.execute('''UPDATE OR IGNORE PlaylistEntity SET listId = ?, trackId = ?, databaseUuid = ?, nextEntityId = ?, membershipReference = ? WHERE id = ?''', (listId, trackId, databaseUuid, '0', membershipReference, id))
                etiqueta_barra2.config(text="SINCRONIZANDO...")
                etiqueta_barra.config(text="UPDATE PLAYLIST INFO...")
                conexion2.commit()
#-----------------------------------------------------------------------------------------------------------

#    # UPDATE TRACKS
                cursor2.execute('SELECT trackId FROM PlaylistEntity WHERE listId ='+ codigo_lista_texto)
                mytracks = cursor2.fetchall()
                for codigo_trackId in mytracks:
                    cursor2.execute('''UPDATE sqlite_sequence SET seq = ? WHERE name = 'Track' ''', ('0',)) # INICIALIZO A 0 EL CONTADOR DE CANCIONES #PARA QUE NO PRODUZCA ERROR DE ID RECICLADO
                    conexion2.commit()
                    codigo_texto = "".join(str(cod) for cod in codigo_trackId)
                    cursor1.execute('SELECT * FROM Track WHERE id = '+ codigo_texto)
                    todas_las_tracks = cursor1.fetchall()
                    for tracks_to_copy in todas_las_tracks:
                        id, playOrder, length, bpm, year, path, filename, bitrate, bpmAnalyzed, albumArtId, fileBytes, title, artist, album, genre, comment, label, composer, remixer, key, rating, albumArt, timeLastPlayed, isPlayed, fileType, isAnalyzed, dateCreated, dateAdded, isAvailable, isMetadataOfPackedTrackChanged, isPerfomanceDataOfPackedTrackChanged, playedIndicator, isMetadataImported, pdbImportKey, streamingSource, uri, isBeatGridLocked, originDAtabaseUuid, originTrackId, streamingFlags, explicitLyrics, lastEditTime = tracks_to_copy
                        cursor2.execute('''UPDATE Track SET id = ?, playOrder = ?, length = ?, bpm = ?, year = ?, path = ?, filename = ?, bitrate = ?, bpmAnalyzed = ?, albumArtId = ?, fileBytes = ?, title = ?, artist = ?, album = ?, genre = ?, comment = ?, label = ?, composer = ?, remixer = ?, key = ?, rating = ?, albumArt = ?, timeLastPlayed = ?, isPlayed = ?, fileType = ?, isAnalyzed = ?, dateCreated = ?, dateAdded = ?, isAvailable = ?, isMetadataOfPackedTrackChanged = ?, isPerfomanceDataOfPackedTrackChanged = ?, playedIndicator = ?, isMetadataImported = ?, pdbImportKey = ?, streamingSource = ?, uri = ?, isBeatGridLocked = ?, originDAtabaseUuid = ?, originTrackId = ?, streamingFlags = ?, explicitLyrics = ?, lastEditTime = ? WHERE id = ?''', (id, playOrder, length, bpm, year, path, filename, bitrate, bpmAnalyzed, albumArtId, fileBytes, title, artist, album, genre, comment, label, composer, remixer, key, rating, albumArt, timeLastPlayed, isPlayed, fileType, isAnalyzed, dateCreated, dateAdded, isAvailable, isMetadataOfPackedTrackChanged, isPerfomanceDataOfPackedTrackChanged, playedIndicator, isMetadataImported, pdbImportKey, streamingSource, uri, isBeatGridLocked, originDAtabaseUuid, originTrackId, streamingFlags, explicitLyrics, lastEditTime, id))
                        etiqueta_barra2.config(text="SINCRONIZANDO...")
                        etiqueta_barra.config(text="UPDATE TRACKS...")
                        progress_bar['value'] = m
                        progress_bar.update_idletasks()
                        m = m + 300/i

##----------------------------------------------------------------------------------------------------------------------------------------------------
#
#    # UPDATE PLAYLISTENTITY ADITIONAL INFO
#
                        cursor1.execute('SELECT * FROM PlaylistEntity WHERE trackId = ?', (id,))
                        inserts = cursor1.fetchall()
                        for lines in inserts:
                            id2, listId2, trackId2, databaseUuid2, nextEntityId2, membershipReference2 = lines
                            if listId2 != listId:
                                cursor2.execute('''UPDATE OR IGNORE PlaylistEntity SET listId = ?, trackId = ?, databaseUuid = ?, nextEntityId = ?, membershipReference = ? WHERE id = ?''', (listId2, trackId2, databaseUuid2, '0', membershipReference2, id))
                                progress_bar['value'] = m
                                progress_bar.update_idletasks()
                                m = m + 300/i
                                etiqueta_barra2.config(text="SINCRONIZANDO...")
                                etiqueta_barra.config(text=('UPDATE Playlist info '+filename))
                conexion2.commit()
                progress_bar['value'] = m
                progress_bar.update_idletasks()
                m = m + 300/i

##-------------------------------------------------------------------------------------------------------------

#    # UPDATE PERFORMANCEDATA

                for codigo_trackId in mytracks:
                    codigo_texto = "".join(str(codi) for codi in codigo_trackId)
                    cursor1.execute('SELECT * FROM PerformanceData WHERE trackId = '+ codigo_texto)
                    todas_las_tracks = cursor1.fetchall()
                    for data_to_copy in todas_las_tracks:
                        trackId, trackData, overviewWaveFormData, beatData, quickCues, loops, thirdPartySourceId, activeOnLoadLoops = data_to_copy
                        cursor2.execute('''UPDATE PerformanceData SET trackData = ?, overviewWaveFormData = ?, beatData = ?, quickCues = ?, loops = ?, thirdPartySourceId = ?, activeOnLoadLoops = ? WHERE trackId = ?''', (trackData, overviewWaveFormData, beatData, quickCues, loops, thirdPartySourceId, activeOnLoadLoops, trackId))
                        etiqueta_barra2.config(text="SINCRONIZANDO...")
                        etiqueta_barra.config(text="UPDATE PERFORMANCE DATA...")
                conexion2.commit()
                progress_bar['value'] = m
                progress_bar.update_idletasks()
                m = m + 300/i
#-----------------------------------------------------------------------------------------------------------

#    # UPDATE ALBUMART

                for codigo_trackId in mytracks:
                    codigo_texto = "".join(str(cod) for cod in codigo_trackId)
                    cursor1.execute('SELECT albumArtId FROM Track WHERE id = '+ codigo_texto)
                    codigo_Art = cursor1.fetchone()
                    if codigo_Art:
                        codigo_Art_texto = "".join(str(go) for go in codigo_Art)
                        cursor1.execute('SELECT * FROM AlbumArt WHERE id = '+ codigo_Art_texto)
                        album_data = cursor1.fetchall()
                        for data_to_copy in album_data:
                            id, hash, albumArt = data_to_copy
                            cursor2.execute('''UPDATE AlbumArt SET id = ?, hash = ?, albumArt = ? WHERE id = ?''', (id, hash, albumArt, id))
                            etiqueta_barra2.config(text="SINCRONIZANDO...")
                            etiqueta_barra.config(text="UPDATE ALBUMART...")
                conexion2.commit()
                progress_bar['value'] = m
                progress_bar.update_idletasks()
                m = m + 300/i
#--------------------------------------------------------------------------------------------------------------
#
#    # UPDATE LOS ARCHIVOS DE MUSICA EN LA RUTA DE DESTINO
#
                for codigo_trackId in mytracks:
                    cursor1.execute('SELECT path FROM Track WHERE id = ?',codigo_trackId)
                    ruta_archivo_origen = cursor1.fetchone()
                    print(f'UPDATE CODIGO_TRACKID:    {codigo_trackId}')
                    if ruta_archivo_origen:
                        ruta_archivo_origen_texto = ''.join(ruta_archivo_origen)

						# REFERENCIA A RUTA DE ARCHIVO
                        if ruta_archivo_origen_texto.startswith('..'):
                            ruta_archivo_origen_modificada = ruta_archivo_origen_texto[2:]
                        else:
                            ruta_archivo_origen_modificada = "/Engine Library/" + ruta_archivo_origen_texto # ¿ES CORRECTO PARA CUALQUIER RUTA A ARCHIVO??

                        ruta_origen_definitiva = valor + ruta_archivo_origen_modificada
                        ruta_destino_definitiva = valor2 + ruta_archivo_origen_modificada
                        etiqueta_barra2.config(text=ruta_archivo_origen_modificada)
                        etiqueta_barra.config(text="UPDATE ARCHIVOS DE MÚSICA...")
                        os.makedirs(os.path.dirname(ruta_destino_definitiva), exist_ok=True)
                        try:
                            if os.path.exists(ruta_destino_definitiva):
                                if filecmp.cmp(ruta_origen_definitiva, ruta_destino_definitiva, shallow=False):
                                    print(f'OMITIENDO: {ruta_origen_definitiva}')
                                else:
                                    shutil.copy(ruta_origen_definitiva, ruta_destino_definitiva)
                                    progress_bar['value'] = m
                                    progress_bar.update_idletasks()
                                    m = m + 30/i
                            else:
                                shutil.copy(ruta_origen_definitiva, ruta_destino_definitiva)
                                progress_bar['value'] = m
                                progress_bar.update_idletasks()
                                m = m + 30/i
                        except FileNotFoundError:
                            messagebox.showwarning("Advertencia", "No se han encontrado los archivos de música en origen.")
                            break
                        except PermissionError:
                            messagebox.showwarning("Advertencia", "No tiene permisos para escribir en destino.")
                            break
                        except Exception as e:
                            messagebox.showwarning("Advertencia", "Error inesperado.")
                            break
## ------------------------------------------------------------------------------------------------------------------------
#
#    # UPDATE STEMS
#
                ruta_carpeta_stems = valor + "/Engine Library/Stems/"
                ruta_carpeta_destino_stems = valor2 + "/Engine Library/Stems/"
                if os.path.exists(ruta_carpeta_stems) and os.path.isdir(ruta_carpeta_stems):
                    for codigo_trackId in mytracks:
                        cursor1.execute('SELECT id FROM Track WHERE id = ?', codigo_trackId)
                        codigos_para_stems = cursor1.fetchall()
                        archivos = [f for f in os.listdir(ruta_carpeta_stems) if os.path.isfile(os.path.join(ruta_carpeta_stems, f))]
                        for nombre in archivos:
                            nombre_hasta_espacio = nombre.split(' ')[0]
                            codigo_stm = "".join(str(stm) for stm in codigo_trackId)
                            if nombre_hasta_espacio == codigo_stm:
                                os.makedirs(os.path.dirname(ruta_carpeta_destino_stems), exist_ok=True)
                                try:
                                    if os.path.exists(ruta_carpeta_destino_stems + nombre):
                                        if filecmp.cmp(ruta_carpeta_stems + nombre, ruta_carpeta_destino_stems + nombre):
                                            print(f'Omitiendo STEM')
                                        else:
                                            shutil.copy(ruta_carpeta_stems + nombre, ruta_carpeta_destino_stems + nombre)
                                    else:
                                        shutil.copy(ruta_carpeta_stems + nombre, ruta_carpeta_destino_stems + nombre)
                                except FileNotFoundError:
                                    messagebox.showwarning("Advertencia", "No se han encontrado el archivo STEM en origen.")
                                    break
                                except PermissionError:
                                    messagebox.showwarning("Advertencia", "No tiene permisos para escribir en destino.")
                                    break
                                except Exception as e:
                                    if e.errno == 28:
                                        messagebox.showwarning("ERROR", "Error DISCO LLENO.")
                                        break
                                    messagebox.showwarning("Advertencia", "Error inesperado.")
                                    break
                            etiqueta_barra2.config(text="STEM FILE "+ nombre)
                            etiqueta_barra.config(text="UPDATE STEMS...")
                            progress_bar['value'] = m
                            progress_bar.update_idletasks()
                            m = m + 300/i
                else:
                    messagebox.showwarning("Advertencia", "No hay carpeta STEMS para sincronizar.")
##-----------------------------------------------------------------------------------------------------------------------------------------------
#
#    # UPDATE SOUNDSWITCH
#
                ruta_carpeta_origen_soundswitch = valor + "/SoundSwitch/" # CARPETA ORIGEN
                ruta_carpeta_destino_soundswitch = valor2 + "/SoundSwitch/" # CARPETA DESTINO
                if os.path.exists(ruta_carpeta_origen_soundswitch) and os.path.isdir(ruta_carpeta_origen_soundswitch): # SI LA CARPETA ORIGEN EXISTE
                    proyects = os.listdir(ruta_carpeta_origen_soundswitch)
                    proyects_folders = [elem for elem in proyects if os.path.isdir(os.path.join(ruta_carpeta_origen_soundswitch))]
                    for folder in proyects_folders: # PARA CADA CARPETA DE PROYECTO
                        ruta_proyecto = ruta_carpeta_origen_soundswitch + folder
                        carpetas = os.listdir(ruta_proyecto)
                        archivos2 = [f for f in os.listdir(ruta_proyecto) if os.path.isfile(os.path.join(ruta_proyecto, f))] # ALMACEN DE LOS ARCHIVOS DE PROYECTO
                        for codigo_trackId in mytracks:
                            cursor1.execute('SELECT path FROM Track WHERE id = ?', codigo_trackId)
                            basic_path = cursor1.fetchone()
                            if basic_path:
                                ruta_musicfile_origen_texto = ''.join(basic_path)
                                if ruta_musicfile_origen_texto.startswith(".."):
                                    ruta_musicfile_origen_modificada = ruta_musicfile_origen_texto[2:]
                                else:
                                    ruta_musicfile_origen_modificada = "/Engine Library/" + ruta_musicfile_origen_texto

                                ruta_musicfile_origen_definitiva = valor + ruta_musicfile_origen_modificada # TENGO LA RUTA AL ARCHIVO DE AUDIO
                                ruta_soundswitch_destino_definitiva = valor2 + ruta_proyecto
                                proceso = subprocess.run(['mediainfo', ruta_musicfile_origen_definitiva], capture_output=True, text=True)
                                tag = 'SOUNDSWITCH_ID'
                                salida = proceso.stdout
                                patron = rf"{tag} *: *(.*)"
                                coincidencias = re.findall(patron, salida)
                                if coincidencias:
                                    valor_tag = coincidencias[0].strip()
                                    directorio_destino = (ruta_carpeta_destino_soundswitch + folder)
                                    directorio_origen_automation_presets = (ruta_proyecto + '/automation_presets')
                                    directorio_destino_automation_presets = (directorio_destino + '/automation_presets')
                                    directorio_origen_recordable = (ruta_proyecto + '/recordable')
                                    directorio_destino_recordable = (directorio_destino + '/recordable')
                                    os.makedirs(directorio_destino, exist_ok=True)
                                    try:
                                        shutil.copytree(directorio_origen_automation_presets, directorio_destino_automation_presets)
                                        shutil.copytree(directorio_origen_recordable, directorio_destino_recordable)
                                    except FileExistsError:
                                        print(f"Procesando {folder} soundswitch file " + valor_tag)
                                    except Exception as e:
                                        print(f"Ocurrió un error: {e}")
                                    for proyect_files in os.listdir(ruta_proyecto):
                                        if proyect_files.startswith('SSAutoLoop'):
                                            ssautoloop_file_origen = os.path.join(ruta_proyecto, proyect_files)
                                            ssautoloop_file_destino = os.path.join(directorio_destino, proyect_files)
                                            shutil.copy(ssautoloop_file_origen, ssautoloop_file_destino)
                                        if proyect_files.endswith('.bin'):
                                            bin_file_origen = os.path.join(ruta_proyecto, proyect_files)
                                            bin_file_destino = os.path.join(directorio_destino, proyect_files)
                                            shutil.copy(bin_file_origen, bin_file_destino)
                                        if proyect_files.endswith('.backup'):
                                            backup_file_origen = os.path.join(ruta_proyecto, proyect_files)
                                            backup_file_destino = os.path.join(directorio_destino, proyect_files)
                                            shutil.copy(backup_file_origen, backup_file_destino)
                                        if proyect_files.startswith('.ssproj'):  # ARCHIVO OCULTO COPIAR PARA QUE FUNCIONE EN SOUNDSWITCH ENGINE STANDALONE MODE
                                            backup_file_origen = os.path.join(ruta_proyecto, proyect_files)
                                            backup_file_destino = os.path.join(directorio_destino, proyect_files)
                                            shutil.copy(backup_file_origen, backup_file_destino)
                                        if proyect_files.startswith(valor_tag):
                                            ss_file_origen = os.path.join(ruta_proyecto, proyect_files)
                                            ss_file_destino = os.path.join(directorio_destino, proyect_files)
                                            if os.path.exists(ss_file_destino):
                                                if filecmp.cmp(ss_file_origen, ss_file_destino, shallow=False):
                                                    print('Omitiendo SoundSwitch File')
                                                else:
                                                    shutil.copy(ss_file_origen, ss_file_destino)
                                            else:
                                                shutil.copy(ss_file_origen, ss_file_destino)
                                        etiqueta_barra2.config(text="SoundSwitch file " + valor_tag)
                                        etiqueta_barra.config(text="UPDATE SOUNDSWITCH FILES...")
                                        progress_bar['value'] = m
                                        progress_bar.update_idletasks()
                                        m = m + 300/i
                else:
                    messagebox.showwarning("Advertencia", "No hay carpeta SoundSwitch para sincronizar.")

#------------------------------------------------------------------------------------


#--------------------- FUNCION PARA CREAR LA VENTANA PRINCIPAL -----------------------
# Crear la ventana principal
def crear_ventana():
    global combo1
    global combo2
    global etiqueta_izquierda
    global etiqueta_derecha
    global etiqueta_barra
    global etiqueta_barra2
    global frame_para_combo1
    global frame_para_texto
    global main_frame
    global tree_left
    global tree_right
    global button1
    global button2
    global button3
    global button4
    global button10
    global resultados1
    global resultados2
    global progress_var
    global ventana
    global databaseUuid

    ventana = tk.Tk()
    ventana.title("Engine DJ SYNCHRONIZE FOR LINUX")
    ventana.geometry("1280x800")  # Ancho: 800 píxeles, Alto: 400 píxeles

# Crear un frame para los combos
    frame_para_combo1 = ttk.Frame(ventana)
    frame_para_combo1.pack(fill=tk.X, expand=False)

# Crear frame para el texto
    frame_para_texto = ttk.Frame(ventana)
    frame_para_texto.pack(fill=tk.X, expand=False)

# Crear frame para los botones de procesar
    frame_para_botones = ttk.Frame(ventana)
    frame_para_botones.pack(fill=tk.X, expand=False)

# Crear un frame para los treeviews
    main_frame = ttk.Frame(ventana)
    main_frame.pack(fill='both', expand=True)

# Crear un frame para la barra
    frame_para_barra = ttk.Frame(ventana)
    frame_para_barra.pack(fill=tk.X, expand=False)

# Crear los Combobox en el primer frame
    combo1 = ttk.Combobox(frame_para_combo1, values=unidades_usb, width=50)
    combo1.pack(padx=10, pady=10, side=tk.LEFT, anchor="w")
    combo1.bind("<<ComboboxSelected>>", on_combobox_selected)

    combo2 = ttk.Combobox(frame_para_combo1, values=unidades_usb, width=50)
    combo2.pack(padx=10, pady=10, anchor="e")
    combo2.bind("<<ComboboxSelected>>", on_combobox2_selected)

# Crear los campos de texto con la información del USB seleccionado en el combobox
    etiqueta_izquierda = tk.Label(frame_para_texto, text="Selecciona una BD", font=("Arial", 10))
    etiqueta_izquierda.pack(side=tk.LEFT, padx=10, pady=10, anchor="w")
    etiqueta_derecha = tk.Label(frame_para_texto, text="Selecciona una BD", font=("Arial", 10))
    etiqueta_derecha.pack(padx=10, pady=10, anchor="e")

    button2 = tk.Button(frame_para_botones, state='disabled', text="PROCESAR CAMBIOS", command=guardar_seleccion_left)
    button2.pack(side=tk.LEFT, padx=10, pady=5, anchor="w")
    button10 = tk.Button(frame_para_botones, state='disabled', text="VER TRACKS", command=mostrar_ventana_tracks_left) # AJUSTAR PARA VER EN OTRA VENTANA LAS TRAKS DE LOS NODOS
    button10.pack(side=tk.LEFT, padx=10, pady=5, anchor="e") 
    button3 = tk.Button(frame_para_botones, state='disabled', text="VER TRACKS", command=mostrar_ventana_tracks_right) # AJUSTAR PARA VER EN OTRA VENTANA LAS TRAKS DE LOS NODOS
    button3.pack(side=tk.RIGHT, padx=10, pady=5, anchor="e")

# Crear el Treeview de la izquierda en el segundo frame
    tree_left = ttk.Treeview(main_frame, height=10, selectmode='extended')
    tree_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    tree_left.bind('<ButtonRelease-1>', seleccionar_nodos_left)

# Crear el frame central
    center_frame = tk.Frame(main_frame)
    center_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

# Crear el Treeview de la derecha
    tree_right = ttk.Treeview(main_frame, height=10)
    tree_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    tree_right.bind('<ButtonRelease-1>', seleccionar_nodos_right)

# Crear el botón
    button1 = tk.Button(center_frame, text="Recargar Unidades", command=recargar_unidades)
    button1.pack(pady=5)

    etiqueta_barra = tk.Label(frame_para_barra, text="SINCRONIZANDO...", font=("Arial", 15))
    etiqueta_barra2 = tk.Label(frame_para_barra, text="TERMINADO", font=("Arial", 15))
    # -------------- OCULTAR ETIQUETA
    etiqueta_barra.pack_forget()  # Oculta el Label
    etiqueta_barra2.pack_forget()

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(frame_para_barra, orient='horizontal', maximum=300, length=500, mode='determinate')
    progress_bar.pack_forget()

    button4 = tk.Button(center_frame, text="SINCRONIZAR ==>", state='disabled', command=lambda: iniciar_sincronizacion_left_to_right(progress_bar))
    button4.pack(pady=5)
    button5 = tk.Button(center_frame, text="SALIR", state='active', command=ventana.destroy)
    button5.pack(side=tk.BOTTOM, pady=5)

    ventana.mainloop()

# --------------------------------------------------------------------------------------------

# Ejecutar la función principal
if __name__ == "__main__":
    crear_ventana()



