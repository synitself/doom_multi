from sprite_object import *
from npc import *
from random import choices, randrange

NPC_CLASSES = {
    'SoldierNPC': SoldierNPC,
    'CacoDemonNPC': CacoDemonNPC,
    'CyberDemonNPC': CyberDemonNPC,
}

class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.npc_list = []
        self.npc_positions = {}
        self.static_sprite_path = 'resources/sprites/static_sprites/'
        self.anim_sprite_path = 'resources/sprites/animated_sprites/'

        if GAME_MODE == 'SERVER':
            self.enemies = 20
            self.npc_types = [SoldierNPC, CacoDemonNPC, CyberDemonNPC]
            self.weights = [70, 20, 10]
            self.restricted_area = {(i, j) for i in range(10) for j in range(10)}
            self.spawn_npc()
        elif GAME_MODE == 'CLIENT':
            add_sprite = self.add_sprite
            add_sprite(AnimatedSprite(game))
            add_sprite(AnimatedSprite(game, pos=(1.5, 1.5)))
            add_sprite(AnimatedSprite(game, pos=(1.5, 7.5)))
            add_sprite(AnimatedSprite(game, pos=(5.5, 3.25)))
            add_sprite(AnimatedSprite(game, pos=(5.5, 4.75)))
            add_sprite(AnimatedSprite(game, pos=(7.5, 2.5)))
            add_sprite(AnimatedSprite(game, pos=(7.5, 5.5)))
            add_sprite(AnimatedSprite(game, pos=(14.5, 1.5)))
            add_sprite(AnimatedSprite(game, pos=(14.5, 4.5)))
            add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 5.5)))
            add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 7.5)))
            add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(12.5, 7.5)))
            add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(9.5, 7.5)))
            add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(14.5, 12.5)))
            add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(9.5, 20.5)))
            add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(10.5, 20.5)))
            add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(3.5, 14.5)))
            add_sprite(AnimatedSprite(game, path=self.anim_sprite_path + 'red_light/0.png', pos=(3.5, 18.5)))
            add_sprite(AnimatedSprite(game, pos=(14.5, 24.5)))
            add_sprite(AnimatedSprite(game, pos=(14.5, 30.5)))
            add_sprite(AnimatedSprite(game, pos=(1.5, 30.5)))
            add_sprite(AnimatedSprite(game, pos=(1.5, 24.5)))

    def setup_npcs_from_server(self, npc_data_list):
        for npc_data in npc_data_list:
            npc_class = NPC_CLASSES[npc_data['type']]
            npc_instance = npc_class(self.game, pos=npc_data['pos'])
            npc_instance.id = npc_data['id']
            self.add_npc(npc_instance)

    def spawn_npc(self):
        for i in range(self.enemies):
            npc = choices(self.npc_types, self.weights)[0]
            pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
            while (pos in self.game.map.world_map) or (pos in self.restricted_area):
                pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
            self.add_npc(npc(self.game, pos=(x + 0.5, y + 0.5)))

    def check_win(self):
        if not len(self.npc_positions):
            self.game.object_renderer.win()
            pg.display.flip()
            pg.time.delay(1500)
            self.game.new_game()

    def update(self):
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        [sprite.update() for sprite in self.sprite_list]
        [npc.update() for npc in self.npc_list]
        if GAME_MODE == 'CLIENT':
            self.check_win()

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)