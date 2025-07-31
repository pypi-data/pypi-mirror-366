"""
Complete physics demo with collision detection
"""

import pygame as pg
from pygame import Color, Vector2
import sys
from pyg_engine import Size, BasicShape, Tag, GameObject, Engine, PymunkRigidBody, PymunkBoxCollider, PymunkCircleCollider, Materials
import os
import sys
from pathlib import Path

# Add the examples directory to the Python path so examples can import from scripts/
examples_dir = Path(__file__).parent
scripts_dir = examples_dir / "scripts"
if scripts_dir.exists():
    sys.path.insert(0, str(scripts_dir))

def get_script_path(script_name):
    """Get the absolute path to a script in the examples/scripts directory."""
    return str(scripts_dir / script_name)

class CameraController(GameObject):
    """Camera controller that keeps all dynamic objects in view."""
    
    def __init__(self, engine):
        super().__init__(name="CameraController", position=Vector2(0, 0), size=Vector2(0, 0), color=Color(0, 0, 0))
        
        self.engine = engine
        
        # Camera bounds for keeping everything in view
        self.camera_bounds = Vector2(2000, 1500)  # World space bounds
    
    def update(self, engine):
        """Update camera to keep all dynamic objects in view."""
        super().update(engine)
        
        # Find all dynamic game objects (exclude static environment)
        dynamic_objects = []
        all_objects = engine._Engine__gameobjects
        
        for obj in all_objects:
            if (obj and obj.enabled and hasattr(obj, 'position') and hasattr(obj, 'size') and 
                hasattr(obj, 'tag') and obj.tag == Tag.Player):  # Only track players
                dynamic_objects.append(obj)
        
        if not dynamic_objects:
            return
        
        # Calculate bounds of all dynamic objects
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for obj in dynamic_objects:
            # Calculate object bounds
            obj_min_x = obj.position.x - obj.size.x/2
            obj_max_x = obj.position.x + obj.size.x/2
            obj_min_y = obj.position.y - obj.size.y/2
            obj_max_y = obj.position.y + obj.size.y/2
            
            min_x = min(min_x, obj_min_x)
            max_x = max(max_x, obj_max_x)
            min_y = min(min_y, obj_min_y)
            max_y = max(max_y, obj_max_y)
        
        # Add padding
        padding = 200  # Increased padding for better visibility
        min_x -= padding
        max_x += padding
        min_y -= padding
        max_y += padding
        
        # Calculate center and size of all objects
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        width = max_x - min_x
        height = max_y - min_y
        
        # Calculate optimal zoom to fit everything
        screen_width, screen_height = engine.getWindowSize().w, engine.getWindowSize().h
        zoom_x = screen_width / width if width > 0 else 1
        zoom_y = screen_height / height if height > 0 else 1
        optimal_zoom = min(zoom_x, zoom_y, 1.5)  # Don't zoom out too much
        optimal_zoom = max(optimal_zoom, 0.3)  # Don't zoom in too much
        
        # Smoothly adjust camera position and zoom
        target_pos = Vector2(center_x, center_y)
        current_pos = engine.camera.position
        
        # Smooth camera movement
        lerp_factor = 0.03  # Adjust for smoother/faster movement
        new_pos = current_pos + (target_pos - current_pos) * lerp_factor
        engine.camera.position = new_pos
        
        # Smooth zoom adjustment
        current_zoom = engine.camera.zoom
        zoom_lerp_factor = 0.02  # Adjust for smoother/faster zoom
        new_zoom = current_zoom + (optimal_zoom - current_zoom) * zoom_lerp_factor
        engine.camera.zoom = new_zoom

def main():
    print("=== Physics Demo: Three Players + Floor ===")

    # Create engine
    engine = Engine(fpsCap=0, windowName="Three Players Physics Demo", size=Size(1200, 800))
    Engine.log_debug = True

    # Configure collision layers
    engine.physics_system.collision_layers = {
        "Player": ["Player", "Environment"],  # Players collide with other players and environment
        "Environment": ["Player"],  # Environment collides with players
        "NoCollision": []  # Objects that don't collide
    }

    print("Creating three players and floor...")

    # ================ PLAYER 1: Color-Changing Detector ================
    detector_player = GameObject(
        name="detector_player",
        basicShape=BasicShape.Circle,
        color=Color(255, 100, 100),  # Light red (will change colors)
        position=Vector2(200, 300),  # Start high up on the left
        size=Vector2(50, 50),
        tag=Tag.Player,
        show_rotation_line=True  # Enable rotation line for this object
    )

    # Add physics components
    detector_player.add_component(PymunkRigidBody,
                                 mass=1,
                                 gravity_scale=1.0,
                                 drag=0.05,  # Moderate drag for natural feel
                                 use_gravity=True,
                                 lock_rotation=False)  # Allow rotation for more dynamic movement

    detector_player.add_component(PymunkCircleCollider,
                                 radius=25,
                                 material=Materials.RUBBER,  # Better friction for control
                                 collision_layer="Player")

    # Add collision detection script
    detector_player.add_script("pyg_engine.collision_detector",
                              original_color=Color(255, 100, 100),      # Light red
                              player_collision_color=Color(255, 255, 0), # Yellow
                              floor_collision_color=Color(0, 255, 0),    # Green
                              both_collision_color=Color(255, 0, 255))   # Magenta
    
    # Add player control script for detector player (WASD only) - same as heavy_player
    detector_player.add_script(get_script_path("player.py"),
                              speed=500,  # Increased speed for faster movement
                              player_id=1,
                              control_mode="velocity",  # Changed to velocity control like heavy_player
                              velocity_smoothing=0.9,  # Same smoothing as heavy_player
                              movement_keys={
                                  'up': [pg.K_w],
                                  'down': [pg.K_s],
                                  'left': [pg.K_a],
                                  'right': [pg.K_d]
                              },
                              use_drag_control=True,
                              drag_force_multiplier=0.5)

    # ================ PLAYER 2: Heavy Bouncy Ball ================
    heavy_player = GameObject(
        name="heavy_player",
        basicShape=BasicShape.Circle,
        color=Color(100, 100, 255),  # Light blue
        position=Vector2(600, 250),  # Center-ish, high up
        size=Vector2(60, 60),
        tag=Tag.Player,
        show_rotation_line=True  # Enable rotation line for this object
    )

    # Heavy with moderate bounce (reduced to prevent oscillations)
    heavy_player.add_component(PymunkRigidBody,
                              mass=3.0,  # Heavy
                              gravity_scale=1.0,  # Normal gravity to reduce oscillation energy
                              drag=0.15,  # Higher drag to dampen oscillations
                              angular_drag=0.2,  # Add angular drag for stability
                              use_gravity=True,
                              lock_rotation=False)  # Allow natural rolling

    heavy_player.add_component(PymunkCircleCollider,
                              radius=30,
                              material=Materials.METAL,  # Less bouncy than BOUNCY material
                              collision_layer="Player")
    
    # Add player control script for heavy player (Arrow keys)
    heavy_player.add_script(get_script_path("player.py"),
                           speed=200,
                           player_id=2,
                           control_mode="velocity",
                           velocity_smoothing=0.9,
                           movement_keys={
                               'up': [pg.K_UP],
                               'down': [pg.K_DOWN],
                               'left': [pg.K_LEFT],
                               'right': [pg.K_RIGHT]
                           },
                           use_drag_control=True,
                           drag_force_multiplier=0.3)

    # ================ PLAYER 3: Light Fast Rectangle ================
    light_player = GameObject(
        name="light_player",
        basicShape=BasicShape.Rectangle,
        color=Color(100, 255, 100),  # Light green
        position=Vector2(1000, 280),  # Right side, high up
        size=Vector2(40, 60),
        tag=Tag.Player
    )

    # Light and fast
    light_player.add_component(PymunkRigidBody,
                              mass=1.8,  # Light
                              gravity_scale=1,
                              drag=0.15,  # Balanced air resistance for Pymunk
                              use_gravity=True,
                              lock_rotation=False)  # Allow natural rotation

    light_player.add_component(PymunkBoxCollider,
                              width=40,
                              height=60,
                              material=Materials.METAL,  # Medium bounce
                              collision_layer="Player")
    
    # Add player control script for light player (IJKL keys)
    light_player.add_script(get_script_path("player.py"),
                           speed=400,
                           player_id=3,
                           control_mode="velocity",
                           velocity_smoothing=0.95,
                           movement_keys={
                               'up': [pg.K_i],
                               'down': [pg.K_k],
                               'left': [pg.K_j],
                               'right': [pg.K_l]
                           },
                           use_drag_control=True,
                           drag_force_multiplier=0.4)

    # ================ FLOOR: Static Environment ================
    floor = GameObject(
        name="main_floor",
        basicShape=BasicShape.Rectangle,
        color=Color(139, 69, 19),  # Brown floor
        position=Vector2(600, 0),  # Bottom center
        size=Vector2(1200, 100),
        tag=Tag.Environment
    )

    # Kinematic rigidbody (doesn't move, but can be collided with)
    floor.add_component(PymunkRigidBody,
                       mass=100.0,  # Heavy (though it won't matter since it's kinematic)
                       is_kinematic=True,  # Won't be affected by physics
                       use_gravity=False)

    floor.add_component(PymunkBoxCollider,
                       width=1200,
                       height=100,
                       material=Materials.WOOD,  # Medium friction, low bounce
                       collision_layer="Environment")

    # ================ WALLS (Optional - for containment) ================
    # Left wall
    left_wall = GameObject(
        name="left_wall",
        basicShape=BasicShape.Rectangle,
        color=Color(100, 100, 100),  # Gray
        position=Vector2(25, 0),
        size=Vector2(50, 800),
        tag=Tag.Environment
    )

    left_wall.add_component(PymunkRigidBody, is_kinematic=True, use_gravity=False)
    left_wall.add_component(PymunkBoxCollider, width=50, height=800,
                           material=Materials.METAL, collision_layer="Environment")

    # Right wall
    right_wall = GameObject(
        name="right_wall",
        basicShape=BasicShape.Rectangle,
        color=Color(100, 100, 100),  # Gray
        position=Vector2(1175, 0),
        size=Vector2(50, 800),
        tag=Tag.Environment
    )

    right_wall.add_component(PymunkRigidBody, is_kinematic=True, use_gravity=False)
    right_wall.add_component(PymunkBoxCollider, width=50, height=800,
                            material=Materials.METAL, collision_layer="Environment")

    # Test platform
    platform1 = GameObject(
            name="platform1",
            basicShape=BasicShape.Rectangle,
            color=Color(100, 100, 100),
            position=Vector2(100, 100),
            size=Vector2(200,50),
            rotation=-15.0,
            tag=Tag.Environment
            )
    platform1.add_component(PymunkRigidBody, is_kinematic=True, use_gravity=False)
    platform1.add_component(PymunkBoxCollider, width=200, height=50,
                            material=Materials.BOUNCY, collision_layer="Environment")

    # ================ ADD ALL OBJECTS TO ENGINE ================
    engine.addGameObject(detector_player)
    engine.addGameObject(heavy_player)
    engine.addGameObject(light_player)
    engine.addGameObject(floor)
    engine.addGameObject(left_wall)
    engine.addGameObject(right_wall)
    engine.addGameObject(platform1)

    # Create a camera controller that keeps all objects in view
    camera_controller = CameraController(engine)
    engine.addGameObject(camera_controller)


    # Print controls
    print("\n=== Physics Demo Controls ===")
    print("Player 1 (Red Circle - Color Changer):")
    print("  - WASD: Move with physics forces")
    print("  - Click and drag: Drag the red circle")
    print("  - Changes color based on collisions")
    print("\nPlayer 2 (Blue Circle - Heavy Ball):")
    print("  - Arrow Keys: Move with velocity control")
    print("  - Click and drag: Drag the blue circle")
    print("  - Heavy and bouncy physics")
    print("\nPlayer 3 (Green Rectangle - Light & Fast):")
    print("  - IJKL: Move with velocity control")
    print("  - Click and drag: Drag the green rectangle")
    print("  - Fast and responsive (responds to gravity)")
    print("\nGeneral Controls:")
    print("  - ESC: Pause/Unpause")
    print("  - Close window to exit")
    print("\nWatch the red circle change colors when it collides!")
    
    # Start the physics simulation
    engine.start()
    sys.exit()

if __name__ == "__main__":
    main()

