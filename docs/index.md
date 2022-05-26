## MyLoyalFilmer
OpenCV, Raspberry PI, Yahboom G1 Tank loyal filmer project.

## Project requirements
```
    py -m pip install --upgrade pip setuptools wheel
    py -m pip install -r requirements.txt
```

## Color track test

Camera image is mirrored.

center: Write down X and Y value: X = 292.5 Y = 401.0
Countours: 25
Color radius:183.11550903320312


left: Write down X and Y value: X = 204.7943878173828 Y = 382.2201232910156
Countours: 38
Color radius:104.79911804199219

right: 
Countours: 35
Color radius:115.29320526123047
Write down X and Y value: X = 461.5 Y = 380.5

# Color track notes

Color track tutorial code is prepared for one time and one direction only.

## Commands

cd  Yahboom_Project/MyLoyalFilmer/src

python3 main.py -desired_duty_cycle 20 -process_timeout 120 -initial_delay 25 -color_to_track RED -mode COLOR_TRACK -initial_x_servo_angle 2100 -initial_y_servo_angle 500 -tracking_laps 0


cd /home/pi
cd  Yahboom_Project/MyLoyalFilmer/src

### Markdown

Markdown is a lightweight and easy-to-use syntax for styling your writing. It includes conventions for

```markdown
Syntax highlighted code block

# Header 1
## Header 2
### Header 3

- Bulleted
- List

1. Numbered
2. List

**Bold** and _Italic_ and `Code` text

[Link](url) and ![Image](src)
```
