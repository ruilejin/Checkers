import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
from Algo import Checkers,Poss

class APP:
    
    def __init__(self):
        super().__init__()
        self.game = Checkers(CHECKER_SIZE)
        self.pre = [self.game.getBoard()]
        self.prePtr = 0
        self.maxDepth =  MAX_DEPTH.get()
        self.player = STARTING_PLAYER
        if self.player == Checkers.WHITE:
            
            self.game.minimaxPlay(1-self.player, maxDepth=self.maxDepth, evaluate=EVALUATION_FUNCTION, enablePrint=False)
            
            self.pre = [self.game.getBoard()]
        
        self.lastX = None
        self.lastY = None
        self.willCapture = False
        self.cnt = 0
        self.btn = [[None]*self.game.size for _ in range(self.game.size)]

        menubar = tk.Menu(master=window)
        menubar.add_command(label="Rules", command=self.showRules)
        window.config(menu=menubar)

        brd_fm = tk.Frame(master=window)
        brd_fm.pack(fill=tk.BOTH, expand=True)
        for i in range(self.game.size):
            brd_fm.columnconfigure(i, weight=1, minsize=IMG_SIZE)
            brd_fm.rowconfigure(i, weight=1, minsize=IMG_SIZE)

            for j in range(self.game.size):
                frame = tk.Frame(master=brd_fm)
                frame.grid(row=i, column=j, sticky="nsew")

                self.btn[i][j] = tk.Button(master=frame, width=IMG_SIZE, height=IMG_SIZE, relief=tk.FLAT)
                self.btn[i][j].bind("<Button-1>", self.click)
                self.btn[i][j].pack(expand=True, fill=tk.BOTH)
                

        opts_fm = tk.Frame(master=window)
        opts_fm.pack(expand=True)

        depth_scale = tk.Scale(master=window, variable=MAX_DEPTH, orient=tk.HORIZONTAL, from_=1, to=5)
        depth_scale.pack()
        MAX_DEPTH.set(4)

        frm_counter = tk.Frame(master=window)
        frm_counter.pack(expand=True)
        self.lbl_counter = tk.Label(master=frm_counter)
        self.lbl_counter.pack()
        
        self.update()
        nextPoss = [move[0] for move in self.game.nextMoves(self.player)]
        self.hints(nextPoss)
        
        window.mainloop()

    def showRules(self):
        """ Show rules of checkers"""
        messagebox.showinfo("Rules","Click to select a piece, and click a position to move piece.\n You can find rules here: 'https://www.ultraboardgames.com/checkers/game-rules.php'")

    def update(self):
        for i in range(self.game.size):
            f = i % 2 == 1
            for j in range(self.game.size):

                if f:
                    self.btn[i][j]['bg'] = 'Sienna'
                else:
                    self.btn[i][j]['bg'] = 'Moccasin'
                img = blank_img
                if self.game.board[i][j] == Checkers.BLACK_MAN:
                    img = b_man_img
                elif self.game.board[i][j] == Checkers.BLACK_KING:
                    img = b_king_img
                elif self.game.board[i][j] == Checkers.WHITE_MAN:
                    img = w_man_img
                elif self.game.board[i][j] == Checkers.WHITE_KING:
                    img = w_king_img

                self.btn[i][j]["image"] = img
                
                f = not f
        self.lbl_counter['text'] = f'No capture moves: {self.cnt}'
        window.update()

    def hints(self, poss: Poss):
        for x in range(self.game.size):
            for y in range(self.game.size):
                defaultbg = self.btn[x][y].cget('bg')
                self.btn[x][y].master.config(highlightbackground=defaultbg, highlightthickness=3)

        for pos in poss:
            x, y = pos
            self.btn[x][y].master.config(highlightbackground="royalblue", highlightthickness=3)

    def click(self, event):
        info = event.widget.master.grid_info()
        x, y = info["row"], info["column"]
        if self.lastX == None or self.lastY == None:
            moves = self.game.nextMoves(self.player)
            found = (x, y) in [move[0] for move in moves]
            
            if found:
                self.lastX = x
                self.lastY = y
                normal, capture = self.game.nextPoss(x, y)
                poss = normal if len(capture) == 0 else capture
                self.hints(poss)
            else:
                print("Invalid position")
            return

        normalPoss, capturePoss = self.game.nextPoss(self.lastX, self.lastY)
        poss = normalPoss if (len(capturePoss) == 0) else capturePoss
        if (x,y) not in poss:
            print("Invalid move")
            if not self.willCapture:
                self.lastX = None
                self.lastY = None
                nextPoss = [move[0] for move in self.game.nextMoves(self.player)]
                self.hints(nextPoss)
            return

        canCapture, removed, _ = self.game.playMove(self.lastX, self.lastY, x, y)
        self.hints([])
        self.update()
        self.cnt += 1
        self.lastX = None
        self.lastY = None
        self.willCapture = False

        if removed != 0:
            self.cnt = 0
        if removed == Checkers.BLACK_KING:
            messagebox.showinfo(message="You lose!", title="Checkers")
            window.destroy()
        if removed == Checkers.WHITE_KING:
            messagebox.showinfo(message="You won!", title="Checkers")
            window.destroy()
        if canCapture:
            _, nextCaptures = self.game.nextPoss(x, y)
            if len(nextCaptures) != 0:
                self.willCapture = True
                self.lastX = x
                self.lastY = y
                self.hints(nextCaptures)
                return
        
        cont, reset = True, False
            
        evaluate = EVALUATION_FUNCTION
        if self.cnt > 20:
            evaluate = Checkers.endGame
            if INCREASE_DEPTH:
                self.maxDepth = 7
        else:
            evaluate = Checkers.evaluate2
            self.maxDepth = MAX_DEPTH.get()
                    
        cont, reset = self.game.minimaxPlay(1-self.player, maxDepth=self.maxDepth, evaluate=evaluate, enablePrint=False)
            
        self.cnt += 1
        if not cont:
            messagebox.showinfo(message="You Won!", title="Checkers")
            window.destroy()
            return
        self.update()
        if reset:
            self.cnt = 0
        if self.cnt >= 100:
            messagebox.showinfo(message="Draw!", title="Checkers")
            window.destroy()
            return
        
        nextPoss = [move[0] for move in self.game.nextMoves(self.player)]
        self.hints(nextPoss)
        if len(nextPoss) == 0:
            messagebox.showinfo(message="You lose!", title="Checkers")
            window.destroy()

        self.pre = self.pre[:self.prePtr+1]
        self.pre.append(self.game.getBoard())
        self.prePtr += 1




window = tk.Tk()
window.title("Checkers")
IMG_SIZE = 60
b_man_img = ImageTk.PhotoImage(Image.open('pics/b_man.png').resize((IMG_SIZE, IMG_SIZE)))
b_king_img = ImageTk.PhotoImage(Image.open('pics/b_king.png').resize((IMG_SIZE, IMG_SIZE)))
w_man_img = ImageTk.PhotoImage(Image.open('pics/w_man.png').resize((IMG_SIZE, IMG_SIZE)))
w_king_img = ImageTk.PhotoImage(Image.open('pics/w_king.png').resize((IMG_SIZE, IMG_SIZE)))
blank_img = ImageTk.PhotoImage(Image.open('pics/blank.png').resize((IMG_SIZE, IMG_SIZE)))


CHECKER_SIZE = 8
STARTING_PLAYER = Checkers.BLACK

MAX_DEPTH = tk.IntVar()

EVALUATION_FUNCTION = Checkers.evaluate2
INCREASE_DEPTH = False
APP()