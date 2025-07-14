import streamlit as st
from datetime import datetime
from streamlit_autorefresh import st_autorefresh


class WelcomePage:
    def __init__(self, refresh_interval_ms=500):
        self.refresh_interval_ms = refresh_interval_ms
        self._initialize_session_state()
        self._set_background()

    def _initialize_session_state(self):
        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False

    def _set_background(self):
        page_bg_img = """
        <style>
        [data-testid="stAppViewContainer"]{
            background-image: url("https://img.freepik.com/premium-photo/currency-exchange-concepts-interbank-payments-use-money-transfer-global-business-fintech-finance-technology-online-banking-online-banking-interbank-payment-concept_35148-11131.jpg?semt=ais_hybrid&w=740");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)

    def display_datetime(self):
       # Auto-refresh the page every refresh_interval_ms milliseconds
        st_autorefresh(interval=self.refresh_interval_ms,
                       limit=None, key="timer")

        now = datetime.now()
        current_time = now.strftime("%I:%M:%S %p")
        current_day = now.strftime("%A, %B %d, %Y")

        st.markdown(f"""
        ### 📅 {current_day}
        ### 🕐 {current_time}
        """)

    def show(self):
        self.display_datetime()
        st.title("WELCOME TO PAYPRO")

        if st.button("Enter", type="primary"):
            st.session_state.logged_in = True
            st.switch_page("pages/loginsignup.py")


if __name__ == "__main__":
    app = WelcomePage()
    app.show()
