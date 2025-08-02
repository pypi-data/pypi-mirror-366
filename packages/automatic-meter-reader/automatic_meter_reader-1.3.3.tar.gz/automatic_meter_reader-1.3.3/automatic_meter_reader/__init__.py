import os
import cv2
import json
import numpy as np
from datetime import datetime
from meter_digits_recognizer import MeterDigitsRecognizer

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

def rotate_image(image, angle_deg):
    image_center = tuple((np.array(image.shape[1::-1]) - 1.0) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle_deg, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

class AutomaticMeterReader:
    
    def __init__(self, camera_model, meter_model):
        self.camera_model = camera_model
        self.meter_model = meter_model
        
        with open(os.path.join(PACKAGE_DIR, "cameras", "%s.json" % (self.camera_model)), "r") as f:
            camcalib = json.load(f)
        self.camera_matrix = np.resize(np.array(camcalib["camera_matrix"]), (3, 3))
        self.distortion_coefs = np.resize(np.array(camcalib["distortion_coefs"]), (1, len(camcalib["distortion_coefs"])))
        self.new_camera_matrix = np.resize(np.array(camcalib["new_camera_matrix"]), (3, 3))
        
        with open(os.path.join(PACKAGE_DIR, "meter_models", meter_model, "meter_config.json"), "r") as f:
            self.meter_config = json.load(f)
        self.template_imgs = []
        for template_conf in self.meter_config["templates"]:
            template_img = cv2.imread(os.path.join(PACKAGE_DIR, "meter_models", self.meter_model, template_conf["file"]))
            self.template_imgs.append(template_img)
    
        self.mdr = MeterDigitsRecognizer()
        self.img_original = None
        self.img_undistorted = None
        self.img_aligned = None
        self.img_debug = None

    def readout(self, img):
        self.img_original = img
        self.undistort_and_prepare()
        self.align_image()
        self.get_measurement()
        self.make_debug_image()
        return self.measurement
    
    def undistort_and_prepare(self):
        self.img_undistorted = cv2.undistort(self.img_original, self.camera_matrix, self.distortion_coefs, None, self.new_camera_matrix)
        # TODO: Integrate into new_camera_matrix
        if "pre_rotation_angle_deg" in self.meter_config:
            self.img_undistorted = rotate_image(self.img_undistorted.copy(), self.meter_config["pre_rotation_angle_deg"])
        if "pre_crop" in self.meter_config:
            x0, y0, dx, dy = self.meter_config["pre_crop"]
            x1, y1 = min(self.img_undistorted.shape[1], x0 + dx), min(self.img_undistorted.shape[0], y0 + dy)
            self.img_undistorted = self.img_undistorted[y0:y1, x0:x1]
        
    def align_image(self):
        src_points, dst_points = [], []
        for template_conf, template_img in zip(self.meter_config["templates"], self.template_imgs):
            x0, y0, dx, dy = template_conf["roi"]

            match = cv2.matchTemplate(self.img_undistorted, template_img, cv2.TM_CCORR_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match)
            top_left = max_loc

            src_points.append((top_left[0] + 0.5 * dx - 0.5, top_left[1] + 0.5 * dy - 0.5))
            dst_points.append((x0 + 0.5 * dx - 0.5, y0 + 0.5 * dy - 0.5))

        M = cv2.getAffineTransform(np.float32(src_points), np.float32(dst_points))
        self.img_aligned = cv2.warpAffine(self.img_undistorted, M, (self.img_undistorted.shape[1], self.img_undistorted.shape[0]), flags=cv2.INTER_LINEAR)

    def get_measurement(self):
        digit_imgs = []
        for i, digit_conf in enumerate(self.meter_config["register"]["digits"]):
            x0, y0, dx, dy = digit_conf["roi"]
            digit_img = self.img_aligned[y0:y0+dy, x0:x0+dx]
            digit_imgs.append(digit_img)
        predictions, confidences = self.mdr.run(digit_imgs)
        
        res = 0.0
        digits = self.meter_config["register"]["digits"]
        for i, digit_conf in enumerate(digits):
            if predictions[i] == 10:
                if i + 1 < len(digits):
                    res = None
                break
            res += digit_conf["multiplier"] * predictions[i]
        
        self.digit_imgs = digit_imgs
        self.predictions = predictions
        self.confidences = confidences
        self.measurement = res
    
    def make_debug_image(self):
        res = self.img_aligned.copy()
        stamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("stamp_str:", stamp_str)

        # Templates
        for template_conf in self.meter_config["templates"]:
            x0, y0, dx, dy = template_conf["roi"]
            pen_width = 1.0
            cv2.rectangle(res, (x0 - 1, y0 - 1), (x0 + dx, y0 + dy), (255, 0, 0), 1)

        # Register
        #x0, y0, dx, dy = self.meter_config["register"]["roi"]
        #cv2.rectangle(res, (x0 - 1, y0 - 1), (x0 + dx, y0 + dy), (0, 0, 255), 1)
        for digit_conf in self.meter_config["register"]["digits"]:
            x0, y0, dx, dy = digit_conf["roi"]
            cv2.rectangle(res, (x0 - 1, y0 - 1), (x0 + dx, y0 + dy), (0, 0, 255), 1)

        # Measurement
        x0, y0, dx, dy = self.meter_config["register"]["roi"]
        font_size = 1.0 / 465.0 * dx
        for i, digit_conf in enumerate(self.meter_config["register"]["digits"]):
            x0, y0, dx, dy = digit_conf["roi"]
            if self.confidences[i] < 0.9:
                color = (0, 0, 255)
            elif self.confidences[i] < 0.995:
                color = (33, 137, 235)
            else:
                color = (56, 245, 39)
            
            cv2.putText(res, "%s" % (str(self.predictions[i]) if self.predictions[i] <= 9 else "-"), (x0 + dx // 4, y0 - dy // 4), cv2.FONT_HERSHEY_SIMPLEX, font_size, color, 3, cv2.LINE_AA)    
            cv2.putText(res, "%.0f" % (1e2 * self.confidences[i]), (x0 - dx // 5, y0 - dy), cv2.FONT_HERSHEY_SIMPLEX, 0.8 * font_size, color, 3, cv2.LINE_AA)    

        # Stamp
        cv2.putText(res, stamp_str, (int(10 * font_size), int(res.shape[0] - 10 * font_size)), cv2.FONT_HERSHEY_SIMPLEX, 0.8 * font_size, color, 3, cv2.LINE_AA)    

        self.img_debug = res

if __name__ == "__main__":
    pass