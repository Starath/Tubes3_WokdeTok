import mysql.connector
import os

class ATSDatabase:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='ats-database-fareltaza35-4318.b.aivencloud.com',
            user='avnadmin',
            password='AVNS_wk8smk5E9W1DPhrWb3D',
            database='defaultdb',
            port=24585,
        )
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def get_connection(self):
        if not self.conn.is_connected():
            self.conn.reconnect()
        return self.conn
    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ApplicantProfile (
                applicant_id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                date_of_birth DATE,
                address VARCHAR(255),
                phone_number VARCHAR(20)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ApplicationDetail (
                detail_id INT AUTO_INCREMENT PRIMARY KEY,
                applicant_id INT NOT NULL,
                applicant_role VARCHAR(100),
                cv_path TEXT,
                FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id)
            )
        ''')
        self.conn.commit()

    def reset_database(self):
        self.cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
        self.cursor.execute('DROP TABLE IF EXISTS ApplicationDetail')
        self.cursor.execute('DROP TABLE IF EXISTS ApplicantProfile')
        self.cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
        self.conn.commit()


    def add_applicant(self, first_name, last_name, date_of_birth, address, phone_number):
        self.cursor.execute('''
            INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number)
            VALUES (%s, %s, %s, %s, %s)
        ''', (first_name, last_name, date_of_birth, address, phone_number))
        self.conn.commit()

    def get_applicant_id(self, first_name, last_name):
        self.cursor.execute('''
            SELECT applicant_id FROM ApplicantProfile
            WHERE first_name=%s AND last_name=%s
        ''', (first_name, last_name))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_or_create_applicant(self, first_name, last_name, date_of_birth="", address="", phone_number=""):
        applicant_id = self.get_applicant_id(first_name, last_name)
        if not applicant_id:
            self.add_applicant(first_name, last_name, date_of_birth, address, phone_number)
            applicant_id = self.cursor.lastrowid
        return applicant_id

    def add_application(self, applicant_id, applicant_role, cv_path):
        self.cursor.execute('''
            INSERT INTO ApplicationDetail (applicant_id, applicant_role, cv_path)
            VALUES (%s, %s, %s)
        ''', (applicant_id, applicant_role, cv_path))
        self.conn.commit()

    def seed(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        for command in sql_script.split(';'):
            command = command.strip()
            if command:
                try:
                    self.cursor.execute(command)
                except mysql.connector.Error as e:
                    print(f"[!] Error: {e}")
        self.conn.commit()


    def get_all_applicants(self):
        self.cursor.execute('SELECT * FROM ApplicantProfile')
        return self.cursor.fetchall()

    def get_all_applications(self):
        self.cursor.execute('SELECT * FROM ApplicationDetail')
        return self.cursor.fetchall()

    def update_applicant(self, applicant_id, first_name, last_name, date_of_birth, address, phone_number):
        self.cursor.execute('''
            UPDATE ApplicantProfile
            SET first_name=%s, last_name=%s, date_of_birth=%s, address=%s, phone_number=%s
            WHERE applicant_id=%s
        ''', (first_name, last_name, date_of_birth, address, phone_number, applicant_id))
        self.conn.commit()

    def delete_applicant(self, applicant_id):
        self.cursor.execute('DELETE FROM ApplicantProfile WHERE applicant_id=%s', (applicant_id,))
        self.conn.commit()

    def update_application(self, detail_id, applicant_id, applicant_role, cv_path):
        self.cursor.execute('''
            UPDATE ApplicationDetail
            SET applicant_id=%s, applicant_role=%s, cv_path=%s
            WHERE detail_id=%s
        ''', (applicant_id, applicant_role, cv_path, detail_id))
        self.conn.commit()

    def delete_application(self, detail_id):
        self.cursor.execute('DELETE FROM ApplicationDetail WHERE detail_id=%s', (detail_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()

    def clear_data(self):
        self.cursor.execute('DELETE FROM ApplicationDetail')
        self.cursor.execute('DELETE FROM ApplicantProfile')
        self.conn.commit()
