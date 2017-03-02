import cv2
import signal
import os
import gtk
import time

from config import Config, overlay_image
from gui import PhotoBoothGUI, GameSelectGUI
from time import sleep
from emotionset import Emotions
from threading import Thread

config = Config()
emotions = Emotions(config)
photo_booth = None

processing_emotion = [False, [-1, "none"], 0, None]
camera_cap = None
#face_detected = False
#current_emotion = [0, "none"]

sad_face = cv2.resize(cv2.imread(config.sad_face, -1), (config.face_width, config.face_height))
happy_face = cv2.resize(cv2.imread(config.happy_face, -1), (config.face_width, config.face_height))
rendered_face = sad_face
current_frame = rendered_face
frame_testing = 0
selected_game = None
current_state = 0
current_emotion = None

def release_handler(signal, frame):
    global camera_cap
    print("Exiting... %s" % str(signal))
    if camera_cap != None:
        camera_cap.release()

    exit(1)

def guess_emotion_loop():
    global emotions, processing_emotion, sad_face, happy_face, rendered_face, current_frame, current_emotion
    
    while True:
        #face_detected = False
        try:
            recieved_emotion = emotions.get(current_frame)
            face_detected = recieved_emotion[0]
            processing_emotion = recieved_emotion

            if not face_detected:
                print("There is not a face detected!")
                #cv2.putText(current_frame, "No face detected", (0, 300), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255))
            else:
                #cv2.putText(current_frame, "Got an emotion %s" % recieved_emotion[1][1], (0, 300), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255))
                print("Got a new emotion! Guessing %s" % recieved_emotion[1])
                
                current_emotion = recieved_emotion[1]

                x_offset = config.face_x
                y_offset = config.face_y
                overlay_image = sad_face if recieved_emotion[1][0] == 0 else happy_face
                s_img = overlay_image
                l_img = current_frame

                rendered_face = l_img #blend_transparent(current_frame, overlay_image)

                #for c in range(0,3):
                #    current_frame[y_offset:y_offset+overlay_image.shape[0], x_offset:x_offset+overlay_image.shape[1], c] = overlay_image[:,:,c] * (overlay_image[:,:,3]/255.0) +  current_frame[y_offset:y_offset+overlay_image.shape[0], x_offset:x_offset+overlay_image.shape[1], c] * (1.0 - overlay_image[:,:,3]/255.0)


            #rendered_face = current_frame.copy()
        except Exception as err:
            print("Failed processing emotion! %s" % str(err))
    

def camera_init():
    global emotions, processing_emotion, face_detected, current_emotion, camera_cap, frame_testing
    camera_cap = cv2.VideoCapture(config.camera_id) # Open camera based on id

    if not camera_cap.isOpened(): # Check to see if the camera is open
        print("Couldn't open camera!")
        exit(1)

    print("Opened the camera!")

    camera_cap.read()

    #frame_testing = 0

    emotion_thread = Thread(target=guess_emotion_loop)
    emotion_thread.setDaemon(True)
    emotion_thread.start()

def camera_loop():
    global emotions, processing_emotion, face_detected, current_emotion, camera_cap, frame_testing, current_frame

    ret, current_frame = camera_cap.read()
    
    if not ret:
        print("Blank frame")
        sleep(config.fail_delay)
        return None

        #cv2.imshow("orignal", current_frame)

        #if rendered_face is not None:
        #    cv2.imshow("rendered", rendered_face)

    #if frame_testing % config.retry_frames == 0:
    #    if not processing_emotion:
    #        processing_emotion = True
    #        #emotion_thread = Thread(target=guess_emotion, args=(current_frame,))
    #        #emotion_thread.setDaemon(True)
    #        #emotion_thread.start()
    #        #print("Guessed emotion %s" % emotions.get(current_frame)[1])
    #    if frame_testing > 900:
    #        frame_testing = 0

    #frame_testing += 1

    return current_frame, processing_emotion
    #cv2.waitKey(30)

start_time = time.time()

def get_topic(questions, question_id):
    for key, topic in questions:
        if topic['id'] == question_id:
            return topic

completed_question = False
completed_timeout = None
total_points = 0
questions_right = 0
questions_wrong = 0
placed_header = False
placed_points = False

def main_game_tick():
    global selected_game, config, current_state, start_time, photo_booth, game, questions, completed_question, completed_timeout, total_points, questions_right, questions_wrong, placed_header, placed_points

    if current_state == 0:
        return # Do nothing

    t = time.time() - start_time # Get elapsed time

    topic = None

    if current_state > 0:
        topic = get_topic(questions, current_state - 1)

    if current_state >= 1:
        if t > 3:
            time_left = float(topic['time_limit']) - t

            update_time = True

            if time_left <= 0.0:
                if completed_question:
                    if completed_timeout is None:
                        completed_timeout = time.time()

                    elapsed_timeout = time.time() - completed_timeout

                    if not placed_points:
                        correct_response = topic['correct_response']

                        print("Question finished\nThe correct response is %s\nThe user displayed this emotion %s\n" % (correct_response, current_emotion))

                        if current_emotion[1] == correct_response:
                            photo_booth.set_header_text(topic['responses']['correct'])
                            total_points += int(topic['points'])
                            photo_booth.set_total_points(total_points)
                            questions_right += 1
                        else:
                            photo_booth.set_header_text(topic['responses']['incorrect'])
                            questions_wrong += 1
    
                        percentage = int((float(questions_right) / (float(questions_wrong + questions_right)) * 100)) if questions_wrong != 0 else 100
                        photo_booth.set_questions_percentage(percentage)
                        update_time = False

                        photo_booth.set_time_left("Next question coming...")

                        placed_points = True

                    if current_state >= len(questions):
                        photo_booth.set_time_left("You finished the game!")
                        update_time = False

                    if elapsed_timeout < config.interval_time:
                        if not current_state >= len(questions):
                            photo_booth.set_time_left("Next question coming up...")
                    elif current_state >= len(questions):
                        print("The player finished the game!")
                        current_state = 0 # Reset the game to zero
                        completed_question = False
                        photo_booth.set_time_left("Not playing a game...")
                        completed_timeout = None
                        return
                    else:
                        #elif completed_timeout
                        current_state += 1 
                        completed_question = False
                        completed_timeout = None
                        placed_header = False
                        placed_points = False
                        start_time = time.time()
                else:
                    completed_question = True
            else:
                if not placed_header:
                    photo_booth.set_header_text(topic['question'])
                    placed_header = True
            if update_time and not placed_points:
                photo_booth.set_time_left("%.1f" % time_left)
        else:
            photo_booth.set_header_text("Next Question. Possible points: %s" % str(topic['points']))
            photo_booth.set_time_left("Starting in a few seconds")

    print("Elasped time: %d" % t)

def main_game_loop():
    global selected_game, config, current_state, photo_booth, start_time, game, questions, total_points, questions_right, questions_wrong, placed_header, placed_points


    print("Starting game %s" % selected_game)
    current_state = 1
    start_time = time.time() + 3.5 #+ datetime.timedelta(seconds=3)
    game = config.get_game_all(selected_game)
    questions = config.get_game_questions(selected_game)
    total_points = 0
    questions_right = 0
    questions_wrong = 0
    photo_booth.set_total_points(total_points)
    photo_booth.set_time_left("Starting...")
    photo_booth.set_header_text("Starting...")
    placed_header = False
    placed_points = False
    print("Set the current game state to 1\nTime started: %d" % start_time)

def game_selected(game_id):
    global selected_game
    print("The game selected is %s" % game_id)
    selected_game = game_id
    main_game_loop()

def gui_select_game():
    game_select_gui = GameSelectGUI(config, game_selected) 
    game_select_gui.start()

def main_game_tick_catched():
    try:
        main_game_tick()
    except Exception as err:
        print("ERROR: %s" % str(err))

if __name__ == "__main__":
    print("Welcome to the decision room emotion tracker developed by: %s" % config.author)
    # Add a on exit handler
    signal.signal(signal.SIGINT, release_handler)
    signal.signal(signal.SIGTERM, release_handler)
    signal.signal(signal.SIGABRT, release_handler)
    signal.signal(signal.SIGILL, release_handler)

    #emotions.train()

    #exit(0)

    # Fixed threading bug
    gtk.disable_setlocale()
    gtk.gdk.threads_init()


    emotions.load_trainer()

    print("Attempting to open camera...")
    camera_init()

    emotion_images = [sad_face, happy_face]

    photo_booth = PhotoBoothGUI(config, camera_loop, emotion_images)
    photo_booth.attach_start(gui_select_game)
    photo_booth.attach_tick(main_game_tick)
    photo_booth.start()

    #emotions.calibrateCascade()
    #emotions.createDataset()
    #emotions.run_test()
    #emotions.train()

    #emotions.train()
