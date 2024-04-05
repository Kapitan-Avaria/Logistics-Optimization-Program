import numpy as np
import requests
import sys
import os
import pygame

from source.database.db_sessions import calc_direct_distances, get_all_segments, get_many_coords_from_db_addresses


map_w = 600
map_h = 450

center_lat = 44.987749
center_lon = 38.957643
spn_lon = 1
spn_lat = 1

map_request = f"http://static-maps.yandex.ru/1.x/?ll={center_lon},{center_lat}&spn={spn_lon},{spn_lat}&size=450,450&l=map"


def get_map_photo(map_request):
    response = requests.get(map_request)
    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)
    content = response.content
    return content


def draw_map(content, map_file="map.png"):
    with open(map_file, "wb") as file:
        file.write(content)

    pygame.init()
    screen = pygame.display.set_mode((map_w, map_h))
    screen.blit(pygame.image.load(map_file), (0, 0))

    pygame.draw.circle(screen, 'black', geocoord_to_map_pixels(np.array([center_lon, center_lat])), 5)
    pygame.draw.circle(screen, 'red', geocoord_to_map_pixels(np.array([center_lon - 0.5, center_lat + 0.5])), 5)
    pygame.draw.circle(screen, 'green', geocoord_to_map_pixels(np.array([center_lon + 0.5, center_lat - 0.5])), 5)
    pygame.draw.circle(screen, 'blue', geocoord_to_map_pixels(np.array([center_lon - 0.5, center_lat - 0.5])), 5)
    pygame.draw.circle(screen, 'magenta', geocoord_to_map_pixels(np.array([center_lon + 0.5, center_lat + 0.5])), 5)

    pygame.draw.circle(screen, 'red', geocoord_to_map_pixels(np.array([38.997269, 45.802001])), 5)
    pygame.draw.circle(screen, 'red', geocoord_to_map_pixels(np.array([39.727067, 44.465523])), 5)

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
    ) / np.abs(np.array([center_lat - coords[0], center_lat - coords[0], center_lon - coords[1], center_lon - coords[1]]))

    # [vert, hor]
    m_per_deg = np.array([m_per_deg[:2].mean(), m_per_deg[2:].mean()])

    # coords_from_center = coords - np.array([center_lon, center_lat])
    # pixel_coords = np.array([map_w, map_h]) / 2 + coords_from_center * np.array([map_h, map_h]) * m_per_deg / m_per_deg_center

    # top_left = np.array([center_lon, center_lat]) + np.array([-spn_lon, spn_lat])
    # coords_from_tl = (coords - top_left)
    # pixel_coords = coords_from_tl / np.array([2 * spn_lon, -2 * spn_lat]) * np.array([map_h, map_h]) #* m_per_deg / m_per_deg_center

    coords_from_center = (coords - np.array([center_lon, center_lat]))
    pixel_coords = (np.array([spn_lon, -spn_lat]) + coords_from_center * m_per_deg / m_per_deg_center) / np.array([2 * spn_lon, -2 * spn_lat]) * np.array([map_h, map_h])  # * m_per_deg / m_per_deg_center

    return pixel_coords


def geocoord_to_map_pixels_rough(coords: np.ndarray):
    coords_from_center = (coords - np.array([center_lon, center_lat]))
    # pixel_coords = np.array([map_w, map_h]) / 2 + coords_from_center * map_h
    pixel_coords = (np.array([spn_lon, -spn_lat]) + coords_from_center) / np.array([2 * spn_lon, -2 * spn_lat]) * np.array([map_h, map_h]) / 4 + 200
    return pixel_coords


def draw_map_rough():
    pygame.init()
    screen = pygame.display.set_mode((map_w, map_h))

    distances = dict()
    coords_dict = dict()

    segments = get_all_segments()
    for segment in segments:
        id_1 = segment["address_1_id"]
        id_2 = segment["address_2_id"]
        coords_dict[id_1] = None
        coords_dict[id_2] = None
        distances[(id_1, id_2)] = segment["direct_distance"]

    coords_dict = get_many_coords_from_db_addresses(coords_dict.keys())
    pixel_coords = geocoord_to_map_pixels_rough(np.array(list(coords_dict.values()))).tolist()
    pixel_coords_dict = dict(zip(coords_dict.keys(), pixel_coords))

    max_dist = max(distances.values())
    min_dist = min(distances.values())

    for (id_1, id_2) in distances.keys():
        shade = max(8, int((1 - (distances[(id_1, id_2)] - min_dist) / (max_dist - min_dist)) * 255))
        pygame.draw.line(screen, (shade, 0, shade), pixel_coords_dict[id_1], pixel_coords_dict[id_2])
    pygame.draw.circle(screen, 'yellow', geocoord_to_map_pixels_rough(np.array([center_lon, center_lat])), 5)
    pygame.draw.circle(screen, 'yellow', geocoord_to_map_pixels(np.array([38.997269, 45.802001])), 5)
    pygame.draw.circle(screen, 'yellow', geocoord_to_map_pixels(np.array([39.727067, 44.465523])), 5)


    pygame.display.flip()
    while pygame.event.wait().type != pygame.QUIT:
        pass
    pygame.quit()
    pass


draw_map_rough()

