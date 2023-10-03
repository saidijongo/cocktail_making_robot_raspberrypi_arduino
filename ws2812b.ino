#include <FastLED.h>

#define NUM_LEDS 6
#define LED_PIN 6

CRGB leds[NUM_LEDS];

#define GROUP_SIZE 2
#define ANIMATION_DELAY 100
#define GLOBAL_BRIGHTNESS 255
bool isFinished = false;

void setup() {
  FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setMaxPowerInVoltsAndMilliamps(5, 500);
  FastLED.setBrightness(100);
  Serial.begin(115200);
  FastLED.clear();
  FastLED.show();
}

void blinkAnimation() {
  static bool isWhite = true;
  while (!isFinished) {
    if (isWhite) {
      fill_solid(leds, NUM_LEDS, CRGB::White);
    } else {
      fill_solid(leds, NUM_LEDS, CRGB::Green);
    }
    FastLED.show();
    isWhite = !isWhite;
    delay(ANIMATION_DELAY);
    if (Serial.available() > 0) {
      String command = Serial.readStringUntil('\n'); // Read until newline character
      command.trim(); // Remove leading/trailing whitespace
      if (command == "FINISHED") {
        stopAnimation();
      } else if (command == "ADIOS") {
        setColor(CRGB(0, 255, 255)); // Set the background color (Ocean blue)
        moveAnimation(CRGB::Red, CRGB(0, 255, 255), GROUP_SIZE); // Move green LEDs on Ocean blue background
        Serial.println("ADIOS LED pattern");
      } else if (command == "LONGISLAND") {
        setColor(CRGB(139, 69, 19)); // Set the background color (Brownish Yellow)
        moveAnimation(CRGB::Red, CRGB(139, 69, 19), GROUP_SIZE); // Move green LEDs on Brownish Yellow background
        Serial.println("Long Island Ice Tea LED pattern");
      } else if (command == "PEACHCRUSH") {
        setColor(CRGB(139, 69, 19)); // Set the background color (Brownish Yellow)
        moveAnimation(CRGB::Red, CRGB(0, 255, 0), GROUP_SIZE); // Move green LEDs on Green background
        Serial.println("Peach Crush LED pattern");
      } else if (command == "MIDORISOUR") {
        setColor(CRGB(255, 140, 0)); // Set the background color (Orange)
        moveAnimation(CRGB::Red, CRGB(0, 255, 0), GROUP_SIZE); // Move green LEDs on Green background
        Serial.println("Midori Sour LED pattern");
      } else if (command == "ALLMOTORS") {
        setColor(CRGB(148, 0, 211)); // Set the background color (Violet)
        moveAnimation(CRGB::Green, CRGB(148, 0, 211), GROUP_SIZE); // Move green LEDs on Violet background
        Serial.println("ALLMOTORS LED pattern");
      } else if (command == "PUMPNUMBER") {
        setColor(CRGB(0, 0, 255)); // Set the background color (Blue)
        moveAnimation(CRGB::Green, CRGB(0, 0, 255), GROUP_SIZE); // Move green LEDs on Blue background
        Serial.println("PUMPNUMBER LED pattern");
      } else if (command == "COMPLETE") {
        blinkAnimation();
        Serial.println("Complete LED pattern");
      } else {
        Serial.println("Invalid command");
      }
    }
  }
}

void setColor(CRGB color) {
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = color;
  }
  FastLED.show();
}

void stopAnimation() {
  isFinished = true;
  FastLED.clear(); // Turn off all LEDs
  FastLED.show();
  Serial.println("Animation stopped");
}

void moveAnimation(CRGB bgColor, CRGB fgColor, int groupSize) {
  while (!isFinished) {
    // Left to right animation
    for (int i = 0; i <= NUM_LEDS - groupSize && !isFinished; i++) {
      for (int j = 0; j < groupSize; j++) {
        leds[i + j] = fgColor;
      }
      FastLED.show();
      delay(ANIMATION_DELAY);
      for (int j = 0; j < groupSize; j++) {
        leds[i + j] = bgColor;
      }
      if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n'); // Read until newline character
        command.trim(); // Remove leading/trailing whitespace
        if (command == "FINISHED") {
          stopAnimation();
        } else if (command == "ADIOS") {
          setColor(CRGB(0, 255, 255)); // Set the background color (Ocean blue)
          moveAnimation(CRGB::Red, CRGB(0, 255, 255), GROUP_SIZE); // Move green LEDs on Ocean blue background
          Serial.println("ADIOS LED pattern");
        } else if (command == "LONGISLAND") {
          setColor(CRGB(139, 69, 19)); // Set the background color (Brownish Yellow)
          moveAnimation(CRGB::Red, CRGB(139, 69, 19), GROUP_SIZE); // Move green LEDs on Brownish Yellow background
          Serial.println("Long Island Ice Tea LED pattern");
        } else if (command == "PEACHCRUSH") {
          setColor(CRGB(255, 229, 180)); // Set the background color (Brownish Yellow)
          moveAnimation(CRGB::Red, CRGB(255, 229, 180), GROUP_SIZE); // Move green LEDs on Green background
          Serial.println("Peach Crush LED pattern");
        } else if (command == "MIDORISOUR") {
          setColor(CRGB(255, 140, 0)); // Set the background color (Orange)
          moveAnimation(CRGB::Red, CRGB(0, 255, 0), GROUP_SIZE); // Move green LEDs on Green background
          Serial.println("Midori Sour LED pattern");
        } else if (command == "ALLMOTORS") {
          setColor(CRGB(148, 0, 211)); // Set the background color (Violet)
          moveAnimation(CRGB::Green, CRGB(148, 0, 211), GROUP_SIZE); // Move green LEDs on Violet background
          Serial.println("ALLMOTORS LED pattern");
        } else if (command == "PUMPNUMBER") {
          setColor(CRGB(0, 0, 255)); // Set the background color (Blue)
          moveAnimation(CRGB::Green, CRGB(0, 0, 255), GROUP_SIZE); // Move green LEDs on Blue background
          Serial.println("PUMPNUMBER LED pattern");
        } else if (command == "COMPLETE") {
          blinkAnimation();
          Serial.println("Complete LED pattern");
        } else {
          Serial.println("Invalid command");
        }
      }
    }

    // Right to left animation
    for (int i = NUM_LEDS - groupSize - 1; i >= 0 && !isFinished; i--) {
      for (int j = 0; j < groupSize; j++) {
        leds[i + j] = fgColor;
      }
      FastLED.show();
      delay(ANIMATION_DELAY);
      for (int j = 0; j < groupSize; j++) {
        leds[i + j] = bgColor;
      }
      if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n'); // Read until newline character
        command.trim(); // Remove leading/trailing whitespace
        if (command == "FINISHED") {
          stopAnimation();
        } else if (command == "ADIOS") {
          setColor(CRGB(0, 255, 255)); // Set the background color (Ocean blue)
          moveAnimation(CRGB::Red, CRGB(0, 255, 255), GROUP_SIZE); // Move green LEDs on Ocean blue background
          Serial.println("ADIOS LED pattern");
        } else if (command == "LONGISLAND") {
          setColor(CRGB(139, 69, 19)); // Set the background color (Brownish Yellow)
          moveAnimation(CRGB::Red, CRGB(139, 69, 19), GROUP_SIZE); // Move green LEDs on Brownish Yellow background
          Serial.println("Long Island Ice Tea LED pattern");
        } else if (command == "PEACHCRUSH") {
          setColor(CRGB(255, 229, 180)); // Set the background color (Brownish Yellow)
          moveAnimation(CRGB::Red, CRGB(255, 229, 180), GROUP_SIZE); // Move green LEDs on Green background
          Serial.println("Peach Crush LED pattern");
        } else if (command == "MIDORISOUR") {
          setColor(CRGB(255, 140, 0)); // Set the background color (Orange)
          moveAnimation(CRGB::Red, CRGB(0, 255, 0), GROUP_SIZE); // Move green LEDs on Green background
          Serial.println("Midori Sour LED pattern");
        } else if (command == "ALLMOTORS") {
          setColor(CRGB(148, 0, 211)); // Set the background color (Violet)
          moveAnimation(CRGB::Green, CRGB(148, 0, 211), GROUP_SIZE); // Move green LEDs on Violet background
          Serial.println("ALLMOTORS LED pattern");
        } else if (command == "PUMPNUMBER") {
          setColor(CRGB(0, 0, 255)); // Set the background color (Blue)
          moveAnimation(CRGB::Green, CRGB(0, 0, 255), GROUP_SIZE); // Move green LEDs on Blue background
          Serial.println("PUMPNUMBER LED pattern");
        } else if (command == "COMPLETE") {
          blinkAnimation();
          Serial.println("Complete LED pattern");
        } else {
          Serial.println("Invalid command");
        }
      }
    }
  }
}


void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Read until newline character
    command.trim(); // Remove leading/trailing whitespace

    if (command == "BLINK") {
      blinkAnimation();
    } else if (command == "ADIOS") {
      setColor(CRGB(0, 255, 255)); // Set the background color (Ocean blue)
      moveAnimation(CRGB::Red, CRGB(0, 255, 255), GROUP_SIZE); // Move green LEDs on Ocean blue background
      Serial.println("ADIOS LED pattern");
    } else if (command == "LONGISLAND") {
      setColor(CRGB(139, 69, 19)); // Set the background color (Brownish Yellow)
      moveAnimation(CRGB::Red, CRGB(139, 69, 19), GROUP_SIZE); // Move green LEDs on Brownish Yellow background
      Serial.println("Long Island Ice Tea LED pattern");
    } else if (command == "PEACHCRUSH") {
      setColor(CRGB(255, 229, 180)); 
      moveAnimation(CRGB::Red, CRGB(255, 229, 180), GROUP_SIZE); // Move green LEDs on Green background
      Serial.println("Peach Crush LED pattern");
    } else if (command == "MIDORISOUR") {
      setColor(CRGB(255, 140, 0)); // Set the background color (Orange)
      moveAnimation(CRGB::Red, CRGB(0, 255, 0), GROUP_SIZE); // Move green LEDs on Green background
      Serial.println("Midori Sour LED pattern");
    } else if (command == "ALLMOTORS") {
      setColor(CRGB(148, 0, 211)); // Set the background color (Violet)
      moveAnimation(CRGB::Green, CRGB(148, 0, 211), GROUP_SIZE); // Move green LEDs on Violet background
      Serial.println("ALLMOTORS LED pattern");
    } else if (command == "PUMPNUMBER") {
      setColor(CRGB(0, 0, 255)); // Set the background color (Blue)
      moveAnimation(CRGB::Green, CRGB(0, 0, 255), GROUP_SIZE); // Move green LEDs on Blue background
      Serial.println("PUMPNUMBER LED pattern");
    } else if (command == "COMPLETE") {
      blinkAnimation();
      Serial.println("Complete LED pattern");
    } else if (command == "FINISHED") {
      stopAnimation();
    } else {
      Serial.println("Invalid command");
    }
  }
}
