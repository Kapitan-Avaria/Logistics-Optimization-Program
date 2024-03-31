import numpy as np
import requests
import sys
import os
import pygame

from database.db_sessions import calc_direct_distances


def get_map_photo(map_request):
    response = requests.get(map_request)
    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)
    map_file = "map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
    pygame.init()
    screen = pygame.display.set_mode((map_w, map_h))
    screen.blit(pygame.image.load(map_file), (0, 0))

    pygame.draw.circle(screen, 'black', geocoord_to_map_pixels(np.array([center_lon, center_lat])), 5)
    pygame.draw.circle(screen, 'red', geocoord_to_map_pixels(np.array([center_lon-0.5, center_lat+0.5])), 5)
    pygame.draw.circle(screen, 'green', geocoord_to_map_pixels(np.array([center_lon+0.5, center_lat-0.5])), 5)
    pygame.draw.circle(screen, 'blue', geocoord_to_map_pixels(np.array([center_lon-0.5, center_lat-0.5])), 5)
    pygame.draw.circle(screen, 'magenta', geocoord_to_map_pixels(np.array([center_lon+0.5, center_lat+0.5])), 5)


    pygame.display.flip()
    while pygame.event.wait().type != pygame.QUIT:
        pass
    pygame.quit()
    os.remove(map_file)


def geocoord_to_map_pixels(coords):
    delta = 0.01
    # [vert, hor]
    m_per_deg_center = calc_direct_distances(
        np.array([center_lat - delta, center_lat]),
        np.array([center_lon, center_lon - delta]),
        np.array([center_lat + delta, center_lat]),
        np.array([center_lon, center_lon + delta])
    ) / (2 * delta)

    # [vert1, vert2, hor1, hor2]
    m_per_deg = calc_direct_distances(
        np.array([center_lat, center_lat, center_lat, coords[0]]),
        np.array([center_lon, coords[1],  center_lon, center_lon]),
        np.array([coords[0],  coords[0],  center_lat, coords[0]]),
        np.array([center_lon, coords[1],  coords[1],  coords[1]])
    ) / np.array([center_lat - coords[0], center_lat - coords[0], center_lon - coords[1], center_lon - coords[1]])

    # [vert, hor]
    m_per_deg = np.array([m_per_deg[:2].mean(), m_per_deg[2:].mean()])



    # top_left = np.array([center_lon, center_lat]) + np.array([-spn_lon, spn_lat])
    # pixel_coords = (coords - top_left) / np.array([2 * spn_lon, -2 * spn_lat]) * np.array([map_h, map_h])

    # return pixel_coords


map_w = 600
map_h = 450

center_lat = 44.987749
center_lon = 38.957643
spn_lon = 1
spn_lat = 1

map_request = f"http://static-maps.yandex.ru/1.x/?ll={center_lon},{center_lat}&spn={spn_lon},{spn_lat}&l=map"
get_map_photo(map_request)

# print(geocoord_to_map_pixels(np.array([center_lat, center_lon])))
# print(geocoord_to_map_pixels(np.array([center_lat+0.5, center_lon+0.5])))
