#!/usr/bin/env python3
"""Quick validation script to test the basic functionality."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_basic_functionality():
    """Test basic functionality of QuoridorEnv."""
    try:
        from quoridor_sim.quoridor_env import QuoridorEnv
        
        print("✓ QuoridorEnv import successful")
        
        # Test 2-player environment
        env = QuoridorEnv(num_players=2, max_walls=10)
        print(f"✓ 2-player env created: obs_shape={env.observation_space.shape}, action_space={env.action_space.n}")
        
        # Test 4-player environment  
        env4 = QuoridorEnv(num_players=4, max_walls=10)
        print(f"✓ 4-player env created: obs_shape={env4.observation_space.shape}, action_space={env4.action_space.n}")
        
        # Test reset
        obs, info = env.reset()
        print(f"✓ Reset works: obs_shape={obs.shape}, obs_type={obs.dtype}")
        
        # Test action decoding
        move_action = env._decode_action(0)
        wall_action = env._decode_action(4)
        print(f"✓ Action decoding works: move={move_action}, wall={wall_action}")
        
        # Test step
        obs2, reward, terminated, truncated, info = env.step(3)
        print(f"✓ Step works: reward={reward}, terminated={terminated}, info={info}")
        
        # Test input validation
        try:
            QuoridorEnv(num_players=3)  # Should fail
            print("✗ Input validation failed - should have raised ValueError")
        except ValueError:
            print("✓ Input validation works")
        
        print("\n🎉 All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)