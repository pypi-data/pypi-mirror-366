import pytest
import time
import matplotlib.pyplot as plt
from pathlib import Path

import mplstyles_seaborn


class TestPerformance:
    
    def test_style_loading_time(self):
        """Test that style loading is reasonably fast."""
        start_time = time.time()
        
        # Load a sample of styles
        test_styles = [
            ('darkgrid', 'dark', 'notebook'),
            ('whitegrid', 'colorblind', 'talk'),
            ('white', 'muted', 'poster'),
            ('dark', 'bright', 'paper'),
            ('ticks', 'pastel', 'notebook')
        ]
        
        for style, palette, context in test_styles:
            mplstyles_seaborn.use_style(style, palette, context)
        
        elapsed_time = time.time() - start_time
        
        # Should complete within 2 seconds for 5 styles
        assert elapsed_time < 2.0, f"Style loading took too long: {elapsed_time:.2f}s"
    
    def test_list_styles_performance(self):
        """Test that listing styles is fast."""
        start_time = time.time()
        
        # Call multiple times to test caching/performance
        for _ in range(10):
            styles = mplstyles_seaborn.list_available_styles()
            assert len(styles) == 120
        
        elapsed_time = time.time() - start_time
        
        # Should complete within 1 second for 10 calls
        assert elapsed_time < 1.0, f"Listing styles took too long: {elapsed_time:.2f}s"
    
    def test_register_styles_performance(self):
        """Test that registering styles is reasonably fast."""
        start_time = time.time()
        
        # Re-register styles multiple times
        for _ in range(5):
            mplstyles_seaborn.register_styles()
        
        elapsed_time = time.time() - start_time
        
        # Should complete within 3 seconds for 5 registrations
        assert elapsed_time < 3.0, f"Style registration took too long: {elapsed_time:.2f}s"
    
    def test_rapid_style_switching(self):
        """Test performance when rapidly switching between styles."""
        styles = ['darkgrid', 'whitegrid', 'dark', 'white', 'ticks']
        palettes = ['dark', 'colorblind', 'muted', 'bright', 'pastel', 'deep']
        contexts = ['paper', 'notebook', 'talk', 'poster']
        
        start_time = time.time()
        
        # Rapidly switch between 50 different combinations
        for i in range(50):
            style = styles[i % len(styles)]
            palette = palettes[i % len(palettes)]
            context = contexts[i % len(contexts)]
            
            mplstyles_seaborn.use_style(style, palette, context)
        
        elapsed_time = time.time() - start_time
        
        # Should complete within 5 seconds for 50 style changes
        assert elapsed_time < 5.0, f"Rapid style switching took too long: {elapsed_time:.2f}s"
    
    def test_memory_usage_stability(self):
        """Test that repeated style applications don't cause memory leaks."""
        import gc
        import sys
        
        # Force garbage collection
        gc.collect()
        
        # Get initial object count
        initial_objects = len(gc.get_objects())
        
        # Apply styles many times
        for i in range(100):
            style = mplstyles_seaborn.STYLES[i % len(mplstyles_seaborn.STYLES)]
            palette = mplstyles_seaborn.PALETTES[i % len(mplstyles_seaborn.PALETTES)]
            context = mplstyles_seaborn.CONTEXTS[i % len(mplstyles_seaborn.CONTEXTS)]
            
            mplstyles_seaborn.use_style(style, palette, context)
            
            # Periodically clean up any figures
            if i % 20 == 0:
                plt.close('all')
                gc.collect()
        
        # Final cleanup
        plt.close('all')
        gc.collect()
        
        # Check final object count
        final_objects = len(gc.get_objects())
        
        # Allow for some increase, but not too much (less than 50% increase)
        object_increase = final_objects - initial_objects
        max_allowed_increase = initial_objects * 0.5
        
        assert object_increase < max_allowed_increase, \
            f"Possible memory leak: {object_increase} new objects created"


class TestScalability:
    
    def test_all_styles_loadable_in_reasonable_time(self):
        """Test that all 120 styles can be loaded in reasonable time."""
        start_time = time.time()
        
        # Test every 5th style to keep test time reasonable
        all_styles = mplstyles_seaborn.list_available_styles()
        sample_styles = all_styles[::5]  # Every 5th style
        
        for style_name in sample_styles:
            plt.style.use(style_name)
        
        elapsed_time = time.time() - start_time
        
        # Should complete within 10 seconds for ~24 styles
        assert elapsed_time < 10.0, f"Loading sample styles took too long: {elapsed_time:.2f}s"
    
    def test_concurrent_style_usage(self):
        """Test that styles work correctly under concurrent access."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def apply_style_worker(style_combo):
            try:
                style, palette, context = style_combo
                mplstyles_seaborn.use_style(style, palette, context)
                
                # Verify it worked by checking a parameter
                font_size = plt.rcParams['font.size']
                results.put(('success', font_size))
            except Exception as e:
                results.put(('error', str(e)))
        
        # Create test combinations
        test_combinations = [
            ('darkgrid', 'dark', 'notebook'),
            ('whitegrid', 'colorblind', 'talk'),
            ('white', 'muted', 'poster'),
            ('dark', 'bright', 'paper'),
        ]
        
        # Run concurrent style applications
        threads = []
        for combo in test_combinations:
            thread = threading.Thread(target=apply_style_worker, args=(combo,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = 0
        while not results.empty():
            result_type, result_value = results.get()
            if result_type == 'success':
                success_count += 1
                assert isinstance(result_value, (int, float))  # font_size should be numeric
            else:
                pytest.fail(f"Concurrent style application failed: {result_value}")
        
        assert success_count == len(test_combinations)


class TestResourceUsage:
    
    def test_style_file_reading_efficiency(self, styles_dir):
        """Test that style files are read efficiently."""
        # Get all style files
        style_files = list(styles_dir.glob("*.mplstyle"))
        
        start_time = time.time()
        
        # Read a sample of style files directly
        sample_files = style_files[::10]  # Every 10th file
        
        for style_file in sample_files:
            with open(style_file, 'r') as f:
                content = f.read()
                # Verify it's not empty
                assert len(content) > 0
        
        elapsed_time = time.time() - start_time
        
        # Should complete within 1 second for ~12 files
        assert elapsed_time < 1.0, f"Reading style files took too long: {elapsed_time:.2f}s"
    
    def test_matplotlib_integration_overhead(self):
        """Test that our style application doesn't add significant overhead."""
        # Time matplotlib's built-in style application
        start_time = time.time()
        for _ in range(10):
            plt.style.use('default')
        matplotlib_time = time.time() - start_time
        
        # Time our style application
        start_time = time.time()
        for _ in range(10):
            mplstyles_seaborn.use_style()
        our_time = time.time() - start_time
        
        # Our overhead should be reasonable (less than 20x matplotlib's time)
        # Handle case where matplotlib_time is very small (close to 0)  
        if matplotlib_time < 0.001:  # Less than 1ms
            # If matplotlib is very fast, just ensure our time is reasonable (< 1 second)
            assert our_time < 1.0, f"Style application took too long: {our_time:.3f}s"
        else:
            overhead_ratio = our_time / matplotlib_time
            # More lenient threshold to account for Windows I/O overhead
            assert overhead_ratio < 20.0, f"Style application overhead too high: {overhead_ratio:.2f}x"


@pytest.mark.slow
class TestStressTests:
    """Stress tests that take longer to run."""
    
    def test_all_styles_comprehensive(self):
        """Test all 120 styles comprehensively (marked as slow)."""
        all_styles = mplstyles_seaborn.list_available_styles()
        
        start_time = time.time()
        
        for style_name in all_styles:
            plt.style.use(style_name)
            
            # Create a simple plot to ensure style is actually applied
            fig, ax = plt.subplots(figsize=(2, 2))
            ax.plot([1, 2, 3], [1, 4, 2])
            plt.close(fig)
        
        elapsed_time = time.time() - start_time
        
        # Should complete within 30 seconds for all 120 styles
        assert elapsed_time < 30.0, f"Testing all styles took too long: {elapsed_time:.2f}s"
    
    def test_extended_style_switching(self):
        """Extended test of style switching (marked as slow)."""
        styles = mplstyles_seaborn.STYLES
        palettes = mplstyles_seaborn.PALETTES
        contexts = mplstyles_seaborn.CONTEXTS
        
        start_time = time.time()
        
        # Test 500 style switches
        for i in range(500):
            style = styles[i % len(styles)]
            palette = palettes[i % len(palettes)]
            context = contexts[i % len(contexts)]
            
            mplstyles_seaborn.use_style(style, palette, context)
            
            # Occasionally clean up
            if i % 100 == 0:
                plt.close('all')
        
        elapsed_time = time.time() - start_time
        
        # Should complete within 20 seconds for 500 switches
        assert elapsed_time < 20.0, f"Extended style switching took too long: {elapsed_time:.2f}s"