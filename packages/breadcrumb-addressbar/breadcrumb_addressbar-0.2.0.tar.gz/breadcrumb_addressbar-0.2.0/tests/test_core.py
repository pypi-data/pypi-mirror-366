"""
Test cases for BreadcrumbAddressBar core functionality.
"""

import pytest

try:
    from PySide6.QtWidgets import QApplication

    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

try:
    from breadcrumb_addressbar import BreadcrumbAddressBar

    BREADCRUMB_AVAILABLE = True
except ImportError:
    BREADCRUMB_AVAILABLE = False


@pytest.mark.skipif(
    not PYSIDE6_AVAILABLE or not BREADCRUMB_AVAILABLE,
    reason="PySide6 or breadcrumb_addressbar not available",
)
class TestBreadcrumbAddressBar:
    """Test cases for BreadcrumbAddressBar class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        # 既存のQApplicationインスタンスがある場合は削除
        app = QApplication.instance()
        if app is None:
            self.app = QApplication([])
        else:
            self.app = app

        self.addressbar = BreadcrumbAddressBar()
        yield
        # テスト終了時のクリーンアップは最小限に

    def test_initial_state(self):
        """Test initial state of the address bar."""
        assert self.addressbar.getPath() == ""
        assert self.addressbar._max_items == 5
        assert self.addressbar._button_height == 32
        assert self.addressbar._font_size == 10

    def test_set_path(self):
        """Test setting a path."""
        test_path = "/home/user/documents"
        self.addressbar.setPath(test_path)
        assert self.addressbar.getPath() == test_path

    def test_path_changed_signal(self):
        """Test pathChanged signal emission."""
        signal_emitted = False
        received_path = ""

        def on_path_changed(path):
            nonlocal signal_emitted, received_path
            signal_emitted = True
            received_path = path

        self.addressbar.pathChanged.connect(on_path_changed)
        test_path = "/home/user/documents"
        self.addressbar.setPath(test_path)

        assert signal_emitted
        assert received_path == test_path

    def test_set_max_items(self):
        """Test setting maximum items."""
        self.addressbar.setMaxItems(3)
        assert self.addressbar._max_items == 3

    def test_set_button_height(self):
        """Test setting button height."""
        self.addressbar.setButtonHeight(40)
        assert self.addressbar._button_height == 40

    def test_set_font_size(self):
        """Test setting font size."""
        self.addressbar.setFontSize(12)
        assert self.addressbar._font_size == 12

    def test_set_separator(self):
        """Test setting separator."""
        separator = " > "
        self.addressbar.setSeparator(separator)
        assert self.addressbar._separator == separator

    def test_set_custom_labels(self):
        """Test setting custom labels."""
        labels = {
            "/home/user": "ホーム",
            "/home/user/documents": "ドキュメント",
        }
        self.addressbar.setCustomLabels(labels)
        assert self.addressbar._custom_labels == labels

    def test_path_splitting_unix(self):
        """Test path splitting for Unix paths."""
        test_path = "/home/user/documents"
        parts = self.addressbar._split_path(test_path)
        expected = [
            ("/", "/"),
            ("home", "/home"),
            ("user", "/home/user"),
            ("documents", "/home/user/documents"),
        ]
        assert parts == expected

    def test_path_splitting_windows(self):
        """Test path splitting for Windows paths."""
        test_path = "C:\\Users\\User\\Documents"
        parts = self.addressbar._split_path(test_path)
        expected = [
            ("C:\\", "C:\\"),
            ("Users", "C:\\Users"),
            ("User", "C:\\Users\\User"),
            ("Documents", "C:\\Users\\User\\Documents"),
        ]
        assert parts == expected

    def test_display_items_within_limit(self):
        """Test display items when within max items limit."""
        path_parts = [("/", "/"), ("home", "/home"), ("user", "/home/user")]
        items = self.addressbar._get_display_items(path_parts)
        assert len(items) == 3
        assert items[0][2] is False  # First item not current
        assert items[2][2] is True  # Last item is current

    def test_display_items_with_ellipsis(self):
        """Test display items with ellipsis when over limit."""
        path_parts = [
            ("/", "/"),
            ("home", "/home"),
            ("user", "/home/user"),
            ("documents", "/home/user/documents"),
            ("work", "/home/user/documents/work"),
            ("project1", "/home/user/documents/work/project1"),
        ]
        self.addressbar.setMaxItems(4)
        items = self.addressbar._get_display_items(path_parts)

        assert len(items) == 4
        assert items[0][0] == "/"  # First item
        assert items[1][0] == "..."  # Ellipsis
        assert items[2][0] == "work"  # Second to last
        assert items[3][0] == "project1"  # Last item (current)
        assert items[3][2] is True  # Last item is current


if __name__ == "__main__":
    pytest.main([__file__])
