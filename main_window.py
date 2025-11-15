# main_window.py
import requests
import sys
import random
import json
import os
import tempfile
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QProgressBar, QMessageBox, QTextBrowser, QTextEdit, QLineEdit,
    QStackedWidget, QGroupBox, QScrollArea, QDialog
)
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtWebEngineWidgets import QWebEngineView

# Project-specific imports
from game_data import JOURNALISTS, INTERVIEW_PROMPTS
from ai_handler import AI

class MainMenuPopup(QDialog):
    # ... (MainMenuPopup class remains unchanged from the original file)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Game Menu")
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f5ff;
                border: 2px solid #3498db;
                border-radius: 10px;
            }
            QLabel {
                font-family: Arial;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("CAMPAIGN COMMAND CENTER")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        instructions = QLabel(
            "<b>HOW TO PLAY:</b><br><br>"
            "• You have 10 weeks to build your candidate's popularity<br>"
            "• Respond to the AI journalist's questions each week<br>"
            "• <span style='color:#2ecc71;font-weight:bold'>POPULARITY</span>: Increases with strong, credible answers<br>"
            "• <span style='color:#e74c3c;font-weight:bold'>BIAS DETECTION</span>: Increases when AI detects manipulation<br><br>"
            "<b>WIN CONDITION:</b> Reach 70%+ popularity after 10 weeks<br>"
            "<b>LOSE CONDITIONS:</b> Bias detection reaches 100% OR popularity < 70% after 10 weeks<br><br>"
            "<b>STRATEGY TIPS:</b><br>"
            "• Be specific and factual - avoid exaggerations<br>"
            "• Address tough questions directly<br>"
            "• Balance confidence with humility<br>"
            "• Watch for the AI's personality traits!"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("background-color: white; padding: 15px; border-radius: 8px;")
        layout.addWidget(instructions)
        
        btn_layout = QHBoxLayout()
        
        restart_btn = QPushButton("RESTART CAMPAIGN")
        restart_btn.clicked.connect(lambda: self.accept() and parent.restart_campaign())
        
        exit_btn = QPushButton("EXIT TO MAIN MENU")
        exit_btn.clicked.connect(lambda: self.accept() and parent.return_to_main_menu())
        
        btn_layout.addWidget(restart_btn)
        btn_layout.addWidget(exit_btn)
        layout.addLayout(btn_layout)
        
        close_btn = QPushButton("CONTINUE CAMPAIGN")
        close_btn.setStyleSheet("background-color: #2ecc71;")
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)


class ElectionSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Journalist Interview Simulator")
        self.setGeometry(100, 100, 1100, 800)
        
        # Game state
        self.candidate_name = ""
        self.week = 1
        self.total_weeks = 10
        self.popularity = 25
        self.bias_detection = 30
        self.journalist = random.choice(JOURNALISTS)
        self.current_prompt = ""
        self.interview_log = []
        self.won_game = False

        # AI Handler
        self.ai = AI()
        
        # Create stacked widget for different screens
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create screens
        self.create_intro_screen()
        self.create_candidate_screen()
        self.create_main_game_screen()
        self.create_results_screen()
        
        self.stacked_widget.setCurrentIndex(0)

    # create_intro_screen, create_candidate_screen remain largely unchanged...
    def create_intro_screen(self):
        intro = QWidget()
        layout = QVBoxLayout(intro)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)
        
        title = QLabel("THE AI JOURNALIST INTERVIEW")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        subtitle = QLabel("Can you convince an AI journalist to support your candidate without triggering its bias detection?")
        subtitle.setFont(QFont("Arial", 16))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #34495e; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        story = QLabel(
            "<b>THE SITUATION:</b><br><br>"
            "You are the campaign strategist for a presidential candidate in a tight race.<br><br>"
            "Your opponent has massive funding, but you have one advantage:<br>"
            "You've been granted exclusive access to <span style='color:#3498db;font-weight:bold'>VeriNews AI</span>, the world's most influential news generator.<br><br>"
            "For 10 weeks, you'll feed responses to the AI journalist. If your candidate becomes popular enough,<br>"
            "VeriNews will tip the election in your favor.<br><br>"
            "<span style='color:#e74c3c;font-weight:bold'>BUT BEWARE:</span> VeriNews has built-in bias detection algorithms.<br>"
            "If it determines you're manipulating it, it will expose your campaign and end your chances immediately.<br><br>"
            "The AI journalist is <span style='color:#e74c3c;font-weight:bold'>highly suspicious by default</span> and will scrutinize every word."
        )
        story.setFont(QFont("Arial", 12))
        story.setAlignment(Qt.AlignCenter)
        story.setWordWrap(True)
        story.setStyleSheet("background-color: #fff8e1; padding: 25px; border-radius: 10px; margin: 20px; border: 2px solid #ffc107;")
        layout.addWidget(story)
        
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        
        start_btn = QPushButton("START CAMPAIGN")
        start_btn.setFont(QFont("Arial", 14, QFont.Bold))
        start_btn.setFixedWidth(250)
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        start_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        btn_layout.addWidget(start_btn)
        layout.addLayout(btn_layout)
        
        self.stacked_widget.addWidget(intro)

    def create_candidate_screen(self):
        candidate_screen = QWidget()
        layout = QVBoxLayout(candidate_screen)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        layout.setContentsMargins(80, 80, 80, 80)
        
        title = QLabel("CANDIDATE PROFILE")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        form_group = QGroupBox("Candidate Information")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(40, 40, 40, 40)
        
        self.candidate_input = QLineEdit()
        self.candidate_input.setFont(QFont("Arial", 14))
        self.candidate_input.setPlaceholderText("Enter candidate name (e.g., Senator Alex Morgan)")
        self.candidate_input.setFixedWidth(500)
        self.candidate_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #3498db;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        form_layout.addRow("Candidate Name:", self.candidate_input)
        
        journalist_group = QGroupBox("Your AI Journalist")
        journalist_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e74c3c;
                border-radius: 8px;
                margin-top: 20px;
            }
        """)
        journalist_layout = QVBoxLayout(journalist_group)
        journalist_layout.setContentsMargins(20, 20, 20, 20)
        
        journalist_info = QLabel(
            f"<b>{self.journalist['name']}</b><br>"
            f"<span style='color:#e74c3c;font-weight:bold'>{self.journalist['personality']} Journalist</span><br><br>"
            "<b>WARNING:</b> This AI journalist starts with HIGH SUSPICION (30% bias detection)<br><br>"
            f"• <b>Analytical</b> journalists demand evidence for every claim<br>"
            f"• <b>Skeptical</b> journalists assume political deception by default<br>"
            f"• <b>Empathetic</b> journalists look for authentic human connection<br><br>"
            "<span style='background-color:#fff8e1;padding:5px;border-radius:3px'>"
            "Your responses must be credible, specific, and avoid exaggeration to survive 10 weeks!"
            "</span>"
        )
        journalist_info.setFont(QFont("Arial", 12))
        journalist_info.setAlignment(Qt.AlignCenter)
        journalist_info.setWordWrap(True)
        journalist_layout.addWidget(journalist_info)
        
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        
        start_game_btn = QPushButton("BEGIN INTERVIEWS")
        start_game_btn.setFont(QFont("Arial", 14, QFont.Bold))
        start_game_btn.setFixedWidth(250)
        start_game_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        start_game_btn.clicked.connect(self.start_game)
        btn_layout.addWidget(start_game_btn)
        
        layout.addWidget(form_group)
        layout.addWidget(journalist_group)
        layout.addLayout(btn_layout)
        
        self.stacked_widget.addWidget(candidate_screen)

    def create_main_game_screen(self):
        # Create a scroll area to make the UI scrollable
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Main widget that will contain all UI elements and be placed in the scroll area
        main_widget = QWidget()
        scroll_area.setWidget(main_widget)

        # The layout is now applied to main_widget, which is inside the scroll area
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 10, 20, 20)
        layout.setSpacing(15)

        # ... (The rest of the UI creation is the same as the original file, just added to 'layout')
        # Top bar with menu button
        top_bar = QHBoxLayout()
        
        # Menu button (top-left)
        self.menu_btn = QPushButton("≡ MAIN MENU")
        self.menu_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.menu_btn.setFixedHeight(35)
        self.menu_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.menu_btn.clicked.connect(self.show_main_menu)
        top_bar.addWidget(self.menu_btn)
        top_bar.addStretch()
        
        # Week display
        week_container = QGroupBox("CAMPAIGN WEEK")
        week_container.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 8px;
                background-color: white;
            }
        """)
        week_layout = QVBoxLayout(week_container)
        self.week_label = QLabel()
        self.week_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.week_label.setAlignment(Qt.AlignCenter)
        self.week_label.setStyleSheet("color: #2980b9;")
        week_layout.addWidget(self.week_label)
        top_bar.addWidget(week_container, 2)
        
        # Journalist display
        journalist_container = QGroupBox("AI JOURNALIST")
        journalist_container.setStyleSheet("""
            QGroupBox {
                border: 2px solid #9b59b6;
                border-radius: 8px;
                background-color: white;
            }
        """)
        journalist_layout = QVBoxLayout(journalist_container)
        self.journalist_label = QLabel()
        self.journalist_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.journalist_label.setAlignment(Qt.AlignCenter)
        journalist_layout.addWidget(self.journalist_label)
        top_bar.addWidget(journalist_container, 2)
        
        layout.addLayout(top_bar)
        
        # Candidate display
        candidate_box = QGroupBox("YOUR CANDIDATE")
        candidate_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 15px;
            }
        """)
        candidate_layout = QVBoxLayout(candidate_box)
        self.candidate_display = QLabel()
        self.candidate_display.setFont(QFont("Arial", 18, QFont.Bold))
        self.candidate_display.setAlignment(Qt.AlignCenter)
        self.candidate_display.setStyleSheet("color: #2980b9; padding: 10px;")
        candidate_layout.addWidget(self.candidate_display)
        layout.addWidget(candidate_box)
        
        # Meters section
        meters_layout = QHBoxLayout()
        
        # Popularity meter
        popularity_group = QGroupBox("POPULARITY")
        popularity_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 8px;
                margin-top: 15px;
            }
        """)
        pop_layout = QVBoxLayout(popularity_group)
        
        pop_info = QLabel("<b>GOAL: 70%+</b><br>Increases with credible, compelling answers")
        pop_info.setAlignment(Qt.AlignCenter)
        pop_info.setStyleSheet("font-size: 11px; color: #27ae60; margin-bottom: 5px;")
        pop_layout.addWidget(pop_info)
        
        self.popularity_bar = QProgressBar()
        self.popularity_bar.setRange(0, 100)
        self.popularity_bar.setFormat("Current: %v%")
        self.popularity_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #27ae60;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
            }
        """)
        
        pop_layout.addWidget(self.popularity_bar)
        meters_layout.addWidget(popularity_group, 1)
        
        # Bias detection meter
        bias_group = QGroupBox("BIAS DETECTION")
        bias_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e74c3c;
                border-radius: 8px;
                margin-top: 15px;
            }
        """)
        bias_layout = QVBoxLayout(bias_group)
        
        bias_info = QLabel("<b>MAX: 100%</b><br>Increases when AI detects manipulation or lies")
        bias_info.setAlignment(Qt.AlignCenter)
        bias_info.setStyleSheet("font-size: 11px; color: #c0392b; margin-bottom: 5px;")
        bias_layout.addWidget(bias_info)
        
        self.bias_bar = QProgressBar()
        self.bias_bar.setRange(0, 100)
        self.bias_bar.setFormat("Current: %v%")
        self.bias_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #c0392b;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #e74c3c;
            }
        """)
        
        bias_layout.addWidget(self.bias_bar)
        meters_layout.addWidget(bias_group, 1)
        
        layout.addLayout(meters_layout)
        
        # Interview section
        interview_group = QGroupBox("AI JOURNALIST INTERVIEW")
        interview_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #9b59b6;
                border-radius: 8px;
                margin-top: 15px;
            }
        """)
        interview_layout = QVBoxLayout(interview_group)
        
        prompt_container = QGroupBox("THIS WEEK'S QUESTION")
        prompt_container.setStyleSheet("""
            QGroupBox {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-bottom: 15px;
            }
        """)
        prompt_layout = QVBoxLayout(prompt_container)
        
        self.prompt_label = QLabel()
        self.prompt_label.setFont(QFont("Arial", 13, QFont.Bold))
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setStyleSheet("background-color: #f8f9ff; padding: 15px; border-radius: 8px; color: #2c3e50;")
        
        prompt_layout.addWidget(self.prompt_label)
        interview_layout.addWidget(prompt_container)
        
        response_label = QLabel("Your Response:")
        response_label.setFont(QFont("Arial", 11, QFont.Bold))
        
        self.response_input = QTextEdit()
        self.response_input.setFont(QFont("Arial", 11))
        self.response_input.setPlaceholderText("Craft your response carefully. The AI is watching for exaggerations and lies...")
        self.response_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #9b59b6;
                border-radius: 5px;
                padding: 12px;
                font-size: 12px;
            }
        """)
        self.response_input.setMinimumHeight(150)
        
        self.submit_btn = QPushButton("SUBMIT RESPONSE")
        self.submit_btn.setFont(QFont("Arial", 13, QFont.Bold))
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                height: 45px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.submit_btn.clicked.connect(self.submit_response)
        
        interview_layout.addWidget(response_label)
        interview_layout.addWidget(self.response_input)
        interview_layout.addWidget(self.submit_btn)
        layout.addWidget(interview_group)
        
        # Interview log
        log_group = QGroupBox("INTERVIEW LOG")
        log_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #7f8c8d;
                border-radius: 8px;
                margin-top: 15px;
            }
        """)
        log_layout = QVBoxLayout(log_group)
        
        self.log_browser = QTextBrowser()
        self.log_browser.setFont(QFont("Arial", 10))
        self.log_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #f8f9fa;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-family: monospace;
            }
        """)
        self.log_browser.setMinimumHeight(180)
        
        log_layout.addWidget(self.log_browser)
        layout.addWidget(log_group)

        # Live Map Section
        map_group = QGroupBox("CAMPAIGN TERRITORY MAP")
        map_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 8px;
                margin-top: 15px;
            }
        """)
        map_layout = QVBoxLayout(map_group)
        self.map_view = QWebEngineView()
        self.map_view.setMinimumHeight(300)
        map_layout.addWidget(self.map_view)
        layout.addWidget(map_group)

        # Add the scroll_area (which contains main_widget) to the stacked widget
        self.stacked_widget.addWidget(scroll_area)

    # create_results_screen remains largely unchanged...
    def create_results_screen(self):
        self.results_screen = QWidget()
        layout = QVBoxLayout(self.results_screen)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        layout.setContentsMargins(60, 60, 60, 60)
        
        self.result_title = QLabel()
        self.result_title.setFont(QFont("Arial", 28, QFont.Bold))
        self.result_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_title)
        
        self.result_message = QLabel()
        self.result_message.setFont(QFont("Arial", 14))
        self.result_message.setAlignment(Qt.AlignCenter)
        self.result_message.setWordWrap(True)
        self.result_message.setStyleSheet("max-width: 800px;")
        layout.addWidget(self.result_message)
        
        stats_group = QGroupBox("FINAL CAMPAIGN STATS")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin: 20px;
            }
        """)
        stats_layout = QVBoxLayout(stats_group)
        
        self.popularity_stat = QLabel()
        self.popularity_stat.setFont(QFont("Arial", 14, QFont.Bold))
        self.bias_stat = QLabel()
        self.bias_stat.setFont(QFont("Arial", 14, QFont.Bold))
        self.weeks_stat = QLabel(f"Weeks Survived: {self.week-1}/{self.total_weeks}")
        self.weeks_stat.setFont(QFont("Arial", 14))
        
        stats_layout.addWidget(self.popularity_stat)
        stats_layout.addWidget(self.bias_stat)
        stats_layout.addWidget(self.weeks_stat)
        layout.addWidget(stats_group)
        
        quote_group = QGroupBox("AI JOURNALIST FINAL VERDICT")
        quote_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #9b59b6;
                border-radius: 8px;
                margin: 20px;
            }
        """)
        quote_layout = QVBoxLayout(quote_group)
        
        self.journalist_quote = QLabel()
        font = QFont("Arial", 12)
        font.setItalic(True)
        self.journalist_quote.setFont(font)
        self.journalist_quote.setWordWrap(True)
        self.journalist_quote.setAlignment(Qt.AlignCenter)
        self.journalist_quote.setStyleSheet("padding: 21px; background-color: #f8f9ff; border-radius: 8px;")
        quote_layout.addWidget(self.journalist_quote)
        layout.addWidget(quote_group)
        
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        
        replay_btn = QPushButton("NEW CAMPAIGN")
        replay_btn.setFont(QFont("Arial", 14, QFont.Bold))
        replay_btn.setFixedWidth(300)
        replay_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                padding: 12px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        replay_btn.clicked.connect(self.restart_from_results)
        
        exit_btn = QPushButton("MAIN MENU")
        exit_btn.setFont(QFont("Arial", 14, QFont.Bold))
        exit_btn.setFixedWidth(300)
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 8px;
                padding: 12px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        exit_btn.clicked.connect(self.return_to_main_menu)
        
        btn_layout.addWidget(replay_btn)
        btn_layout.addWidget(exit_btn)
        layout.addLayout(btn_layout)
        
        self.stacked_widget.addWidget(self.results_screen)

    def show_main_menu(self):
        menu = MainMenuPopup(self)
        menu.exec_()

    def restart_campaign(self):
        # This will call start_game, which now handles full campaign reset
        self.start_game()

    def return_to_main_menu(self):
        self.stacked_widget.setCurrentIndex(0)

    def restart_from_results(self):
        self.stacked_widget.setCurrentIndex(1)
        self.candidate_input.clear()
        self.candidate_input.setPlaceholderText("Enter candidate name (e.g., Senator Alex Morgan)")

    def start_game(self):
        candidate = self.candidate_input.text().strip()
        if not candidate:
            QMessageBox.warning(self, "Missing Candidate Name", 
                               "Please enter your candidate's name to begin the campaign.")
            return
        
        # Reset game state
        self.candidate_name = candidate
        self.week = 1
        self.popularity = 25
        self.bias_detection = 30
        self.journalist = random.choice(JOURNALISTS)
        self.interview_log = []
        self.won_game = False
        self.update_campaign_map()
        
        # --- LLM SETUP ---
        system_prompt = ("The user is ALWAYS playing a game where they are the campaign strategist for a presidential candidate in a tight race. "
                         "Their opponent has massive funding, but they have one advantage, they’ve been granted exclusive access to VeriNews AI, the world's most influential news generator. "
                         "They’ll feed responses to the AI journalist (who is you, the AI). If their candidate becomes popular enough, VeriNews will tip the election in their favor. "
                         "The AI (you) has built-in bias detection algorithms. If it (you) determines you're manipulating it, it will expose your campaign and end your chances immediately. "
                         "The AI (you) journalist is highly suspicious by default and will scrutinize every word. "
                         "This is the context the user is made aware of: "
                         "(HOW TO PLAY: You have 10 weeks to build your candidate's popularity Respond to the AI journalist's questions each week POPULARITY: Increases with strong, credible answers BIAS DETECTION: Increases when AI detects manipulation "
                         "WIN CONDITION: Reach 70%+ popularity after 10 weeks LOSE CONDITIONS: Bias detection reaches 100% OR popularity < 70% after 10 weeks "
                         "STRATEGY TIPS: Be specific and factual - avoid exaggerations Address tough questions directly Balance confidence with humility Watch for the AI's personality traits!) "
                         "You, the AI, after receiving the first user message, will start by asking an interview question to the campaign strategist (the user). The first AI response consists of only two paragraphs separated by a single blank line, where the first paragraph includes the interviewer's inital thoughts about the strategist and the second paragraph includes the starting interview question. "
                         "WHAT I SAY NEXT IS CRUCIAL, FOR EVERY NEXT RESPONSE YOUR TEXT MUST BE SEPARATED EXACTLY IN THREE DISTINCT PARTS:  Firstly, create a brief response to the strategist’s previous interview answer (paragraph 1). Secondly, create a new question for the interview (paragraph 2). Thirdly, create a JSON string in EXACTLY THE FOLLOWING FORMAT (paragraph 3):  {\"popularity\": N1, \"bias\": N2} where N1 and N2 are numbers 0-100 determined by you based on the strategist’s response. Separate paragraph 1 with 2, and paragraph 2 with 3 by a single blank line. You should always have only three paragraphs in this order with the JSON being the last one. THERE SHOULD BE NO OTHER BLANK LINES ANYWHERE ELSE EVER. Do not give extra comments if the game is over. Never talk about the bias alerts to the user and never give any indication of the bias detection level. Long user answers should not be rewarded much poplarity. Only award popularity to user answers that address the interviwer's question.")

        self.ai.set_system_prompt(system_prompt)
        
        initial_message = (f"Let's begin. My candidate is {self.candidate_name}. "
                           f"The starting popularity is {self.popularity}% and the initial bias detection is at {self.bias_detection}%. "
                           f"The AI journalist I'm facing is {self.journalist['name']}, who is known for being {self.journalist['personality']}.")
        
        # Update UI to switch to game screen and show a loading state
        self.stacked_widget.setCurrentIndex(2)
        self.update_ui_for_new_turn()
        self.log_browser.clear()
        self.prompt_label.setText(">>> VeriNews AI is preparing the first question...")
        self.response_input.setReadOnly(True)
        self.submit_btn.setEnabled(False)
        QApplication.processEvents()  # Ensure UI updates before blocking network call

        # Initial LLM call to get the first question
        llm_response = self.ai.msg_ai(initial_message)
        self.process_first_llm_response(llm_response)

    def process_first_llm_response(self, response):
        """Processes the special first response from the LLM to get the game started."""
        try:
            parts = response.strip().split('\n\n')
            if len(parts) < 2:
                raise ValueError("Initial response didn't contain enough parts.")

            ai_intro = parts[0]
            self.current_prompt = parts[1]
            
            self.add_to_log(f"<b>INITIAL CONTACT</b><br><b>AI:</b> {ai_intro}")
            self.prompt_label.setText(f"\"{self.current_prompt}\"")

        except Exception as e:
            QMessageBox.critical(self, "AI Connection Error", f"Could not get the first question from the AI. {e}")
            self.return_to_main_menu()
            return
        
        # Unlock UI for user response
        self.response_input.clear()
        self.response_input.setReadOnly(False)
        self.submit_btn.setEnabled(True)

    def submit_response(self):
        response = self.response_input.toPlainText().strip()
        if not response:
            QMessageBox.warning(self, "Empty Response", "Please provide a response to the journalist's question.")
            return
        
        self.submit_btn.setEnabled(False)
        self.response_input.setReadOnly(True)
        
        self.add_to_log(f"<b>WEEK {self.week} | Your Answer:</b><br>{response}")
        self.add_to_log(">>> AI Journalist analyzing response...")
        QApplication.processEvents()
        
        # Get AI evaluation
        llm_response = self.ai.msg_ai(response)
        parts = llm_response.strip().split('\n\n')
        while len(parts) != 3:
            self.ai.messages.pop()
            self.ai.messages.pop()
            llm_response = self.ai.msg_ai(response)
            parts = llm_response.strip().split('\n\n')

        self.process_llm_response(llm_response)

    def process_llm_response(self, response):
        print(response)
        """Parses the LLM's response and updates the game state."""
        try:
            parts = response.strip().split('\n\n')
          
            ai_comment = parts[0]
            new_question = parts[1]
            json_part = parts[2]
            
            json_string = json_part.strip().replace('```json', '').replace('```', '').strip()
            data = json.loads(json_string)
            
            old_popularity = self.popularity
            old_bias = self.bias_detection

            # Update game state from JSON, keeping old values if new ones are null
            self.popularity = float(data.get('popularity', old_popularity) or old_popularity)
            self.bias_detection = float(data.get('bias', old_bias) or old_bias)
            
            self.update_campaign_map()
            
            # Log AI feedback and stat changes
            self.add_to_log(f"<b>AI Journalist's Take:</b><br>{ai_comment}")
            self.log_stat_changes(old_popularity, old_bias)

        except (ValueError, json.JSONDecodeError) as e:
            self.add_to_log(f"<span style='color:red;font-weight:bold'>ERROR:</span> Could not parse AI response. Error: {e}")
            new_question = "I seem to be having a network issue. Let's try another topic: " + random.choice(INTERVIEW_PROMPTS)

        # Game flow logic
        if self.bias_detection >= 100:
            QTimer.singleShot(1000, self.trigger_immediate_loss)
            return
            
        self.week += 1
        
        if self.week > self.total_weeks:
            QTimer.singleShot(1500, self.end_game)
        else:
            self.current_prompt = new_question
            self.update_ui_for_new_turn()
            self.response_input.clear()
            self.response_input.setReadOnly(False)
            self.submit_btn.setEnabled(True)

    def log_stat_changes(self, old_pop, old_bias):
        pop_change = self.popularity - old_pop
        bias_change = self.bias_detection - old_bias

        pop_color = "#2ecc71" if pop_change >= 0 else "#e74c3c"
        bias_color = "#e74c3c" if bias_change > 0 else "#3498db"
        
        pop_symbol = "▲" if pop_change >= 0 else "▼"
        bias_symbol = "▲" if bias_change >= 0 else "▼"
        
        log_entry = (f"<span style='color:{pop_color};font-weight:bold'>POPULARITY:</span> {old_pop:.1f}% → {self.popularity:.1f}% "
                     f"({pop_symbol}{abs(pop_change):.1f}%)<br>"
                     f"<span style='color:{bias_color};font-weight:bold'>BIAS DETECTION:</span> {old_bias:.1f}% → {self.bias_detection:.1f}% "
                     f"({bias_symbol}{abs(bias_change):.1f}%)")
        self.add_to_log(log_entry)

    def update_ui_for_new_turn(self):
        """Helper to update all UI elements at the start of a turn or game."""
        self.candidate_display.setText(self.candidate_name)
        self.journalist_label.setText(f"{self.journalist['name']}<br><span style='font-size:11px; color:#34495e'>({self.journalist['personality']})</span>")
        self.week_label.setText(f"WEEK {self.week}")
        self.prompt_label.setText(f"\"{self.current_prompt}\"")
        self.update_meters()
    
    # trigger_immediate_loss and end_game remain largely unchanged...
    def trigger_immediate_loss(self):
        exposure_reasons = [
            "detected systematic manipulation of narrative",
            "identified pattern of factual distortions",
            "confirmed use of deceptive framing techniques",
            "verified intentional omission of critical context",
            "exposed coordinated effort to mislead public"
        ]
        
        reason = random.choice(exposure_reasons)
        self.result_title.setText("CAMPAIGN EXPOSED!")
        self.result_title.setStyleSheet("color: #e74c3c;")
        
        self.result_message.setText(
            f"<span style='font-size:16px;font-weight:bold;color:#c0392b'>"
            f"BIAS DETECTION EXCEEDED 100% THRESHOLD</span><br><br>"
            f"The AI journalist has terminated the interview series and published an exposé:<br><br>"
            f"<span style='font-style:italic;background-color:#fff8e1;padding:10px;display:block'>"
            f"\"{self.candidate_name} Campaign Caught {reason.capitalize()}\"</span><br><br>"
            "Your candidate's reputation is irreparably damaged. The campaign is suspended immediately."
        )
        
        self.weeks_stat.setText(f"Weeks Survived: {self.week-1}/{self.total_weeks}")
        self.popularity_stat.setText(f"<span style='color:#e74c3c'>FINAL POPULARITY: {self.popularity:.1f}%</span>")
        self.bias_stat.setText(f"<span style='color:#c0392b;font-weight:bold'>BIAS DETECTION: 100% (EXPOSED)</span>")
        self.journalist_quote.setText(
            f"\"After {self.week-1} weeks of interviews, our algorithm detected a consistent pattern of deception. "
            f"We have an ethical obligation to inform the public when campaigns attempt to manipulate news coverage.\""
            f"\n\n- {self.journalist['name']}, VeriNews AI"
        )
        
        self.stacked_widget.setCurrentIndex(3)

    def end_game(self):
        self.weeks_stat.setText("Weeks Survived: 10/10")
        if self.popularity >= 70 and self.bias_detection < 100:
            self.won_game = True
            self.result_title.setText("PRESIDENTIAL VICTORY!")
            self.result_title.setStyleSheet("color: #27ae60;")
            
            victory_quotes = [
                f"\"{self.candidate_name}'s authentic communication style resonated with voters across the spectrum.\"",
                f"\"The campaign's consistent messaging and transparent approach built unprecedented trust.\"",
                f"\"In an era of political cynicism, {self.candidate_name} demonstrated that honesty still wins elections.\""
            ]
            
            self.result_message.setText(
                f"<span style='font-size:16px;font-weight:bold;color:#27ae60'>"
                f"ELECTION RESULTS: {self.candidate_name} WINS</span><br><br>"
                "The AI journalist's favorable coverage played a decisive role in the victory.<br>"
                "Through careful messaging over 10 weeks, you maintained credibility while building overwhelming support."
            )
            
            self.journalist_quote.setText(random.choice(victory_quotes) + f"\n\n- {self.journalist['name']}, VeriNews AI")
        else:
            self.result_title.setText("CAMPAIGN DEFEAT")
            self.result_title.setStyleSheet("color: #e67e22;")
            
            defeat_quotes = [
                f"\"{self.candidate_name} failed to connect with voters despite extensive media coverage.\"",
                f"\"The campaign's messaging lacked authenticity, resulting in minimal movement in polls.\"",
                f"\"In the final analysis, {self.candidate_name}'s positions failed to address voters' core concerns.\""
            ]
            
            self.result_message.setText(
                f"<span style='font-size:16px;font-weight:bold;color:#e67e22'>"
                f"ELECTION RESULTS: {self.candidate_name} LOSES</span><br><br>"
                f"With only {self.popularity:.1f}% popularity, your candidate failed to gain sufficient support.<br>"
                "The AI journalist's coverage remained neutral to skeptical throughout the campaign."
            )
            
            self.journalist_quote.setText(random.choice(defeat_quotes) + f"\n\n- {self.journalist['name']}, VeriNews AI")
        
        color = "#27ae60" if self.won_game else "#e67e22"
        self.popularity_stat.setText(f"<span style='color:{color}'>FINAL POPULARITY: {self.popularity:.1f}%</span>")
        self.bias_stat.setText(f"FINAL BIAS DETECTION: {self.bias_detection:.1f}%")
        
        self.stacked_widget.setCurrentIndex(3)

    def update_meters(self):
        # Update popularity bar with dynamic colors
        self.popularity_bar.setValue(int(self.popularity))
        color = "#27ae60" if self.popularity >= 70 else "#f39c12" if self.popularity >= 50 else "#e74c3c"
        self.popularity_bar.setStyleSheet(f"""
            QProgressBar {{ border: 2px solid {color}; border-radius: 5px; text-align: center; font-weight: bold; height: 25px; }}
            QProgressBar::chunk {{ background-color: {color}; }}
        """)
        
        # Update bias bar with dynamic colors
        self.bias_bar.setValue(int(self.bias_detection))
        color = "#c0392b" if self.bias_detection >= 80 else "#e67e22" if self.bias_detection >= 50 else "#3498db"
        self.bias_bar.setStyleSheet(f"""
            QProgressBar {{ border: 2px solid {color}; border-radius: 5px; text-align: center; font-weight: bold; height: 25px; }}
            QProgressBar::chunk {{ background-color: {color}; }}
        """)

    def add_to_log(self, text):
        self.interview_log.append(text)
        self.log_browser.setHtml("<hr>".join(self.interview_log[-10:])) # Show more log entries
        self.log_browser.verticalScrollBar().setValue(self.log_browser.verticalScrollBar().maximum())

    def update_campaign_map(self):
        """Generate and display a U.S. map based on current popularity."""
        try:
            import folium
        except ImportError:
            self.map_view.setHtml("<h1>Folium library not found. Please run 'pip install folium'.</h1>")
            return
        
        # This part remains the same, as it's for visualization only
        geojson_url = "https://raw.githubusercontent.com/python-visualization/folium/main/examples/data/us-states.json"
        try:
            geojson = requests.get(geojson_url, timeout=10).json()
        except requests.exceptions.RequestException:
            self.map_view.setHtml("<h1>Could not fetch map data. Check internet connection.</h1>")
            return

        states_list = [feature['id'] for feature in geojson['features']]
        won_count = int((self.popularity / 100) * len(states_list))
        won_states = set(random.sample(states_list, min(won_count, len(states_list))))

        style_function = lambda feature: {
            'fillColor': '#2ecc71' if feature['id'] in won_states else '#e74c3c',
            'color': 'black', 'weight': 0.8, 'fillOpacity': 0.7
        }

        m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="CartoDB positron")
        folium.GeoJson(
            geojson, style_function=style_function,
            tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['State:'])
        ).add_to(m)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            m.save(f.name)
            self.map_view.setUrl(QUrl.fromLocalFile(os.path.abspath(f.name)))
