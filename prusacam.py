from picamera2 import Picamera2
import time
picam2 = Picamera2()
camera_config = picam2.create_still_configuration()
picam2.configure(camera_config)
picam2.start()
time.sleep(2)
picam2.capture_file("pytest.jpg")
picam2.stop()