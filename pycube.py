import numpy as np 
import time
from tkinter import *

class Cube3:
	'''
	3 by 3 Rubik's Cube Object

	Cube is represented in 2D numpy array.

	Face orientation are stored in a 1D array. 

	Turns are quarter turns. The turn function accepts commands argumands from 0-11. 0-5 are clockwise turns. 6-11 are counter clockwise turns.
	Commands are associated with the face index. If commands are greater than 5 then commands minus 6 results in the face index. 

	FRONT(0)  RIGHT(1)  BACK(3)   LEFT(4)   UP(2)     DOWN(5)
	| 0  1  2 | 0  1  2 | 0  1  2 | 0  1  2 | 0  1  2 | 0  1  2 |
	| 7  .  3 | 7  .  3 | 7  .  3 | 7  .  3 | 7  .  3 | 7  .  3 |
	| 6  5  4 | 6  5  4 | 6  5  4 | 6  5  4 | 6  5  4 | 6  5  4 |  

	'''

	def __init__(self):
		#Cube representation
		self.stickers = np.empty((6, 8), dtype=np.int8)
		for i in range(6):
			for j in range(8):
				self.stickers[i][j] = i

		self.face_orientation_array = np.zeros(6, dtype=np.int8)
		self.face_orientation_index_shift = lambda i, o: i - 8 + o*2
		self.rotate_face_cw = lambda i: i + 1 if i + 1 < 4 else 0
		self.rotate_face_ccw = lambda i: i - 1 if i - 1 >= 0 else 0
		
		#2) perimeter
		#face indecies (up, right, down, left)
		p0 = [(2, [6, 5, 4]), (1, [0, 7, 6]), (5, [2, 1, 0]), (4, [4, 3, 2])]
		p1 = [(2, [4, 3, 2]), (3, [0, 7, 6]), (5, [4, 3, 2]), (0, [4, 3, 2])]
		p2 = [(3, [2, 1, 0]), (1, [2, 1, 0]), (0, [2, 1, 0]), (4, [2, 1, 0])]
		p3 = [(2, [2, 1, 0]), (4, [0, 7, 6]), (5, [6, 5, 4]), (1, [4, 3, 2])]
		p4 = [(2, [0, 7, 6]), (0, [0, 7, 6]), (5, [0, 7, 6]), (3, [4, 3, 2])]
		p5 = [(0, [6, 5, 4]), (1, [6, 5, 4]), (3, [6, 5, 4]), (4, [6, 5, 4])]

		self.perimeter_array = np.array([p0, p1, p2, p3, p4, p5])

	def turn(self, t):
		#CLOCKWISE
		if t < 6:
			#HANDLE FACE
			#use lamda function to update orientation array
			self.face_orientation_array[t] = self.rotate_face_cw(self.face_orientation_array[t])
			#HANDLE PERIMETER
			#the stickers on the perimeter of the face can be turned with three flops
			#flopping avoids temporary variables 
			for i in reversed(range(3)):
				self.perimeter_flop(self.perimeter_array[t][i], self.perimeter_array[t][i-1])
		else:
			t -= 6
			#HANDLE FACE
			self.face_orientation_array[t] = self.rotate_face_ccw(self.face_orientation_array[t])
			#HANDLE PERIMETER
			for i in range(3):
				self.perimeter_flop(self.perimeter_array[t][i], self.perimeter_array[t][i+1])

			
	def perimeter_flop(self, a, b):
		#Face index a[0]
		#Sticker index a[1] (will be a list)
		for i in range(3):
			ai = self.face_orientation_index_shift(a[1][i], self.face_orientation_array[a[0]])
			bi = self.face_orientation_index_shift(b[1][i], self.face_orientation_array[b[0]])
			self.stickers[a[0]][ai], self.stickers[b[0]][bi] = self.stickers[b[0]][bi], self.stickers[a[0]][ai]

	def get_sticker(self, a, b):
		#a: face index
		#b: sticker index
		return self.stickers[a][self.face_orientation_index_shift(b, self.face_orientation_array[a])]

	def print_cube(self):
		face_list = ["FRONT", "RIGHT", "TOP", "BACK", "LEFT", "BOTTOM"]
		for i in range(6):
			print(face_list[i])
			j = self.face_orientation_array[i]
			print("%d  %d  %d"%(self.stickers[[i], self.face_orientation_index_shift(0, j)], 
				self.stickers[[i], self.face_orientation_index_shift(1, j)], 
				self.stickers[[i], self.face_orientation_index_shift(2, j)]))
			print("%d  %d  %d"%(self.stickers[[i], self.face_orientation_index_shift(7, j)], i, 
				self.stickers[[i], self.face_orientation_index_shift(3, j)]))
			print("%d  %d  %d"%(self.stickers[[i], self.face_orientation_index_shift(6, j)], 
				self.stickers[[i], self.face_orientation_index_shift(5, j)], 
				self.stickers[[i], self.face_orientation_index_shift(4, j)]))

class Cube3Gui:
	'''
	FRONT(0)  RIGHT(1)  BACK(3)   LEFT(4)   UP(2)     DOWN(5)
	| 0  1  2 | 0  1  2 | 0  1  2 | 0  1  2 | 0  1  2 | 0  1  2 |
	| 3  4  5 | 3  4  5 | 3  4  5 | 3  4  5 | 3  4  5 | 3  4  5 | 
	'''
	def __init__(self, cube):
		self.root = Tk()
		self.root.title('Cube Viz')
		self.canvas = Canvas(self.root, width=800, height=650)
		self.canvas.pack(expand=YES, fill=BOTH)

		self.cube = cube

		self.gui_stickers = list()
		self.sticker_transform = {0:0, 1:1, 2:2, 3:7, 5:3, 6:6, 7:5, 8:4}
		outline='black'
		#FRONT(0) RIGHT(1) BACK(3) LEFT(4) UP(2) DOWN(5)
		self.fill={0:'red', 1:'blue', 2:'white', 3:'orange', 4:'green', 5:'yellow'} 
		face_origin = [[1, 1], [2, 1], [1, 0], [3, 1], [0, 1], [1, 2]]
		width=1
		s_size = 25
		s_space = 5
		f_space = 3*s_size+4*s_space
		points_list = list()
		for yi in range(3):
			for xi in range(3):
				x0 = xi*(s_size + s_space)
				y0 = yi*(s_size + s_space)
				x1 = (xi+1)*(s_size + s_space)
				y1 = yi*(s_size + s_space)
				x2 = (xi+1)*(s_size + s_space)
				y2 = (yi+1)*(s_size + s_space)
				x3 = xi*(s_size + s_space)
				y3 = (yi+1)*(s_size + s_space)

				points_list.append([x0, y0, x1, y1, x2, y2, x3, y3])

		for i in range(6):
			for j in range(2):
				face_origin[i][j] = face_origin[i][j] * f_space + 25

		for i in range(6):
			face_stickers = list()
			for j in range(9):
				points = list()
				points = points_list[j].copy()
				for k in [0,2,4,6]:
					points[k] = points[k] + face_origin[i][0]
					points[k+1] = points[k+1] + face_origin[i][1]
				face_stickers.append(self.canvas.create_polygon(points, outline=outline, fill=self.fill[i], width=width))
			self.gui_stickers.append(face_stickers)
		self.update_stickers()

	def update_stickers(self):
		for i in range(6):
			# print()
			# print(i)
			# print()
			# print("%d %d %d"%(self.cube.get_sticker(i, self.sticker_transform[0]), self.cube.get_sticker(i, self.sticker_transform[1]), self.cube.get_sticker(i, self.sticker_transform[2])))
			# print("%d %d %d"%(self.cube.get_sticker(i, self.sticker_transform[3]), i, self.cube.get_sticker(i, self.sticker_transform[5])))
			# print("%d %d %d"%(self.cube.get_sticker(i, self.sticker_transform[6]), self.cube.get_sticker(i, self.sticker_transform[7]), self.cube.get_sticker(i, self.sticker_transform[8])))
			for j in range(9):
				if j == 4:
					self.canvas.itemconfigure(self.gui_stickers[i][j], fill=self.fill[i]) 
				else:
					self.canvas.itemconfigure(self.gui_stickers[i][j], fill=self.fill[self.cube.get_sticker(i, self.sticker_transform[j])]) 

	def update_root(self):
		self.root.update()

def make_turn_list(size):
	turn_list = np.random.randint(12, size=size)
	reverse = turn_list[::-1]
	for i in range(len(reverse)):
		if reverse[i] <6:
			reverse[i] += 6
		else:
			reverse[i] -= 6
	return np.concatenate((turn_list, reverse), axis=None)
if __name__ == '__main__':
	turn_list = [0, 1, 2, 3, 4, 5, 11, 10, 9, 8, 7, 6]
	print(turn_list)
	count = 0
	c = Cube3()
	gui = Cube3Gui(c)
	gui.update_root()
	while True:
		try:
			time.sleep(1)
			c.turn(turn_list[count])
			gui.update_stickers()
			gui.update_root()
			time.sleep(1)
			c.turn(turn_list[count])
			gui.update_stickers()
			gui.update_root()
			count += 1
			if count > 11:
				count = 0
		except KeyboardInterrupt:
			break
