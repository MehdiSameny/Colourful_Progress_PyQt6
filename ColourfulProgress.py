#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt6.QtCore import QLineF, QRect, QRectF, Qt, QAbstractAnimation, QCoreApplication, QEvent, QTime
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QTransform
from PyQt6.QtWidgets import (QApplication, QGridLayout, QProgressBar, QSlider, QStyleOptionProgressBar, QWidget)
from enum import IntEnum


ScrollBarFadeOutDuration = 200.0
ScrollBarFadeOutDelay = 450.0
StyleAnimationUpdate = 213


class QStyleAnimation(QAbstractAnimation):
    FrameRate = IntEnum('FrameRate', ['DefaultFps', 'SixtyFps', 'ThirtyFps', 'TwentyFps', 'FifteenFps'])

    def __init__(self, *args, **kwargs):
        super(QStyleAnimation, self).__init__(*args, **kwargs)
        self._delay = 0
        self._duration = -1
        self._startTime = QTime.currentTime()
        self._fps = self.FrameRate.ThirtyFps
        self._skip = 0

    def target(self):
        return self.parent()

    def duration(self):
        return self._duration

    def setDuration(self, duration):
        self._duration = duration

    def delay(self):
        return self._delay

    def setDelay(self, delay):
        self._delay = delay

    def startTime(self):
        return self._startTime

    def setStartTime(self, time):
        self._startTime = time

    def frameRate(self):
        return self._fps

    def setFrameRate(self, fps):
        self._fps = fps

    def updateTarget(self):
        event = QEvent(QEvent.Type(StyleAnimationUpdate))
        event.setAccepted(False)
        QCoreApplication.sendEvent(self.target(), event)
        if not event.isAccepted():
            self.stop()

    def start(self):
        self._skip = 0
        super(QStyleAnimation, self).start(QAbstractAnimation.DeletionPolicy.KeepWhenStopped)

    def isUpdateNeeded(self):
        return self.currentTime() > self._delay

    def updateCurrentTime(self, _):
        self._skip += 1
        if self._skip >= self._fps:
            self._skip = 0
            if self.parent() and self.isUpdateNeeded():
                self.updateTarget()


class QProgressStyleAnimation(QStyleAnimation):

    def __init__(self, speed, *args, **kwargs):
        super(QProgressStyleAnimation, self).__init__(*args, **kwargs)
        self._speed = speed
        self._step = -1

    def animationStep(self):
        return self.currentTime() / (1000.0 / self._speed)

    def progressStep(self, width):
        step = self.animationStep()
        progress = (step * width / self._speed) % width
        if ((step * width / self._speed) % (2 * width)) >= width:
            progress = width - progress
        return progress

    def speed(self):
        return self._speed

    def setSpeed(self, speed):
        self._speed = speed

    def isUpdateNeeded(self):
        if super(QProgressStyleAnimation, self).isUpdateNeeded():
            current = self.animationStep()
            if self._step == -1 or self._step != current:
                self._step = current
                return True
        return False


class ColourfulProgress(QProgressBar):

    def __init__(self, *args, **kwargs):
        self._color = kwargs.pop('color', QColor(43, 194, 83))
        self._fps = kwargs.pop('fps', 60)
        self._lineWidth = kwargs.pop('lineWidth', 50)  # 线条宽度
        self._radius = kwargs.pop('radius', None)  # None为自动计算圆角
        self._animation = None
        super(ColourfulProgress, self).__init__(*args, **kwargs)
        self.setColor(self._color)
        self.setFps(self._fps)
        self.setLineWidth(self._lineWidth)
        self.setRadius(self._radius)

    def setOrient(self, orient):
        self.setOrientation(orient)
        print(orient)

    def setColor(self, color):
        self._color = QColor(color) if isinstance(color, (QColor, Qt.GlobalColor)) else QColor(43, 194, 83)

    def setFps(self, fps):
        self._fps = max(int(fps), 1) if isinstance(fps, (int, float)) else 60

    def setLineWidth(self, width):
        self._lineWidth = max(int(width), 0) if isinstance(width, (int, float)) else 50

    def setRadius(self, radius):
        self._radius = max(int(radius), 1) if isinstance(radius, (int, float)) else None

    def paintEvent(self, _):
        option = QStyleOptionProgressBar()
        self.initStyleOption(option)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(0.5, 0.5)

        vertical = self.orientation() == Qt.Orientation.Vertical
        inverted = option.invertedAppearance
        indeterminate = (option.minimum == option.maximum) or (option.minimum < option.progress < option.maximum)
        rect = option.rect

        if vertical:
            rect = QRect(rect.left(), rect.top(), rect.height(), rect.width())
            m = QTransform.fromTranslate(rect.height(), 0)
            m.rotate(90.0)
            painter.setTransform(m, True)

        maxWidth = rect.width()
        progress = max(option.progress, option.minimum)
        totalSteps = max(1, option.maximum - option.minimum)
        progressSteps = progress - option.minimum
        progressBarWidth = int(progressSteps * maxWidth / totalSteps)
        width = progressBarWidth
        radius = max(1, (min(width,
                             self.width() if vertical else self.height()) //
                         4) if self._radius is None else self._radius)

        reverse = (not vertical and option.direction == Qt.LayoutDirection.RightToLeft) or vertical
        if inverted:
            reverse = not reverse

        path = QPainterPath()
        if not reverse:
            progressBar = QRectF(rect.left(), rect.top(), width, rect.height())
        else:
            progressBar = QRectF(rect.right() - width, rect.top(), width, rect.height())

        path.addRoundedRect(progressBar, radius, radius)
        painter.setClipPath(path)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._color)
        painter.drawRoundedRect(progressBar, radius, radius)

        if not indeterminate:
            if self._animation:
                self._animation.stop()
                self._animation = None
        else:
            color = self._color.lighter(320)
            color.setAlpha(80)
            painter.setPen(QPen(color, self._lineWidth))

            if self._animation:
                if self._animation.state() == QProgressStyleAnimation.State.Stopped:
                    self._animation.start()
                step = int(self._animation.animationStep() % self._lineWidth)
            else:
                step = 0
                self._animation = QProgressStyleAnimation(self._fps, self)
                self._animation.start()

            startX = int(progressBar.left() - rect.height() - self._lineWidth)
            endX = int(rect.right() + self._lineWidth)

            if (not inverted and not vertical) or (inverted and vertical):
                lines = [
                    QLineF(x + step, progressBar.bottom(),
                           x + rect.height() + step, progressBar.top())
                    for x in range(startX, endX, self._lineWidth)
                ]
            else:
                lines = [
                    QLineF(x - step, progressBar.bottom(),
                           x + rect.height() - step, progressBar.top())
                    for x in range(startX, endX, self._lineWidth)
                ]
            painter.drawLines(lines)

