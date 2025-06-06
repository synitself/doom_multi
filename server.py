import socket
import threading
import pickle
import pygame as pg
from sprite_object import *

from settings import SERVER_PORT, FPS
from map import Map
from object_handler import ObjectHandler
from pathfinding import PathFinding
from npc import NPC, SoldierNPC, CacoDemonNPC, CyberDemonNPC


class GameServerMock:
    def __init__(self):
        self.player = None  # <-- ПЕРЕМЕСТИТЕ ЭТУ СТРОКУ В НАЧАЛО
        self.map = Map(self)
        self.object_handler = ObjectHandler(self)
        self.pathfinding = PathFinding(self)
        self.delta_time = 1.0


class Server:
    def __init__(self):
        self.host = '0.0.0.0'
        self.port = SERVER_PORT
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.player_id_counter = 0

        self.clock = pg.time.Clock()
        self.game_mock = GameServerMock()

        self.npcs = self.game_mock.object_handler.npc_list
        for npc in self.npcs:
            npc.game = self.game_mock

        self.game_state = {
            'players': {},
            'npcs': {}
        }
        self.update_npc_state()

        try:
            self.socket.bind((self.host, self.port))
        except socket.error as e:
            print(f"Ошибка привязки сокета: {e}")
            exit()

    def update_npc_state(self):
        for i, npc in enumerate(self.npcs):
            self.game_state['npcs'][i] = {
                'pos': (npc.x, npc.y),
                'health': npc.health,
                'alive': npc.alive,
                'pain': npc.pain,
            }

    def run_game_logic(self):
        while True:
            delta = self.clock.tick(FPS)
            self.game_mock.delta_time = delta / 1000.0 if delta > 0 else 0.016

            for npc in self.npcs:
                if not npc.alive or not self.game_state['players']:
                    continue

                closest_player = None
                min_dist = float('inf')

                for p_id, p_data in self.game_state['players'].items():
                    dist = ((npc.x - p_data['pos'][0]) ** 2 + (npc.y - p_data['pos'][1]) ** 2) ** 0.5
                    if dist < min_dist:
                        min_dist = dist
                        closest_player = pg.sprite.Sprite()
                        closest_player.pos = p_data['pos']
                        closest_player.map_pos = int(p_data['pos'][0]), int(p_data['pos'][1])

                if closest_player:
                    self.game_mock.player = closest_player
                    npc.update()

            self.update_npc_state()

    def _threaded_client(self, conn, player_id):
        self.clients[conn] = player_id

        initial_pos = (1.5 + player_id, 5)
        self.game_state['players'][player_id] = {'pos': initial_pos, 'angle': 0, 'health': 100, 'shot': False}

        conn.send(pickle.dumps({'id': player_id, 'state': self.game_state}))

        while True:
            try:
                client_data = pickle.loads(conn.recv(4096))
                if not client_data:
                    break

                self.game_state['players'][player_id].update(client_data)
                conn.sendall(pickle.dumps(self.game_state))

            except (ConnectionResetError, EOFError, pickle.UnpicklingError):
                break

        print(f"Клиент ID {player_id} отключился")
        del self.game_state['players'][player_id]
        del self.clients[conn]
        conn.close()

    def run(self):
        self.socket.listen()
        print(f"Сервер запущен на {self.host}:{self.port} и ожидает подключений...")

        logic_thread = threading.Thread(target=self.run_game_logic, daemon=True)
        logic_thread.start()

        while True:
            conn, addr = self.socket.accept()
            print(f"Подключен: {addr}")
            thread = threading.Thread(target=self._threaded_client, args=(conn, self.player_id_counter))
            thread.daemon = True
            thread.start()
            self.player_id_counter += 1