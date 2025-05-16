import pygame
import sys

# Board data: 3 layers of 8x8 boards
board_format = [
    [
        [None, 'w', None, 'w', None, 'w', None, 'w'],
        ['w', None, 'w', None, 'w', None, 'w', None],
        [None, 'w', None, 'w', None, 'w', None, 'w'],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        ['b', None, 'b', None, 'b', None, 'b', None],
        [None, 'b', None, 'b', None, 'b', None, 'b'],
        ['b', None, 'b', None, 'b', None, 'b', None]
    ] for _ in range(3)
]

# Init Pygame
pygame.init()
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREY = (128, 128, 128)

screen = pygame.display.set_mode((WIDTH, HEIGHT))


def draw_squares(screen, board_index):
    screen.fill(BLACK)
    for row in range(ROWS):
        for col in range(row % 2, COLS, 2):
            pygame.draw.rect(screen, WHITE, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    # Draw board label in top-left corner
    font = pygame.font.SysFont(None, 48)
    text = font.render(str(board_index + 1), True, BLUE)
    screen.blit(text, (10, 10))


def get_row_col_from_mouse(pos):
    x, y = pos
    return y // SQUARE_SIZE, x // SQUARE_SIZE


class Piece:
    PADDING = 15
    OUTLINE = 2

    def __init__(self, row, col, color, b):
        self.row = row
        self.col = col
        self.color = color
        self.board = b
        self.king = False
        self.k2 = False
        self.direction = -1 if color == RED else 1
        self.x = self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = self.col * SQUARE_SIZE + SQUARE_SIZE // 2
        self.y = self.row * SQUARE_SIZE + SQUARE_SIZE // 2

    def make_king(self):
        self.king = True

    def draw(self, screen):
        radius = SQUARE_SIZE // 2 - self.PADDING
        pygame.draw.circle(screen, GREY, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(screen, self.color, (self.x, self.y), radius)
        if self.k2:
            crown = pygame.image.load('crown-clip-art-24.png')
            crown = pygame.transform.scale(crown, (50, 50))
            screen.blit(crown, (self.x - crown.get_width() // 2, self.y - crown.get_height() // 2))
        elif self.king:
            crown = pygame.image.load('crown.png')
            crown = pygame.transform.scale(crown, (44, 25))
            screen.blit(crown, (self.x - crown.get_width() // 2, self.y - crown.get_height() // 2))


class Board:
    def get_piece(self, row, col, b):
        val = board_format[b][row][col]
        if val is None:
            return None

        if val == 'K':  # RED k2
            color = RED
            piece = Piece(row, col, color, b)
            piece.king = True
            piece.k2 = True
            return piece
        elif val == 'k':  # WHITE k2
            color = WHITE
            piece = Piece(row, col, color, b)
            piece.king = True
            piece.k2 = True
            return piece
        else:
            color = RED if val.lower() == 'b' else WHITE
            piece = Piece(row, col, color, b)
            if val.isupper():
                piece.make_king()
            return piece

    def draw(self, screen, b):
        draw_squares(screen, b)
        for row in range(ROWS):
            for col in range(COLS):
                val = board_format[b][row][col]
                if val is not None:
                    # Handle special k2 pieces first
                    if val == 'K':
                        color = RED
                        piece = Piece(row, col, color, b)
                        piece.king = True
                        piece.k2 = True
                    elif val == 'k':
                        color = WHITE
                        piece = Piece(row, col, color, b)
                        piece.king = True
                        piece.k2 = True
                    else:
                        color = RED if val.lower() == 'b' else WHITE
                        piece = Piece(row, col, color, b)
                        if val.isupper():
                            piece.make_king()
                    piece.draw(screen)

    def move(self, piece, row, col, b):
        board_format[piece.board][piece.row][piece.col], board_format[b][row][col] = board_format[b][row][col], board_format[piece.board][piece.row][piece.col]


    def remove(self, pieces, b):
        for piece in pieces:
            board_format[b][piece.row][piece.col] = None

    def has_valid_moves(self, color):
        for b in range(3):
            for row in range(ROWS):
                for col in range(COLS):
                    piece = self.get_piece(row, col, b)
                    if piece and piece.color == color:
                        moves = self.get_valid_moves(piece, b)
                        if moves:
                            return True
        return False

    def has_pieces(self, color):
        for b in range(3):
            for row in range(ROWS):
                for col in range(COLS):
                    piece = self.get_piece(row, col, b)
                    if piece and piece.color == color:
                        return True
        return False

    def get_valid_moves(self, piece, b):
        moves = {}
        if piece.k2:
            directions = [  # 8 directions
                (-1, -1), (-1, 1), (1, -1), (1, 1),  # diagonals
                (-1, 0), (1, 0),
                (0, -1), (0, 1),
            ]
        elif piece.king:
            directions = [  # 8 directions
                (-1, -1), (-1, 1), (1, -1), (1, 1),  # diagonals
            ]
        else:
            # Only forward diagonals for regular pieces
            directions = [(piece.direction, -1), (piece.direction, 1)]

        for dy, dx in directions:
            row = piece.row + dy
            col = piece.col + dx

            if 0 <= row < ROWS and 0 <= col < COLS:
                target = board_format[b][row][col]
                if target is None:
                    moves[(row, col)] = []
                elif (piece.color == RED and target in ['w', 'W', 'k']) or (piece.color == WHITE and target in ['b', 'B', 'K']):
                    jump_row = row + dy
                    jump_col = col + dx
                    if 0 <= jump_row < ROWS and 0 <= jump_col < COLS and board_format[b][jump_row][jump_col] is None:
                        jumped_piece = self.get_piece(row, col, b)
                        moves[(jump_row, jump_col)] = [jumped_piece]

        return moves


class Game:
    def __init__(self, screen):
        self.board = Board()
        self.turn = RED
        self.selected = None
        self.valid_moves = {}
        self.screen = screen
        self.visible_board = 0
        self.sub_turn = 0
        self.k2_moved = False

    def update(self):
        pygame.display.set_caption(f"3D Checkers - Board {self.visible_board + 1}")
        self.board.draw(self.screen, self.visible_board)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def select(self, row, col, b):
        if self.selected:
            result = self._move(row, col, b)
            if not result:
                self.selected = None
                self.select(row, col, b)
        else:
            piece = self.board.get_piece(row, col, b)
            if piece is not None and piece.color == self.turn:
                if piece.k2 and self.k2_moved:
                    return False  # Prevent moving another k2 this turn
                self.selected = piece
                self.valid_moves = self.board.get_valid_moves(piece, b)
                return True
        return False

    def _move(self, row, col, b):
        if self.selected and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col, b)

            if (self.selected.color == RED and row == 0) or (self.selected.color == WHITE and row == ROWS - 1):
                self.selected.make_king()
            if ((self.selected.color == RED and row == ROWS - 1) or (
                    self.selected.color == WHITE and row == 0)) and self.selected.king:
                self.selected.k2 = True

            # Preserve king status in board_format
            if self.selected.k2:
                board_format[b][row][col] = 'K' if self.selected.color == RED else 'k'
            elif self.selected.king:
                board_format[b][row][col] = 'B' if self.selected.color == RED else 'W'
            else:
                board_format[b][row][col] = 'b' if self.selected.color == RED else 'w'

            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped, b)

            # ✅ Set k2_moved BEFORE resetting selected
            if self.selected.k2:
                self.k2_moved = True
                print("k2 moved!")

            self.advance_turn()
            return True

        return False

    def display_centered_message(self, message, duration=3000):
        font = pygame.font.SysFont(None, 72)
        BRIGHT_GREEN = (0, 255, 0)
        text = font.render(message, True, BRIGHT_GREEN)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        # Draw final frame
        self.board.draw(self.screen, self.visible_board)
        self.screen.blit(text, text_rect)
        pygame.display.update()
        pygame.time.wait(duration)

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.screen, BLUE,
                               (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 15)

    def advance_turn(self):
        self.valid_moves = {}
        self.selected = None

        # After a move, check if the current player has any valid moves left for the remaining sub-turns
        if self.sub_turn < 2:
            self.sub_turn += 1
            if not self.board.has_valid_moves(self.turn):
                winner = "White" if self.turn == RED else "Red"
                self.display_centered_message(f"{winner} wins!", 3000)
                pygame.quit()
                sys.exit()

        else:
            # Completed 3 moves, switch turn
            self.sub_turn = 0
            self.k2_moved = False
            self.turn = WHITE if self.turn == RED else RED

            # Before new player starts, check if THEY have any valid moves
            if not self.board.has_valid_moves(self.turn) or not self.board.has_pieces(self.turn):
                winner = "White" if self.turn == RED else "Red"
                self.display_centered_message(f"{winner} wins!", 3000)
                pygame.quit()
                sys.exit()


def main():
    clock = pygame.time.Clock()
    game = Game(screen)
    run = True

    while run:
        global board_format
        clock.tick(60)
        game.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and game.visible_board > 0:
                    game.visible_board -= 1
                elif event.key == pygame.K_DOWN and game.visible_board < len(board_format) - 1:
                    game.visible_board += 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                game.select(row, col, game.visible_board)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
