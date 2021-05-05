import pygame
import pickle
from os import path

pygame.init()

# on definit un montre qui servira pour les cooldowns par exemple ou pour les fps, frame per secondes du jeu
# c'est tres utile
clock = pygame.time.Clock()
FPS = 80

# variable ecran
largeur_ecran = 1600
hauteur_ecran = 960

# definition des variables pour les couleurs, pour le texte par exemple, cela simplifie le code
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)

# definition nom du projet et de la variable screen qui régit l'ecran. Le screen est indispensable
pygame.display.set_caption("Projet NSI")
screen = pygame.display.set_mode((largeur_ecran, hauteur_ecran), pygame.NOFRAME)
screen.set_alpha(None)

# la variable game_tile permet de dessiner le grilage ainsi que pour definir les blocs du monde
game_tile = 64
# variable controlant si le joueur est en vie : game_player_over = 0, le joueur est en vie; game_player_over = -1, le joueur
# est mort; game_player_over = 1, le joueur prend un portail et change donc de niveau
# variable indispensable
game_player_over = 0
# variable pour les images des boutons
restart_button_img = pygame.image.load('assets/reset_button.png')
start_button_img = pygame.image.load('assets/start_button3.png')
history_button_img = pygame.image.load('assets/history_button.png')
save_data_button_img = pygame.image.load('assets/history_button.png')
credits_button_image = pygame.image.load('assets/credits_button.png')
back_button_image = pygame.image.load('assets/back_button.png')
quit_button_image = pygame.image.load('assets/quit_button.png')
# variable pour savoir si le jeu est lancé ou si on est sur le menu général
main_menu = False
key_menu = False
history_menu = True
game_play = False
credits_menu = False

# variable nombre de fragments de clés
key_fragment_number = 0
# variable pour les polices et les tailles d'ecriture
font = pygame.font.SysFont('Syne mono', 55)
font_score = pygame.font.SysFont('Syne mono', 50)
font_tips = pygame.font.SysFont('Syne mono', 25)
font_history = pygame.font.SysFont('Syne mono', 30)
# variable pour generer les levels
level = 1
max_levels = 7
normal_key_number = 8
reset_key_number = 0
game_end = 0
tile_cooldown = 20


# ----------------------------------------------------------------------------------------------------------------------!
# fonction qui permet de dessiner du texte à l'écran
def draw_text(text, font, text_col, x, y):
    image = font.render(text, True, text_col)
    # on affiche l'image sur l'ecran aux coordonnées saisis par le codeur
    screen.blit(image, (x, y))


# fonction qui permet de vider tout les groupes de sprite comme les blobs, les clés...
# on load ensuite le level
def reset_level(level):
    player.reset()
    blob_enemy_group.empty()
    spikes_group.empty()
    key_fragment_group.empty()
    portal_group.empty()

    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = Map(world_data)

    return world


# ----------------------------------------------------------------------------------------------------------------------!

# création d'une classe pour les boutons, ils sont configurables
class Button():
    # il faut saisir l'image qu'on souhaite, ainsi que les coordonnées
    def __init__(self, x, y, image):
        # image du bouton
        self.image = image
        # position du bouton
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # variable afin de savoir si le bouton est cliqué
        # il est utile pour faire en sorte qu'on ne puisse cliquer qu'une fois qu'on ai relaché la souris
        self.clicked = False

    # fonction pour dessiner le bouton et savoir s'il est cliqué
    def draw(self):
        # variable qui nous retourne si une action est effectuée
        action = False

        # variable permettant de connaître la postion de la souris
        pos = pygame.mouse.get_pos()

        # si la position de la souris correspond à l'endroit du bouton, s'il y a collision entre les deux
        if self.rect.collidepoint(pos):
            # si le clic gauche = [0] est égal 1, donc si il est enfoncé et que la variable clicked = False
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                # il y a action
                action = True
                # il y a un clic
                self.clicked = True

        # si le clic gauche est désenfoncé, s'il est égal à 1
        if pygame.mouse.get_pressed()[0] == 0:
            # le clic est remis sur False, l'action de clic peut etre rééffectuée
            self.clicked = False

        # on l'affiche sur l'ecran
        screen.blit(self.image, self.rect)

        # on retourne l'action
        return action


# On cree une classe qui est en fait un carré noir qui bouge, on y colle ensuite du texte avec la fonction draw_text
class ending_block(pygame.sprite.Sprite):

    def __init__(self, x, y, speed, text, font, text_color):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/black_square.png')
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x
        self.speed = speed
        self.text = text
        self.font = font
        self.text_color = text_color

    def update(self):
        self.rect.y -= self.speed

        screen.blit(self.image, self.rect)

        draw_text(self.text, self.font, self.text_color, self.rect.x, self.rect.y)


# ----------------------------------------------------------------------------------------------------------------------!

# Classe du joueur, controlant ses mouvements, ses dégâts, ses updates, ses animations...
class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.reset()

    # def right_move(self):               Code de test, se révèle infructueux, ca marche mais tout dépend de la boucle du jeu
    # je m'explique, avant dans la boucle du jeu, on regardait si une touche X etait pressé, et
    #  on effectuait le mouvement en consequence en faisant appel au fonctions.
    # ma technique actuel est de creer la fonction update, de la mettre dans la boucle du jeu et elle execute les mouvements
    # directement depuis la fonction update en recuperant la touche pressé et regarde si elle a un correspondant.
    # la methode que j'utilise me parait etre meilleur car il n'y a pas besoin de creer des dizaines de fonctions,
    # et au niveau des variables concernant le joueur, exemple sa velocité ou sa position, cela crée une meilleur
    # compatibilité et une simplicité concernant les importations un peu partout

    # from main import game
    # self.rect.x += self.velocity_x
    # game.player.image = pygame.image.load('assets/sprite_player_right_run.png')

    # def left_move(self):

    # from main import game
    # self.rect.x -= self.velocity_x
    # game.player.image = pygame.image.load('assets/sprite_player_left_run.png')

    # def jump(self):

    # print('ze')
    # if not self.jumped:

    # self.rect.y += self.vel_y
    # self.jumped = True

    # self.vel_y += 1
    # if self.vel_y > 15:
    # self.rect.y += 15

    # if self.rect.bottom > 832:
    # self.rect.bottom = 832

    # self.jumped = False

    # fonction update ou tout est géré concernant le joueur
    def update(self, game_player_over):
        # l'update de sa position au debut de chaque update, quand le joueur se mouvoit on ajoute ou retire une quantite dx au joeur qu'on ajoute ensuite
        # a son self.rect.x, ce qui modifie sa position. Exemple: le joueur fait un mouvement sur la droite, on ajoute 5 a dx. A la fin de la boucle
        # on ajoute dx a la position du joueur, c'est le principe du mouvement du joueur.
        dx = 0
        dy = 0

        # si la varialbe game_player_over = 0, donc si le joueur est vivant
        # on y met ici ses mouvements, ses collisions, ses animations
        if game_player_over == 0:
            # on nomme la variable key, la touche pressée par le joueur
            key = pygame.key.get_pressed()
            # si la touche Z est pressée, si le dash est sur False, et si le cooldown de la competence = 0
            if key[pygame.K_z] and self.dash == False and self.dash_cooldown == 0:
                # si l'animation = 1, donc si la derniere touche pressée est R alors le dash s'effectue sur la droite
                if self.animation == 1:
                    # on avance l'update de la position en x à + 250
                    dx += 250
                    # on definit les postions pour dessiner les traits
                    pos1 = (self.rect.x, self.rect.y + 10)
                    pos2 = (self.rect.x + 250, self.rect.y + 10)
                    # on dessine le trait
                    pygame.draw.line(screen, (255, 255, 255), pos1, pos2, 1)
                    # pareil
                    pos3 = (self.rect.x, self.rect.y + 64)
                    pos4 = (self.rect.x + 250, self.rect.y + 64)
                    # pareil
                    pygame.draw.line(screen, (255, 255, 255), pos3, pos4, 1)
                    # pareil
                    pos5 = (self.rect.x, self.rect.y + 118)
                    pos6 = (self.rect.x + 250, self.rect.y + 118)
                    # pareil
                    pygame.draw.line(screen, (255, 255, 255), pos5, pos6, 1)
                    # animation de dash
                    dash = Dash_animation(player.rect.x + 250, player.rect.y + 64)
                    dash_animation_group.add(dash)
                # si l'animation = -1, donc si la derniere touche pressée est E alors le dash s'effectue sur la gauche
                elif self.animation == -1:
                    # on recule l'update de la postion en x à - 250
                    dx -= 250
                    # on definit les postions pour dessiner les traits
                    pos1 = (self.rect.x, self.rect.y + 10)
                    pos2 = (self.rect.x - 250, self.rect.y + 10)
                    # on definit les postions pour dessiner les traits
                    pygame.draw.line(screen, (255, 255, 255), pos1, pos2, 1)
                    # pareil
                    pos3 = (self.rect.x, self.rect.y + 64)
                    pos4 = (self.rect.x - 250, self.rect.y + 64)
                    # pareil
                    pygame.draw.line(screen, (255, 255, 255), pos3, pos4, 1)
                    # pareil
                    pos5 = (self.rect.x, self.rect.y + 118)
                    pos6 = (self.rect.x - 250, self.rect.y + 118)
                    # pareil
                    pygame.draw.line(screen, (255, 255, 255), pos5, pos6, 1)
                    # animation de dash
                    dash = Dash_animation(player.rect.x - 250, player.rect.y + 64)
                    dash_animation_group.add(dash)
                # on met le dash sur True
                self.dash = True
                # on met un cooldown
                self.dash_cooldown = 1000
            # si la touche espace est pressée et si le jump est sur False
            if key[pygame.K_SPACE] and self.jumped == False:
                # on retire 15 a la velocité en y
                self.vel_y = -15
                # on met le jump sur True pour eviter de spam le jump
                self.jumped = True
            # si la touche E est pressée
            if key[pygame.K_e]:
                # on retire 5 a l'update de la position en x
                dx -= 5
                # on change l'image du joueur pour qu'il ait un sprite à gauche qui coure
                self.image = pygame.image.load('assets/sprite_player_left__run.png')
                # on met la variable animation sur -1 pour gérer le changement d'animation du joueur lorqu'il ne bouge pas
                # ainsi que pour gérer les balles
                self.animation = -1
            # si la touche R est pressée
            if key[pygame.K_r]:
                # on ajoute 5 a l'update de position en x
                dx += 5
                # on change l'image du joueur pour qu'il ait un sprite à droite qui coure
                self.image = pygame.image.load('assets/sprite_player_right__run.png')
                # on change la variable animation
                self.animation = 1
            # si la touche P est pressée
            if key[pygame.K_p]:
                pass
                # si le cooldown pour tirer est = 0
                if self.bullet_cooldown == 0:
                    # on remet un cooldown pour tirer
                    self.bullet_cooldown = 30
                    # from Animation_group_enemy import wave_bullet_group, Wave_bullet
                    # on genere la balle
                    wave_bullet_add = Wave_bullet(player.rect.centerx + (0.6 * player.rect.size[0] * player.animation),
                                                  player.rect.centery, player.animation)
                    # on l'add au group de sprite des autres balles
                    wave_bullet_group.add(wave_bullet_add)

            # on applique la gravité sur le joueur, plus cette valeur est basse plus la gravité est haute et plus on vole,
            # et plus elle est haute plus la gravité est basse
            self.vel_y += 0.70
            # on determine le cooldown pour rejump, la valeur etant superieur à celle du jump, il est impossible de jump
            # et voler à l'infini
            if self.vel_y > 16:
                self.vel_y = 16
                # on remet le jump pour sauter a chaque fois
                self.jumped = False
            # on ajoute a l'update de la position la velocité en y
            dy += self.vel_y

            # cooldown pour le dash
            if self.dash_cooldown > 0:
                # on baisse de 1 la valeur jusqu'à 0 où on pourra utiliser le dash
                self.dash_cooldown -= 1
                # on remet le dash a chaque fois pour etre sur qu'il est disonible
                self.dash = False

            # cooldown pour la balle, pour eviter d'avoir a rester appuyer sur P
            if self.bullet_cooldown > 0:
                # on baisse de 1 la valeur
                self.bullet_cooldown -= 1

            # self.is_falling = True

            # collisions avec les tiles de la map
            # il est important de mettre les collisions avant les touches, car il y aurai des problemes pour la variable
            # dx
            for tile in world.tile_list:
                # si on arrive en face d'une tile, l'update de la position de met à 0, pour eviter de passer a travers
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.largeur, self.hauteur):
                    # on annule l'update de la position
                    dx = 0
                # on gere les collisions concernant le haut et le bas de la tile
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.largeur, self.hauteur):
                    # si le haut du joueur tape le bas de la tile
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        # on annule la velocité en y du joueur pour eviter de traverser la tile
                        self.vel_y = 0
                    # si le bas du joueur touche le haut d'une tile
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        # on annule la velocité en y du joueur pour eviter de traverser la tile
                        self.vel_y = 0
                        # on remet le jump car on sait qu'il a touche le haut d'une tile
                        self.jumped = False
                        # self.is_falling = False

            # si le joueur rentre en collision avec le blob
            if pygame.sprite.spritecollide(self, blob_enemy_group, False):
                # on met la variable game_player_over sur -1 pour signifier que le joueur est mort et faire les actions
                # en conséquences
                game_player_over = -1

            # si le joueur rentre en collision avec les spikes
            if pygame.sprite.spritecollide(self, spikes_group, False):
                # on met la variable game_player_over sur -1 pour signifier que le joueur est mort et faire les actions
                # en conséquences
                game_player_over = -1

            if pygame.sprite.spritecollide(self, portal_group, False):
                if normal_key_number == key_fragment_number:
                    game_player_over = 1
                else:
                    draw_text("Vous n'avez pas récolté tous les fragments de clés !", font, white, 350, 150)

            if pygame.sprite.spritecollide(self, boss_group, False):
                game_player_over = -1

            if pygame.sprite.spritecollide(self, boss_bullet_group, True):
                game_player_over = -1

            # on ajoute dx et dy a la position du joueur pour le déplacer
            self.rect.x += dx
            self.rect.y += dy

            # si le joueur dépasse le bas de l'écran, il est automatiquement replacé
            # utile en cas de bug
            if self.rect.bottom > 960:
                self.rect.bottom = 960
                dy = 0

            # si le joueur dépasse l'ecran, il est bloqué
            if self.rect.x >= 1536:
                self.rect.x = 1536
            if self.rect.x < 0:
                self.rect.x = 0

        # si le joueur est mort, car la variable game_player_over = -1
        elif game_player_over == -1:
            # death_animation = Death_animation(self.rect.centerx, self.rect.centery)
            # death_animation_group.add(death_animation)
            # mettre ajour le compteur pour l'animation de mort du joueur
            self.death_counter += 1
            # si l'animation est terminée, alors on affiche une image sans rien
            if self.death_counter >= 21:
                self.image = pygame.image.load('assets/player_death_animation/player_death_final.png')
            # en dessous du nombre de frame dans l'animation, alors on update l'image en fonction du compteur
            elif self.death_counter <= 20:
                self.image = pygame.image.load(
                    'assets/player_death_animation/player_death_animation' + str(self.death_counter) + '.png')
            # dessiner le texte 'vous etes décédé
            draw_text('Vous êtes décécé ! Vous pouvez appuyez sur le bouton RETRY pour réapparaître', font, green, 55,
                      64)
            # dessiner le attention
            draw_text(
                'Attention : lorsque vous réapparaîssez, tous les monstres et les fragments de clés réapparaîssent, cela inclu donc également votre compteur de fragments',
                font_tips, red, 150, 230)

        # afficher le joueur sur l'ecran
        screen.blit(self.image, self.rect)

        # on retourne la variable game_player_over pour mettre à jour le joueur
        return game_player_over

    # fonction qui regroupe toutes les variables du joueur qui seront utilisés
    # elle permet de reset le joueur lorsqu'on clique sur le bouton RETRY
    def reset(self):
        # variable pour l'image de face quand on lance le jeu
        self.image = pygame.image.load('assets/sprite_player_front_final.png')
        # self.image_verification = pygame.image.load('')
        # variable velocité
        self.vel_x = 0
        self.vel_y = 0
        # on met les variables jump et dash sur False pour pouvoir sauter et dash directement
        self.jumped = False
        self.dash = False
        # variable cooldown pour le dash, l'animation de cercle et de balles
        self.dash_cooldown = 1
        self.circle_cooldown = 1
        self.bullet_cooldown = 0
        # variable pour l'animation de mort
        self.death_counter = 0

        # positiondu joueur
        self.rect = self.image.get_rect()
        # position de base du joueur lorsqu'il spawn
        self.rect.x = 128
        self.rect.y = 800
        # variable pour la hauteur et largeur de l'ecran, utile pour les collisions
        self.hauteur = self.image.get_height()
        self.largeur = self.image.get_width()
        # variable animation du joueur
        self.animation = 0

    # fonction animation du joueur, elle s'active lorsque le joueur ne presse aucune touches, cela permet de changer
    # le sprite du joueur. Exemple; la derniere touche pressée par le joueur est R, donc il se trouve sur la droite
    # cela change le sprite du joueur sur la droite qui coure en sprite sur la droite qui est statique
    # il passe de 'sprite_player_right__run.png' à 'sprite_player_right__norun.png'
    # pareil pour la gauche
    def player_animation(self):

        if self.animation == 1:
            self.image = pygame.image.load('assets/sprite_player_right__norun.png')
        if self.animation == -1:
            self.image = pygame.image.load('assets/sprite_player_left__norun.png')


# --------------------------------------------------------------------------------------------------------------------!

# class qui permet d'effectuer une animation lors du dash
class Dash_animation(pygame.sprite.Sprite):
    def __init__(self, x, y):

        pygame.sprite.Sprite.__init__(self)
        self.images = []
        # on genere les images pour les mettre dans une liste
        for num in range(1, 16):
            img = pygame.image.load(f"assets/circle_animation_dash/circle_animation_dash{num}.png").convert_alpha()
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()

        if player.animation == 1:
            self.rect.center = [player.rect.x + 250, player.rect.y + 64]
        elif player.animation == -1:
            self.rect.center = [player.rect.x - 250, player.rect.y + 64]
        elif player.animation == 0:
            pass
        self.counter = 0

    def update(self):
        dash_speed = 4
        # update explosion animation
        self.counter += 1

        if self.counter >= dash_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        # si l'animation est complete on tue la class
        if self.index >= len(self.images) - 1 and self.counter >= dash_speed:
            self.kill()


dash_animation_group = pygame.sprite.Group()


# class pour l'animation de la balle qui se détruit lors de l'impact d'une plateforme
# le procédé est le meme que pour le dash_animation
class Hitshot_tile_animation(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 15):
            img = pygame.image.load(f"assets/hitshot_animation/hitshot_animation{num}.png").convert_alpha()
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y + 32]
        self.counter = 0

    def update(self):
        hitshot_speed = 4
        self.counter += 1

        if self.counter >= hitshot_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        if self.index >= len(self.images) - 1 and self.counter >= hitshot_speed:
            self.kill()


hitshot_tile_animation_group = pygame.sprite.Group()


# ----------------------------------------------------------------------------------------------------------------------!
# class pour generer la balle
class Wave_bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.damage = 1
        self.image = pygame.image.load('assets/wave_projectile.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.rect.x = x
        self.rect.y = y
        self.direction = player.animation
        self.hauteur = self.image.get_height()
        self.largeur = self.image.get_width()

    def update(self):
        # le sens de la balle est defini par la direction du joueur
        self.rect.x += (self.direction * self.speed)
        # si le joueur n'a pas d'animation, on tue la balle
        if player.animation == 0:
            self.kill()
        # si la balle depasse l'ecran on la tue pour eviter les gros lags spikes
        if self.rect.right < 0 or self.rect.left > largeur_ecran:
            self.kill()
        # s'il y a collision avec un objet du monde, notamment la plateforme,on joue l'animation
        # de desintégration de la balle
        for tile in world.tile_list:
            if tile[1].colliderect(self.rect.x, self.rect.y, self.largeur, self.hauteur):
                hitshot_tile = Hitshot_tile_animation(self.rect.x + 18, self.rect.y)
                hitshot_tile_animation_group.add(hitshot_tile)
                self.kill()
        # if pygame.sprite.spritecollide(wave_bullet_group, False):
        # self.kill()


wave_bullet_group = pygame.sprite.Group()


# ----------------------------------------------------------------------------------------------------------------------!
# class pour les spikes
class Spikes(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/spikes.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.counter = 0
        self.damage = 1
        self.rect.x = x
        self.rect.y = y


spikes_group = pygame.sprite.Group()


# ----------------------------------------------------------------------------------------------------------------------!
# class portail
class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('assets/portal.png')
        self.image = pygame.transform.scale(img, (game_tile, game_tile * 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


portal_group = pygame.sprite.Group()


# class pour les fragments le clés
class Key_fragment(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/key_fragment2.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


key_fragment_group = pygame.sprite.Group()


# Classe du blob
class Blob_enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # self.images = []
        # for num in range(1, 4):
        # img = pygame.image.load(f"assets/blob_enemy_animation/blob_enemy_animation{num}.png")
        # self.images.append(img)
        # self.index = 0
        # self.image = self.images[self.index]

        # on definit l'image de base
        self.image = pygame.image.load('assets/blob_enemy_animation/blob_enemy_animation1.png')
        # on recupere sa position
        self.rect = self.image.get_rect()
        # compteur varaible pour l'animation
        self.counter = 0
        # on recupere ses postions precise en x et y pour pouvoir le placer sur la map
        self.rect.x = x
        self.rect.y = y

    # fonction update du mob, où on gere ses animations et les collisions
    def update(self):

        # blob_animation_speed = 4

        self.counter += 1
        # if self.counter >= blob_animation_speed and self.index < len(self.images) - 1:
        # self.counter = 0
        # self.index += 1
        # self.image = self.images[self.index]

        # if self.index >= len(self.images) and self.counter >= blob_animation_speed:
        # self.index = 0
        # self.counter = 0
        # self.image = self.images[1]
        #
        #
        # A FIXER SI J'AI LE TEMPS
        #
        # tous les 15 ticks, l'animation change et revient a 0 quand elle est terminée
        if self.counter == 15:
            self.image = pygame.image.load('assets/blob_enemy_animation/blob_enemy_animation1.png')
        elif self.counter == 30:
            self.image = pygame.image.load('assets/blob_enemy_animation/blob_enemy_animation2.png')
        elif self.counter == 45:
            self.image = pygame.image.load('assets/blob_enemy_animation/blob_enemy_animation3.png')
            self.counter = 0

        # collisions avec la balle, entre deux sprites. L'argument True veut dire le sprite qui rentre en contact avec le blob
        # est supprimé
        if pygame.sprite.spritecollide(self, wave_bullet_group, True):
            # on supprime egalement le blob
            self.kill()


# on cree un groupe de blob pour pouvoir les afficher dans la boucle.
# on les ajoute dans ce groupe quand on veut les faire spawn
blob_enemy_group = pygame.sprite.Group()


# ----------------------------------------------------------------------------------------------------------------------!

# class du boss
class Boss(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/boss_try3.png').convert_alpha()
        # self.image = pygame.transform.scale(img, (896, 896)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = 40
        self.shot_counter = 0
        self.game_end = 0

    def update(self):

        global game_end

        if game_end == 0:
            # si la balle touche le boss, alors il perd de la vie

            self.shot_counter += 1

            if pygame.sprite.spritecollide(self, wave_bullet_group, True):
                self.health -= 1
            # s'il n'a plus de vie, on le tue
            if self.health == 0:
                self.kill()
                game_end = 1
            # tous les 500 ticks, on fait tirer une balle sur la position du joueur
            if self.shot_counter == 500:
                # start_bullet_pos = random.choice(bullet_pos)
                boss_bullet_add = Boss_bullet(self.rect.centerx + (0.6 * self.rect.size[0] * -1), player.rect.y)
                boss_bullet_group.add(boss_bullet_add)
                self.shot_counter = 0

        if game_end == 1:
            pass


boss_group = pygame.sprite.Group()


# balle du boss
class Boss_bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 5
        self.image = pygame.image.load('assets/boss_bullet.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        #meme procede que pour la balle du joueur
        self.rect.x -= self.speed

        if self.rect.x < 0:
            self.kill()


boss_bullet_group = pygame.sprite.Group()


# -----------------------------------------------------------------------------------------------------------------------!
#class map
class Map():

    def __init__(self, data):
        self.tile_list = []
        tile = []

        sprite_platform = pygame.image.load('assets/platform.png').convert_alpha()
        sprite_full_platform = pygame.image.load('assets/full_platform.png').convert_alpha()

        numero_ligne = 0
        #pour les lignes du fichier
        for row in data:
            numero_colonne = 0
            #on regarde le chiffre dans la data
            for tile in row:
                #si le chiffre est 1 alors
                if tile == 1:
                    #on l'ajoute à un groupe qui permettra de l'afficher, le supprimer...etc
                    #On utilise ce procédé pour toutes les autres tiles
                    key_fragment_add = Key_fragment(numero_colonne * game_tile, numero_ligne * game_tile)
                    key_fragment_group.add(key_fragment_add)
                #si le chiffre est 2 alors.. et etc...
                if tile == 2:
                    img = sprite_platform
                    img_rect = img.get_rect()
                    img_rect.x = numero_colonne * game_tile
                    img_rect.y = numero_ligne * game_tile
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 3:
                    spikes_add = Spikes(numero_colonne * game_tile, numero_ligne * game_tile)
                    spikes_group.add(spikes_add)

                if tile == 4:
                    blob_enemy_add = Blob_enemy(numero_colonne * game_tile, numero_ligne * game_tile)
                    blob_enemy_group.add(blob_enemy_add)
                if tile == 5:
                    portal_add = Portal(numero_colonne * game_tile, numero_ligne * game_tile - game_tile)
                    portal_group.add(portal_add)
                if tile == 6:
                    img = sprite_full_platform
                    img_rect = img.get_rect()
                    img_rect.x = numero_colonne * game_tile
                    img_rect.y = numero_ligne * game_tile
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 7:
                    test_boss_add = Boss(numero_colonne * game_tile, numero_ligne * game_tile)
                    boss_group.add(test_boss_add)
                #on ajoute une colonne
                numero_colonne += 1
            #on ajoute une ligne
            numero_ligne += 1
    #on dessine la map selon les paramètres de la tile
    def draw(self):

        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


# ----------------------------------------------------------------------------------------------------------------------!

running = True
# fullscreen = False
background = pygame.image.load('assets/game_background.png').convert_alpha()
black_background = pygame.image.load('assets/black_screen.png').convert_alpha()
credits_background = pygame.image.load('assets/credits_back.png').convert_alpha()

#fonction pour dessiner un grillage, juste pour le design
def grillage():
    for ligne in range(0, 26):
        pygame.draw.line(screen, (255, 255, 255), (0, ligne * game_tile), (largeur_ecran, ligne * game_tile))
    for ligne in range(0, 26):
        pygame.draw.line(screen, (255, 255, 255), (ligne * game_tile, 0), (ligne * game_tile, hauteur_ecran))


# ----------------------------------------------------------------------------------------------------------------------!

# world_data = [
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5],
# ]

# ----------------------------------------------------------------------------------------------------------------------!
#on genere le 1er level
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = Map(world_data)
player = Player()
#on genere tous les boutons, les textes....etc
right_player = pygame.image.load('assets/sprite_player_right__run.png')
left_player = pygame.image.load('assets/sprite_player_left__run.png')
circle_animation_dash = pygame.image.load('assets/circle_animation_dash/circle_animation_dash15.png')
restart_button = Button(largeur_ecran // 2 - 175, hauteur_ecran // 2, restart_button_img)
start_button = Button(largeur_ecran // 2 - 275, hauteur_ecran // 2 - 200, start_button_img)
history_button = Button(largeur_ecran // 2 - 270, hauteur_ecran // 2 + 300, history_button_img)
save_data_button = Button(largeur_ecran // 2 - 270, hauteur_ecran // 2 + 150, history_button_img)
credits_button = Button(1100, 750, credits_button_image)
back_button = Button(-50, 750, back_button_image)
quit_button = Button(0, 0, quit_button_image)

key_visual_score = Key_fragment(-10, 20)
key_visual_fragment_group = pygame.sprite.Group()
key_visual_fragment_group.add(key_visual_score)
key_frame = pygame.image.load('assets/key_frame2.png')
text_cooldown1 = 500  # 500
text_cooldown2 = 600  # 600
final_text_cooldown = 600  # 600

final_moving1 = ending_block(550, 960, 2, "Vous avez tué le boss final", font, white)
final_moving2 = ending_block(550, 960, 2, "Le royaume des blobs a pris fin", font, white)
final_moving3 = ending_block(550, 960, 2, "Bravo et merci d'avoir joué", font, white)
next_move = 0

# ----------------------------------------------------------------------------------------------------------------------!

while running:
    #on genere l'histoire du début
    #on fait des boucles imbriqués qui décremente des valeurs a chaque tours de boucles
    #de ce fait, on genere les textes au fur et a mesure
    #c'est pas le truc le plus optimisé
    if history_menu:
        screen.blit(black_background, (0, 0))
        draw_text(
            "'Eh...Euh ! Où..suis-je ? Je..qui suis-je. Je crois que mon prénom commence par un G; ga, gi, gr...go'",
            font_history, white, 300, 200)

        if text_cooldown1 == 0:
            draw_text(
                "'Oui c'est ça ! Go ! GONTRAN, ça y est ça me revient ! Mais qu'est-ce que je fais ici, et pourquoi est-ce que je suis dans un forêt ?'",
                font_history, white, 150, 400)

            if text_cooldown2 == 0:
                draw_text(
                    "'AHHHHH ! Mais qu'est-ce que c'est que cette chose visqueuse ? un blob ?! Peut importe, il faut que je parte, et vite !'",
                    font_history, white, 250, 600)

                if final_text_cooldown == 0:
                    #si la cinématique des finie, alors on active le menu principal
                    history_menu = False
                    main_menu = True

                elif final_text_cooldown != 0:
                    final_text_cooldown -= 1

            elif text_cooldown2 != 0:
                text_cooldown2 -= 1

        elif text_cooldown1 != 0:
            text_cooldown1 -= 1


    else:
        history_menu = False

        screen.blit(background, (0, 0))
        # grillage()
        if main_menu:
            #selon les boutons cliqués, on active les menus où les instructions correspondantes
            draw_text('Déplacez vous avec E et R, tirez avec P, et faites un dash avec Z', font, white, 250, 600)
            draw_text('/!\ NE JOUEZ AU JEU QUE SI LA RESOLUTION DE VOTRE ECRAN EST SUPERIEUR A 1600x900', font_tips, white, 400, 300)
            if start_button.draw():
                main_menu = False
                game_play = True
            if credits_button.draw():
                main_menu = False
                credits_menu = True
            if quit_button.draw():
                running = False
                main_menu = False
                pygame.quit()
        #CE BOUT DE CODE PERMET DE SAVE LES LEVELS A PARTIR DE LA DATA CONFIGURABLE A LA MAIN LIGNE 826 à 842
        # if save_data_button.draw():
        #   pickle_out = open(f'level_data', 'wb')
        #  pickle.dump(world_data, pickle_out)
        # pickle_out.close()

        elif main_menu == False and game_play == True:
            #si le bouton start est cliqué, le gameplay est activé

            history_menu = False
            #si le jeu n'est pas fini
            if game_end == 0:
                #ON UPDATE, CREE ET DESSINE TOUT LES SPRITES, CLASS...ETC
                wave_bullet_group.update()
                wave_bullet_group.draw(screen)
                dash_animation_group.draw(screen)
                dash_animation_group.update()
                hitshot_tile_animation_group.draw(screen)
                hitshot_tile_animation_group.update()
                spikes_group.draw(screen)
                world.draw()
                blob_enemy_group.draw(screen)
                key_fragment_group.draw(screen)
                key_visual_fragment_group.draw(screen)
                portal_group.draw(screen)
                boss_group.draw(screen)
                boss_bullet_group.draw(screen)
                screen.blit(key_frame, (0, 0))
                #si le joueur est en vie alors on update les monstres
                if game_player_over == 0:
                    blob_enemy_group.update()
                    boss_bullet_group.update()
                    boss_group.update()
                    #si le joueur touche une clé alors on incrémente le compteur des fragments de clés
                    if pygame.sprite.spritecollide(player, key_fragment_group, True):
                        if game_player_over == 0:
                            key_fragment_number += 1

                            if key_fragment_number == 41:
                                pass

                    if game_end == 0:
                        #on affiche le nombre de fragments de clés
                        if game_player_over == 0:
                            draw_text('X ' + str(key_fragment_number), font_score, white, 40, 32)
                        #si le joueur meurt on reset son nombre de clés à la normale
                        if game_player_over == -1:
                            draw_text('X ' + str(reset_key_number), font_score, white, 40, 32)

                    else:
                        pass
                #ON UPDATE LE JOUEUR
                game_player_over = player.update(game_player_over)
                if game_player_over == -1:
                    if restart_button.draw():
                        #on reset le monde si le joueur est mort et clique sur le bouton restart
                        key_fragment_number = reset_key_number
                        world_data = []
                        world = reset_level(level)
                        game_player_over = 0
                #si le joueur touche un portail et qu'il a le nombre de clés nécessaire
                if game_player_over == 1:
                    level += 1
                    if level == 7:
                        #si le level est le 7 alors plus besoin de clés car c'est la phase de boss
                        key_fragment_number = 0
                        reset_key_number = 0
                    #si on est sur le niveau 6, le nombre de clés est spécifiques
                    if level == 6:
                        reset_key_number = 40
                        normal_key_number = 41
                    if level <= 5:
                        #si le level est inf ou egal a 5 alors on augmente de 8 le nombre de clés normales, et celle de reset
                        normal_key_number += 8
                        reset_key_number += 8
                    if level <= max_levels:
                        world_data = []
                        world = reset_level(level)
                        game_player_over = 0
            else:
                #si le jeu est terminé, si le boss est tué, alors on affiche les textes de fin et on affiche le fond
                screen.blit(black_background, (0, 0))
                final_moving1.update()
                next_move += 1
                if next_move > 200:
                    final_moving2.update()
                    if next_move > 400:
                        final_moving3.update()

        #menu de crédits, on affiche un fond d'ecran différent et on affiche tout les textes nécessaires
        elif main_menu == False and credits_menu == True:
            screen.blit(credits_background, (0, 0))
            if back_button.draw():
                credits_menu = False
                main_menu = True
            draw_text("Où j'ai appris les débuts de pygame; une classe; les mouvements... : Graven sur youtube",
                      font_tips, white, 500, 50)
            draw_text(
                "La ligne directrice que j'ai suivi et qui m'a pas mal aidé notamment pour tirer, les tilemaps : Coding with russ sur youtube",
                font_tips, white, 350, 100)
            draw_text("Stack Overflow évidemment, qui m'a aidé sur les erreurs de programmes", font_tips, white, 600,
                      150)
            draw_text(
                "Elthen, à qui j'ai emprunté un design de portail : https://elthen.itch.io/2d-pixel-art-portal-sprites",
                font_tips, white, 450, 200)
            draw_text(
                "Bleachfan190 pour le design en grande partie du joueur : https://www.deviantart.com/bleachfan190/art/LIMBO-Sprite-358445232",
                font_tips, white, 350, 250)
            draw_text('http://pixelartmaker.com/art/4d8349e217c1d18 pour le bouton start', font_tips, white, 600, 300)
            draw_text('http://pixelartmaker.com/art/a8e695821e8f090 pour le bouton credits', font_tips, white, 600, 350)
            draw_text('http://pixelartmaker.com/art/c8eeec256677062 pour le bouton quit', font_tips, white, 600, 400)
            draw_text('http://pixelartmaker.com/art/54c086c26230c86 pour le bouton back', font_tips, white, 600, 450)
            draw_text('Logiciel :', font_tips, white, 750, 750)
            draw_text('Photoshop', font_tips, white, 750, 850)
            draw_text('Pycharm', font_tips, white, 750, 900)
    #on update tout ce qui a avant
    pygame.display.flip()
    #si on quitte le jeu avec la croix alors le programme se ferme
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            print("Le jeu se ferme")

        # elif event.type == pygame.RESIZABLE:                TEST TOUCHES ET RESIZE

        # if not fullscreen:
        # screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        # elif event.type == pygame.KEYDOWN:
        # game.pressed[event.key] = True

        # elif event.type == pygame.KEYUP:
        # game.pressed[event.key] = False
    #si aucune touche n'est pressé alors cela permet de changer l'animation du joueur, voir ligne 453
    if not any(pygame.key.get_pressed()):
        # player.image = pygame.image.load('assets/sprite_player_front_final.png')
        player.player_animation()
    #on cale le nombre de FPS sur la variable en début de programme
    clock.tick(FPS)
pygame.quit()
