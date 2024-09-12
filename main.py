from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QComboBox, \
    QDateTimeEdit, QMessageBox, QMenuBar, QAction, QDialog, QFormLayout
from PyQt5.QtCore import QDateTime
from PyQt5.QtGui import QFont
import random
import sys
import json
import requests
from datetime import datetime
from plyer import notification

# Списки для выбора значений
alarm_types = ["Capacity", "Communications", "Data", "Environmental", "Equipment", "Management", "Security", "Software",
               "Synchronization Timing", "Untyped"]
probable_causes = ["bandwidthReduced_thresholdCrossed", "queueSize_thresholdFatal",
                   "loggingCapacityReduced_thresholdCrossed",
                   "alarmReportingReduced_thresholdCrossed", "thresholdCrossed", "storage_thresholdCrossed",
                   "systemResourcesOverload_thresholdFatal",
                   "alarmIndicationSignal_fail", "alternateModulationSignal_fault"]
perceived_severities = ["Critical", "Major", "Minor", "Warning", "Indeterminate"]


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("Настройки")
        self.layout = QFormLayout()

        # Поля для host и token с увеличением размеров и многострочными
        self.host = QTextEdit(self)
        self.host.setFixedHeight(80)
        self.token = QTextEdit(self)
        self.token.setFixedHeight(80)

        # Загрузка сохранённых настроек
        self.load_settings()

        self.layout.addRow("Host:", self.host)
        self.layout.addRow("Token:", self.token)

        # Кнопка для сохранения настроек
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_settings)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump({'host': self.host.toPlainText(), 'token': self.token.toPlainText()}, f)
        QMessageBox.information(self, "Сохранено", "Настройки сохранены.")

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.host.setText(settings['host'])
                self.token.setText(settings['token'])
        except FileNotFoundError:
            pass


class AlarmApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Генератор Событий TRS-Alarm events Generator')
        self.setGeometry(100, 100, 600, 600)

        # Шрифт для приложения
        font = QFont("Arial", 12)
        self.setFont(font)

        # Центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout
        self.layout = QVBoxLayout()

        # Поля для атрибутов
        self.alarmId = QLineEdit(self)
        self.externalAlarmId = QLineEdit(self)
        self.alarmedObjectId = QLineEdit(self)
        self.idCI = QLineEdit(self)  # Поле для нового атрибута idCI
        self.alarmType = QComboBox(self)
        self.alarmType.addItems(alarm_types)
        self.probableCause = QComboBox(self)
        self.probableCause.addItems(probable_causes)
        self.perceivedSeverity = QComboBox(self)
        self.perceivedSeverity.addItems(perceived_severities)
        self.specificProblem = QLineEdit(self)
        self.specificProblem.setText("-")
        self.alarmDetails = QLineEdit(self)
        self.alarmDetails.setText("-")
        self.sourceSystem = QLineEdit(self)
        self.sourceSystem.setText("Генератор Событий TRS Events Generator")
        self.alarmRaisedTime = QDateTimeEdit(self)
        self.alarmRaisedTime.setDateTime(QDateTime.currentDateTime())

        # Добавляем все поля в Layout
        self.layout.addWidget(QLabel("Alarm ID"))
        self.layout.addWidget(self.alarmId)
        self.layout.addWidget(QLabel("External Alarm ID"))
        self.layout.addWidget(self.externalAlarmId)
        self.layout.addWidget(QLabel("Alarmed Object ID"))
        self.layout.addWidget(self.alarmedObjectId)
        self.layout.addWidget(QLabel("ID CI"))  # Новый атрибут
        self.layout.addWidget(self.idCI)
        self.layout.addWidget(QLabel("Alarm Type"))
        self.layout.addWidget(self.alarmType)
        self.layout.addWidget(QLabel("Probable Cause"))
        self.layout.addWidget(self.probableCause)
        self.layout.addWidget(QLabel("Perceived Severity"))
        self.layout.addWidget(self.perceivedSeverity)
        self.layout.addWidget(QLabel("Specific Problem"))
        self.layout.addWidget(self.specificProblem)
        self.layout.addWidget(QLabel("Alarm Details"))
        self.layout.addWidget(self.alarmDetails)
        self.layout.addWidget(QLabel("Source System"))
        self.layout.addWidget(self.sourceSystem)
        self.layout.addWidget(QLabel("Alarm Raised Time"))
        self.layout.addWidget(self.alarmRaisedTime)

        # Кнопка для генерации случайных значений
        self.random_button = QPushButton("Заполнить случайные значения", self)
        self.random_button.clicked.connect(self.fill_random_values)
        self.layout.addWidget(self.random_button)

        # Применение Layout
        self.central_widget.setLayout(self.layout)

        # Верхнее меню
        self.menu_bar = self.menuBar()
        self.settings_action = QAction("Настройки", self)
        self.settings_action.triggered.connect(self.open_settings_dialog)
        self.menu_bar.addAction(self.settings_action)

        self.send_action = QAction("Отправить событие", self)
        self.send_action.triggered.connect(self.send_event)
        self.menu_bar.addAction(self.send_action)

        # Загрузка настроек
        self.load_settings()

    def fill_random_values(self):
        self.alarmId.setText(str(random.randint(1000, 9999)))
        self.externalAlarmId.setText(str(random.randint(1000, 9999)))
        self.alarmedObjectId.setText(str(random.randint(1000, 9999)))
        self.idCI.setText(str(random.randint(1000, 9999)))  # Генерация случайного значения для idCI
        self.alarmType.setCurrentText(random.choice(alarm_types))
        self.probableCause.setCurrentText(random.choice(probable_causes))
        self.perceivedSeverity.setCurrentText(random.choice(perceived_severities))
        self.alarmRaisedTime.setDateTime(QDateTime.currentDateTime())
        QMessageBox.information(self, "Заполнено", "Все параметры заполнены случайными значениями.")

    def open_settings_dialog(self):
        self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.exec_()

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.host = settings['host']
                self.token = settings['token']
        except FileNotFoundError:
            self.host = ''
            self.token = ''

    def send_event(self):
        # Формирование данных для запроса
        alarm_data = {
            "alarmId": self.alarmId.text(),
            "externalAlarmId": self.externalAlarmId.text(),
            "alarmedObjectId": self.alarmedObjectId.text(),
            "idCI": self.idCI.text(),  # Добавлен новый параметр в запрос
            "alarmType": self.alarmType.currentText(),
            "probableCause": self.probableCause.currentText(),
            "perceivedSeverity": self.perceivedSeverity.currentText(),
            "specificProblem": self.specificProblem.text(),
            "alarmDetails": self.alarmDetails.text(),
            "sourceSystem": self.sourceSystem.text(),
            "alarmRaisedTime": self.alarmRaisedTime.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        }

        # Отправка POST-запроса
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
            response = requests.post(self.host, json=alarm_data, headers=headers)
            if response.status_code == 200:
                # Ограничиваем длину текста для уведомления
                response_text = response.text[:200]  # Обрезаем до 200 символов

                # Push-уведомление с использованием plyer
                notification.notify(
                    title="Запрос отправлен",
                    message=f"Ответ: {response_text[:200]}",  # Ограничение до 256 символов
                    timeout=5
                )

                # Полный ответ можно вывести в отдельное диалоговое окно
                QMessageBox.information(self, "Успех", f"Полный ответ: {response.text}")
            else:
                # Полный ответ можно вывести в отдельное диалоговое окно
                QMessageBox.information(self, "Успех", f"Полный ответ: {response.text}")
                notification.notify(
                    title="Ошибка",
                    message=f"Ошибка: {response.status_code}",
                    timeout=5
                )
        except Exception as e:
            notification.notify(
                title="Ошибка",
                message=f"Произошла ошибка: {str(e)[:200]}...",  # Ограничение текста ошибки
                timeout=5
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = AlarmApp()
    main_window.show()
    sys.exit(app.exec_())
