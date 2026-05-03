from src.core.graph import should_continue

def test_should_continue():
    # Iteration count < 2 should return 'refine'
    state_1 = {"iteration_count": 0}
    assert should_continue(state_1) == "refine"
    
    state_2 = {"iteration_count": 1}
    assert should_continue(state_2) == "refine"
    
    # Iteration count >= 2 should return 'end'
    state_3 = {"iteration_count": 2}
    assert should_continue(state_3) == "end"
    
    state_4 = {"iteration_count": 5}
    assert should_continue(state_4) == "end"
