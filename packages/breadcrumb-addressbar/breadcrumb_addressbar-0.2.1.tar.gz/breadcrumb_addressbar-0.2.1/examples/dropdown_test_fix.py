#!/usr/bin/env python3
"""
Dropdown Test Fix - Test various solutions for QComboBox dropdown issues

Test different approaches to fix QComboBox dropdown not closing in WSL2.
"""

import os
import sys

from PySide6.QtCore import QEvent, Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)


class DropdownTestFixWindow(QMainWindow):
    """Test window for QComboBox dropdown fixes."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dropdown Test Fix")
        self.setGeometry(100, 100, 700, 400)

        # メインウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # タイトル
        title_label = QLabel("QComboBox ドロップダウン修正テスト")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin: 10px;"
        )
        layout.addWidget(title_label)

        # テスト1: フォーカスイベントを使用
        test1_layout = QHBoxLayout()
        test1_label = QLabel("テスト1 (フォーカスイベント):")
        test1_layout.addWidget(test1_label)

        self.combo1 = QComboBox()
        self.combo1.addItems(["オプション1", "オプション2", "オプション3"])
        self.combo1.activated.connect(self.on_combo1_activated)
        self.combo1.installEventFilter(self)
        test1_layout.addWidget(self.combo1)

        layout.addLayout(test1_layout)

        # テスト2: より長い遅延
        test2_layout = QHBoxLayout()
        test2_label = QLabel("テスト2 (長い遅延):")
        test2_layout.addWidget(test2_label)

        self.combo2 = QComboBox()
        self.combo2.addItems(["選択肢A", "選択肢B", "選択肢C"])
        self.combo2.activated.connect(self.on_combo2_activated)
        test2_layout.addWidget(self.combo2)

        layout.addLayout(test2_layout)

        # テスト3: 複数回のhidePopup
        test3_layout = QHBoxLayout()
        test3_label = QLabel("テスト3 (複数回hidePopup):")
        test3_layout.addWidget(test3_label)

        self.combo3 = QComboBox()
        self.combo3.addItems(["項目X", "項目Y", "項目Z"])
        self.combo3.activated.connect(self.on_combo3_activated)
        test3_layout.addWidget(self.combo3)

        layout.addLayout(test3_layout)

        # テスト4: ウィンドウ外クリックで閉じる
        test4_layout = QHBoxLayout()
        test4_label = QLabel("テスト4 (ウィンドウ外クリック):")
        test4_layout.addWidget(test4_label)

        self.combo4 = QComboBox()
        self.combo4.addItems(["テストA", "テストB", "テストC"])
        self.combo4.activated.connect(self.on_combo4_activated)
        test4_layout.addWidget(self.combo4)

        layout.addLayout(test4_layout)

        # ログ表示
        self.log_label = QLabel("ログ: ドロップダウンをテストしてください")
        self.log_label.setStyleSheet(
            "background: #f8f8f8; padding: 10px; border: 1px solid #ccc;"
        )
        self.log_label.setWordWrap(True)
        layout.addWidget(self.log_label)

        print("Dropdown Test Fix を開始しました")

    def eventFilter(self, obj, event):
        """イベントフィルター"""
        if obj == self.combo1 and event.type() == QEvent.FocusOut:
            print("フォーカスアウトイベントを検出")
            QTimer.singleShot(
                10, lambda: self._force_close_dropdown(self.combo1)
            )
        return super().eventFilter(obj, event)

    def _force_close_dropdown(self, combo_box):
        """強制的にドロップダウンを閉じる"""
        print(f"強制的にドロップダウンを閉じます: {combo_box}")
        combo_box.hidePopup()
        combo_box.clearFocus()
        self.setFocus()
        # 複数回試行
        QTimer.singleShot(50, lambda: combo_box.hidePopup())
        QTimer.singleShot(100, lambda: combo_box.hidePopup())

    def _close_dropdown(self, combo_box):
        """ドロップダウンを閉じる"""
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

        # より長い遅延でドロップダウンを閉じる
        QTimer.singleShot(200, lambda: self._close_dropdown(self.combo2))

    def on_combo3_activated(self, index: int) -> None:
        """テスト3のアクティベート処理"""
        text = self.combo3.currentText()
        print(f"テスト3 アクティベート: {text}")
        self.log_label.setText(f"ログ: テスト3 アクティベート → {text}")

        # 複数回ドロップダウンを閉じる
        QTimer.singleShot(50, lambda: self._force_close_dropdown(self.combo3))

    def on_combo4_activated(self, index: int) -> None:
        """テスト4のアクティベート処理"""
        text = self.combo4.currentText()
        print(f"テスト4 アクティベート: {text}")
        self.log_label.setText(f"ログ: テスト4 アクティベート → {text}")

        # 即座にドロップダウンを閉じる
        self._force_close_dropdown(self.combo4)


def main():
    """メイン関数"""
    # WSL2環境でのQt設定
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    app = QApplication(sys.argv)

    # ウィンドウを作成して表示
    window = DropdownTestFixWindow()
    window.show()

    # イベントループ開始
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
