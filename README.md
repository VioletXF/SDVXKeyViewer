# SDVXKeyViewer
A simple key viewer for Sound Voltex KONASUTE. [Demo(Youtube)](https://www.youtube.com/watch?v=YcGjHjSztH0)

[Download from Releases](https://github.com/VioletXF/SDVXKeyViewer/releases/latest)


![image](https://github.com/VioletXF/SDVXKeyViewer/assets/27609690/925e53b0-f5bb-4e17-833b-4ed886854f08)

# Shortcuts
- `Delete` - reset key counts
- `ESC` - exit

# Configuration
You can customize the viewer by editing `settings.ini`
```ini
[Keys]
start = 0
bt_a = 1
bt_b = 2
bt_c = 3
bt_d = 4
fx_l = 5
fx_r = 6

[Colors]
; opacity of backgrounds of buttons and tsumami
bg_opacity = 1
; opacity of buttons when pressed
button_led_opacity = 1
text_opacity = 1
; opacity of tsumami's direction indicator, when not rotating
tsumami_indicator_off_opacity = 0.2
; opacity of tsumami's direction indicator, when rotating
tsumami_indicator_on_opacity = 1
; opacity of tsumami's LED, rotating
tsumami_led_opacity = 0.2

[Size]
; size of a single BT in pixels
unit = 100
scroll_to_resize = true

[Other]
polling_rate = 240
always_on_top = false
; resets key counts when you press start
reset_counts_on_start = false
```
