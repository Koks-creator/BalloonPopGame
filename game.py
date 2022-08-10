from random import randint
from time import time
from typing import Tuple
import cv2
import mediapipe as mp
import pygame
from pygame import mixer
import numpy as np

pygame.init()
mixer.init()


def reset_balloon():
    rect_balloon.x = randint(100, img.shape[1] - 100)
    rect_balloon.y = img.shape[0] + 50


def get_hands_lms(img_to_proc: np.array, draw=True) -> Tuple[np.array, list]:
    lms = []
    h, w, _ = img_to_proc.shape

    img_rgb = cv2.cvtColor(img_to_proc, cv2.COLOR_BGR2RGB)
    results_class = hands.process(img_rgb)
    results = results_class.multi_hand_landmarks

    if results:
        for landmark in results:
            if draw:
                mp_draw.draw_landmarks(img_to_proc, landmark, mp_hands.HAND_CONNECTIONS)
            for lm in landmark.landmark:
                x = int(lm.x * w)
                y = int(lm.y * h)

                lms.append((x, y))
        cv2.circle(img_to_proc, lms[8], 15, (255, 0, 255), -1)
    return img, lms


width, height = 1280, 720
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Balloon Pop Game")

fps = 30
clock = pygame.time.Clock()

mixer.music.load("pop.wav")
mixer.music.set_volume(0.7)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=.6, min_tracking_confidence=.6)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
img_balloon = pygame.image.load("BalloonRed.png").convert_alpha()
rect_balloon = img_balloon.get_rect()
rect_balloon.x, rect_balloon.y = 500, 800
font = pygame.font.Font(pygame.font.get_default_font(), 50)

speed = 15
score = 0
cursor_x, cursor_y = False, False
start_time = None
total_time = None
total_scores = None

start = True
window_type = "menu"

while start:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            start = False
            pygame.quit()

    success, img = cap.read()

    img = cv2.resize(img, (1280, 720))
    img = cv2.flip(img, 1)

    img, lms_list = get_hands_lms(img)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_rgb = np.rot90(img_rgb)
    frame = pygame.surfarray.make_surface(img_rgb).convert()
    frame = pygame.transform.flip(frame, True, False)
    window.blit(frame, (0, 0))
    window.blit(img_balloon, rect_balloon)

    if lms_list:
        cursor_x, cursor_y = lms_list[8]
        cv2.circle(img, (cursor_x, cursor_y), 15, (255, 0, 255), -1)

    if window_type == "menu":
        start_button = pygame.draw.rect(window, (150, 150, 0), pygame.Rect(450, 270, 340, 100))
        start_button_border = pygame.draw.rect(window, (255, 255, 255), pygame.Rect(445, 270, 340, 100), 10)
        start_button_text = font.render("START", True, (255, 255, 255))
        window.blit(start_button_text, (540, 295))

        if start_button.collidepoint(cursor_x, cursor_y) and lms_list:
            window_type = "game"
            start_time = time()
            total_scores = 0

    if window_type == "game":
        curr_time = round(time() - start_time, 2)
        rect_balloon.y -= speed

        if rect_balloon.y < 0:
            window_type = "end_menu"
            total_time = curr_time
            total_scores = score
            rect_balloon.x, rect_balloon.y = 500, 800

        if lms_list:
            if rect_balloon.collidepoint(cursor_x, cursor_y):
                reset_balloon()
                score += 10
                speed += 1.25
                mixer.music.play()

        text_score = font.render(f"Score: {score}", True, (255, 100, 50))
        text_time = font.render(f"Time: {curr_time}s", True, (255, 100, 50))
        window.blit(text_score, (20, 20))
        window.blit(text_time, (920, 20))

    if window_type == "end_menu":
        try_again_button = pygame.draw.rect(window, (150, 150, 0), pygame.Rect(440, 200, 400, 100))
        try_again_button_border = pygame.draw.rect(window, (255, 255, 255), pygame.Rect(440, 200, 400, 100), 10)
        try_again_button_text = font.render("Try again", True, (255, 255, 255))
        window.blit(try_again_button_text, (525, 225))

        total_scores_label = pygame.draw.rect(window, (150, 150, 0), pygame.Rect(470, 330, 340, 70))
        total_scores_border = pygame.draw.rect(window, (255, 255, 255), pygame.Rect(470, 330, 340, 70), 10)

        font2 = pygame.font.Font(pygame.font.get_default_font(), 30)
        total_scores_text = font2.render(f"Total score: {total_scores}", True, (255, 255, 255))
        window.blit(total_scores_text, (540, 350))

        total_time_label = pygame.draw.rect(window, (150, 150, 0), pygame.Rect(485, 430, 305, 70))
        total_time_border = pygame.draw.rect(window, (255, 255, 255), pygame.Rect(485, 430, 305, 70), 10)

        font3 = pygame.font.Font(pygame.font.get_default_font(), 25)
        total_scores_text = font2.render(f"Total time: {total_time}s", True, (255, 255, 255))
        window.blit(total_scores_text, (510, 450))

        if try_again_button.collidepoint(cursor_x, cursor_y) and lms_list:
            window_type = "game"
            start_time = time()

    pygame.display.update()
    clock.tick(fps)

