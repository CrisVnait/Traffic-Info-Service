import sys
import urllib
from multiprocessing import Process, Manager

import webserver
import ccnn

# URLs of the relevant cameras
cameras = [
    ("Karlsruhe-Nord-A", "https://www.svz-bw.de/kamera/ftpdata/KA031/KA031_gross.jpg?1525809142"),
    ("Karlsruhe-Nord-B", "https://www.svz-bw.de/kamera/ftpdata/KA032/KA032_gross.jpg?1525809471"),
    ("Karlsruhe-Mitte-A", "https://www.svz-bw.de/kamera/ftpdata/KA041/KA041_gross.jpg?1525809496"),
    ("Karlsruhe-Mitte-B", "https://www.svz-bw.de/kamera/ftpdata/KA042/KA042_gross.jpg?1525809515"),
    ("Ettlingen-A", "https://www.svz-bw.de/kamera/ftpdata/KA061/KA061_gross.jpg?1525809536"),
    ("Ettlingen-B", "https://www.svz-bw.de/kamera/ftpdata/KA062/KA062_gross.jpg?1525809551"),
]

# Number of cars that are defined as 100% traffic density for the respective camera
camera_max_cars = {
    "Karlsruhe-Nord-A": 33,
    "Karlsruhe-Nord-B": 36,
    "Karlsruhe-Mitte-A": 28,
    "Karlsruhe-Mitte-B": 36,
    "Ettlingen-A": 30,
    "Ettlingen-B": 29,
}


def retrieve_image(url, path_to_save_location):
    opener = urllib.request.build_opener()
    opener.addheaders = [("Referer", "https://www.svz-bw.de")]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, path_to_save_location)


def start_json_server():
    print("Starting jsonserver")
    webserver.start(predictions)


def count_cars(camera_name, url, predictions):
    while True:
        # Download image
        path_to_save_location = "data/A5-webcams/images/{}.jpg".format(camera_name)
        retrieve_image(url, path_to_save_location)

        prediction = ccnn.main(sys.argv[1:], camera_name + ".jpg")
        predictions[camera_name] = prediction  # Variable shared between processes
        print(predictions)


if __name__ == '__main__':
    with Manager() as manager:
        predictions = manager.dict()  # Variable shared between processes

        # Start a new process for each camera
        for camera in cameras:
            camera_name = camera[0]
            url = camera[1]
            process = Process(target=count_cars, args=(camera_name, url, predictions))
            process.start()

        print("CCNN-processes started")

        server_process = Process(target=start_json_server)
        server_process.start()
        server_process.join()


