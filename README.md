# Control de Humanoide y Sincronización de Objeto (BeerBottle) en Webots

Este proyecto implementa un controlador de tipo **Supervisor** para un robot humanoide (`pedestrian1`) en el simulador Webots. El objetivo principal es permitir el desplazamiento del humanoide mediante el teclado, asegurando que un objeto externo (`beer_bottle`) permanezca rígidamente vinculado a su mano derecha mediante transformaciones matriciales.

---

## 1. Implementación del Entorno

Para cumplir con los requerimientos de la práctica, se realizaron las siguientes acciones en la escena:

*   **Adición de Nodo**: Se integró un nodo de tipo `BeerBottle` desde la biblioteca de objetos de Webots (`nodos/webots projects/objects/beerbottle`).
*   **Identificación por DEF**: Se asignó el nombre DEF `beer_bottle` al objeto para poder manipular su campo de traslación y rotación desde el controlador.
*   **Posicionamiento Inicial**: Se ubicó manualmente la botella cerca de la mano derecha del humanoide para establecer los valores de *offset* iniciales.

---

## 2. Razonamiento Matemático y Algebraico

El núcleo del proyecto consiste en mantener la botella en la mano del peatón independientemente de su movimiento o rotación. Dado que la botella no es un nodo hijo del humanoide, se aplicó **álgebra de sistemas de referencia**.

### i. Definición del Vector de Offset
Se definió un vector constante que representa la posición de la mano respecto al centro de masa del humanoide en su sistema de coordenadas local:
*   `OFFSET_X = 0.0`
*   `OFFSET_Y = -0.3` (Hacia la derecha del cuerpo)
*   `OFFSET_Z = -0.5` (Altura de la mano)

### ii. Transformación de Coordenadas (Local a Global)
Para que el desplazamiento sea coherente cuando el humanoide gira, el vector de offset debe ser rotado por la misma magnitud que el cuerpo. Se utilizó una **Matriz de Rotación en Z ($R_z$)** para transformar el offset local a coordenadas mundiales:

$$R_z = \begin{bmatrix} \cos(\theta) & -\sin(\theta) & 0 \\ \sin(\theta) & \cos(\theta) & 0 \\ 0 & 0 & 1 \end{bmatrix}$$

En el código, el cálculo se realiza así:
`pos_botella_mundial = pos_peaton_global + (R_z * offset_local)`.

### iii. Sincronización de Rotación
Para que la botella mantenga la misma orientación que el humanoide, se extrae el ángulo de rotación $\theta$ del nodo `pedestrian1` y se aplica al nodo `beer_bottle` en cada paso de la simulación, manteniendo ambos sistemas de referencia alineados.

