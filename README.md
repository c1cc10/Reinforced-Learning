# Reinforced-Learning
experiment and base code for article explaining my understanding of the matter

# Tris-rl-c1
That's my first experiment based on what I read in R. Sutton's book: "Reinforced Learning, an introduction". It's a tic-tac-toe player which can race against itself or against a human player.

# Run the example
First make sure you have access to *python3* (python  _VERSION 3_) application. 
Then download *tris_rl_c1.py* file 
Run tris_rl_c1.py file using *python3* interpreter.
If you just run it, then it will play 10000 (ten thousands) games against another Computer player and then it will ask you if you want to get along playing human vs computer. If you have a go on it, then please remember Computer should start first in order to exploit its learning. 
If you like to have one more interactive experience, then:
* run _python3_ to get CLI.
* import the file as a module:

	import tris_rl_c1 as tris

* initialize the Game by setting robot-war-mode ON: 

	mio = tris.Game(True)

* have it play some games, so that it can build up a good experience:

	for i in range(0,100000):
	    mio.start()

* Once it's done, try it by yourself. First disengage robot-war-mode:

	mio.robowar = False

* then just start it:

	mio.start()

# game instructions
Game always starts by asking you if you want to start first. Just press y or n and go on. Note: computer is best trained as first player
Application will always show you odds for each square and then the moves you and your opponent made:

		 0.23885325972807286 | 0.41511698006788766 | 0.4436637195270866
		 ---------------
		 0.30529222927263944 | 0.8290913187615254 | 0.23943512627592367
		 ---------------
		 0.309520799310112 | 0.2645851601321948 | 0.33661570292095344
	valutation:
	0.8290913187615254

		   |   |
		 ---------
		   | X |
		 ---------
		   |   |
	Where will you move? (0 - 8):

In this case, computer goes first and in its experience the best square to start with is the centered one. Then it asks its opponent where she's going to check. numbers represent squares as shown below:

	  0 | 1 | 2
	 -----------
	  3 | 4 | 5
	 -----------
	  6 | 7 | 8

Yeah I know this console interface is crap, but that's beside the point, ain't it? So if you want to answer by checking the upper middle square, just press '1' and enter:

	Where will you move? (0 - 8):1
	Fine...

		   | O |
		 ---------
		   | X |
		 ---------
		   |   |

Computer then gets the board from its memory and assets the odds:

	 0.4904832841553881 | 0.0 | 0.9763545738530495
	 ---------------
	 0.4505676516574461 | 0.0 | 0.2
	 ---------------
	 0.368 | 0.39713126660791453 | 0.26928084757195964
   
It shows what it came up to resolve:

	valutation:
	0.9763545738530495

and then it just shows you the updated board:

		   | O | X
		 ---------
		   | X |
		 ---------
		   |   |
	Where will you move? (0 - 8):
