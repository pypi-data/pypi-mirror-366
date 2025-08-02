#!/usr/bin/env python3
"""
Dropdown Test - Test QComboBox dropdown behavior

Simple test to isolate QComboBox dropdown issues.
"""

import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)


class DropdownTestWindow(QMainWindow):
    """Test window for QComboBox dropdown behavior."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dropdown Test")
        self.setGeometry(100, 100, 600, 300)

        # メインウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # タイトル
        title_label = QLabel("QComboBox ドロップダウンテスト")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin: 10px;"
        )
        layout.addWidget(title_label)

        # テスト1: 基本的なQComboBox
        test1_layout = QHBoxLayout()
        test1_label = QLabel("テスト1 (基本):")
        test1_layout.addWidget(test1_label)

        self.combo1 = QComboBox()
        self.combo1.addItems(["オプション1", "オプション2", "オプション3"])
        self.combo1.activated.connect(self.on_combo1_activated)
        test1_layout.addWidget(self.combo1)

        layout.addLayout(test1_layout)

        # テスト2: currentIndexChangedを使用
        test2_layout = QHBoxLayout()
        test2_label = QLabel("テスト2 (currentIndexChanged):")
        test2_layout.addWidget(test2_label)

        self.combo2 = QComboBox()
        self.combo2.addItems(["選択肢A", "選択肢B", "選択肢C"])
        self.combo2.activated.connect(self.on_combo2_activated)
        self.combo2.currentIndexChanged.connect(
            lambda _: QTimer.singleShot(
                50, lambda: self._close_dropdown(self.combo2)
            )
        )
        test2_layout.addWidget(self.combo2)

        layout.addLayout(test2_layout)

        # テスト3: 手動でhidePopup
        test3_layout = QHBoxLayout()
        test3_label = QLabel("テスト3 (手動hidePopup):")
        test3_layout.addWidget(test3_label)

        self.combo3 = QComboBox()
        self.combo3.addItems(["項目X", "項目Y", "項目Z"])
        self.combo3.activated.connect(self.on_combo3_activated)
        test3_layout.addWidget(self.combo3)

        layout.addLayout(test3_layout)

        # ログ表示
        self.log_label = QLabel("ログ: ドロップダウンをテストしてください")
        self.log_label.setStyleSheet(
            "background: #f8f8f8; padding: 10px; border: 1px solid #ccc;"
        )
        self.log_label.setWordWrap(True)
        layout.addWidget(self.log_label)

        print("Dropdown Test を開始しました")

    def _close_dropdown(self, combo_box):
        """ドロップダウンを強制的に閉じる"""
        print(f"ドロップダウンを閉じます: {combo_box}")
        combo_box.hidePopup()
        combo_box.clearFocus()
        self.setFocus()

    def on_combo1_activated(self, index: int) -> None:
        """テスト1のアクティベート処理"""
        text = self.combo1.currentText()
        print(f"テスト1 アクティベート: {text}")
        self.log_label.setText(f"ログ: テスト1 アクティベート → {text}")

    def on_combo2_activated(self, index: int) -> None:
        """テスト2のアクティベート処理"""
        text = self.combo2.currentText()
        print(f"テスト2 アクティベート: {text}")
        self.log_label.setText(f"ログ: テスト2 アクティベート → {text}")

    def on_combo3_activated(self, index: int) -> None:
        """テスト3のアクティベート処理"""
        text = self.combo3.currentText()
        print(f"テスト3 アクティベート: {text}")
        self.log_label.setText(f"ログ: テスト3 アクティベート → {text}")

        # 手動でドロップダウンを閉じる
        QTimer.singleShot(100, lambda: self._close_dropdown(self.combo3))


def main():
    """メイン関数"""
    app = QApplication(sys.argv)

    # ウィンドウを作成して表示
    window = DropdownTestWindow()
    window.show()

    # イベントループ開始
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
