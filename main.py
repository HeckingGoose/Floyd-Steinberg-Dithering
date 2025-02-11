# Imports
import pygame, os, sys

# Const
FILE_TYPE = ".png"
SOURCE_FILENAME = "AlbumArt"
OUTPUT_PATH = "Output"
OUTPUT_FILENAME = SOURCE_FILENAME + "_out"
TARGET_HEIGHT = 600
PROCESSING_TITLE = "Processing..."
DONE_TITLE = "Displaying: " + OUTPUT_FILENAME

# Config
BITSPERCHANNEL = 1
QUANTISATION_LEVELS = 2 ** BITSPERCHANNEL
QUANTISE_SIZE = 255 / (QUANTISATION_LEVELS - 1)

# Initialise display part of pygame
pygame.display.init()

# Load test image
raw = pygame.image.load(SOURCE_FILENAME + FILE_TYPE)

# Fetch dimensions
width, height = raw.get_size()

# Create a display to make pygame happy
display = pygame.display.set_mode(((TARGET_HEIGHT / height) * width, TARGET_HEIGHT), 0, 32)

# Convert image to a format pygame will play nicer with
source = raw.convert_alpha()

# Set icon
pygame.display.set_icon(source)

# Set text
pygame.display.set_caption(PROCESSING_TITLE)

# Create an output surface
output = pygame.surface.Surface((width, height))

# Functions
def Clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))
def GetNewValueAndError(sourceValue):
    # Round to quant size
    new = int(QUANTISE_SIZE * round(sourceValue/QUANTISE_SIZE))
    error = sourceValue - new
    return (new, error)
    
    return (new, error)
def TrySet(surface, x, y, errorR, errorG, errorB, errorA, percent):
    # If this pixel is valid
    if x >= 0 and y >= 0 and x < surface.get_size()[0] and y < surface.get_size()[1]:
        # Get the source colour
        raw = surface.get_at((x, y))

        # Add error and clamp
        raw = (Clamp(raw.r + errorR * percent, 0, 255), Clamp(raw.g + errorG * percent, 0, 255), Clamp(raw.b + errorB * percent, 0, 255), Clamp(raw.a + errorA * percent, 0, 255))

        # Apply
        surface.set_at((x, y), raw)
    # Return surface 
    return surface
def DoleOutError(surface, x, y, errorR, errorG, errorB, errorA):
    # Error spread:
    # Source pixel: None
    # Right pixel: 7/16
    # Bottom Right pixel: 1/16
    # Bottom pixel: 5/16
    # Bottom Left pixel: 3/16

    # Do error
    surface = TrySet(surface, x + 1, y, errorR, errorG, errorB, errorA, 7 / 16)
    surface = TrySet(surface, x + 1, y + 1, errorR, errorG, errorB, errorA, 1 / 16)
    surface = TrySet(surface, x, y + 1, errorR, errorG, errorB, errorA, 5 / 16)
    surface = TrySet(surface, x - 1, y + 1, errorR, errorG, errorB, errorA, 3 / 16)

    # Return surf
    return surface

# Loop through every row of pixels
for y in range(height):
    # Loop through pixel in the current row
    for x in range(width):
        # Get colour of this pixel
        colour = source.get_at((x, y))

        # Get new values of this pixel
        r, errorR = GetNewValueAndError(colour.r)
        g, errorG = GetNewValueAndError(colour.g)
        b, errorB = GetNewValueAndError(colour.b)
        a, errorA = GetNewValueAndError(colour.a)

        # Dole out error
        source = DoleOutError(source, x, y, errorR, errorG, errorB, errorA)

        # Set new pixel colour
        output.set_at((x, y), (r, g, b, a))
        
# Set text
pygame.display.set_caption(DONE_TITLE)

# Check directory exists
if (not os.path.isdir(OUTPUT_PATH)):
    # Make path
    os.mkdir(OUTPUT_PATH)

# Write out
pygame.image.save(output, OUTPUT_PATH + "/" + OUTPUT_FILENAME + FILE_TYPE)

# Set image
display.blit(pygame.transform.scale(output, ((TARGET_HEIGHT / height) * width, TARGET_HEIGHT)), (0, 0))
pygame.display.update()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
