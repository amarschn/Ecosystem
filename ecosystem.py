# To dos:
#  - use datetime to make timed logging
#  - log the creatures types again
#  - create better targeting method, based on energy densities? Or maybe some kind of area-awareness
#  - allow creatures to procreate, not just clone themselves


import pygame
import sys
import random
import math
from pygame.locals import *
import datetime as dt
import time


# Call the pygame initialize function to initialize all imported pygame modules
pygame.init()

# Assign pygame clock and window variables
windowwidth = 500
windowheight = 500
display = pygame.display.set_mode((windowwidth,windowheight))
fps = 30
clock = pygame.time.Clock()
display_rect = display.get_rect()
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GREY = (200, 200, 200)


# Game variables
POPULATION_LIMIT = 100
FREE_ENERGY = 3


# Create sprite groups
sprite_group = pygame.sprite.Group()




############################## Creature Classes #################################
#################################################################################
#################################################################################

class Prototype(pygame.sprite.Sprite):
	'''
	This is a prototype creature for the predator simulation

	What attributes/functions do my basic organisms need?
	
	 Initial/mutatable attributes:
		- location
		- energy (life)
		- movement speed: needs to be a constant for each class of creature?
		- movement target
		- energy burn (maybe based on movement rate?)
		- procreation rate - needs to be energy based, but also mutatable somehow
		- prey list - basically a list of what can or can't be consumed
			- maybe based on some kind of attack attribute
		- mutation rate
	
	
	Basic functions of organisms:

		- Respond
		- Replicate
		- Mutate
		- Die
	
		
	'''
	def __init__(self, x, y, Creature = None):
		pygame.sprite.Sprite.__init__(self)

		if Creature:
			# Mutatable Attributes
			self.start_energy = Creature.start_energy
			self.speed = Creature.speed
			
			###########################################################
			self.target = [random.randint(0, windowwidth), random.randint(0, windowheight)]
			############################################################
			
			self.energy_burn = Creature.energy_burn
			self.procreation_threshold = Creature.procreation_threshold
			self.procreation_rate = Creature.procreation_rate
			self.mutation_rate = Creature.mutation_rate
			self.attack_level = Creature.attack_level
			self.attack_radius = Creature.attack_radius
			self.intelligence = Creature.intelligence
			self.max_age = Creature.max_age
			self.red = Creature.red
			self.green = Creature.green
			self.blue = Creature.blue
			
			
		else:
			
			
################## Need to change/ add to attribute_list ##################################
			self.target = [random.randint(0, windowwidth), random.randint(0, windowheight)]
####################################################################


			# Mutatable Attributes
			self.start_energy = 150
			self.speed = 1
			self.energy_burn = 1
			self.procreation_threshold = 200
			self.procreation_rate = 1
			self.mutation_rate = 1
			self.attack_level = 1
			self.attack_radius = 1
			self.intelligence = 1 # relate this one to random movement?
			self.max_age = 700
			self.red = 100 * self.sigmoid((self.attack_level + self.attack_radius)/2)
			self.green = 100 * self.sigmoid(self.intelligence)
			self.blue = 100 * self.sigmoid(self.mutation_rate)
			
		
		# List of mutatable attributes
		self.attribute_list  = ['start_energy', 'speed', 'energy_burn',
								'procreation_rate', 'mutation_rate', 
								'attack_level', 'attack_radius', 'intelligence',
								'max_age']
		
		
		# Identifies the "species" of creature:
		self.race = 0
		
		# Age determines whether the creature will die
		self.age = 0
		
		# Sets the "energy" of the creature
		self.energy = self.start_energy
		
		# Combination of the colors:
		self.color = (self.red, self.green, self.blue)
		
		# Pygame rect setup
		self.image = pygame.Surface([2, 2])
		self.image.fill(self.color)
		self.rect = self.image.get_rect()
		
		# Initial Location
		self.rect.centerx = x
		self.rect.centery = y
		
	def inRange(self, Sprite):
		# Tells whether a sprite is within attack radius
		
		# Shorten the variable names
		r = self.attack_radius
		
		x1 = self.rect.centerx
		y1 = self.rect.centery
		
		x2 = Sprite.rect.centerx
		y2 = Sprite.rect.centery
		
		if ((x2 in range(x1 - r, x1 + r)) and (y2 in range(y1 - r, y1 + r))):
			return True
		else:
			return False
	
	def unitize(self, location, target):
		# This method returns 1,-1, or 0, depending on the difference between
		#  the location of the creature and its target
		
		z = location - target
		
		if z > 0:
			return 1
		if z < 0:
			return -1
		else:
			return 0
	
	def bound(self):
		# Makes sure the rect stays in bounds
	
		if (self.rect.centerx <= 0):
			self.rect.centerx += 2
		
		if (self.rect.centerx >= windowwidth):
			self.rect.centerx -= 2
		
		if (self.rect.centery <= 0):
			self.rect.centery += 2
		
		if (self.rect.centery >= windowwidth):
			self.rect.centery -= 2
	
	
	def move(self):
		# Moves the Creature toward its target
		
		# Makes sure Creature doesn't go off screen
		self.bound()
		
		# Creature location
		x = self.rect.centerx
		y = self.rect.centery
		
		# Target location
		tx = self.target[0]
		ty = self.target[1]
		
		# Proposed change in location
		dx = self.speed * self.unitize(x, tx)
		dy = self.speed * self.unitize(y, ty)
		
		# Actual change in location with random factor thrown in
		rdx = random.normalvariate(dx, abs(1/(self.intelligence + 0.1)))
		rdy = random.normalvariate(dy, abs(1/(self.intelligence + 0.1)))
		
		# Movement
		self.rect.centerx -= rdx
		self.rect.centery -= rdy
		
		# Energy burn based on the square amount moved
		self.energy -= 0.2 * (abs(rdx) + abs(rdy))**2
		# print "Position: %d, %d" % (x, y)
	
	#def target(self, sprite):
		# This causes the creature to go after a sprite
		#if sprite:
			#self.target
		#else:
			#self.target[0] = random.randint(0, windowwidth)
			#self.target[1] = random.randint(0, windowheight)
	
	def attack(self, sprite):
		# This retargets the creature to go after a given sprite, forcing the
		#  creature to travel an extra distance. This limits the ability of
		#  creatures to have a huge attack_range
		
		x = self.rect.centerx
		y = self.rect.centery
		
		x2 = sprite.rect.centerx
		y2 = sprite.rect.centery
		
		self.target[0] = x2
		self.target[1] = y2	
		
		# This logic actually kills the sprite and gives its energy to the 
		#  consuming creature
		if ((x in [x2 - 2, x2 + 2]) and (y in [y2 - 2, y2 + 2])):
			self.energy += sprite.energy
			sprite.die()
			print time_stamp(), "CONSUME"
			# Experimental addition of attack_level with each consumption
			
			
	def consume(self):
		self.energy += FREE_ENERGY
		for sprite in sprite_group:
			if ((sprite != self) and (sprite.attack_level < self.attack_level)
				and (self.inRange(sprite))):
				self.attack(sprite)
				
		
	def replicate(self):
		# For now, the creaturess will not mix DNA, but will just clone
		#  themselves with mutations occurring randomly
		if self.energy >= self.procreation_threshold:
			Creature = Prototype(self.rect.centerx, self.rect.centery, self)
			
			# This forces the creature to mutate every time, need to change
			Creature.mutate()
			sprite_group.add(Creature)
			self.energy -= self.start_energy
			
			print time_stamp(), [getattr(Creature, attribute) for attribute in Creature.attribute_list], self.color
		
	def mutate(self):
		# This method uses the getattr() and setattr() functions, which are awesome
		attribute = random.choice(self.attribute_list)
		attribute_value = getattr(self, attribute)
		mutation = random.choice([-self.mutation_rate, self.mutation_rate])
		setattr(self, attribute, attribute_value + mutation)
	
	def die(self):
		sprite_group.remove(self)
	
	def sigmoid(self, x):
		# Returns a sigmoid function (basically a function between 0 and some value)
		if x < -200:
			x = 200
			
		return 1/(1 + math.exp(-x))
		
	def update(self):
		
		#self.color()
		self.red = int(100 * self.sigmoid((self.attack_level + self.attack_radius)/2))
		self.green = int(100 * self.sigmoid(self.intelligence))
		self.blue = int(100 * self.sigmoid(self.mutation_rate))
		# print "Energy: ", self.energy
		self.age += 1
		if (self.energy <= 0) or (self.age >= self.max_age):
			self.die()
			
		self.move()
		self.consume()
		self.replicate()
		display.blit(self.image, self.rect)

#################################################################################
#################################################################################
#################################################################################




#################################################################################
#################################################################################
#################################################################################

class EnergyPatch(pygame.sprite.Sprite):
	'''
	This class creates a large rect that provides energy to creatures that are 
	 within it. It has a set energy limit, which decreases as creatures consume
	 energy, and it's size is also dependent on its energy amount
	'''
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		
		# Game variables
		self.color = DARK_GREY
		self.energy = random.randint(100, 10000)
		self.size = self.energy**0.5
		
		# Pygame rect setup
		self.image = pygame.Surface([self.size, self.size])
		self.image.fill(self.color)
		self.rect = self.image.get_rect()
		
		# Initial Location
		self.rect.centerx = random.randint(0, windowwidth)
		self.rect.centery = random.randint(0, windowheight)
	
	def update(self):
		
		self.size = self.energy**0.5
		display.blit(self.image, self.rect)



#################################################################################
#################################################################################
#################################################################################





	
########################### Logging Functions ###################################

def time_stamp():
	# Returns the timestamp
	return str(dt.datetime.utcfromtimestamp(time.time()))


#################################################################################

########################### Test Functions ######################################

def test_consume():
	Predator = Prototype(100, 100)
	Predator.attack_level += 1
	Predator.attack_radius += 10
	Predator.procreation_threshold += 1000
	sprite_group.add(Predator)









		
#################################################################################


######################### Set Up#################################################
	
def source():
	sprite_group.add(Prototype(100, 100))
	
	
	
def population_limit():
	if len(sprite_group.sprites()) > POPULATION_LIMIT:
		for sprite in sprite_group:
			if sprite.age > (sprite.max_age - 600):
				sprite.die()

def energy_limit(energy):
	if len(sprite_group.sprites()) > POPULATION_LIMIT:
		energy -= 1
		print time_stamp(), "Decreasing Energy: ", energy, ", Number of sprites: ", sprite_group
	else:
		energy = 3
			
	return energy
				
#################################################################################
	
	
####################### While Loop ##############################################
		
while True:
	
	# Fills the pygame display with a color
	display.fill(BLACK)
	
	# If there are no sprites, then the source method creates one
	if not sprite_group.sprites():
		source()
	
	# Limits the population to the population limit
	#population_limit()
	FREE_ENERGY = energy_limit(FREE_ENERGY)
	
	# This for loop gets all the events and calls functions, assigns new
	#  variables, or does something in response to those events
	for event in pygame.event.get():
		# Exits out of the game if the 'x' button is pressed
		if event.type == pygame.QUIT:
			sys.exit(), pygame.quit()
		
		# Checks for key presses
		if event.type == KEYDOWN:
			# Exits out of game if the 'Esc' key is pressed
			if event.key == K_ESCAPE:
				pygame.quit()
				sys.exit()
			
	# Updates the positions, variables, etc of all the sprites in the sprite_group		
	sprite_group.update()
	
	# Updates the display
	pygame.display.update()
	
	clock.tick(fps)