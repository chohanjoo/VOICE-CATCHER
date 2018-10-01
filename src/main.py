from __future__ import division

from src.visual import *
from src.listen import *
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

import dlib


from multiprocessing import Process, Queue

import cv2



def visualize_frame(q, bubble_q):

    # -*- coding: utf-8 -*-

    # 동영상 파일 열기
    cap = cv2.VideoCapture(0)
    cap.set(3, 720)  # CV_CAP_PROP_FRAME_WIDTH
    cap.set(4, 360)  # CV_CAP_PROP_FRAME_HEIGHT

    # 잘 열렸는지 확인
    if cap.isOpened() == False:
        exit()


    # 윈도우 생성 및 사이즈 변경
    cv2.namedWindow("HJ")

    # 재생할 파일의 넓이 얻기
    width_frame = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    # 재생할 파일의 높이 얻기
    height_frame = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    # 재생할 파일의 프레임 레이트 얻기
    fps = cap.get(cv2.CAP_PROP_FPS)

    print('width {0}, height {1}, fps {2}'.format(width_frame, height_frame, fps))


    # 얼굴 인식용
    face_cascade = cv2.CascadeClassifier()
    face_cascade.load('haarcascade_frontface.xml')




    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

    #얼굴들의 입술 포인트들을 저장하는 리스트
    lippoint = []

    # 입술 각 지점의 높이를 저장하기 위한 list 변수
    height = []
    weight = []
    
    #화자의 입술 정보를 저장하는 리스트
    speaking_lip = [[0, 0]]
    esc = True
    tmp_x, tmp_y = (0, 0)
    x, y = (200, 200)
    while (True):
        speech_bubble = cv2.imread("word2.png", 1)
        # 파일로 부터 이미지 얻기
        ret, frame = cap.read()
        # 더 이상 이미지가 없으면 종료
        # 재생 다 됨
        if frame is None:
            break;

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)

        # 얼굴 갯수만큼 loop가 돌면서 움직인 입술 위치정보를 lippoint 변수에 저장한다. (visualize_facial_landmarks 함수에서 lippoint 변수에 값을 저장)
        for (i, rect) in enumerate(rects):
            # determine the facial landmarks for the face region, then
            # convert the landmark (x, y)-coordinates to a NumPy array
            shape = predictor(gray, rect)
            shape = shape_to_numpy_array(shape)
            frame = visualize_facial_landmarks(frame, shape, i, lippoint)

            height.clear()
            weight.clear()

            #가져온 입술의 정보를 x값는 weight 리스트에, y값은 height 리스트에 저장한다.
            for point in lippoint[i]:
                height.append(point[1])
                weight.append(point[0])

            #입술안의 삼각형 각도를 구한다.
            tany = (lippoint[i][18][1] - lippoint[i][0][1]) / (lippoint[i][18][0] - lippoint[i][0][0])

            #입술안의 삼각형 한 각의 탄젠트 값이 0.25를 넘으면 말하고 있다고 간주
            if tany > 0.25:
                speaking_lip = lippoint[i]


        #이전의 있던 입술 정보를 초기화한다.
        weight.clear()
        height.clear()

        # 가져온 입술의 정보를 x값는 weight 리스트에, y값은 height 리스트에 저장한다.
        for tp in speaking_lip:
            weight.append(tp[0])
            height.append(tp[1])


        if bubble_q.qsize() != 0:
            bubble_size = bubble_q.get()
            #작은 말풍선를 화면에 띄울 때 말풍선의 위치 조정
            if bubble_size == 1:
                x, y = (200, 200)
            #큰 말풍선을 화면에 띄울 때 말풍선의 위치 조정
            elif bubble_size == 2:
                x = 300
                y = 300


        tmp_x = x
        tmp_y = y
        
        #말풍선의 위치가 음수가 되지않도록 하면서 얼굴 왼쪽으로 위치를 잡아준다.
        while True:
            if min(weight) - tmp_x >= 0:
                break;
            else:
                tmp_x -= 10

        while True:
            if height[weight.index(min(weight))] - tmp_y >= 0:
                break;
            else:
                tmp_y -= 10

        k = cv2.waitKey(1)
        
        # esc키가 눌리면 esc flag를 바꾸어 배경이 다른 말풍선을 띄워준다.
        if k == 27: esc = not esc
        
        #배경이 투명한 말풍선을 띄워준다.
        if esc == True and type(speech_bubble) != type(None):
            bitOperation(frame,min(weight) - tmp_x, height[weight.index(min(weight))] - tmp_y, speech_bubble)
        #배경이 흰색인 말풍선을 띄워준다.
        elif esc == False and type(speech_bubble) != type(None):
            bitOperation2(frame,min(weight) - tmp_x, height[weight.index(min(weight))] - tmp_y, speech_bubble)


        #입술이 움직이고 있고 음성이 들릴 때
        if q.qsize() > 0:
            data = q.get()

            #q에 있던 값이 1이면 캘린더 명령어 입력을 기다리고 잇는 것이므로 검은띠를 출력한다
            if data == 1:
                overlay = frame.copy()
                cv2.rectangle(frame, (0, int(height_frame) - 60), (int(width_frame), int(height_frame) - 30), (0, 0, 0),
                              -1)
                q.put(1)
                cv2.addWeighted(overlay, 0.5, frame, 1 - 0.5, 0, frame)

        # 얼굴 인식된 이미지 화면 표시
        cv2.imshow("HJ", frame)

    # 재생 파일 종료
    cap.release()
    # 윈도우 종료
    cv2.destroyAllWindows()



def main():
    procs = []
    #화면에 화자가 있고 출력할 문자열이 있는지 확인하는 Queue
    q = Queue()
    
    #작은 말풍선을 출력할지 큰 말풍선을 출력할지 결정하는 Queue
    bubble_q = Queue()
    #멀티 프로세싱으로 frame출력하는 프로그램 start
    proc = Process(target=visualize_frame, args=(q, bubble_q,))
    procs.append(proc)
    proc.start()
    
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = 'ko-KR'  # a BCP-47 language tag
    
    #마이크로 들어오는 speech를 google cloud platform의 speech to text api 호출하여 말풍선에 문자열 저장
    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses, q, bubble_q)


if __name__ == '__main__':
    main()