import pygame as pg


class Spritesheet():
	def __init__(self, filename):
		try:
			self.spritesheet = pg.image.load(filename).convert_alpha()
		except pg.error as e:
			print(f'Unable to load spritesheet image: {filename}')
			raise SystemExit(e)

	def sprite_at(self, rect, colorkey=None):
		# Loads a single sprite
		rect = pg.Rect(rect)
		sprite = pg.Surface(rect.size).convert()
		sprite.blit(self.spritesheet, (0, 0), rect)
		if colorkey is not None:
			if colorkey == -1:
				colorkey = sprite.get_at((0, 0))
			sprite.set_colorkey(colorkey, pg.RLEACCEL)
		return sprite

	def sprites_at(self, rects, colorkey=None):
		# Loads multiple sprites and returns them as a list
		return [self.sprite_at(rect, colorkey) for rect in rects]