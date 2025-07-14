import streamlit as st
from datetime import datetime
import random
import pymysql
from pymysql.cursors import DictCursor


class SlipIDGenerator:
    @staticmethod
    def generate():
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_num = random.randint(1000, 9999)
        return f"SLIP-{timestamp}-{random_num}"


class EmployeeSalary:
    def __init__(self, employee_id, gross_salary, present_days,
                 total_days, username,):
        self.employee_id = employee_id
        self.gross_salary = gross_salary
        self.present_days = present_days
        self.total_days = total_days
        self.username = username
        self.calculation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.slip_id = SlipIDGenerator.generate()

        self.proportional_salary = None
        self.pf = None
        self.hra = None
        self.tax = None
        self.da = None
        self.medical_insurance = 1000  # fixed
        self.transport_allowance = None
        self.bonus = None
        self.attendance_pct = None
        self.total_deductions = None
        self.take_home = None

    def calculate(self):
        self.proportional_salary = (
            self.gross_salary * self.present_days) / self.total_days
        self.pf = self.proportional_salary * 0.12
        self.hra = self.proportional_salary * 0.10
        self.tax = self.proportional_salary * 0.15
        self.da = self.proportional_salary * 0.08
        self.transport_allowance = self.proportional_salary * 0.02
        self.attendance_pct = (self.present_days / self.total_days) * 100
        self.bonus = self.proportional_salary * 0.05 if self.attendance_pct >= 75 else 0
        self.total_deductions = self.pf + self.tax
        self.take_home = self.proportional_salary - self.total_deductions + self.bonus

    def to_dict(self):
        return {
            "slip_id": self.slip_id,
            "employee_id": self.employee_id,
            "username": self.username,
            "calculation_date": self.calculation_date,
            "present_days": self.present_days,
            "total_days": self.total_days,
            "gross_salary": round(self.gross_salary, 2),
            "proportional_salary": round(self.proportional_salary, 2),
            "pf_deduction": round(self.pf, 2),
            "tax_deduction": round(self.tax, 2),
            "hra": round(self.hra, 2),
            "da": round(self.da, 2),
            "medical_insurance": round(self.medical_insurance, 2),
            "transport_allowance": round(self.transport_allowance, 2),
            "bonus": round(self.bonus, 2),
            "attendance_percentage": round(self.attendance_pct, 2),
            "total_deductions": round(self.total_deductions, 2),
            "take_home_salary": round(self.take_home, 2),
        }


class EmployeeDataStorageMySQL:
    def __init__(self, host='localhost', user="root", password='root', database='employee_salary_data_db'):
        self.connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='employee_salary_data_db',
            cursorclass=DictCursor,
            autocommit=True
        )

    def save_employee_data(self, employee_data: dict):
        with self.connection.cursor() as cursor:
            sql = """
            INSERT INTO salary_slips (
                slip_id, employee_id, username, calculation_date,
                present_days, total_days, gross_salary, proportional_salary,
                pf_deduction, tax_deduction, hra, da, medical_insurance,
                transport_allowance, bonus, attendance_percentage,
                total_deductions, take_home_salary
            ) VALUES (
                %(slip_id)s, %(employee_id)s, %(username)s, %(calculation_date)s,
                %(present_days)s, %(total_days)s, %(gross_salary)s, %(proportional_salary)s,
                %(pf_deduction)s, %(tax_deduction)s, %(hra)s, %(da)s, %(medical_insurance)s,
                %(transport_allowance)s, %(bonus)s, %(attendance_percentage)s,
                %(total_deductions)s, %(take_home_salary)s
            )
            """
            cursor.execute(sql, employee_data)

    def close(self):
        self.connection.close()


class SalaryCalculatorApp:
    def __init__(self):
        self.username = st.session_state.get("username", "User")
        self.logged_in = st.session_state.get("logged_in", False)
        self.salary_slip_data = None
        # Initialize MySQL storage (update credentials accordingly)
        self.storage = EmployeeDataStorageMySQL(
            host='localhost',
            user='admin',
            password='password',
            database='employee_salary_data_db'
        )

    def validate_inputs(self, employee_id, gross_salary, present_days, total_days):
        if not employee_id or gross_salary <= 0 or present_days < 0 or total_days <= 0:
            st.error("Please fill all fields correctly!")
            return False
        if present_days > total_days:
            st.error("Present Days cannot be more than Total Working Days!")
            return False
        return True

    def display_salary_breakdown(self, emp_salary: EmployeeSalary):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Salary Breakdown")
            st.write(f"**Slip ID:** {emp_salary.slip_id}")
            st.write(f"**Employee ID:** {emp_salary.employee_id}")
            st.write(
                f"**Present Days:** {emp_salary.present_days}/{emp_salary.total_days}")
            st.write(f"**Gross Salary:** ₹{emp_salary.gross_salary:,.2f}")
            st.write(
                f"**Proportional Salary:** ₹{emp_salary.proportional_salary:,.2f}")
        with col2:
            st.subheader("Allowance & Deduction Breakdown")
            st.write(f"**PF (12%):** -₹{emp_salary.pf:,.2f}")
            st.write(f"**Tax (15%):** -₹{emp_salary.tax:,.2f}")
            st.write(f"**HRA (10%):** +₹{emp_salary.hra:,.2f}")
            st.write(f"**DA (8%):** +₹{emp_salary.da:,.2f}")
            st.write(
                f"**Medical Insurance:** ₹{emp_salary.medical_insurance:,.2f}")
            st.write(
                f"**Transport Allowance (2%):** ₹{emp_salary.transport_allowance:,.2f}")
            st.write(
                f"**Bonus (5% if attendance > 75%):** +₹{emp_salary.bonus:,.2f}")
            st.write("---")
            st.write(
                f"**Total Deductions:** ₹{emp_salary.total_deductions:,.2f}")
        st.markdown("---")
        st.markdown(f"##  **Take Home Salary: ₹{emp_salary.take_home:,.2f}**")

    def display_salary_slip(self, emp_salary: EmployeeSalary):
        with st.expander("View summarized salary slip"):
            st.write(f"""
            **SALARY SLIP**

            Slip ID: {emp_salary.slip_id}
            Employee ID: {emp_salary.employee_id}
            Present Days: {emp_salary.present_days}/{emp_salary.total_days}
            Calculation Date: {emp_salary.calculation_date}

            **EARNINGS:**
            Proportional Salary: ₹{emp_salary.proportional_salary:,.2f}
            HRA: ₹{emp_salary.hra:,.2f}
            DA: ₹{emp_salary.da:,.2f}
            Medical Insurance: ₹{emp_salary.medical_insurance:,.2f}
            Transport Allowance: ₹{emp_salary.transport_allowance:,.2f}
            Bonus: ₹{emp_salary.bonus:,.2f}

            **DEDUCTIONS:**
            PF: ₹{emp_salary.pf:,.2f}
            Tax: ₹{emp_salary.tax:,.2f}
            Total Deductions: ₹{emp_salary.total_deductions:,.2f}

            **NET PAY (Take Home): ₹{emp_salary.take_home:,.2f}
            """)

    def salary_page(self):
        if not self.logged_in:
            st.switch_page("main.py")

        st.title("SALARY CALCULATOR")
        st.write(f"Welcome, {self.username}!")

        with st.form("salary_form"):
            employee_id = st.text_input("Employee ID", placeholder="tan9575vy")
            gross_salary = st.number_input(
                "Gross Salary (₹)", min_value=0.0, step=1000.0, max_value=100000000.0)
            present_days = st.number_input(
                "Present Days", min_value=0, max_value=31, step=1)
            total_days = st.number_input(
                "Total Working Days", min_value=0, max_value=31, step=1, value=30)

            calculate = st.form_submit_button("Calculate Salary")

        if calculate:
            if self.validate_inputs(employee_id, gross_salary, present_days, total_days):
                emp_salary = EmployeeSalary(
                    employee_id, gross_salary, present_days, total_days, self.username)
                emp_salary.calculate()

                # Save to MySQL
                self.storage.save_employee_data(emp_salary.to_dict())
                st.success("Salary Calculated Successfully!")

                self.salary_slip_data = emp_salary.to_dict()
                st.session_state['salary_slip_data'] = self.salary_slip_data

                self.display_salary_breakdown(emp_salary)
                self.display_salary_slip(emp_salary)

        if st.session_state.get('salary_slip_data'):
            if st.button("Print Slip"):
                st.switch_page("pages/slip_generator.py")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Calculate Again"):
                st.rerun()
        with col2:
            if st.button("Logout"):
                st.session_state.clear()
                st.rerun()

    def close(self):
        self.storage.close()


if __name__ == "__main__":
    app = SalaryCalculatorApp()
    app.salary_page()
