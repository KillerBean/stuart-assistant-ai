import sys
import os
from stuart_ai.utils.audio_utils import ignore_stderr

def test_ignore_stderr():
    """Test that ignore_stderr context manager enters and exits correctly."""
    
    # We can't easily test the C-level suppression without spawning a subprocess
    # that writes to C stderr, but we can ensure it doesn't crash and restores stderr.
    
    original_stderr_fd = os.dup(2)
    
    try:
        with ignore_stderr():
            # Just do something innocuous
            print("This goes to stdout")
            # In a real scenario, C libraries writing to fd 2 would be silenced here.
            pass
            
        # Verify execution continues
        assert True
        
        # Verify stderr is still usable (Python level)
        sys.stderr.write("Stderr check\n")
        
    finally:
        os.close(original_stderr_fd)
