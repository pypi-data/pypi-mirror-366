import os
import cv2
from automatic_meter_reader import AutomaticMeterReader

def test_readout():
    img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_image.jpg")
    img = cv2.imread(img_path)

    camera_model = "espcam_120_deg"
    meter_model = "wehrle_hot"
    amr = AutomaticMeterReader(camera_model, meter_model)
    res = amr.readout(img)

    assert res is not None
    print("Measurement: %.3f" % (res))
    assert abs(res - 935.780) < 1e-2