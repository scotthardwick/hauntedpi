import pygame, time

pygame.init()
pygame.mixer.init()
sounda= pygame.mixer.Sound("/home/pi/hauntedpi/scenes/audio/marketplace_1.wav")

sounda.play()
time.sleep (20)