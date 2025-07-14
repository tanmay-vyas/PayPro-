import streamlit as st
from fpdf import FPDF


class SalarySlipPDF:
    """Class to generate a PDF for salary slip."""

    def __init__(self, slip_data):
        self.slip_data = slip_data
        self.pdf = FPDF()
        self.pdf.add_page()
        self.pdf.set_font("Arial", size=12)

    def add_header(self):
        self.pdf.cell(0, 10, "SALARY SLIP", ln=True, align='C')
        self.pdf.ln(10)

    def add_employee_info(self):
        self.pdf.cell(
            0, 10, f"Slip ID: {self.slip_data.get('slip_id', 'N/A')}", ln=True)
        self.pdf.cell(
            0, 10, f"Employee ID: {self.slip_data.get('employee_id', 'N/A')}", ln=True)
        self.pdf.cell(
            0, 10, f"Employee Name: {self.slip_data.get('username', 'N/A')}", ln=True)
        self.pdf.cell(
            0, 10, f"Date: {self.slip_data.get('calculation_date', 'N/A')}", ln=True)
        self.pdf.cell(
            0, 10, f"Present Days: {self.slip_data.get('present_days', 0)}/{self.slip_data.get('total_days', 0)}", ln=True)
        self.pdf.ln(10)

    def add_earnings(self):
        self.pdf.cell(0, 10, "EARNINGS", ln=True)
        self.pdf.cell(
            0, 10, f"Proportional Salary: Rs.{self.slip_data.get('proportional_salary', 0):,.2f}", ln=True)
        self.pdf.cell(
            0, 10, f"HRA (10%): Rs.{self.slip_data.get('hra', 0):,.2f}", ln=True)
        self.pdf.cell(
            0, 10, f"DA (8%): Rs.{self.slip_data.get('da', 0):,.2f}", ln=True)
        self.pdf.cell(
            0, 10, f"Medical Insurance: Rs.{self.slip_data.get('medical_insurance', 0):,.2f}", ln=True)
        self.pdf.cell(
            0, 10, f"Transport Allowance (2%): Rs.{self.slip_data.get('transport_allowance', 0):,.2f}", ln=True)
        self.pdf.cell(
            0, 10, f"Bonus (5%): Rs.{self.slip_data.get('bonus', 0):,.2f}", ln=True)
        self.pdf.ln(10)

    def add_deductions(self):
        self.pdf.cell(0, 10, "DEDUCTIONS", ln=True)
        self.pdf.cell(
            0, 10, f"PF (12%): Rs.{self.slip_data.get('pf_deduction', 0):,.2f}", ln=True)
        self.pdf.cell(
            0, 10, f"Tax (15%): Rs.{self.slip_data.get('tax_deduction', 0):,.2f}", ln=True)
        self.pdf.cell(
            0, 10, f"Total Deductions: Rs.{self.slip_data.get('total_deductions', 0):,.2f}", ln=True)
        self.pdf.ln(10)

    def add_net_pay(self):
        self.pdf.set_font("Arial", "B", size=14)
        self.pdf.cell(
            0, 10, f"NET PAY: Rs.{self.slip_data.get('take_home_salary', 0):,.2f}", ln=True)

    def generate(self):
        self.add_header()
        self.add_employee_info()
        self.add_earnings()
        self.add_deductions()
        self.add_net_pay()
        pdf_bytes = self.pdf.output(dest='S').encode('latin1')
        return pdf_bytes


class SlipGeneratorApp:
    """Class to handle the slip generator Streamlit page."""

    def __init__(self):
        self.slip_data = st.session_state.get('salary_slip_data')

    def check_login(self):
        if not st.session_state.get("logged_in"):
            st.switch_page("main.py")

    def show(self):
        self.check_login()
        st.title("SALARY SLIP")

        if not self.slip_data:
            st.error("No salary slip data found. Please calculate salary first.")
            if st.button("Back to Calculator"):
                st.switch_page("pages/salary_calculator.py")
            return

        self.display_slip_info()
        self.display_download_button()

    def display_slip_info(self):
        slip_data = self.slip_data
        st.markdown("---")
        st.subheader("Employee Information")
        st.write(f"**Slip ID:** {slip_data.get('slip_id', 'N/A')}")
        st.write(f"**Employee ID:** {slip_data.get('employee_id', 'N/A')}")
        st.write(f"**Employee Name:** {slip_data.get('username', 'N/A')}")
        st.write(f"**Date:** {slip_data.get('calculation_date', 'N/A')}")
        st.write(
            f"**Present Days:** {slip_data.get('present_days', 0)}/{slip_data.get('total_days', 0)}")
        st.write(f"**Gross Salary:** {slip_data.get('gross_salary', 'N/A')}")
        st.markdown("---")
        st.subheader("EARNINGS")
        st.write(
            f"Proportional Salary: ₹{slip_data.get('proportional_salary', 0):,.2f}")
        st.write(f"HRA (10%): ₹{slip_data.get('hra', 0):,.2f}")
        st.write(f"DA (8%): ₹{slip_data.get('da', 0):,.2f}")
        st.write(
            f"Medical Insurance: ₹{slip_data.get('medical_insurance', 0):,.2f}")
        st.write(
            f"Transport Allowance (2%): ₹{slip_data.get('transport_allowance', 0):,.2f}")
        st.write(f"Bonus (5%): ₹{slip_data.get('bonus', 0):,.2f}")
        st.markdown("---")
        st.subheader("DEDUCTIONS")
        st.write(f"PF (12%): ₹{slip_data.get('pf_deduction', 0):,.2f}")
        st.write(f"Tax (15%): ₹{slip_data.get('tax_deduction', 0):,.2f}")
        st.write(
            f"**Total Deductions: ₹{slip_data.get('total_deductions', 0):,.2f}**")
        st.markdown("---")
        st.markdown(
            f"# **NET PAY: ₹{slip_data.get('take_home_salary', 0):,.2f}**")
        st.markdown("---")

    def display_download_button(self):
        col1, col2 = st.columns(2)
        with col1:
            pdf_generator = SalarySlipPDF(self.slip_data)
            pdf_bytes = pdf_generator.generate()
            st.download_button(
                label="Download Salary Slip as PDF",
                data=pdf_bytes,
                file_name=f"salary_slip_{self.slip_data.get('employee_id', 'unknown')}.pdf",
                mime='application/pdf'
            )
        with col2:
            if st.button("Back to Calculator"):
                st.switch_page("pages/salary_calculator.py")


if __name__ == "__main__":
    app = SlipGeneratorApp()
    app.show()
