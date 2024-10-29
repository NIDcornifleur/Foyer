import time
import random
from w1thermsensor import W1ThermSensor
from rpi_ws281x import PixelStrip, Color

# Configurations pour le WS2812B
LED_COUNT = 142        # Nombre de LEDs dans le strip
LED_PIN = 18          # Broche GPIO où est connecté le strip
LED_FREQ_HZ = 800000  # Fréquence LED signal
LED_DMA = 10          # DMA Channel
LED_BRIGHTNESS = 201  # Luminosité max
LED_INVERT = False    # Inversion signal
LED_CHANNEL = 0       # Channel

# Initialisation du strip LED
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

# Initialisation du capteur DS18B20
sensor = W1ThermSensor()

def get_color_temperature(temp_celsius):
    """
    Détermine la couleur de base en fonction de la température.
    """
    if temp_celsius < 40:
        return Color(0, 0, 255)  # Bleu pour les températures en dessous de 40
    elif 40 <= temp_celsius < 75:
        return Color(0, 255, 255)  # Cyan pour les températures entre 40 et 100
    elif 75 <= temp_celsius < 100:
        return Color(0, 255, 0)  # Vert pour les températures entre 100 et 150
    else:  # temp_celsius >= 150
        return Color(255, 0, 0)  # Rouge pour les températures au-dessus de 150

def flicker_effect(base_color, flicker_intensity=50):
    """
    Applique un effet de scintillement autour d'une couleur de base avec une intensité moyenne.
    """
    # Extraire les composantes RGB
    r = (base_color >> 16) & 0xFF
    g = (base_color >> 8) & 0xFF
    b = base_color & 0xFF
    
    # Appliquer une variation aléatoire douce autour de chaque composante
    r = max(0, min(255, r + random.randint(-flicker_intensity, flicker_intensity)))
    g = max(0, min(255, g + random.randint(-flicker_intensity, flicker_intensity)))
    b = max(0, min(255, b + random.randint(-flicker_intensity, flicker_intensity)))
    
    return Color(r, g, b)

def interpolate_color(color1, color2, factor):
    """
    Interpole entre deux couleurs en fonction d'un facteur (0 à 1).
    """
    r1 = (color1 >> 16) & 0xFF
    g1 = (color1 >> 8) & 0xFF
    b1 = color1 & 0xFF
    
    r2 = (color2 >> 16) & 0xFF
    g2 = (color2 >> 8) & 0xFF
    b2 = color2 & 0xFF
    
    r = int(r1 + (r2 - r1) * factor)
    g = int(g1 + (g2 - g1) * factor)
    b = int(b1 + (b2 - b1) * factor)
    
    return Color(r, g, b)

try:
    print("Script démarré. Initialisation des composants...")
    
    # Lecture initiale de la température
    temperature = sensor.get_temperature()
    base_color = get_color_temperature(temperature)
    print(f"Température initiale : {temperature:.2f}°C")

    while True:
        # Mettez à jour la température toutes les 10 secondes
        new_temperature = sensor.get_temperature()
        new_color = get_color_temperature(new_temperature)
        
        # Afficher la température
        print(f"Température : {new_temperature:.2f}°C")
        
        # Interpolation de la couleur
        for i in range(256):  # Nombre d'étapes de la transition
            factor = i / 255
            interpolated_color = interpolate_color(base_color, new_color, factor)
            
            # Appliquer le scintillement à chaque LED
            for j in range(strip.numPixels()):
                flicker_color = flicker_effect(interpolated_color)
                strip.setPixelColor(j, flicker_color)

            # Afficher les LEDs et attendre un court instant pour un scintillement fluide
            strip.show()
            time.sleep(1.1)  # Délai pour une transition plus fluide
            
        # Mettre à jour la couleur de base après la transition
        base_color = new_color

        # Pause pour éviter une lecture trop fréquente
        time.sleep(.10)

except KeyboardInterrupt:
    # Éteindre les LEDs avant de quitter
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()
    print("Script arrêté.")
