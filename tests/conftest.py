#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""pytest 公共配置"""

import os
import sys
from pathlib import Path

# UI 测试使用无界面后端，避免在 CI / 无桌面环境卡住
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# 保证可以直接导入 src 包
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox


@pytest.fixture(scope="session")
def qapp():
    """整个测试会话共用一个 QApplication"""
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(autouse=True)
def dialogs(monkeypatch):
    """拦截模态弹窗，返回被调用的提示文本列表"""
    calls = []

    def fake(parent, title, text, *args, **kwargs):
        calls.append(text)
        return QMessageBox.Ok

    monkeypatch.setattr(QMessageBox, "information", staticmethod(fake))
    monkeypatch.setattr(QMessageBox, "warning", staticmethod(fake))
    monkeypatch.setattr(QMessageBox, "critical", staticmethod(fake))
    return calls


@pytest.fixture
def images(tmp_path):
    """生成 12 张临时贴图（超过 8 张上限）"""
    from PIL import Image

    paths = []
    for i in range(12):
        path = tmp_path / f"tex_{i:02d}.png"
        Image.new("RGB", (32, 32), (30 + i * 5, 60, 120)).save(path)
        paths.append(str(path))
    return paths


@pytest.fixture
def window(qapp):
    """真实主窗口（用于端到端验证信号连接）"""
    from src.ui.main_window import MainWindow

    win = MainWindow()
    yield win
    win.close()
