import sys
from PyQt6.QtWidgets import QApplication
from shiyunzi.view.login_view import LoginView
from shiyunzi.utils.task_manager import kickoff

def main():
    kickoff()
    app = QApplication(sys.argv)
    login_window = LoginView()
    login_window.show()
    return app.exec()

if __name__ == '__main__':
    sys.exit(main()) 