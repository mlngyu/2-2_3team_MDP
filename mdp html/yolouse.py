import cv2
import torch
import threading
import mysql.connector
import queue
import cv2

objectnumber = 0
frame_queue = queue.Queue()
num = 0
max = 4

def get_frame():
    ret, frame = cap.read()
    # frame = cv2.flip(frame,0)
    # frame = cv2.resize(frame,dsize=(640,640))
    return ret,frame

def process_frames():
    global objectnumber
    global num

    ret, frame = get_frame()
    results = model(frame)
    confidences = results.xyxy[0][:, 4]
    class_label = results.xyxy[0][:, 5]
    threshold = 0.55
    high_confidence_indices = confidences > threshold
    boxes = results.xyxy[0][high_confidence_indices].cpu().numpy()
    objectnumber = int(len(results.xyxy[0][high_confidence_indices]))
    insert_query = "INSERT INTO test VALUES (%s,%s, %s)"
    delete_query = "DELETE FROM test ORDER BY number ASC LIMIT 1;"
    # cursor.execute(delete_query)
    # cursor.execute(insert_query,(str(objectnumber),str(num),str(max)))
    num += 1
    # connection.commit()
    color = (0, 255, 0)
    thickness = 2

    for box in boxes:
        start_x, start_y, end_x, end_y, confidence, class_label = box
        cv2.rectangle(frame, (int(start_x), int(start_y)), (int(end_x), int(end_y)), color, thickness)
        label = f'{model.names[int(class_label)]}: {confidence:.2f}'
        cv2.putText(frame, label, (int(start_x), int(start_y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)

    objectnumber_s = f'count : {objectnumber}'
    cv2.putText(frame, objectnumber_s, (20,30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
    frame_queue.put(frame)

host = '183.111.138.176'
user = 'imminho'
password = 'mu3102!!'
database = 'imminho'
connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
cursor = connection.cursor()
insert_query = "INSERT INTO test VALUES (0,0,0)"
delete_query = "DELETE FROM test"
# cursor.execute(delete_query)
# cursor.execute(insert_query)
# cursor.execute(insert_query)
# cursor.execute(insert_query)
# connection.commit()

model = torch.hub.load('ultralytics/yolov5', 'custom', path='C:/Users/user/Downloads/best8.pt', force_reload=True)
# model = torch.hub.load('ultralytics/yolov5', 'custom', path='C:/Users/user/Downloads/best5-int8.tflite', force_reload=True)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
# cap.set(cv2.CAP_PROP_FPS,1)

while(1):
    processing_thread = threading.Thread(target=process_frames)

    processing_thread.start()

    try:
        frame = frame_queue.get(timeout=1) 
        cv2.imshow('', frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            print('q')
            break
    except queue.Empty:
        pass

    processing_thread.join()

cap.release()
cv2.destroyAllWindows()