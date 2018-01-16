import sys 
from time import sleep
import pygame

from bullet import Bullet
from alien import Alien

def check_keydown_events(event, ai_settings, screen, ship, bullets):
	if event.type == pygame.KEYDOWN:
		if event.key == pygame.K_RIGHT:
			ship.moving_right = True
		elif event.key == pygame.K_LEFT:
			ship.moving_left = True
		elif event.key == pygame.K_SPACE:
			fire_bullet(ai_settings, screen, ship, bullets)
		elif event.key == pygame.K_q:
			sys.exit()

def fire_bullet(ai_settings, screen, ship, bullets):
	if len(bullets) < ai_settings.bullets_allowed:
		new_bullet = Bullet(ai_settings, screen, ship)
		bullets.add(new_bullet)

def check_keyup_events(event, ai_settings, screen, ship, bullets):
	if event.type == pygame.KEYUP:
		if event.key == pygame.K_RIGHT:
			ship.moving_right = False
		elif event.key == pygame.K_LEFT:
			ship.moving_left = False

def check_events(ai_settings, screen, stats, play_button, ship, 
		aliens, bullets):

	#Watch for keyboard and mouse events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		elif event.type == pygame.KEYDOWN:
			check_keydown_events(event, ai_settings, screen, ship, bullets)
		elif event.type == pygame.KEYUP:
			check_keyup_events(event, ai_settings, screen, ship, bullets)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			mouse_x, mouse_y = pygame.mouse.get_pos()
			check_play_button(ai_settings, screen, stats, play_button, 
				ship, aliens, bullets, mouse_x, mouse_y)

def check_play_button(ai_settings, screen, stats, play_button, ship, 
		aliens, bullets, mouse_x, mouse_y):
	
	#start game when player clicks PLAY
	button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
	if button_clicked and not stats.game_active:
		ai_settings.initialize_dynamic_settings()
		pygame.mouse.set_visible(False)
		
		stats.reset_stats()
		stats.game_active = True

		aliens.empty()
		bullets.empty()

		create_fleet(ai_settings, screen, ship, aliens)
		ship.center_ship()

def update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets, 
		play_button):

	screen.fill(ai_settings.bg_color)

	for bullet in bullets.sprites():
		bullet.draw_bullet()
	ship.blitme()
	aliens.draw(screen)
	sb.show_score()

	if not stats.game_active:
		play_button.draw_button()

	# Makes most recently drawn screen visible
	pygame.display.flip()

def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
	#delete old bullets
	bullets.update()

	for bullet in bullets.copy():
		if bullet.rect.bottom <= 0:
			bullets.remove(bullet)

	check_bullet_alien_collision(ai_settings, screen, stats, sb,
		 ship, aliens, bullets)

def check_bullet_alien_collision(ai_settings, screen, stats, sb,
		 ship, aliens, bullets):

	#remove bullets and aliens that have collided
	collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
	if collisions:
		for aliens in collisions.values():
			stats.score += ai_settings.alien_points * len(aliens)
			sb.prep_score()
		check_high_score(stats, sb)

	if len(aliens) == 0:
		#destroy exsisting bullets, speed up game and create new fleet
		bullets.empty()
		ai_settings.increase_speed()
		create_fleet(ai_settings, screen, ship, aliens)
			
def get_number_aliens_x(ai_settings, alien_width):
	#determine number of aliens that fit in a row
	available_space_x = ai_settings.screen_width - 2 * alien_width
	number_aliens_x = int(available_space_x / (2 * alien_width))
	return number_aliens_x

def get_number_rows(ai_settings, ship_height, alien_height):
	#determine number of rows of aliens that fit on screen
	available_space_y = (ai_settings.screen_height - 
							(3 * alien_height) - ship_height)
	number_rows = int(available_space_y / (2 * alien_height))
	return number_rows

def create_alien(ai_settings, screen, aliens, alien_number, row_number):
	#create an alien and place it in the row
	alien = Alien(ai_settings, screen)
	alien_width = alien.rect.width
	alien.x = alien_width + 2 * alien_width * alien_number
	alien.rect.x = alien.x
	alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
	aliens.add(alien)

def create_fleet(ai_settings, screen, ship, aliens):
	alien = Alien(ai_settings, screen)
	number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
	number_rows = get_number_rows(ai_settings, ship.rect.height,
		alien.rect.height)

	#create the fleet
	for row_number in range(number_rows):
		for alien_number in range(number_aliens_x):
			create_alien(ai_settings, screen, aliens, 
				alien_number, row_number)

def check_fleet_edges(ai_settings, aliens):
	for alien in aliens.sprites():
		if alien.check_edges():
			change_fleet_direction(ai_settings, aliens)
			break

def change_fleet_direction(ai_settings, aliens):
	#drop entire fleet and change direction
	for alien in aliens.sprites():
		alien.rect.y += ai_settings.fleet_drop_speed
	ai_settings.fleet_direction *= -1

def ship_hit(ai_settings, stats, screen, ship, aliens, bullets):
	#respond to ship being hit
	if stats.ships_left > 0:
		stats.ships_left -= 1

		aliens.empty()
		bullets.empty()
		create_fleet(ai_settings, screen, ship, aliens)
		ship.center_ship()

		sleep(0.5)
	else:
		stats.game_active = False
		pygame.mouse.set_visible(True)

def check_aliens_bottom(ai_settings,stats, screen, ship, aliens, bullets):
	#check if any aliens have reached bottom of screen
	screen_rect = screen.get_rect()
	for alien in aliens.sprites():
		if alien.rect.bottom >= screen_rect.bottom:
			ship_hit(ai_settings, stats, screen, ship, aliens, bullets)
			break

def update_aliens(ai_settings, stats, screen, ship, aliens, bullets):
	#update position of all aliens
	check_fleet_edges(ai_settings, aliens)
	aliens.update()

	#look for alien-ship collisions
	if pygame.sprite.spritecollideany(ship, aliens):
		ship_hit(ai_settings, stats, screen, ship, aliens, bullets)
		print("Ship hit!!")
	check_aliens_bottom(ai_settings,stats, screen, ship, aliens, bullets)

def check_high_score(stats, sb):
	if stats.score > stats.high_score:
		stats.high_score = stats.score
		sb.prep_high_score()