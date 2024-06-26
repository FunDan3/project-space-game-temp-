from .default_component import default_component
import asyncio
import time
import random
import pygame
import hashlib
import multiprocessing as mp
import os
def cpu_load(): #I want it to feel like a crash with fans going off and stuff
	while True:
		x = random.randint(2, 128)*2
cpu_cores = mp.cpu_count()

is_dev = os.path.exists("../development.mark") # If true disables "anticheat"
anticheat_message = "You wouldn't be able to become fat looser without cheats!" #When playing shooter dude told me something in spanish and it translated to russian "Без читов ты не сможешь стать толстым неудачником". I tried conveying its meaning to english.
expected_game_hash = ""
using_cheats = False

def hash(path, first = True):
	if os.path.isdir(path):
		path += ("/" if not path.endswith("/") else "")
		filelist = os.listdir(path)
		hashes = b""
		for file in filelist:
			file_path = path+file
			hashes += hash(file_path, first = False)
		path_hash = hashlib.new("md5") #tbh I dont care about hash collisions. Real 'hacker' would disable anticheat in no time.
		path_hash.update(hashes)
	else:
		path_hash = hashlib.new("md5")
		with open(path, "rb") as f:
			path_hash.update(f.read())
	if first:
		return path_hash.hexdigest()
	else:
		return path.encode("utf-8") + path_hash.digest()

def load_anticheat():
	global using_cheats
	real_game_hash = hash("./")
	using_cheats = not is_dev and real_game_hash != expected_game_hash #I KNOW IT MAY BE SOME NO BAD INTENT MODS. IDC! I CALL IT HOWEVER I WANT!!!
	if is_dev:
		print(f"Game hash is '{real_game_hash}'.")

class text_oneline(default_component):
	load_anticheat = load_anticheat #to make it visible to other files

	position = None
	size = None

	color = None
	font = None
	rendered_surface = None

	border_color = None
	border = None

	filler_color = None

	boxed = None
	cheated = False

	def __init__(self, position, size, text, color = None, border_size = 2, border_color = None, filler_color = None, font = None, boxed = True):
		if not border_color:
			border_color = [255] * 3
		if not filler_color:
			filler_color = [128] * 3
		if not color:
			color = [255] * 3
		if not font:
			if not pygame.font.get_init():
				pygame.font.init()
			font = pygame.font.Font(size = 64) #to keep resolution high. Only affects performance during initialization and text updates.
		self.position = position
		self.size = size

		self.color = color
		self.font = font
		self.update_text(text)

		self.boxed = boxed

		self.filler_color = filler_color

		self.border_color = border_color
		self.border = [
                        position[0] - border_size,
                        position[1] - border_size,
                        size[0] + border_size*2,
                        size[1] + border_size*2]

	def update_text(self, text):
		if using_cheats and random.randint(0, 100) == 0: #1% chance
			text = anticheat_message
			self.cheated = True
		rendered_text = self.font.render(text, True, self.color)
		width, height = rendered_text.get_size()
		factors = (1/(width/self.size[0]), 1/(height/self.size[1]))
		self.rendered_surface = pygame.transform.scale_by(rendered_text, min(factors))

	def render_on(self, surface):
		async def freeze():
			await self.renderer.one_time_loop()
			processes = [mp.Process(target = cpu_load) for _ in range(cpu_cores)]
			[process.start() for process in processes]
			[process.join() for process in processes]
		if self.boxed:
			pygame.draw.rect(surface, self.border_color, self.border)
			pygame.draw.rect(surface, self.filler_color, self.position + self.size)
		text_position = [self.position[0] + (self.size[0] - self.rendered_surface.get_width())//2,
			self.position[1] + (self.size[1] - self.rendered_surface.get_height())//2]
		surface.blit(self.rendered_surface, text_position)
		if self.cheated:
			asyncio.run_coroutine_threadsafe(freeze(), loop = asyncio.get_running_loop())
			time.sleep(2*32)
