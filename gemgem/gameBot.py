import random, time, pygame, sys, cv2
import gemgem
import numpy as np

PADDING = 44
WIDTH = gemgem.BOARDWIDTH
HEIGHT = gemgem.BOARDHEIGHT
IMAGESIZE = gemgem.GEMIMAGESIZE
LIGHTBLUE = gemgem.LIGHTBLUE
NUMGEMIMAGES = gemgem.NUMGEMIMAGES


# check in 1x4 area if there are some matches
def area1x4(board):
    for w in range(WIDTH - 3):
        for h in range(HEIGHT):
            area = board[w:w + 4, h].T
            unique, counts = np.unique(area, return_counts=True)
            if 3 in counts:
                unique_value = unique[np.where(counts > 2)][0]
                ind = np.where(area != unique_value)[0][0]
                x1 = w + ind
                y1 = h
                if ind == 2:
                    x2 = h + ind + 1
                else:
                    x2 = h + ind - 1
                y2 = h
                return {'x': x1, 'y': y1}, {'x': x2, 'y': y2}


# check in 4x1 area if there are some matches
def area4x1(board):
    for w in range(WIDTH):
        for h in range(HEIGHT - 3):
            area = board[w, h:h + 4].T
            unique, counts = np.unique(area, return_counts=True)
            if 3 in counts:
                val = unique[np.where(counts > 2)][0]
                ind = np.where(area != val)[0][0]
                x1 = w
                y1 = h + ind
                x2 = w
                if ind == 2:
                    y2 = h + ind + 1
                else:
                    y2 = h + ind - 1
                return {'x': x1, 'y': y1}, {'x': x2, 'y': y2}


# check in 2x3 area if there are some matches
def area2x3(board):
    for w in range(WIDTH - 2):
        for h in range(HEIGHT - 1):
            area = board[w:w + 3, h:h + 2].T
            unique, counts = np.unique(area, return_counts=True)
            if 3 in counts:
                val = unique[np.where(counts > 2)][0]
                for k in range(2):
                    ind = np.where(area[k] != val)[0][0]
                    if area[(k + 1) % 2, ind] == val and len(np.where(area[k] == val)[0]) == 2:
                        x1 = w + ind
                        y1 = h + k
                        x2 = w + ind
                        y2 = h + (k + 1) % 2
                        return {'x': x1, 'y': y1}, {'x': x2, 'y': y2}


# check in 3x2 area if there are some matches
def area3x2(board):
    for w in range(WIDTH - 1):
        for h in range(HEIGHT - 2):
            area = board[w:w + 2, h:h + 3].T
            unique, counts = np.unique(area, return_counts=True)
            if 3 in counts:
                val = unique[np.where(counts > 2)][0]
                for k in range(2):
                    ind = np.where(area[:, k] != val)[0][0]
                    if len(np.where(area[:, k] == val)[0]) == 2 and area[ind, (k + 1) % 2] == val:
                        x1 = w + k
                        y1 = h + ind
                        x2 = w + (k + 1) % 2
                        y2 = h + ind
                        return {'x': x1, 'y': y1}, {'x': x2, 'y': y2}

def bot_move():
    board = np.zeros((8, 8))
    img = cv2.imread('screenshot.jpg', cv2.IMREAD_UNCHANGED)

    # creating the board
    for i in range(WIDTH):
        for j in range(HEIGHT):
            cropped = img[PADDING + (IMAGESIZE * i):PADDING + (IMAGESIZE * (i + 1)),
                      PADDING + (IMAGESIZE * j):PADDING + (IMAGESIZE * (j + 1))]
            cropped[0, :] = cropped[-1, :] = cropped[:, 0] = cropped[:, -1] = LIGHTBLUE[::-1]

            for n in range(1, NUMGEMIMAGES + 1):
                gem = cv2.imread('gem{}.png'.format(str(n)), cv2.IMREAD_UNCHANGED)
                mask = gem[:, :, 3] == 0
                gem[mask] = [*LIGHTBLUE[::-1], 255]

                new_gem = cv2.cvtColor(gem, cv2.COLOR_BGRA2BGR)[:, :, :3]
                diff = cv2.subtract(cropped, new_gem)
                b, g, r = cv2.split(diff)
                if (500 < len(b[np.where(b > 30)]) < 900) and \
                        (500 < len(g[np.where(g > 30)]) < 900) and \
                        (500 < len(r[np.where(r > 30)]) < 900):
                    board[j, i] = n - 1
                    break

    if area2x3(board):
        return area2x3(board)
    elif area3x2(board):
        return area3x2(board)
    elif area1x4(board):
        return area1x4(board)
    elif area4x1(board):
        return area4x1(board)
    else:
        return None, None


def myRunGame():
    # Plays through a single game. When the game is over, this function returns.

    # initalize the board
    gameBoard = gemgem.getBlankBoard()
    score = 0
    gemgem.fillBoardAndAnimate(gameBoard, [], score)  # Drop the initial gems.

    # initialize variables for the start of a new game
    firstSelectedGem = None
    lastMouseDownX = None
    lastMouseDownY = None
    gameIsOver = False
    lastScoreDeduction = time.time()
    clickContinueTextSurf = None

    field_updated = True
    game_started = True
    while True:  # main game loop
        clickedSpace = None

        if field_updated and not game_started and not gameIsOver:
            pygame.image.save(gemgem.DISPLAYSURF, "screenshot.jpg")
            firstSelectedGem, clickedSpace = bot_move()
            field_updated = False

        for event in pygame.event.get():  # event handling loop
            if event.type == gemgem.QUIT or (event.type == gemgem.KEYUP and event.key == gemgem.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == gemgem.KEYUP and event.key == gemgem.K_BACKSPACE:
                return  # start a new game

            elif event.type == gemgem.MOUSEBUTTONUP:
                if gameIsOver:
                    return  # after games ends, click to start a new game

                if event.pos == (lastMouseDownX, lastMouseDownY):
                    # This event is a mouse click, not the end of a mouse drag.
                    clickedSpace = gemgem.checkForGemClick(event.pos)
                else:
                    # this is the end of a mouse drag
                    firstSelectedGem = gemgem.checkForGemClick((lastMouseDownX, lastMouseDownY))
                    clickedSpace = gemgem.checkForGemClick(event.pos)
                    if not firstSelectedGem or not clickedSpace:
                        # if not part of a valid drag, deselect both
                        firstSelectedGem = None
                        clickedSpace = None
            elif event.type == gemgem.MOUSEBUTTONDOWN:
                # this is the start of a mouse click or mouse drag
                lastMouseDownX, lastMouseDownY = event.pos

        if clickedSpace and not firstSelectedGem:
            # This was the first gem clicked on.
            firstSelectedGem = clickedSpace
        elif clickedSpace and firstSelectedGem:
            # Two gems have been clicked on and selected. Swap the gems.
            firstSwappingGem, secondSwappingGem = gemgem.getSwappingGems(gameBoard, firstSelectedGem, clickedSpace)
            if firstSwappingGem == None and secondSwappingGem == None:
                # If both are None, then the gems were not adjacent
                firstSelectedGem = None  # deselect the first gem
                continue

            # Show the swap animation on the screen.
            boardCopy = gemgem.getBoardCopyMinusGems(gameBoard, (firstSwappingGem, secondSwappingGem))
            gemgem.animateMovingGems(boardCopy, [firstSwappingGem, secondSwappingGem], [], score)

            # Swap the gems in the board data structure.
            gameBoard[firstSwappingGem['x']][firstSwappingGem['y']] = secondSwappingGem['imageNum']
            gameBoard[secondSwappingGem['x']][secondSwappingGem['y']] = firstSwappingGem['imageNum']

            # See if this is a matching move.
            matchedGems = gemgem.findMatchingGems(gameBoard)
            if matchedGems == []:
                # Was not a matching move; swap the gems back
                gemgem.GAMESOUNDS['bad swap'].play()
                gemgem.animateMovingGems(boardCopy, [firstSwappingGem, secondSwappingGem], [], score)
                gameBoard[firstSwappingGem['x']][firstSwappingGem['y']] = firstSwappingGem['imageNum']
                gameBoard[secondSwappingGem['x']][secondSwappingGem['y']] = secondSwappingGem['imageNum']
            else:
                # This was a matching move.
                scoreAdd = 0
                while matchedGems != []:
                    # Remove matched gems, then pull down the board.

                    # points is a list of dicts that tells fillBoardAndAnimate()
                    # where on the screen to display text to show how many
                    # points the player got. points is a list because if
                    # the playergets multiple matches, then multiple points text should appear.
                    points = []
                    for gemSet in matchedGems:
                        scoreAdd += (10 + (len(gemSet) - 3) * 10)
                        for gem in gemSet:
                            gameBoard[gem[0]][gem[1]] = gemgem.EMPTY_SPACE
                        points.append({'points': scoreAdd,
                                       'x': gem[0] * gemgem.GEMIMAGESIZE + gemgem.XMARGIN,
                                       'y': gem[1] * gemgem.GEMIMAGESIZE + gemgem.YMARGIN})
                    random.choice(gemgem.GAMESOUNDS['match']).play()
                    score += scoreAdd

                    # Drop the new gems.
                    gemgem.fillBoardAndAnimate(gameBoard, points, score)

                    # Check if there are any new matches.
                    matchedGems = gemgem.findMatchingGems(gameBoard)
                field_updated = True
            firstSelectedGem = None

            if not gemgem.canMakeMove(gameBoard):
                gameIsOver = True

        # Draw the board.
        gemgem.DISPLAYSURF.fill(gemgem.BGCOLOR)
        gemgem.drawBoard(gameBoard)
        if firstSelectedGem != None:
            gemgem.highlightSpace(firstSelectedGem['x'], firstSelectedGem['y'])
        if gameIsOver:
            if clickContinueTextSurf == None:
                # Only render the text once. In future iterations, just
                # use the Surface object already in clickContinueTextSurf
                clickContinueTextSurf = gemgem.BASICFONT.render('Final Score: %s (Click to continue)' % (score), 1,
                                                                gemgem.GAMEOVERCOLOR, gemgem.GAMEOVERBGCOLOR)
                clickContinueTextRect = clickContinueTextSurf.get_rect()
                clickContinueTextRect.center = int(gemgem.WINDOWWIDTH / 2), int(gemgem.WINDOWHEIGHT / 2)
            gemgem.DISPLAYSURF.blit(clickContinueTextSurf, clickContinueTextRect)
        elif score > 0 and time.time() - lastScoreDeduction > gemgem.DEDUCTSPEED:
            # score drops over time
            score -= 1
            lastScoreDeduction = time.time()
        gemgem.drawScore(score)
        pygame.display.update()
        gemgem.FPSCLOCK.tick(gemgem.FPS)

        if game_started:
            pygame.image.save(gemgem.DISPLAYSURF, "screenshot.jpg")
            game_started = False


gemgem.runGame = myRunGame

if __name__ == '__main__':
    gemgem.main()
