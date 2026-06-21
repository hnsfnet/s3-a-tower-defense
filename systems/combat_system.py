from tower import Projectile, LightningEffect, Explosion


class CombatSystem:
    def __init__(self):
        pass

    def update(self, dt, towers, enemies, projectiles, effects):
        all_rewards = []

        for tower in towers:
            rewards = tower.update(dt, enemies, projectiles, effects)
            all_rewards.extend(rewards)

        for proj in projectiles:
            rewards = proj.update(dt, enemies)
            all_rewards.extend(rewards)

        for explosion in effects:
            if isinstance(explosion, Explosion):
                explosion.update(dt)

        for effect in effects:
            if isinstance(effect, LightningEffect):
                effect.update(dt)

        return all_rewards

    def cleanup(self, projectiles, effects):
        alive_projectiles = [p for p in projectiles if p.active]
        alive_effects = [e for e in effects if e.active]
        return alive_projectiles, alive_effects

    def update_enemies(self, dt, enemies):
        for enemy in enemies:
            enemy.update(dt)

    def cleanup_dead_enemies(self, enemies):
        return [e for e in enemies if e.alive]
