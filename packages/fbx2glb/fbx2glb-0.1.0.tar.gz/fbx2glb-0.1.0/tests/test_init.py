import unittest
import sys

class TestPackageImport(unittest.TestCase):
    """Test that the package can be imported correctly."""

    def test_import_package(self):
        """Test that the package can be imported."""
        try:
            import fbx2glb
            print("Python path:", sys.path)
            print("fbx2glb.__file__:", fbx2glb.__file__)
            print("fbx2glb dir:", dir(fbx2glb))
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import fbx2glb package")

    def test_version(self):
        """Test that the package has a version."""
        import fbx2glb
        self.assertIsNotNone(fbx2glb.__version__)
        self.assertIsInstance(fbx2glb.__version__, str)

    def test_imports(self):
        """Test that the package exports the expected functions."""
        import fbx2glb
        self.assertTrue(hasattr(fbx2glb, 'convert_file'))
        self.assertTrue(hasattr(fbx2glb, 'batch_convert'))
        self.assertTrue(hasattr(fbx2glb, 'generate_component'))
        self.assertTrue(hasattr(fbx2glb, 'detect_fbx_version'))
        self.assertTrue(hasattr(fbx2glb, 'setup_logging'))
        self.assertTrue(hasattr(fbx2glb, 'find_conversion_tool'))
        self.assertTrue(hasattr(fbx2glb, 'FBX_SDK_AVAILABLE'))

if __name__ == '__main__':
    unittest.main()
