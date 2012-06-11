#!/usr/bin/python
# -*- encoding: utf-8 -*-

from global_vars import *
import sys, random, numpy as ny
import mlp


class Game:
	""" Play a game of Connect Four. """


	def __init__( self, ai ):
		self.ai = ai
		self._init_field()


	def _init_field( self ):
		""" Init play field. """

		self.board = ny.array( [[STONE_BLANK] * FIELD_HEIGHT] * FIELD_WIDTH )
		self.current_height = [0] * FIELD_WIDTH


	def input_validate( self, x ):
		""" Validates the chosen column x. """

		# Try to cast to a number
		try:
			x = int( x )
		except:
			return False

		# Outside of game board width.
		if x < 1 or x > FIELD_WIDTH:
			return False

		# Column is full.
		if self.current_height[x - 1] >= FIELD_HEIGHT:
			return False

		return True


	def check_win( self ):
		""" Check the game board if someone has won.

		Returns the stone value of the winner.
		"""

		count = 0
		for x in range( FIELD_WIDTH ):
			for y in range( FIELD_HEIGHT ):
				stone = self.board[x][y]
				# We only care about players, not blank fields
				if stone == STONE_BLANK:
					count = 0; continue

				# Look up
				for i in range( 1, CONNECT ):
					if y + i >= FIELD_HEIGHT:
						count = 0; break
					# C-c-c-combo breaker!
					if stone != self.board[x][y + i]:
						count = 0; break
					count += 1
				# All stones connected: Winner found!
				if count + 1 == CONNECT:
					return stone

				# Look right
				for i in range( 1, CONNECT ):
					if x + i >= FIELD_WIDTH:
						count = 0; break
					if stone != self.board[x + i][y]:
						count = 0; break
					count += 1
				if count + 1 == CONNECT:
					return stone

				# Look diagonal right
				for i in range( 1, CONNECT ):
					if x + i >= FIELD_WIDTH or y + i >= FIELD_HEIGHT:
						count = 0; break
					if stone != self.board[x + i][y + i]:
						count = 0; break
					count += 1
				if count + 1 == CONNECT:
					return stone

				# Look diagonal left
				for i in range( 1, CONNECT ):
					if x - i < 0 or y + i >= FIELD_HEIGHT:
						count = 0; break
					if stone != self.board[x - i][y + i]:
						count = 0; break
					count += 1
				if count + 1 == CONNECT:
					return stone

		return STONE_BLANK


	def check_board_full( self ):
		""" Returns true if there are no more free fields,
		false otherwise. """

		if ny.shape( ny.where( self.board == STONE_BLANK ) )[1] == 0:
			return True
		return False


	def play( self ):
		""" Start playing. """

		while 1:
			try:
				x = raw_input( ">> Column: " )
			except EOFError: print; break
			except KeyboardInterrupt: print; break

			# Validate user input
			if not self.input_validate( x ):
				print "No valid field position!"
				continue
			x = int( x ) - 1

			# Place human stone
			y = self.current_height[x]
			self.current_height[x] += 1
			self.board[x][y] = STONE_HUMAN

			self.print_board( self.board )

			winner = self.check_win()
			if winner == STONE_HUMAN:
				print "You won!"
				break
			elif winner == STONE_AI:
				print "The AI won!"
				break

			# Place AI stone
			# ("opp" as in "opponent")
			opp_win = { "col": -1, "diff": 100.0 }
			opp_draw = { "col": -1, "diff": 100.0 }
			opp_loss = { "col": -1, "diff": 100.0 }

			for x in range( FIELD_WIDTH ):
				# Cell (y) in this column (x) we are currently testing
				y = self.current_height[x]
				if y >= FIELD_HEIGHT:
					continue

				# Don't change the real game board
				board_copy = self.board.copy()
				board_copy[x][y] = STONE_AI

				# Array format for the AI: 7x6 -> 1x42
				ai_board_format = []
				for i in range( FIELD_WIDTH ):
					ai_board_format.extend( board_copy[i] )

				# Get the possible outcome
				ai_output = self.ai.use( ai_board_format )[0][0]
				print x, ai_output

				# Difference between targets and output
				diff_loss = LOSS - ai_output
				diff_win = WIN - ai_output
				diff_draw = DRAW - ai_output

				if diff_loss < 0.0: diff_loss *= -1
				if diff_win < 0.0: diff_win *= -1
				if diff_draw < 0.0: diff_draw *= -1

				# Close to (opponents) LOSS
				if diff_loss <= diff_draw and diff_loss <= diff_win:
					if diff_loss < opp_loss["diff"]:
						opp_loss["col"] = x
						opp_loss["diff"] = diff_loss

				# Close to DRAW
				elif diff_draw <= diff_loss and diff_draw <= diff_win:
					if diff_draw < opp_draw["diff"]:
						opp_draw["col"] = x
						opp_draw["diff"] = diff_draw

				# Close to (opponents) WIN
				else:
					if diff_win < opp_win["diff"]:
						opp_win["col"] = x
						opp_win["diff"] = diff_win


			# Select best possible result
			print opp_loss, opp_draw, opp_win

			# We want the opponent to loose
			if opp_loss["col"] >= 0:
				use_pos = opp_loss["col"]

			# If that is not possible, at least go for a draw
			elif opp_draw["col"] >= 0:
				use_pos = opp_draw["col"]

			# Ugh, fine, if there is no other choice
			elif opp_win["col"] >= 0:
				use_pos = opp_win["col"]

			# This shouldn't happen
			else:
				print "-- The AI has no idea what to do and stares mindlessly at a cloud outside the window."
				print "-- The cloud looks like a rabbit riding a pony."
				print "-- You win by forfeit."
				break

			print "AI places stone in column " + str( use_pos + 1 ) + "."
			y = self.current_height[use_pos]
			self.board[use_pos][y] = STONE_AI
			self.current_height[use_pos] += 1

			self.print_board( self.board )

			winner = self.check_win()
			if winner == STONE_HUMAN:
				print "You won!"
				break
			elif winner == STONE_AI:
				print "The AI won!"
				break

			# Draw
			if self.check_board_full():
				print "No more free fields. It's a draw!"
				break

		print "Game ended."


	def print_board( self, board ):
		""" Print the current game board. """

		for y in reversed( range( FIELD_HEIGHT ) ):
			sys.stdout.write( " | " )
			for x in range( FIELD_WIDTH ):
				field = ' '
				if board[x][y] == STONE_HUMAN:
					field = 'x'
				elif board[x][y] == STONE_AI:
					field = 'o'
				sys.stdout.write( field + " | " )
			print ''
		sys.stdout.write( ' ' )
		print '¯' * ( FIELD_WIDTH * 4 + 1 )



if __name__ == "__main__":
	# Small test
	g = Game( None )
	print g.board
	g.print_board( g.board )
	print "Well, nothing crashed …"