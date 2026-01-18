from ultralytics import YOLO
import cv2
import time
import numpy as np
from picamera2 import Picamera2

import paho.mqtt.client as mqtt

mqtt_broker_ip = "mqtt.alcoolis.me"

# MQTT
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to {mqtt_broker_ip} with result code {reason_code}")
    
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect

mqttc.connect(mqtt_broker_ip, 1883, 60)
print("test")
    
def detect_heads_yolo(image, model):
    """
    Détecte les têtes dans une seule frame et retourne l'image annotée, le temps d'exécution et le nombre de personnes détectées.
    Args:
        image (numpy.ndarray): Image d'entrée.
        model (YOLO): Modèle YOLOv8 chargé.
    Returns:
        output_image (numpy.ndarray): Image annotée avec les boîtes englobantes des têtes.
        inference_time (float): Temps d'inférence en secondes.
        people_count (int): Nombre de personnes détectées.
    """
    
    # Classe 0 = personne
    start_time = time.time()
    results = model(image, classes=[0], verbose=False, stream=False) 
    inference_time = time.time() - start_time
    
    output_image = image.copy()
    people_count = 0
    
    if results and results[0].boxes:
        people_count = len(results[0].boxes) 

        #for box in results[0].boxes:
            # Récuperer les coordonnées de la boîte qui entoure la personne
            #x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
            
            # Transformer la boîte de la personne en boîte de la tête pour eviter de saturer l'image
            #person_height = y2 - y1
            #head_height = int(person_height * 0.3) 

            # Dessin de la boîte de la tête
            #cv2.rectangle(output_image, 
                          #(x1, y1), 
                          #(x2, y1 + head_height), 
                          #(0, 255, 0), 2)  
            
    return output_image, inference_time, people_count

def add_text_overlay(image, inference_time, fps, average_count):
    """Ajoute des informations textuelles sur l'image.
    Args:
        image (numpy.ndarray): Image d'entrée.
        inference_time (float): Temps d'inférence en secondes.
        fps (float): Images par seconde.
        current_count (int): Nombre actuel de personnes détectées.
        average_count (float): Nombre moyen de personnes détectées par seconde.
    """
    height, width, _ = image.shape

    cv2.putText(image, 
                f"Inference: {inference_time*1000:.1f}ms", 
                (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cv2.putText(image, 
                f"FPS: {fps:.1f}", 
                (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)


    count_text = f"MOY. P/S: {int(average_count):d}"
    text_size, _ = cv2.getTextSize(count_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 3)
    
    text_x = width - text_size[0] - 20 
    text_y = 50 
    
    cv2.rectangle(image, 
                  (text_x - 10, text_y - text_size[1] - 10), 
                  (width, text_y + 10), 
                  (0, 0, 0), # Fond noir
                  -1) 
    
    cv2.putText(image, 
                count_text, 
                (text_x, text_y), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3) # Texte blanc


def live_camera_detection(model_path='yolov8n.pt'):
    """Initialise la caméra et effectue la détection en temps réel avec un compteur de personnes moyen par seconde.
    Args:
        model_path (str): Chemin vers le modèle YOLOv8.
    """
    # On utilise le modèle YOLOv8 ici mais on peut uriliser tous les autres modèles yolo, testé avec 11n sans problème

    print("Chargement du modèle YOLOv8...")
    try:
        model = YOLO(model_path)
    except Exception as e:
        print(f"Erreur lors du chargement du modèle : {e}")
        return

    # Ligne a modif sur la raspberry pi car pas compatible avec cv2.VideoCapture(0), faut utiliser piCamera2
    cap = cv2.VideoCapture(0) 

    if not cap.isOpened():
        print("Erreur: Impossible d'ouvrir le flux vidéo.")
        return

    # Variables pour le calcul global des FPS
    frame_count = 0
    global_start_time = time.time()
    
    # Variables pour le calcul de la moyenne perso par seconde
    avg_start_time = time.time()
    count_history = []
    average_people_count = 0.0 

    try:
        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                print("Impossible de recevoir la frame")
                break
            
            height, width, _ = frame.shape 
            
            # Compter les têtes dans la frame actuelle
            processed_frame, inference_time, current_people_count = detect_heads_yolo(frame, model)
            
            # Ajouter le compte actuel à la liste de l'historique
            count_history.append(current_people_count)

            # Calcul de la moyenne par seconde
            elapsed_avg_time = time.time() - avg_start_time
            
            if elapsed_avg_time >= 1.0:
                if count_history:
                    average_people_count = np.mean(count_history)
                else:
                    average_people_count = 0.0
                
                count_history = []
                avg_start_time = time.time()
            
            # Calcul des FPS globaux
            #frame_count += 1
            #elapsed_global_time = time.time() - global_start_time
            #fps = frame_count / elapsed_global_time if elapsed_global_time > 0 else 0
            
            # Afficher la frame traitée avec l'overlay d'informations
            #add_text_overlay(processed_frame, inference_time, fps, average_people_count)
            #cv2.imshow('YOLOv8 detection + compteur de tetes', processed_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"Erreur lors du traitement vidéo : {e}")
        
    finally:
        cap.release()
        cv2.destroyAllWindows()


def live_camera_detection_picamera2(model_path='yolov8n.pt'):
    """Initialise la caméra PiCamera2 et effectue la détection en temps réel.
    Args:
        model_path (str): Chemin vers le modèle YOLOv8.
    """
    print("Chargement du modèle YOLOv8...")
    try:
        model = YOLO(model_path)
    except Exception as e:
        print(f"Erreur lors du chargement du modèle : {e}")
        return
    picam2 = Picamera2()

    config = picam2.create_still_configuration(main={"size": (1920, 1080), "format": "RGB888"})

    picam2.configure(config)
    picam2.start()

    print("Starting video stream... Press 'q' to exit.")

    # Variables pour le calcul global des FPS
    frame_count = 0
    global_start_time = time.time()
    
    # Variables pour le calcul de la moyenne perso par seconde
    avg_start_time = time.time()
    count_history = []
    average_people_count = 0.0 

    try:
        while True:
            frame = picam2.capture_array()
            
            height, width, _ = frame.shape 
            
            # Compter les têtes dans la frame actuelle
            processed_frame, inference_time, current_people_count = detect_heads_yolo(frame, model)
            
            # Ajouter le compte actuel à la liste de l'historique
            count_history.append(current_people_count)

            # Calcul de la moyenne par seconde
            elapsed_avg_time = time.time() - avg_start_time
            
            if elapsed_avg_time >= 1.0:
                if count_history:
                    average_people_count = np.mean(count_history)
                else:
                    average_people_count = 0.0
                
                count_history = []
                avg_start_time = time.time()
            
            # Calcul des FPS globaux
            frame_count += 1
            elapsed_global_time = time.time() - global_start_time
            fps = frame_count / elapsed_global_time if elapsed_global_time > 0 else 0
            
            # Afficher la frame traitée avec l'overlay d'informations
            #add_text_overlay(processed_frame, inference_time, fps, average_people_count)
            #cv2.imshow('YOLOv8 detection + compteur de tetes', processed_frame)
            
            mqttc.publish("limon", f'{{"people": {average_people_count}}}')
            
            print(f"nb_personnes : {average_people_count}")
            print(f"fps : {fps}")

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        print(f"Erreur lors du traitement vidéo : {e}")
        
    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    mqttc.loop_start()
    live_camera_detection_picamera2(model_path='yolov11n-face.pt')
    mqttc.loop_stop()