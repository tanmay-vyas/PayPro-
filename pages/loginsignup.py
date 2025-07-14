from datetime import datetime
import streamlit as st
import pymysql
from pymysql.cursors import DictCursor


class UserManager:
    def __init__(self, host='localhost', user='root', password='root', database='signup_db'):
        self.connection = pymysql.connect(
            user=user,
            password=password,
            database=database,
            cursorclass=DictCursor
        )

    def _set_background(self):
        page_bg_img = """
        <style>
        [data-testid="stAppViewContainer"]{
            background-image: url("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTbnFMFz_PC5XKL47zTI-alZTld2w5atgRkuQ&s");
            background-size: cover;
            background-position: centre;
            background-repeat: no-repeat;
        }
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)

    def username_exists(self, username):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users WHERE username=%s", (username,))
            return cursor.fetchone() is not None

    def verify_login(self, username, password):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT password FROM users WHERE username=%s", (username,))
            row = cursor.fetchone()
            return row and row['password'] == password

    def add_user(self, fullname, phone, dob, email, username, password):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (fullname, phone, dob, email, username, password) VALUES (%s, %s, %s, %s, %s, %s)",
                (fullname, phone, dob.strftime("%Y-%m-%d"), email, username, password)
            )
            self.connection.commit()

    def close(self):
        self.connection.close()


class AuthApp:
    def __init__(self):
        self.user_manager = UserManager()
        st.session_state.setdefault("mode", "Login")
        st.session_state.setdefault("logged_in", False)

    def run(self):
        self.user_manager._set_background()
        st.title("Login / Sign Up")
        mode = st.sidebar.selectbox(
            "Choose Action",
            ["Login", "Sign Up"],
            index=0 if st.session_state.mode == "Login" else 1
        )
        st.session_state.mode = mode

        if mode == "Sign Up":
            self.sign_up_page()
        elif mode == "Login":
            self.login_page()

    def sign_up_page(self):
        with st.form("SignUpForm"):
            st.subheader("Create a new account")
            name = st.text_input("Enter your fullname")
            phone_no = st.number_input(
                "Enter your Phone number📱", min_value=1000000000,
                max_value=9999999999, step=1, format="%d")
            dob = st.date_input("Date of birth", max_value=datetime.today().date(),
                                min_value=datetime(1960, 1, 1).date())
            gmail = st.text_input("Email ID")
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input(
                "Confirm Password", type="password")

            if st.form_submit_button("Sign Up"):
                capatilized_name = name.title()

                if not name.strip():
                    st.error("Full name cannot be empty.")
                elif not (1000000000 <= phone_no <= 9999999999):
                    st.error("Please enter a valid 10-digit phone number.")
                elif new_username == "" or new_password == "":
                    st.error("Username and password cannot be empty.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif self.user_manager.username_exists(new_username):
                    st.error("Username already exists. Please choose another.")
                elif not gmail.lower().endswith("@gmail.com"):
                    st.error("Please enter a valid Gmail address.")
                else:
                    self.user_manager.add_user(
                        capatilized_name, phone_no, dob, gmail, new_username, new_password
                    )
                    st.success(
                        "Account created successfully! You can now log in.")
                    st.session_state.mode = "Login"
                    st.rerun()
        if st.button("Go to Login"):
            st.session_state.mode = "Login"
            st.rerun()

    def login_page(self):
        st.subheader("Log in to your account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Login"):
                if username == "" or password == "":
                    st.error("Please enter both username and password.")
                elif self.user_manager.verify_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"Welcome, {username}!")
                    st.switch_page('pages/salary_calculator.py')
                else:
                    st.error("Invalid username or password.")

        with col2:
            if st.button("Go to Sign Up"):
                st.session_state.mode = "Sign Up"
                st.rerun()

        if st.button("Back to Home"):
            st.switch_page('main.py')
            st.info("Back to home (implement navigation if needed).")


if __name__ == "__main__":
    app = AuthApp()
    app.run()
