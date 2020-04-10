# PanTilt-Face-Tracking-System

The goal of pan and tilt object tracking is for the camera to stay centered upon an object. Typically this tracking is accomplished with
two servos. In our case, we have one servo for panning left and right. We have a separate servo for tilting up and down.

We have four processes:
- [Object center](https://github.com/akshaykrishak/PanTilt-Face-Tracking-System/blob/master/object_detection/objcenter.py) - Finds the face 
- [PID A](https://github.com/akshaykrishak/PanTilt-Face-Tracking-System/blob/master/object_detection/pid.py) - Panning 
- [PID B](https://github.com/akshaykrishak/PanTilt-Face-Tracking-System/blob/master/object_detection/pid.py) - Tilting 
- [Set servos](https://github.com/akshaykrishak/PanTilt-Face-Tracking-System/blob/master/pan_tilt_tracking.py) - Takes the output of the PID processes and tells each servo the angle it needs to steer to

Finally, we’ll tune our PIDs independently and deploy the system.

