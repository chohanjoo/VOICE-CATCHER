from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import numpy as np

import cv2

def text_wrap(text, font, max_width):
    lines = []
    # If the width of the text is smaller than image width
    # we don't need to split it, just add it to the lines array
    # and return
    if font.getsize(text)[0] <= max_width:
        lines.append(text)
    else:
        # split the line by spaces to get words
        words = text.split(' ')
        i = 0
        # append every word to a line while its width is shorter than image width
        while i < len(words):
            line = ''
            while i < len(words) and font.getsize(line + words[i] + " ")[0] <= max_width:
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            # when the line gets longer than the max width do not append the word,
            # add the line to the lines array
            lines.append(line)
    return lines


def draw_text(text,bubble_q):
    # open the background file

    #입력된 글자가 28자 미만이면 작은 말풍선에 문자열 작성
    if len(text) < 28:
        img = Image.open('speech_bubble.png')
        x = 40
        y = 30
        #작은 말풍선이면 bubble_q에 1을 넣는다
        bubble_q.put(1)
    #입력된 글자가 그 이상이면 말풍선의 크기를 키워 문자열 작성
    else:
        img = Image.open('speech_bubble.png')
        img_array = np.array(img)
        img_resize = cv2.resize(img_array, (280, 180), interpolation=cv2.INTER_AREA)
        img = Image.fromarray(img_resize)
        x = 50
        y = 40

        #큰 말풍선이면 bubble_q에 2를 넣는다
        bubble_q.put(2)
    draw = ImageDraw.Draw(img)

    # size() returns a tuple of (width, height)
    image_size = img.size
    img_size = list(image_size)

    for i in range(2):
        img_size[i] -= 80


    # create the ImageFont instance
    font = ImageFont.truetype('BMYEONSUNG_ttf.ttf', 18, encoding="unic")

    color = 'rgb(0, 0, 100)'

    lines = text_wrap(text, font, img_size[0])
    line_height = font.getsize('hg')[1]

    for line in lines:
        # draw the line on the image
        draw.text((x, y), line, fill=color, font=font)

        # update the y position so that we can use it for next line
        y = y + line_height
    # save the image
    img.save('word2.png', optimize=True)
    # get shorter lines
