#!/usr/bin/env python3
"""
Phase 2 Example - Advanced Features

Demonstrates the new features added in Phase 2:
- Folder selection popup
- Keyboard navigation
- Theme support
- Enhanced customization
"""

import logging
import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from breadcrumb_addressbar import BreadcrumbAddressBar, get_theme_manager
from breadcrumb_addressbar.logger_setup import setup_logger


class Phase2DemoWindow(QMainWindow):
    """Demo window for Phase 2 features."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Breadcrumb Address Bar - Phase 2 Demo")
        self.setGeometry(100, 100, 900, 400)

        # ロガーをセットアップ
        self.logger = setup_logger(level=logging.INFO)

        # メインウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # タイトル
        title_label = QLabel("Phase 2 機能デモ")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin: 10px;"
        )
        layout.addWidget(title_label)

        # パンくずリスト型アドレスバー
        self.addressbar = BreadcrumbAddressBar()
        self.addressbar.pathChanged.connect(self.on_path_changed)
        self.addressbar.folderSelected.connect(self.on_folder_selected)
        layout.addWidget(self.addressbar)

        # コントロールパネル
        controls_layout = QHBoxLayout()

        # セパレーター設定
        separator_label = QLabel("セパレーター:")
        controls_layout.addWidget(separator_label)

        self.separator_combo = QComboBox()
        self.separator_combo.addItems(["なし", " > ", " / ", " \\ "])
        self.separator_combo.activated.connect(self.on_separator_activated)
        controls_layout.addWidget(self.separator_combo)

        # ボタンサイズ
        size_label = QLabel("ボタンサイズ:")
        controls_layout.addWidget(size_label)

        self.size_combo = QComboBox()
        self.size_combo.addItems(["28px", "32px", "36px", "40px"])
        self.size_combo.setCurrentText("32px")
        self.size_combo.activated.connect(self.on_size_activated)
        controls_layout.addWidget(self.size_combo)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # 機能説明
        features_layout = QHBoxLayout()

        # 左側：キーボードナビゲーション
        keyboard_label = QLabel(
            "キーボードナビゲーション:\n"
            "• Tab: ボタン間を移動\n"
            "• Enter/Space: ボタンを選択\n"
            "• 矢印キー: ボタン間を移動"
        )
        keyboard_label.setStyleSheet(
            "background: #f0f0f0; padding: 10px; border-radius: 5px;"
        )
        features_layout.addWidget(keyboard_label)

        # 中央：テーマ対応
        theme_label = QLabel(
            "テーマ対応 (qt-theme-manager):\n"
            "• qt-theme-managerと統合\n"
            "• 利用可能なテーマを自動検出\n"
            "• テーマ切り替えに対応"
        )
        theme_label.setStyleSheet(
            "background: #fff0e0; padding: 10px; border-radius: 5px;"
        )
        features_layout.addWidget(theme_label)

        # 右側：フォルダ選択
        popup_label = QLabel(
            "フォルダ選択ポップアップ:\n"
            "• 最下層ボタンをクリック\n"
            "• フォルダ一覧が表示される\n"
            "• フォルダを選択して移動"
        )
        popup_label.setStyleSheet(
            "background: #e0f0ff; padding: 10px; border-radius: 5px;"
        )
        features_layout.addWidget(popup_label)

        layout.addLayout(features_layout)

        # ログ表示エリア
        self.log_label = QLabel("ログ: 操作を開始してください")
        self.log_label.setStyleSheet(
            "background: #f8f8f8; padding: 10px; border: 1px solid #ccc;"
        )
        self.log_label.setWordWrap(True)
        layout.addWidget(self.log_label)

        # 初期パスを設定
        initial_path = os.path.expanduser("~/Documents")
        if not os.path.exists(initial_path):
            initial_path = os.path.expanduser("~")
        self.addressbar.setPath(initial_path)

        self.logger.info("Phase 2 Demo を開始しました")

        # テーママネージャーの情報を表示
        try:
            theme_manager = get_theme_manager()
            available_themes = theme_manager.get_available_themes()
            current_theme = theme_manager.get_current_theme_name()
            self.logger.info(
                f"利用可能なテーマ: {list(available_themes.keys())}"
            )
            self.logger.info(f"現在のテーマ: {current_theme}")
        except RuntimeError as e:
            self.logger.error(f"テーママネージャーの初期化に失敗: {e}")

    def on_path_changed(self, path: str) -> None:
        """パス変更時の処理"""
        self.logger.info(f"パス変更: {path}")
        self.log_label.setText(f"ログ: パスが変更されました → {path}")

    def on_folder_selected(self, path: str) -> None:
        """フォルダ選択時の処理"""
        self.logger.info(f"フォルダ選択: {path}")
        self.log_label.setText(f"ログ: フォルダが選択されました → {path}")

    def on_separator_activated(self, index: int) -> None:
        """セパレーター変更時の処理"""
        separator = self.separator_combo.currentText()
        self.logger.info(f"セパレーター変更: {separator}")
        self.addressbar.setSeparator(separator)
        self.log_label.setText(
            f"ログ: セパレーターが変更されました → '{separator}'"
        )

    def on_size_activated(self, index: int) -> None:
        """ボタンサイズ変更時の処理"""
        size = self.size_combo.currentText()
        height = int(size.replace("px", ""))
        self.logger.info(f"ボタンサイズ変更: {height}px")
        self.addressbar.setButtonHeight(height)
        self.log_label.setText(
            f"ログ: ボタンサイズが変更されました → {height}px"
        )


def main():
    """メイン関数"""
    app = QApplication(sys.argv)

    # アプリケーション情報
    app.setApplicationName("Breadcrumb Address Bar - Phase 2 Demo")
    app.setApplicationVersion("0.2.0")
    app.setOrganizationName("Your Organization")

    # ウィンドウを作成して表示
    window = Phase2DemoWindow()
    window.show()

    # イベントループ開始
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
