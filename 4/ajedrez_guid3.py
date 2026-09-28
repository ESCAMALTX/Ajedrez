import tkinter as tk
import chess
import chess.engine

STOCKFISH_PATH = "C:\\Users\\escam\\Downloads\\stockfish-windows-x86-64-avx2\\stockfish\\d.exe"

engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

board = chess.Board()

SIZE = 70
OFFSET = 30

selected_square = None
best_move = None
mi_color = chess.WHITE

pieza_unicode = {
"P": "♙",
"R": "♖",
"N": "♘",
"B": "♗",
"Q": "♕",
"K": "♔",
"p": "♟",
"r": "♜",
"n": "♞",
"b": "♝",
"q": "♛",
"k": "♚"
}

piezas_mov = {
"N":"♘",
"B":"♗",
"R":"♖",
"Q":"♕",
"K":"♔"
}

def elegir_color():

    global mi_color

    ventana = tk.Toplevel()
    ventana.title("Elegir color")

    tk.Label(ventana,text="¿Qué color juegas?",font=("Arial",12)).pack(pady=10)

    def blancas():
        global mi_color
        mi_color = chess.WHITE
        ventana.destroy()

    def negras():
        global mi_color
        mi_color = chess.BLACK
        ventana.destroy()

    tk.Button(ventana,text="Blancas",width=10,command=blancas).pack(pady=5)
    tk.Button(ventana,text="Negras",width=10,command=negras).pack(pady=5)

    root.wait_window(ventana)

def elegir_coronacion():

    ventana = tk.Toplevel()
    ventana.title("Coronación")

    pieza = tk.IntVar()

    tk.Label(ventana,text="Elige pieza",font=("Arial",12)).pack(pady=10)

    def elegir(p):
        pieza.set(p)
        ventana.destroy()

    tk.Button(ventana,text="♕ Reina",width=10,command=lambda:elegir(chess.QUEEN)).pack(pady=3)
    tk.Button(ventana,text="♖ Torre",width=10,command=lambda:elegir(chess.ROOK)).pack(pady=3)
    tk.Button(ventana,text="♗ Alfil",width=10,command=lambda:elegir(chess.BISHOP)).pack(pady=3)
    tk.Button(ventana,text="♘ Caballo",width=10,command=lambda:elegir(chess.KNIGHT)).pack(pady=3)

    root.wait_window(ventana)

    return pieza.get()


def analizar():

    global best_move

    info = engine.analyse(board, chess.engine.Limit(depth=18))

    score = info["score"].white()

    if score.is_mate():
        evaluacion = f"Mate en {score.mate()}"
    else:
        evaluacion = f"{score.score()/100:.2f}"

    best_move = info["pv"][0]

    mejor = board.san(best_move)

    for letra in piezas_mov:
        mejor = mejor.replace(letra, piezas_mov[letra])

    texto.set(f"Mejor jugada: {mejor} | Eval: {evaluacion}")

    dibujar_tablero()


def dibujar_tablero():

    canvas.delete("all")

    colors = ["#FFFFFF", "#1EFF00"]

    for row in range(8):
        for col in range(8):

            if mi_color == chess.WHITE:
                square = chess.square(col, 7-row)
            else:
                square = chess.square(7-col, row)

            color = colors[(row + col) % 2]

            x1 = OFFSET + col * SIZE
            y1 = OFFSET + row * SIZE
            x2 = x1 + SIZE
            y2 = y1 + SIZE

            if selected_square == square:
                color = "#F7EC59"

            canvas.create_rectangle(x1,y1,x2,y2,fill=color)

            piece = board.piece_at(square)

            if piece:

                canvas.create_text(
                    x1 + SIZE/2,
                    y1 + SIZE/2,
                    text=pieza_unicode[piece.symbol()],
                    font=("Arial",36)
                )

    if selected_square is not None:

        for move in board.legal_moves:

            if move.from_square == selected_square:

                col = chess.square_file(move.to_square)
                row = 7 - chess.square_rank(move.to_square)

                if mi_color == chess.BLACK:
                    col = 7 - col
                    row = 7 - row

                x = OFFSET + col * SIZE + SIZE/2
                y = OFFSET + row * SIZE + SIZE/2

                canvas.create_oval(x-8,y-8,x+8,y+8,fill="black")

    if best_move:

        c1 = chess.square_file(best_move.from_square)
        r1 = 7 - chess.square_rank(best_move.from_square)

        c2 = chess.square_file(best_move.to_square)
        r2 = 7 - chess.square_rank(best_move.to_square)

        if mi_color == chess.BLACK:
            c1 = 7 - c1
            r1 = 7 - r1
            c2 = 7 - c2
            r2 = 7 - r2

        x1 = OFFSET + c1 * SIZE + SIZE/2
        y1 = OFFSET + r1 * SIZE + SIZE/2
        x2 = OFFSET + c2 * SIZE + SIZE/2
        y2 = OFFSET + r2 * SIZE + SIZE/2

        canvas.create_line(
            x1,y1,x2,y2,
            width=4,
            arrow=tk.LAST,
            fill="blue"
        )

    letras = "abcdefgh"
    for i in range(8):

        letra = letras[i] if mi_color == chess.WHITE else letras[7-i]

        canvas.create_text(
            OFFSET + i * SIZE + SIZE/2,
            OFFSET + 8 * SIZE + 12,
            text=letra,
            font=("Arial",12)
        )

    for i in range(8):

        numero = str(8-i) if mi_color == chess.WHITE else str(i+1)

        canvas.create_text(
            OFFSET - 10,
            OFFSET + i * SIZE + SIZE/2,
            text=numero,
            font=("Arial",12)
        )


def click(event):

    global selected_square

    col = (event.x - OFFSET) // SIZE
    row = (event.y - OFFSET) // SIZE

    if col < 0 or col > 7 or row < 0 or row > 7:
        return

    if mi_color == chess.WHITE:
        square = chess.square(col, 7-row)
    else:
        square = chess.square(7-col, row)

    if selected_square is None:

        selected_square = square

    else:

        pieza = board.piece_at(selected_square)

        # Detectar coronación de peón
        if pieza and pieza.piece_type == chess.PAWN:

            fila = chess.square_rank(square)

            if fila == 7 or fila == 0:

                promo = elegir_coronacion()

                # Si el usuario cerró la ventana
                if promo is None or promo == "":
                    selected_square = None
                    dibujar_tablero()
                    return

                move = chess.Move(selected_square, square, promotion=promo)

            else:
                move = chess.Move(selected_square, square)

        else:
            move = chess.Move(selected_square, square)

        if move in board.legal_moves:

            board.push(move)
            analizar()

        selected_square = None

    dibujar_tablero()


root = tk.Tk()
root.title("Ajedrez PRO")

canvas = tk.Canvas(root,width=SIZE*8 + OFFSET*2,height=SIZE*8 + OFFSET*2)
canvas.pack()

canvas.bind("<Button-1>",click)

texto = tk.StringVar()
label = tk.Label(root,textvariable=texto,font=("Arial",14))
label.pack()

elegir_color()

analizar()
dibujar_tablero()

root.mainloop()

engine.quit()