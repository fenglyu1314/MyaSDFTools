#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""图像状态同步回归测试

约束：图像集合的唯一数据源是 ImageManager。
UI 卡片只负责展示和发出「删除意图」，任何增删都必须经过模型，
否则会出现「界面删了、后端还在」的状态漂移。

历史缺陷：删除卡片只清理 UI 列表，current_images 只增不减，
累积导入 8 张后即使界面只剩几张也提示上限，贴图无法更新，只能重启。
"""

import pytest

from src.core.image_manager import MAX_IMAGES, ImageManager


# ---------------------------------------------------------------- 模型层

def test_add_images_fills_up_to_limit(images):
    manager = ImageManager()

    result = manager.add_images(images[:MAX_IMAGES])

    assert len(result.added) == MAX_IMAGES
    assert manager.count == MAX_IMAGES
    assert manager.is_full


def test_over_limit_files_are_rejected(images):
    manager = ImageManager()
    manager.add_images(images[:MAX_IMAGES])

    result = manager.add_images(images[MAX_IMAGES:])

    assert result.added == []
    assert len(result.over_limit) == len(images) - MAX_IMAGES
    assert manager.count == MAX_IMAGES


def test_duplicates_do_not_consume_quota(images):
    manager = ImageManager()
    manager.add_images(images[:2])

    result = manager.add_images([images[0], images[1], images[2]])

    assert result.duplicated == images[:2]
    assert result.added == [images[2]]
    assert manager.count == 3


def test_remove_image_frees_quota(images):
    manager = ImageManager()
    manager.add_images(images[:MAX_IMAGES])

    assert manager.remove_image(images[0]) is True

    assert manager.count == MAX_IMAGES - 1
    assert not manager.is_full
    assert manager.add_images([images[MAX_IMAGES]]).added == [images[MAX_IMAGES]]


def test_invalid_file_is_reported_not_counted(tmp_path):
    manager = ImageManager()
    broken = tmp_path / "broken.png"
    broken.write_text("not an image", encoding="utf-8")

    result = manager.add_images([str(broken)])

    assert result.invalid == [str(broken)]
    assert manager.count == 0


# ---------------------------------------------------------------- 端到端（含 UI 信号）

def test_deleting_card_releases_quota(window, images, dialogs):
    handler = window.event_handler
    container = window.components["image_cards_container"]

    handler._add_images(images[:MAX_IMAGES])
    assert container.get_image_count() == MAX_IMAGES

    container._remove_image(images[0])  # 等价于点击卡片上的“删除”

    assert handler.image_count == MAX_IMAGES - 1
    assert images[0] not in handler.image_manager.get_image_paths()

    dialogs.clear()
    handler._add_images([images[MAX_IMAGES]])

    assert images[MAX_IMAGES] in handler.current_images
    assert dialogs == []  # 不应再弹出配额提示


def test_deleted_texture_can_be_reimported(window, images, dialogs):
    handler = window.event_handler
    container = window.components["image_cards_container"]
    handler._add_images(images[:2])

    container._remove_image(images[0])
    dialogs.clear()
    handler._add_images([images[0]])

    assert images[0] in handler.current_images
    assert dialogs == []
    assert any(card.get_image_path() == images[0] for card in container.image_cards)


def test_limit_message_shown_once(window, images, dialogs):
    handler = window.event_handler
    handler._add_images(images[:MAX_IMAGES])

    dialogs.clear()
    handler._add_images(images[MAX_IMAGES:])

    assert len(dialogs) == 1
    assert handler.image_count == MAX_IMAGES


def test_current_images_is_readonly_snapshot(window, images):
    handler = window.event_handler
    handler._add_images(images[:3])

    snapshot = handler.current_images

    assert isinstance(snapshot, tuple)
    with pytest.raises(AttributeError):
        snapshot.append("hack")  # 外部无法写回模型
    assert handler.image_count == 3


def test_generation_snapshot_excludes_deleted(window, images):
    """生成 SDF 读取的就是这份快照，已删除的图像不得参与计算"""
    handler = window.event_handler
    container = window.components["image_cards_container"]
    handler._add_images(images[:3])

    container._remove_image(images[1])

    assert handler.current_images == (images[0], images[2])


def test_clear_releases_all_quota(window, images):
    handler = window.event_handler
    container = window.components["image_cards_container"]
    handler._add_images(images[:MAX_IMAGES])

    handler.handle_clear_images()

    assert handler.image_count == 0
    assert container.get_image_count() == 0
    handler._add_images(images[:MAX_IMAGES])
    assert handler.image_count == MAX_IMAGES
