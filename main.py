import pygame as pg
import sys
from settings import *

if GAME_MODE == 'CLIENT':
    from map import *
    from player import *
    from raycasting import *
    from object_renderer import *
    from sprite_object import SpriteObject
    from network import Network
    from object_handler import *
    from weapon import *
    from sound import *
    from pathfinding import *

    class RemotePlayer(SpriteObject):
        def __init__(self, game, pos=(11.5, 3.5)):
            super().__init__(game, path='resources/sprites/npc/soldier/0.png', pos=pos, scale=0.6, shift=0.38)

        def update_pos(self, pos, angle):
            self.x, self.y = pos
            self.angle = angle

        def update(self):
            pass


    class Game:
        def __init__(self):
            self.network = Network()
            initial_data = self.network.get_initial_data()
            if not initial_data:
                print("Не удалось подключиться к серверу.")
                sys.exit()

            self.player_id = initial_data['id']
            self.game_state = initial_data['state']

            pg.init()
            pg.mouse.set_visible(False)
            self.screen = pg.display.set_mode(RES)
            pg.event.set_grab(True)
            self.clock = pg.time.Clock()
            self.delta_time = 1
            self.global_trigger = False
            self.global_event = pg.USEREVENT + 0
            pg.time.set_timer(self.global_event, 40)
            self.new_game()

        def new_game(self):
            self.map = Map(self)
            player_initial_pos = self.game_state['players'][self.player_id]['pos']
            self.player = Player(self)
            self.player.x, self.player.y = player_initial_pos
            self.object_renderer = ObjectRenderer(self)
            self.raycasting = RayCasting(self)
            self.object_handler = ObjectHandler(self)
            self.object_handler.remote_players = {}
            self.weapon = Weapon(self)
            self.sound = Sound(self)
            self.pathfinding = PathFinding(self)
            pg.mixer.music.play(-1)

        def update(self):
            self.player.update()
            player_data = {
                'pos': self.player.pos,
                'angle': self.player.angle,
                'health': self.player.health,
                'shot': self.player.shot
            }

            new_game_state = self.network.send(player_data)
            if not new_game_state:
                print("Потеряно соединение с сервером.")
                pg.quit()
                sys.exit()
            self.game_state = new_game_state

            self.update_remote_players()
            self.update_npcs_from_state()

            self.raycasting.update()
            self.object_handler.update()
            self.weapon.update()

            pg.display.flip()
            self.delta_time = self.clock.tick(FPS)
            pg.display.set_caption(f'{self.clock.get_fps() :.1f}')

        def update_remote_players(self):
            if not self.game_state: return
            remote_player_ids = self.game_state['players'].keys() - {self.player_id}

            for p_id in list(self.object_handler.remote_players.keys()):
                if p_id not in remote_player_ids:
                    del self.object_handler.remote_players[p_id]

            for p_id in remote_player_ids:
                p_data = self.game_state['players'][p_id]
                if p_id not in self.object_handler.remote_players:
                    self.object_handler.remote_players[p_id] = RemotePlayer(self, pos=p_data['pos'])
                else:
                    self.object_handler.remote_players[p_id].update_pos(p_data['pos'], p_data['angle'])

        def update_npcs_from_state(self):
            if not self.game_state: return
            for i, npc_obj in enumerate(self.object_handler.npc_list):
                if i in self.game_state['npcs']:
                    npc_data = self.game_state['npcs'][i]
                    npc_obj.x, npc_obj.y = npc_data['pos']
                    npc_obj.health = npc_data['health']
                    npc_obj.alive = npc_data['alive']
                    npc_obj.pain = npc_data['pain']

        def draw(self):
            self.object_renderer.draw()
            self.weapon.draw()

        def check_events(self):
            self.global_trigger = False
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    self.network.client.close()
                    pg.quit()
                    sys.exit()
                elif event.type == self.global_event:
                    self.global_trigger = True
                self.player.single_fire_event(event)

        def run(self):
            while True:
                self.check_events()
                self.update()
                self.draw()

elif GAME_MODE == 'SERVER':
    from server import Server


if __name__ == '__main__':
    if GAME_MODE == 'SERVER':
        print("Запуск в режиме СЕРВЕРА.")
        server = Server()
        server.run()
    elif GAME_MODE == 'CLIENT':
        print("Запуск в режиме КЛИЕНТА.")
        game = Game()
        game.run()
    else:
        print(f"Ошибка: неизвестный GAME_MODE '{GAME_MODE}' в settings.py")
        print("Доступные режимы: 'CLIENT', 'SERVER'")