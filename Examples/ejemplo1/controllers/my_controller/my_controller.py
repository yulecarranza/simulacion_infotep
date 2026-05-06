from controller import Supervisor, Keyboard
from sympy import Matrix, cos, sin
import math

# --- Inicialización ---
supervisor = Supervisor()
paso_tiempo = int(supervisor.getBasicTimeStep())

# Obtener los nodos del humanoide y de la botella
nodo_peaton = supervisor.getFromDef("pedestrian1")
nodo_botella = supervisor.getFromDef("beer_bottle")

if nodo_peaton is None or nodo_botella is None:
    print("ERROR: No se encontraron los nodos (pedestrian1 o beer bottle)")

# Parámetros de movimiento
TAMANO_PASO = 0.05          # metros por paso
PASO_ANGULO = math.pi / 36  # 5 grados por paso

# --- Offset de la botella respecto a la mano/peatón ---
# Define aquí qué tan lejos de la base del humanoide está la mano
# (Ajusta estos valores según la posición inicial que le des en Webots)
OFFSET_X = 0.0
OFFSET_Y = -0.3  # Aproximadamente a un lado del cuerpo
OFFSET_Z = -0.5   # Altura de la mano

# Activar teclado
teclado = supervisor.getKeyboard()
teclado.enable(paso_tiempo)

# ---------------------------------------------------------------
# Desplazamiento en X o Y del sistema de referencia del humanoide
# ---------------------------------------------------------------
def trasladar(nodo, dx_local, dy_local):
    campo_traslacion = nodo.getField("translation")
    pos = campo_traslacion.getSFVec3f()
    P_vieja = Matrix([pos[0], pos[1], pos[2]])

    # Ángulo actual del humanoide
    campo_rotacion = nodo.getField("rotation")
    _, _, _, angulo = campo_rotacion.getSFRotation()

    R_z = Matrix([
        [cos(angulo), -sin(angulo), 0],
        [sin(angulo),  cos(angulo), 0],
        [          0,            0, 1]
    ])

    d_local = Matrix([dx_local, dy_local, 0])
    d_mundial = R_z * d_local
    P_nueva = P_vieja + d_mundial

    campo_traslacion.setSFVec3f([
        float(P_nueva[0]),
        float(P_nueva[1]),
        float(P_nueva[2])
    ])

# ---------------------------------------------------------------
# Rotación alrededor de Z (horario / antihorario)
# ---------------------------------------------------------------
def rotar_z(nodo, delta_angulo):
    campo_rotacion = nodo.getField("rotation")
    _, _, _, angulo = campo_rotacion.getSFRotation()
    campo_rotacion.setSFRotation([0, 0, 1, angulo + delta_angulo])

# ---------------------------------------------------------------
# Actualizar la posición de la botella en la mano
# ---------------------------------------------------------------
def actualizar_posicion_botella(peaton_nodo, botella_nodo):
    # Obtener posición y ángulo del humanoide
    campo_traslacion = peaton_nodo.getField("translation")
    pos = campo_traslacion.getSFVec3f()
    
    campo_rotacion = peaton_nodo.getField("rotation")
    _, _, _, angulo = campo_rotacion.getSFRotation()

    # Matriz de rotación del humanoide
    R_z = Matrix([
        [cos(angulo), -sin(angulo), 0],
        [sin(angulo),  cos(angulo), 0],
        [          0,            0, 1]
    ])

    # Offset de la botella en el sistema local del humanoide
    offset_local = Matrix([OFFSET_X, OFFSET_Y, OFFSET_Z])
    offset_mundial = R_z * offset_local

    # Nueva posición absoluta de la botella
    pos_botella_x = pos[0] + float(offset_mundial[0])
    pos_botella_y = pos[1] + float(offset_mundial[1])
    pos_botella_z = pos[2] + float(offset_mundial[2])

    # Aplicar al nodo de la botella
    campo_botella_traslacion = botella_nodo.getField("translation")
    campo_botella_traslacion.setSFVec3f([pos_botella_x, pos_botella_y, pos_botella_z])

    # Sincronizar la rotación para que apunte en la misma dirección
    campo_botella_rotacion = botella_nodo.getField("rotation")
    campo_botella_rotacion.setSFRotation([0, 0, 1, angulo])

# ---------------------------------------------------------------
# Instrucciones en consola
# ---------------------------------------------------------------
print("=== Control de teclado ===")
print("↑ / ↓  → Mover adelante / atrás     (eje X local)")
print("← / →  → Mover izquierda / derecha  (eje Y local)")
print("Q / E  → Rotar antihorario / horario (alrededor de Z)")
print("==========================")

# ---------------------------------------------------------------
# Bucle principal - Tiempo - Simulación
# ---------------------------------------------------------------
while supervisor.step(paso_tiempo) != -1:

    # Mantener siempre la botella en la mano antes de verificar el teclado
    if nodo_peaton is not None and nodo_botella is not None:
        actualizar_posicion_botella(nodo_peaton, nodo_botella)

    tecla = teclado.getKey()

    if nodo_peaton is not None and tecla != -1:

        # --- Traslación en eje X ---
        if tecla == Keyboard.UP:
            print("Adelante", end='\r')
            trasladar(nodo_peaton, TAMANO_PASO, 0.0)

        elif tecla == Keyboard.DOWN:
            print("Atras", end='\r')
            trasladar(nodo_peaton, -TAMANO_PASO, 0.0)

        # --- Traslación en eje Y ---
        elif tecla == Keyboard.LEFT:
            print("Izquierda", end='\r')
            trasladar(nodo_peaton, 0.0, TAMANO_PASO)

        elif tecla == Keyboard.RIGHT:
            print("Derecha", end='\r')
            trasladar(nodo_peaton, 0.0, -TAMANO_PASO)

        # --- Rotación alrededor de Z ---
        elif tecla == ord('Q'):
            print("Rotar Antihorario", end='\r')
            rotar_z(nodo_peaton, PASO_ANGULO)

        elif tecla == ord('E'):
            print("Rotar Horario", end='\r')
            rotar_z(nodo_peaton, -PASO_ANGULO)