## MyLoyalFilmer
OpenCV, Raspberry PI, Yahboom G1 Tank loyal filmer project.

### Project requirements
```
    py -m pip install --upgrade pip setuptools wheel
    py -m pip install -r requirements.txt
```

## Battery
The battery takes approximately 1 hour and 10 minutes to charge.

### Color track test

Camera image is mirrored.

Film saving resolution: 640 X 480
Film display resolution: 640 X 480

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

### Color track notes

Color track tutorial code is prepared for one time and one direction only.

Color track work.

Resolution
----------
640 X 480

Center
------
320 X 240

Rule of three for x
-------------------

With X angle, we have target dot
With current x-angle, we have center dot 320
X/current x-angle = target dot/320

X = current x-angle * target dot/320

Example
-------
X = 160 * (204.7943878173828/320) = 102,397195
    degrees * pixels/pixels
    degrees * ...
X = 160 * (500/320) = 250

Base example
------------
X = 90 * 0/320 = 0


Rule of three for y
-------------------

With Y angle, we have target dot
With current y-angle, we have center dot 240
X/current x-angle = target dot/240

Y = current y-angle * target dot/240

This is not right because dot 0 0 doesn't mean 0 0 angle and 640 240 doesn't mean 180 180 angle.

### Commands

cd  Yahboom_Project/MyLoyalFilmer/src

python3 main.py -desired_duty_cycle 20 -process_timeout 120 -initial_delay 25 -color_to_track RED -mode COLOR_TRACK -initial_x_servo_angle 2300 -initial_y_servo_angle 1600 -tracking_laps 0

python3 main.py -desired_duty_cycle 20 -process_timeout 30 -initial_delay 25 -color_to_track RED -mode COLOR_TRACK -initial_x_servo_angle 160 -initial_y_servo_angle 80 -tracking_laps 0 -alternative_camera_servos no -debug yes

python3 Yahboom_Project/MyLoyalFilmer/src/main.py -desired_duty_cycle 40 -process_timeout 30 -initial_delay 25 -color_to_track RED -mode INFINITE_TRACK_LINE_AND_COLOR_TRACK -initial_x_servo_angle 160 -initial_y_servo_angle 80 -tracking_laps 0 -alternative_camera_servos no -debug no


cd /home/pi
cd  Yahboom_Project/MyLoyalFilmer/src

### Servo movement notes

Servos turn better degree by degree. Pulse widht unit by pulse width unit works bad. Direct turning works good but is inconsistent.

Test.

python3 main.py -mode TEST_CAMERA_SERVO_CONTROL -alternative_camera_servos yes

### Camera notes

1280*960 resolution seems equal or even worse, and frame rate is worse.
640*480 resolution is good.

FPSs are consistently better with AVI format than with MP4, but only 0.1 - 0.2 FPS.

 v4l2-ctl --list-formats-ext
ioctl: VIDIOC_ENUM_FMT
        Type: Video Capture

        [0]: 'YUYV' (YUYV 4:2:2)
                Size: Discrete 640x480
                        Interval: Discrete 0.033s (30.000 fps)
                Size: Discrete 352x288
                        Interval: Discrete 0.033s (30.000 fps)
                Size: Discrete 320x240
                        Interval: Discrete 0.033s (30.000 fps)
                Size: Discrete 176x144
                        Interval: Discrete 0.033s (30.000 fps)
                Size: Discrete 160x120
                        Interval: Discrete 0.033s (30.000 fps)
                Size: Discrete 1280x960
                        Interval: Discrete 0.033s (30.000 fps)
        [1]: 'MJPG' (Motion-JPEG, compressed)
                Size: Discrete 640x480
                        Interval: Discrete 0.033s (30.000 fps)
                Size: Discrete 352x288
                        Interval: Discrete 0.033s (30.000 fps)
                Size: Discrete 320x240
                        Interval: Discrete 0.033s (30.000 fps)
                Size: Discrete 176x144
                        Interval: Discrete 0.033s (30.000 fps)
                Size: Discrete 160x120
                        Interval: Discrete 0.033s (30.000 fps)
                Size: Discrete 1280x960
                        Interval: Discrete 0.033s (30.000 fps)


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
