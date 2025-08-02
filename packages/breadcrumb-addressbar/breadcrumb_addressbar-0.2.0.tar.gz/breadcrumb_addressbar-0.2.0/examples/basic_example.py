#!/usr/bin/env python3
"""
Basic example of using BreadcrumbAddressBar.

This example demonstrates the basic usage of the breadcrumb address bar
in a simple file manager application.
"""

import logging
import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# ライブラリをインポート
from breadcrumb_addressbar import BreadcrumbAddressBar
from breadcrumb_addressbar.logger_setup import setup_logger


class FileManagerWindow(QMainWindow):
    """Simple file manager window with breadcrumb address bar."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Breadcrumb Address Bar Demo")
        self.setGeometry(100, 100, 800, 600)

        # ロガーをセットアップ
        self.logger = setup_logger(level=logging.INFO)

        # メインウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # レイアウト
        layout = QVBoxLayout(central_widget)

        # ツールバー
        toolbar = QHBoxLayout()

        # フォルダ選択ボタン
        browse_button = QPushButton("フォルダ選択")
        browse_button.clicked.connect(self.browse_folder)
        toolbar.addWidget(browse_button)

        # 現在のパス表示
        self.path_label = QLabel("パス: ")
        toolbar.addWidget(self.path_label)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # パンくずリスト型アドレスバー
        self.addressbar = BreadcrumbAddressBar()
        self.addressbar.pathChanged.connect(self.on_path_changed)
        self.addressbar.folderSelected.connect(self.on_folder_selected)
        layout.addWidget(self.addressbar)

        # 設定ボタン
        settings_layout = QHBoxLayout()

        # セパレーター設定
        separator_button = QPushButton("セパレーター: >")
        separator_button.clicked.connect(
            lambda: self.addressbar.setSeparator(" > ")
        )
        settings_layout.addWidget(separator_button)

        # セパレーターなし
        no_separator_button = QPushButton("セパレーターなし")
        no_separator_button.clicked.connect(
            lambda: self.addressbar.setSeparator("")
        )
        settings_layout.addWidget(no_separator_button)

        # ボタンサイズ設定
        size_button = QPushButton("ボタンサイズ: 40px")
        size_button.clicked.connect(
            lambda: self.addressbar.setButtonHeight(40)
        )
        settings_layout.addWidget(size_button)

        # フォントサイズ設定
        font_button = QPushButton("フォントサイズ: 12pt")
        font_button.clicked.connect(lambda: self.addressbar.setFontSize(12))
        settings_layout.addWidget(font_button)

        settings_layout.addStretch()
        layout.addLayout(settings_layout)

        # 情報表示エリア
        info_label = QLabel(
            "情報: パンくずリストのボタンをクリックしてフォルダを移動してください"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: gray; padding: 20px;")
        layout.addWidget(info_label)

        # 初期パスを設定
        initial_path = os.path.expanduser("~")
        self.addressbar.setPath(initial_path)

    def browse_folder(self):
        """フォルダ選択ダイアログを表示"""
        folder = QFileDialog.getExistingDirectory(
            self, "フォルダを選択", self.addressbar.getPath()
        )
        if folder:
            self.addressbar.setPath(folder)

    def on_path_changed(self, path: str) -> None:
        """パス変更時の処理"""
        self.path_label.setText(f"パス: {path}")
        self.logger.info(f"パスが変更されました: {path}")

    def on_folder_selected(self, path: str) -> None:
        """フォルダ選択時の処理"""
        self.logger.info(f"フォルダが選択されました: {path}")
        # ここで実際のファイルマネージャーの処理を行う
        # 例: フォルダ内容の表示、ファイル一覧の更新など


def main():
    """メイン関数"""
    app = QApplication(sys.argv)

    # アプリケーション情報
    app.setApplicationName("Breadcrumb Address Bar Demo")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("Your Organization")

    # ウィンドウを作成して表示
    window = FileManagerWindow()
    window.show()

    # イベントループ開始
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
