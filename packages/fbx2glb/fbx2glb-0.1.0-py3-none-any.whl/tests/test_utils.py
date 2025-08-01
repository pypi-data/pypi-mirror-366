import unittest
import logging
import tempfile
import json
import os
from pathlib import Path

from fbx2glb.utils import setup_logging, load_config

class TestUtils(unittest.TestCase):
    """Test utility functions."""

    def test_setup_logging(self):
        """Test that setup_logging creates a logger with the correct configuration."""
        logger = setup_logging(level=logging.DEBUG)

        # Check that the logger has the correct name
        self.assertEqual(logger.name, 'fbx2glb')

        # Check that the logger has the correct level
        self.assertEqual(logger.level, logging.DEBUG)

        # Check that the logger has a handler
        self.assertEqual(len(logger.handlers), 1)

        # Check that the handler has the correct level
        self.assertEqual(logger.handlers[0].level, logging.DEBUG)

    def test_load_config_default(self):
        """Test that load_config returns the default configuration when no config file is found."""
        config = load_config(config_path=None)

        # Check that the config has the expected default values
        self.assertIsNone(config['defaultMethod'])
        self.assertEqual(config['fallbackMethods'], ['fbx2gltf', 'blender'])
        self.assertIsNone(config['blenderPath'])
        self.assertEqual(config['outputFormat'], 'glb')
        self.assertTrue(config['preserveAnimations'])
        self.assertTrue(config['optimizeMeshes'])

    def test_load_config_custom(self):
        """Test that load_config loads a custom configuration file."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            custom_config = {
                'defaultMethod': 'blender',
                'blenderPath': '/custom/path/to/blender',
                'outputFormat': 'gltf',
                'preserveAnimations': False
            }
            json.dump(custom_config, temp_file)
            temp_file_path = temp_file.name

        try:
            # Load the config
            config = load_config(config_path=temp_file_path)

            # Check that the config has the expected values
            self.assertEqual(config['defaultMethod'], 'blender')
            self.assertEqual(config['blenderPath'], '/custom/path/to/blender')
            self.assertEqual(config['outputFormat'], 'gltf')
            self.assertFalse(config['preserveAnimations'])
            self.assertTrue(config['optimizeMeshes'])  # Default value not overridden
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)

if __name__ == '__main__':
    unittest.main()
